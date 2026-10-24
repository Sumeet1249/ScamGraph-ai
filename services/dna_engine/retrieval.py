"""ScamDNA Candidate Retrieval Index.

Implements two-stage candidate generation to prevent O(N^2) comparison scaling
bottlenecks across large historical incident corpuses.
Stage 1: Inverted index retrieval by family hypothesis, journey prefix, and high-impact tactics.
Stage 2: Detailed 8-dimensional pairwise alignment on top-K candidate set.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

from packages.schemas.dna import (
    DNADimensionType,
    ScamDNA,
    ScamDNAMatch,
)
from services.dna_engine.similarity import ScamDNASimilarityEngine

logger = logging.getLogger("dna_engine.retrieval")


class DNACandidateIndex:
    """In-memory candidate retrieval index for efficient sub-linear DNA matching."""

    def __init__(self, similarity_engine: Optional[ScamDNASimilarityEngine] = None):
        self.similarity_engine = similarity_engine or ScamDNASimilarityEngine()
        self.dnas: Dict[str, ScamDNA] = {}
        
        # Inverted index mappings
        self.family_index: Dict[str, Set[str]] = defaultdict(set)
        self.journey_stage_index: Dict[str, Set[str]] = defaultdict(set)
        self.tactic_index: Dict[str, Set[str]] = defaultdict(set)
        self.channel_index: Dict[str, Set[str]] = defaultdict(set)

    def index_dna(self, dna: ScamDNA) -> None:
        """Indexes a ScamDNA instance across inverted candidate keys."""
        self.dnas[dna.dna_id] = dna

        # 1. Family index
        for fam, conf in dna.family_hypotheses.items():
            if conf >= 0.20:
                self.family_index[fam].add(dna.dna_id)

        # 2. Journey stages index
        jrn_dim = dna.dimensions.get(DNADimensionType.JOURNEY.value)
        if jrn_dim and jrn_dim.available:
            for stg in jrn_dim.features.get("stage_sequence", []):
                self.journey_stage_index[stg].add(dna.dna_id)

        # 3. High-impact tactics index
        tac_dim = dna.dimensions.get(DNADimensionType.TACTIC.value)
        if tac_dim and tac_dim.available:
            for tac in tac_dim.features.get("tactics", []):
                self.tactic_index[tac].add(dna.dna_id)

        # 4. Channels index
        inf_dim = dna.dimensions.get(DNADimensionType.INFRASTRUCTURE.value)
        if inf_dim and inf_dim.available:
            for ch in inf_dim.features.get("channels", []):
                self.channel_index[ch].add(dna.dna_id)

    def retrieve_candidates(self, query_dna: ScamDNA, top_k: int = 50) -> List[ScamDNA]:
        """Stage 1: Fast filtering to retrieve candidate DNA IDs with highest heuristic overlap."""
        candidate_scores: Dict[str, float] = defaultdict(float)

        # Family overlap
        for fam, conf in query_dna.family_hypotheses.items():
            if conf >= 0.20 and fam != "UNKNOWN":
                for did in self.family_index.get(fam, []):
                    if did != query_dna.dna_id:
                        candidate_scores[did] += 2.0 * conf

        # Journey stages overlap
        jrn_dim = query_dna.dimensions.get(DNADimensionType.JOURNEY.value)
        if jrn_dim and jrn_dim.available:
            for stg in jrn_dim.features.get("stage_sequence", []):
                for did in self.journey_stage_index.get(stg, []):
                    if did != query_dna.dna_id:
                        candidate_scores[did] += 1.0

        # Tactic overlap
        tac_dim = query_dna.dimensions.get(DNADimensionType.TACTIC.value)
        if tac_dim and tac_dim.available:
            for tac in tac_dim.features.get("tactics", []):
                for did in self.tactic_index.get(tac, []):
                    if did != query_dna.dna_id:
                        candidate_scores[did] += 1.5

        # Channels overlap
        inf_dim = query_dna.dimensions.get(DNADimensionType.INFRASTRUCTURE.value)
        if inf_dim and inf_dim.available:
            for ch in inf_dim.features.get("channels", []):
                for did in self.channel_index.get(ch, []):
                    if did != query_dna.dna_id:
                        candidate_scores[did] += 0.5

        if not candidate_scores:
            # Fallback: return up to top_k all registered DNAs
            return [d for did, d in list(self.dnas.items())[:top_k] if did != query_dna.dna_id]

        # Rank candidates by heuristic score
        sorted_candidates = sorted(candidate_scores.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
        return [self.dnas[did] for did, _ in sorted_candidates if did in self.dnas]

    def find_similar(self, query_dna: ScamDNA, top_k: int = 5) -> List[ScamDNAMatch]:
        """Two-Stage Matching: Fast retrieval -> Detailed 8-dimensional pairwise comparison."""
        candidates = self.retrieve_candidates(query_dna, top_k=top_k * 5)
        matches: List[ScamDNAMatch] = []

        for cand in candidates:
            match = self.similarity_engine.compare(query_dna, cand)
            matches.append(match)

        # Sort matches by overall similarity descending
        matches.sort(key=lambda m: m.overall_similarity, reverse=True)
        return matches[:top_k]
