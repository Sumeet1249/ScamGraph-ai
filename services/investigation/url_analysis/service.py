"""Unified URL Investigation Service (Step 16).

Coordinates URL normalization, SSRF protection, lexical feature extraction,
DNS resolution, RDAP lookups, TLS inspections, and safe redirect following.
Produces canonical Evidence and Entity collections with partial-failure tolerance.
"""

from datetime import datetime, timezone
import time
from typing import List, Optional
from uuid import uuid4

from services.api.app.domain.enums import EntityType, EvidenceSource
from services.api.app.domain.models import Entity, Evidence
from services.investigation.url_analysis.dns_analyzer import DNSAnalyzer
from services.investigation.url_analysis.lexical import LexicalAnalyzer
from services.investigation.url_analysis.models import (
    NormalizedURL,
    SafetyResult,
    URLFeatureSet,
    URLInvestigationResult,
)
from services.investigation.url_analysis.normalizer import URLNormalizationError, URLNormalizer
from services.investigation.url_analysis.rdap_analyzer import RDAPAnalyzer
from services.investigation.url_analysis.redirect_analyzer import RedirectAnalyzer
from services.investigation.url_analysis.safety import URLSafetyValidator
from services.investigation.url_analysis.tls_analyzer import TLSAnalyzer


class URLInvestigationService:
    """Orchestrates comprehensive, resilient infrastructure intelligence on URLs."""

    def __init__(
        self,
        dns: Optional[DNSAnalyzer] = None,
        rdap: Optional[RDAPAnalyzer] = None,
        tls: Optional[TLSAnalyzer] = None,
        redirect: Optional[RedirectAnalyzer] = None,
    ):
        self.dns_analyzer = dns or DNSAnalyzer()
        self.rdap_analyzer = rdap or RDAPAnalyzer()
        self.tls_analyzer = tls or TLSAnalyzer()
        self.redirect_analyzer = redirect or RedirectAnalyzer()

    async def investigate_url(
        self,
        incident_id: str,
        raw_url: str,
    ) -> URLInvestigationResult:
        """Executes full multi-layer URL investigation pipeline."""
        start_time = time.perf_counter()
        inv_id = f"inv-url-{uuid4().hex[:8]}"
        all_evidence: List[Evidence] = []
        all_entities: List[Entity] = []
        all_errors: List[str] = []

        # 1. Normalize URL
        try:
            norm_url = URLNormalizer.normalize(raw_url)
        except URLNormalizationError as e:
            duration = (time.perf_counter() - start_time) * 1000
            return URLInvestigationResult(
                investigation_id=inv_id,
                status="rejected",
                safety=SafetyResult(is_safe=False, reasons=[str(e)]),
                errors=[f"Normalization error: {e}"],
                duration_ms=round(duration, 2),
            )

        # 2. SSRF & Safety Validation
        safety = URLSafetyValidator.validate_url(norm_url)
        if not safety.is_safe:
            duration = (time.perf_counter() - start_time) * 1000
            return URLInvestigationResult(
                investigation_id=inv_id,
                status="rejected",
                normalized_url=norm_url,
                safety=safety,
                errors=safety.reasons,
                duration_ms=round(duration, 2),
            )

        # Automatically extract canonical URL and Domain entities
        all_entities.append(
            Entity(
                id=f"ent-url-{uuid4().hex[:8]}",
                entity_type=EntityType.URL,
                normalized_value=norm_url.normalized_url.lower(),
                display_value=norm_url.normalized_url,
            )
        )
        if norm_url.registered_domain:
            all_entities.append(
                Entity(
                    id=f"ent-dom-{uuid4().hex[:8]}",
                    entity_type=EntityType.DOMAIN,
                    normalized_value=norm_url.registered_domain.lower(),
                    display_value=norm_url.registered_domain,
                )
            )

        # 3. Lexical URL Features
        try:
            features = LexicalAnalyzer.extract_features(norm_url)
            lex_evidence = LexicalAnalyzer.generate_evidence(incident_id, norm_url, features)
            all_evidence.extend(lex_evidence)
        except Exception as e:
            features = None
            all_errors.append(f"Lexical analysis error: {e}")

        # 4. DNS Resolution
        try:
            dns_ev, dns_ent, dns_err = self.dns_analyzer.analyze(incident_id, norm_url)
            all_evidence.extend(dns_ev)
            all_entities.extend(dns_ent)
            all_errors.extend(dns_err)
        except Exception as e:
            all_errors.append(f"DNS analyzer exception: {e}")

        # 5. RDAP Domain Registration Intelligence
        try:
            rdap_ev, rdap_ent, rdap_err = await self.rdap_analyzer.analyze(incident_id, norm_url)
            all_evidence.extend(rdap_ev)
            all_entities.extend(rdap_ent)
            all_errors.extend(rdap_err)
        except Exception as e:
            all_errors.append(f"RDAP analyzer exception: {e}")

        # 6. TLS Certificate Inspection
        try:
            tls_ev, tls_ent, tls_err = self.tls_analyzer.analyze(incident_id, norm_url)
            all_evidence.extend(tls_ev)
            all_entities.extend(tls_ent)
            all_errors.extend(tls_err)
        except Exception as e:
            all_errors.append(f"TLS analyzer exception: {e}")

        # 7. Safe Redirect Following
        try:
            redir_ev, redir_hops, redir_err = await self.redirect_analyzer.analyze(incident_id, norm_url)
            all_evidence.extend(redir_ev)
            all_errors.extend(redir_err)
        except Exception as e:
            all_errors.append(f"Redirect analyzer exception: {e}")

        # 8. URL Machine Learning Risk Classification (Step 27)
        ml_prediction_dict = None
        try:
            from ml.url.classifier import URLRiskClassifier
            ml_classifier = URLRiskClassifier()
            ml_pred = ml_classifier.predict(norm_url.normalized_url)
            ml_prediction_dict = ml_pred.model_dump()

            if ml_pred.is_malicious or ml_pred.risk_tier in ("HIGH_RISK", "MALICIOUS", "SUSPICIOUS"):
                all_evidence.append(
                    Evidence(
                        id=f"evi-url-ml-{uuid4().hex[:8]}",
                        incident_id=incident_id,
                        source=EvidenceSource.URL_ANALYZER,
                        signal="ML_HIGH_RISK_URL_DETECTED" if ml_pred.is_malicious else "ML_SUSPICIOUS_URL_DETECTED",
                        observation=f"ML URL analysis evaluated {ml_pred.malicious_probability*100:.1f}% risk score ({ml_pred.risk_tier}). Primary factors: {', '.join(ml_pred.top_risk_factors[:2])}",
                        confidence=ml_pred.confidence,
                        timestamp=datetime.now(timezone.utc),
                        metadata=ml_prediction_dict,
                    )
                )
        except Exception as e:
            all_errors.append(f"URL ML classifier exception: {e}")

        duration = (time.perf_counter() - start_time) * 1000
        partial = len(all_errors) > 0 and len(all_evidence) > 0
        status = "partial" if partial else ("failed" if not all_evidence and all_errors else "completed")

        return URLInvestigationResult(
            investigation_id=inv_id,
            status=status,
            normalized_url=norm_url,
            safety=safety,
            features=features,
            entities=all_entities,
            evidence=all_evidence,
            errors=all_errors,
            partial_results=partial,
            duration_ms=round(duration, 2),
            ml_prediction=ml_prediction_dict,
        )


# Global instance
url_investigation_service = URLInvestigationService()
