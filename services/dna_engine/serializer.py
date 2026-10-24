"""ScamDNA Serializers.

Transforms complex 8-dimensional ScamDNA and match results into:
1. ConsumerDNAView: Plain-language, privacy-safe, non-technical explanation.
2. AnalystDNAView: Full dimensional breakdown, reason codes, vectors, and audit trace.
"""

from __future__ import annotations

from typing import Any, Dict, List

from packages.schemas.dna import (
    ConsumerDNAView,
    DNADimensionType,
    ScamDNA,
    ScamDNAMatch,
    VariantStatus,
)


class DNASerializer:
    """Serializes ScamDNA and match results for consumer and analyst consumption."""

    @staticmethod
    def serialize_consumer_view(dna: ScamDNA, match: ScamDNAMatch) -> ConsumerDNAView:
        """Produces a clean, privacy-preserving consumer summary without technical jargon."""
        # Top family
        top_fam = "SUSPICIOUS PATTERN"
        if dna.family_hypotheses:
            best_fam = max(dna.family_hypotheses.items(), key=lambda kv: kv[1])[0]
            fam_names = {
                "JOB_TASK": "Part-Time Task Scam",
                "DIGITAL_ARREST": "Law Enforcement / Authority Extortion",
                "INVESTMENT": "High-Return Trading Fraud",
                "KYC_BANK": "Bank & KYC Impersonation Phishing",
                "FAKE_SUPPORT_REFUND": "Fake Customer Support & Refund Scam",
            }
            top_fam = fam_names.get(best_fam, best_fam.replace("_", " ").title())

        # Verdict text
        verdict_labels = {
            VariantStatus.KNOWN_PATTERN: "Confirmed Match to Known Scam Pattern",
            VariantStatus.LIKELY_VARIANT: "High Similarity to Known Scam Pattern",
            VariantStatus.POSSIBLE_VARIANT: "Emerging Pattern with Similar Traits",
            VariantStatus.NOVEL_PATTERN: "Unrecognized / Potential Novel Pattern",
            VariantStatus.INSUFFICIENT_EVIDENCE: "Insufficient Data for Pattern Matching",
        }
        verdict_str = verdict_labels.get(match.variant_status, "Pattern Match Pending")

        # Behavioral traits
        traits = []
        jrn = dna.dimensions.get(DNADimensionType.JOURNEY.value)
        if jrn and jrn.available:
            stages = jrn.features.get("stage_sequence", [])
            if "PLATFORM_MIGRATION" in stages:
                traits.append("Conversation moved from social media to private messaging (WhatsApp/Telegram)")
            if "REWARD_OR_FAKE_PROFIT" in stages:
                traits.append("Small initial profits or rewards offered to build trust")
            if "INITIAL_PAYMENT" in stages or "PAYMENT_ESCALATION" in stages:
                traits.append("Demands for security deposits or escalating VIP payments")
            if "WITHDRAWAL_BLOCK" in stages:
                traits.append("Fund withdrawal restricted citing taxes or clearance requirements")

        tac = dna.dimensions.get(DNADimensionType.TACTIC.value)
        if tac and tac.available:
            tactics = tac.features.get("tactics", [])
            if "AUTHORITY" in tactics:
                traits.append("Caller claimed official police, court, or government authority")
            if "ISOLATION" in tactics or "SECRECY" in tactics:
                traits.append("Instructed to keep communication secret and avoid contacting family")
            if "THREAT" in tactics or "FEAR" in tactics:
                traits.append("Threats of immediate arrest or legal action used to force compliance")

        if not traits:
            traits = ["Multiple behavioral similarities identified in communication structure"]

        # Recommended actions
        action = "PAUSE before proceeding. Independently verify the organization through official public contact directories."
        if match.variant_status in (VariantStatus.KNOWN_PATTERN, VariantStatus.LIKELY_VARIANT):
            action = "DO NOT transfer any funds or share OTPs/passwords. This pattern strongly matches confirmed scams."

        conf_str = "HIGH" if match.match_confidence >= 0.70 else ("MODERATE" if match.match_confidence >= 0.45 else "LOW")

        return ConsumerDNAView(
            incident_id=dna.incident_id,
            summary_headline=f"Pattern Alert: {top_fam}",
            variant_verdict=verdict_str,
            why_it_matches=match.matched_features,
            behavioral_traits=traits[:4],
            recommended_action=action,
            confidence_label=conf_str,
        )

    @staticmethod
    def serialize_analyst_view(dna: ScamDNA, match: Optional[ScamDNAMatch] = None) -> Dict[str, Any]:
        """Produces comprehensive forensic telemetry for fraud analysts."""
        dim_summary = {}
        for k, dim in dna.dimensions.items():
            dim_summary[k] = {
                "available": dim.available,
                "quality": dim.quality.value,
                "confidence": dim.confidence,
                "features": dim.features,
                "evidence_count": len(dim.evidence_ids),
            }

        view = {
            "dna_id": dna.dna_id,
            "schema_version": dna.schema_version,
            "incident_id": dna.incident_id,
            "family_hypotheses": dna.family_hypotheses,
            "overall_quality": dna.quality.value,
            "confidence": dna.confidence,
            "canonical_signature": dna.canonical_signature,
            "available_dimensions": dna.available_dimensions,
            "missing_dimensions": dna.missing_dimensions,
            "dimensions": dim_summary,
            "source_versions": dna.source_versions,
            "created_at": dna.created_at.isoformat(),
        }

        if match:
            view["match_result"] = {
                "match_id": match.match_id,
                "target_dna_id": match.target_dna_id,
                "overall_similarity": match.overall_similarity,
                "match_confidence": match.match_confidence,
                "variant_status": match.variant_status.value,
                "dimension_scores": match.dimension_scores,
                "matched_features": match.matched_features,
                "contradictions": match.contradictions,
                "reason_codes": match.reason_codes,
                "explanation": match.explanation,
            }

        return view
