"""Multi-Source Candidate Retriever (Phase 3B - Sections 9-12, 68-73).

Implements Stage 1 candidate generation across:
1. Exact & normalized entity overlap (UPI, Phone, Domain, Telegram)
2. ScamDNA candidate indexing
3. Journey family & stage sequence neighbors
4. Temporal window neighborhood
Deduplicates candidate incidents and bounds evaluation budgets to avoid O(N^2) scaling.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
from packages.schemas.correlation import CandidateIncident
from services.correlation_engine.config import CorrelationConfig
from services.dna_engine.retrieval import DNACandidateIndex

logger = logging.getLogger("correlation_engine.retriever")


class CandidateRetriever:
    """Discovers promising incident candidates for deep correlation scoring."""

    def __init__(
        self,
        config: Optional[CorrelationConfig] = None,
        dna_index: Optional[DNACandidateIndex] = None,
    ):
        self.config = config or CorrelationConfig.load()
        self.dna_index = dna_index or DNACandidateIndex()

        # In-memory entity inverted index: canonical_id -> Set[incident_id]
        self._entity_index: Dict[str, Set[str]] = {}
        # Inverted index for scam family: family -> Set[incident_id]
        self._family_index: Dict[str, Set[str]] = {}
        # Incident observation timestamps: incident_id -> datetime
        self._incident_timestamps: Dict[str, datetime] = {}
        # Incident metadata cache: incident_id -> Dict[str, Any]
        self._incident_cache: Dict[str, Dict[str, Any]] = {}

    def index_incident(
        self,
        incident_id: str,
        entities: Optional[List[Dict[str, Any]]] = None,
        scam_family: Optional[str] = None,
        observed_at: Optional[datetime] = None,
        dna_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Indexes an incident into candidate retrieval lookup tables."""
        ts = observed_at or datetime.now(timezone.utc)
        self._incident_timestamps[incident_id] = ts
        self._incident_cache[incident_id] = {
            "incident_id": incident_id,
            "scam_family": scam_family or "UNKNOWN",
            "observed_at": ts,
            "dna_id": dna_id,
            "entities": entities or [],
            "metadata": metadata or {},
        }

        # Index canonical entities
        for ent in (entities or []):
            val = ent.get("canonical_value") or ent.get("value") or ent.get("entity_id")
            ent_type = ent.get("entity_type", "UNKNOWN")
            if val and ent_type != "PLATFORM":
                val_clean = str(val).strip().lower()
                self._entity_index.setdefault(val_clean, set()).add(incident_id)

        # Index family
        if scam_family:
            self._family_index.setdefault(scam_family.upper(), set()).add(incident_id)

    def retrieve_candidates(
        self,
        source_incident_id: str,
        source_entities: Optional[List[Dict[str, Any]]] = None,
        source_family: Optional[str] = None,
        source_dna_id: Optional[str] = None,
        observed_at: Optional[datetime] = None,
    ) -> List[CandidateIncident]:
        """Retrieves and deduplicates candidates from multiple independent retrieval channels."""
        candidates: Dict[str, CandidateIncident] = {}
        src_ts = observed_at or self._incident_timestamps.get(source_incident_id, datetime.now(timezone.utc))

        # ---------------------------------------------------------------------
        # Channel 1: Exact / Normalized Entity Overlap
        # ---------------------------------------------------------------------
        ent_candidates = 0
        for ent in (source_entities or []):
            val = ent.get("canonical_value") or ent.get("value") or ent.get("entity_id")
            ent_type = ent.get("entity_type", "UNKNOWN")
            if not val or ent_type == "PLATFORM":
                continue

            val_str = str(val).strip()
            val_clean = val_str.lower()
            val_upper = val_str.upper()

            # Ignore generic brand super-nodes and common CDNs in initial retrieval
            if val_upper in self.config.generic_brands or val_clean in self.config.common_infrastructure_domains:
                continue

            matched_incidents = self._entity_index.get(val_clean, set())
            for inc_id in matched_incidents:
                if inc_id == source_incident_id:
                    continue
                if inc_id not in candidates:
                    candidates[inc_id] = CandidateIncident(
                        incident_id=inc_id,
                        source_reasons=[f"SHARED_ENTITY({ent_type}:{val_clean})"],
                        retrieval_score=0.85,
                        shared_identifiers=[val_clean],
                        observed_at=self._incident_timestamps.get(inc_id),
                    )
                else:
                    candidates[inc_id].source_reasons.append(f"SHARED_ENTITY({ent_type}:{val_clean})")
                    candidates[inc_id].shared_identifiers.append(val_clean)
                    candidates[inc_id].retrieval_score = min(1.0, candidates[inc_id].retrieval_score + 0.15)

                ent_candidates += 1
                if ent_candidates >= self.config.max_candidates_per_source:
                    break

        # ---------------------------------------------------------------------
        # Channel 2: ScamDNA Candidate Retrieval
        # ---------------------------------------------------------------------
        if source_dna_id:
            dna_matches = self.dna_index.find_candidates(
                query_dna_id=source_dna_id,
                query_family=source_family,
                max_results=self.config.max_candidates_per_source,
            )
            for d_id, match_score in dna_matches:
                # Find which incident owns this DNA
                for inc_id, cached in self._incident_cache.items():
                    if cached.get("dna_id") == d_id and inc_id != source_incident_id:
                        if inc_id not in candidates:
                            candidates[inc_id] = CandidateIncident(
                                incident_id=inc_id,
                                source_reasons=[f"SCAM_DNA_NEIGHBOR(score={round(match_score, 2)})"],
                                retrieval_score=match_score,
                                dna_id=d_id,
                                scam_family=cached.get("scam_family"),
                                observed_at=cached.get("observed_at"),
                            )
                        else:
                            candidates[inc_id].source_reasons.append(f"SCAM_DNA_NEIGHBOR(score={round(match_score, 2)})")
                            candidates[inc_id].retrieval_score = max(candidates[inc_id].retrieval_score, match_score)
                        break

        # ---------------------------------------------------------------------
        # Channel 3: Family & Temporal Neighborhood
        # ---------------------------------------------------------------------
        if source_family and source_family.upper() != "UNKNOWN":
            fam_incidents = self._family_index.get(source_family.upper(), set())
            for inc_id in list(fam_incidents)[: self.config.max_candidates_per_source]:
                if inc_id == source_incident_id:
                    continue
                inc_ts = self._incident_timestamps.get(inc_id, src_ts)
                days_diff = abs((src_ts - inc_ts).total_seconds()) / 86400.0

                if days_diff <= self.config.time_window_days:
                    if inc_id not in candidates:
                        candidates[inc_id] = CandidateIncident(
                            incident_id=inc_id,
                            source_reasons=[f"TEMPORAL_FAMILY_NEIGHBOR({source_family}, {round(days_diff, 1)}d)"],
                            retrieval_score=0.45,
                            scam_family=source_family,
                            observed_at=inc_ts,
                        )
                    else:
                        candidates[inc_id].source_reasons.append(f"TEMPORAL_FAMILY_NEIGHBOR({round(days_diff, 1)}d)")

        # Sort candidates by retrieval score descending and apply budget cap
        sorted_candidates = sorted(candidates.values(), key=lambda c: c.retrieval_score, reverse=True)
        return sorted_candidates[: self.config.max_total_candidates]
