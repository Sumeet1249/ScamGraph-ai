"""ScamGraph Evidence Fusion and Risk Engine V1 (Step 13).

Strictly enforces:
1. RISK != CONFIDENCE (Threat Risk Index vs Evidence Confidence).
2. Centralized configuration weights.
3. Deduplication of correlated multi-source evidence (avoids double-counting).
4. Explicit INSUFFICIENT_EVIDENCE handling.
5. Counter-evidence retention and calibrated discounting.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

from services.api.app.domain import (
    Incident,
    Event,
    Evidence,
    PatternMatch,
    GraphCorrelation,
    RiskAssessment,
    RiskLevel,
    ConfidenceLevel,
    EvidenceSource,
    MatchLevel,
)
from services.pattern_engine.matcher.risk_config import (
    THREAT_CATEGORY_POINTS,
    PATTERN_MATCH_AMPLIFICATION,
    COUNTER_EVIDENCE_DISCOUNT_POINTS,
    MIN_SOURCES_FOR_HIGH_CONFIDENCE,
    MIN_SOURCES_FOR_MEDIUM_CONFIDENCE,
    RISK_LEVEL_THRESHOLDS,
)


def categorize_signal(signal: str) -> str:
    """Normalizes fine-grained detector signal names into canonical threat categories.
    
    Only signals that directly indicate suspicious/fraudulent intent map to a threat
    category. Neutral observations (e.g. 'PAYMENT_FIELD_PRESENT' on any legitimate
    e-commerce site, 'LOGIN_FORM_PRESENT', 'CLAIMED_BRAND') return 'UNKNOWN' and are
    excluded from the Threat Risk Index to prevent false positives.
    """
    sig = signal.upper()

    # ── Exclusions: neutral TinyFish observation signals ──
    # These are factual observations present on ANY legitimate payment or login portal.
    # They must NOT contribute to the Threat Risk Index on their own.
    _NEUTRAL_OBSERVATION_SIGNALS = {
        "PAYMENT_FIELD_PRESENT",
        "PAYMENT_IDENTIFIER_OBSERVED",
        "LOGIN_FORM_PRESENT",
        "CLAIMED_BRAND",
        "FINANCIAL_CLAIM",
        "PHONE_OBSERVED",
        "EMAIL_OBSERVED",
        "REDIRECT_OBSERVED",
    }
    if sig in _NEUTRAL_OBSERVATION_SIGNALS:
        return "UNKNOWN"

    if any(k in sig for k in ["IMPERSONAT", "OFFICIAL", "AUTHORITY", "POLICE", "ENFORCEMENT", "EMPLOYMENT", "JOB"]):
        return "IMPERSONATION"
    if any(k in sig for k in ["URGENCY", "FEAR", "THREAT", "CUTOFF", "RETURN", "PROMISE", "LURE", "ARREST", "PENALTY", "ISOLATION", "COERCION"]):
        return "URGENCY"
    if any(k in sig for k in ["OTP", "ONE_TIME_PASSWORD", "OTP_FIELD", "OTP_INPUT"]):
        return "OTP_REQUEST"
    if any(k in sig for k in ["CREDENTIAL", "PASSWORD", "AADHAAR", "PAN", "IDENTITY", "CREDENTIAL_COLLECTION"]):
        return "CREDENTIAL_REQUEST"
    # Only map to PAYMENT_REQUEST for clearly suspicious/fraudulent payment signals
    if any(k in sig for k in [
        "INDIVIDUAL_VPA", "COLLECT_REQUEST", "REGISTRATION_OR_BADGE_FEE",
        "REGISTRATION_FEE", "DEPOSIT", "ESCROW",
        "PAYMENT_REQUEST", "VPA", "FINANCIAL_CONTEXT",
    ]):
        return "PAYMENT_REQUEST"
    if any(k in sig for k in ["SUSPICIOUS_URL", "TYPOSQUAT", "BRAND_TYPOSQUAT", "SUSPICIOUS_TLD", "NEWLY_REGISTERED_DOMAIN", "UNVERIFIED_EMPLOYER_DOMAIN", "UNVERIFIED_DOMAIN"]):
        return "SUSPICIOUS_URL"
    return "UNKNOWN"


def is_counter_evidence(ev: Evidence) -> bool:
    """Identifies established legitimate indicators."""
    sig = ev.signal.upper()
    obs = ev.observation.lower()

    # Guard against negated words (e.g. UNVERIFIED matching VERIFIED, 'no legitimate' matching legitimate)
    if any(k in sig for k in ["UNVERIFIED", "NOT_VERIFIED", "UNREGISTERED"]):
        return False
    if any(neg in obs for neg in ["no legitimate", "not legitimate", "not safe", "unsafe"]):
        return False

    counter_signals = [
        "BENIGN",
        "ESTABLISHED_LONG_TERM",
        "OFFICIAL_MERCHANT_VPA_VERIFIED",
        "SEBI_RBI_REGISTERED",
        "IN_PERSON_STATION_VERIFICATION",
        "OFFICIAL_ENTERPRISE_EMAIL_DOMAIN",
    ]
    return any(k in sig for k in counter_signals)


class RiskEngineV1:
    """Evaluates multi-source evidence fusion to produce explainable RiskAssessment."""

    @staticmethod
    def evaluate(
        incident: Incident,
        events: List[Event],
        evidence_list: List[Evidence],
        pattern_matches: Optional[List[PatternMatch]] = None,
        graph_correlations: Optional[List[GraphCorrelation]] = None,
    ) -> RiskAssessment:
        p_matches = pattern_matches or []
        g_correlations = graph_correlations or []

        # 1. Separate Supporting vs Counter-Evidence
        supporting_evidence = [e for e in evidence_list if not is_counter_evidence(e)]
        counter_evidence = [e for e in evidence_list if is_counter_evidence(e)]

        # 2. Deduplicate Evidence Observations to Prevent Double-Counting
        # Map: category -> highest confidence Evidence item
        deduped_threats: Dict[str, Evidence] = {}
        contributing_evidence_ids: Dict[str, List[str]] = {}

        for ev in supporting_evidence:
            cat = categorize_signal(ev.signal)
            if cat == "UNKNOWN":
                continue
            contributing_evidence_ids.setdefault(cat, []).append(ev.id)
            if cat not in deduped_threats or ev.confidence > deduped_threats[cat].confidence:
                deduped_threats[cat] = ev

        distinct_categories = set(deduped_threats.keys())
        distinct_sources: Set[EvidenceSource] = {e.source for e in supporting_evidence}

        # Check if journey contains an actual payment event
        has_payment_event = any("PAYMENT" in ev.event_type.value for ev in events)

        # 3. Handle INSUFFICIENT_EVIDENCE
        # If fewer than 2 independent threat categories exist and no direct payment intent is present
        if len(distinct_categories) < 2 and not (has_payment_event and "IMPERSONATION" in distinct_categories):
            reason_codes = [
                f"[RC_INSUFFICIENT_DATA] Evidence ID: {e.id} -> Observed '{e.signal}' without corroborating categories."
                for e in supporting_evidence
            ] or ["[RC_NO_THREATS] No corroborated threat indicators observed."]

            return RiskAssessment(
                incident_id=incident.id,
                risk_score=15,
                risk_level=RiskLevel.LOW,
                evidence_confidence=ConfidenceLevel.LOW,
                confidence_level=ConfidenceLevel.LOW,
                reason_codes=reason_codes,
                counter_evidence=[c.signal for c in counter_evidence],
                pattern_matches=p_matches,
                graph_correlations=g_correlations,
                insufficient_evidence=True,
                assessed_at=datetime.now(timezone.utc),
            )

        # 4. Compute Threat Risk Index (0 - 100 Integer)
        # Sum base category points weighted by observation confidence
        accumulated_points = 0.0
        reason_codes: List[str] = []

        for cat, ev in deduped_threats.items():
            base_pts = THREAT_CATEGORY_POINTS.get(cat, 15)
            w_pts = base_pts * ev.confidence
            accumulated_points += w_pts
            e_ids = contributing_evidence_ids.get(cat, [ev.id])
            reason_codes.append(
                f"[RC_{cat}] Evidence ID(s): {', '.join(e_ids)} ({ev.source.value}) -> {ev.observation}"
            )

        # Pattern match amplification
        best_pattern_level = "NONE"
        if p_matches:
            best_pm = max(p_matches, key=lambda p: p.confidence)
            best_pattern_level = best_pm.match_level.value
            amp = PATTERN_MATCH_AMPLIFICATION.get(best_pattern_level, 0)
            accumulated_points += amp
            if amp > 0:
                reason_codes.append(
                    f"[RC_PATTERN_AMPLIFICATION] Pattern '{best_pm.pattern_name}' match level is {best_pattern_level} (+{amp} pts)"
                )

        # Known relationship amplification (e.g. shared graph nodes)
        if g_correlations:
            accumulated_points += THREAT_CATEGORY_POINTS.get("KNOWN_RELATIONSHIP", 10)
            reason_codes.append("[RC_GRAPH_CORRELATION] Correlated shared infrastructure detected across incidents.")

        # Counter-evidence discount
        if counter_evidence:
            discount = len(counter_evidence) * COUNTER_EVIDENCE_DISCOUNT_POINTS
            accumulated_points = max(5.0, accumulated_points - discount)
            for c in counter_evidence:
                reason_codes.append(f"[RC_COUNTER_EVIDENCE] Evidence ID: {c.id} -> {c.observation} (-{COUNTER_EVIDENCE_DISCOUNT_POINTS} pts)")

        final_risk_score = int(round(min(100.0, max(0.0, accumulated_points))))

        # 5. Risk Level Assignment
        if final_risk_score >= RISK_LEVEL_THRESHOLDS["HIGH"]:
            risk_level = RiskLevel.HIGH
        elif final_risk_score >= RISK_LEVEL_THRESHOLDS["MEDIUM"]:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        # 6. Confidence Level Calibration (Measured Independently)
        # Consider number of independent evidence sources and data completeness
        if len(distinct_sources) >= MIN_SOURCES_FOR_HIGH_CONFIDENCE and len(distinct_categories) >= 3:
            conf_level = ConfidenceLevel.HIGH
        elif len(distinct_sources) >= MIN_SOURCES_FOR_MEDIUM_CONFIDENCE and len(distinct_categories) >= 2:
            conf_level = ConfidenceLevel.MEDIUM
        else:
            conf_level = ConfidenceLevel.LOW

        # Special calibration: Strong pattern match with sparse evidence results in elevated risk but LOWER confidence
        if best_pattern_level == "STRONG" and len(distinct_sources) == 1:
            conf_level = ConfidenceLevel.LOW

        return RiskAssessment(
            incident_id=incident.id,
            risk_score=final_risk_score,
            risk_level=risk_level,
            evidence_confidence=conf_level,
            confidence_level=conf_level,
            reason_codes=reason_codes,
            counter_evidence=[c.signal for c in counter_evidence],
            pattern_matches=p_matches,
            graph_correlations=g_correlations,
            insufficient_evidence=False,
            assessed_at=datetime.now(timezone.utc),
        )


# Global instance
risk_engine_v1 = RiskEngineV1()
