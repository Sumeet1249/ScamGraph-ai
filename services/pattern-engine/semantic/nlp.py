"""Multilingual Semantic Signal Extractor.

Harvested from VECTPHISH and Indian scam taxonomy research.
Analyzes English, Hindi, and Hinglish messages for:
- Urgency & coercion cues
- Official entity impersonation
- Unsolicited task/job lures
"""

import re
from typing import Dict, List
from packages.schemas import EvidenceSignal, SignalDimension, SignalSeverity, ProvenanceRecord

# Multilingual pattern dictionaries
URGENCY_PATTERNS = [
    # English
    r"\b(immediately|urgent|within\s+\d+\s+hours?|account\s+blocked|suspended|electricity\s+disconnected|power\s+cutoff)\b",
    r"\b(last\s+warning|final\s+notice|penalty|late\s+fee|disconnect\s+tonight)\b",
    # Hindi / Hinglish
    r"\b(turant|abhee|bijli\s+kat\s+jayegi|light\s+kat\s+di\s+jayegi|aaj\s+raat|sampark\s+kare)\b",
    r"\b(jaldi|khata\s+band|rok\s+diya\s+gaya|dhyan\s+de)\b",
]

IMPERSONATION_PATTERNS = [
    # Utilities & Telecom
    r"\b(electricity\s+officer|electricity\s+department|electricity\s+board|mahavitaran|bescom|tata\s+power|bses|uppcl)\b",
    r"\b(bijli\s+adhikari|bijli\s+vibhag|bijli\s+board|call\s+officer|contact\s+officer)\b",
    # Banking & Gov
    r"\b(sbi\s+kyc|hdfc\s+bank|icici\s+alert|pan\s+card\s+update|aadhaar\s+suspended|income\s+tax\s+refund)\b",
    r"\b(police\s+department|customs\s+officer|courier\s+hold|india\s+post)\b",
]

JOB_LURE_PATTERNS = [
    r"\b(work\s+from\s+home|part[\s-]time\s+job|daily\s+earning|earn\s+\d+00|telegram\s+task|like\s+video)\b",
    r"\b(ghar\s+baithe\s+kamaye|roj\s+kamaye|simple\s+task)\b",
]


class SemanticSignalExtractor:
    """Extracts typed psychological and semantic evidence signals from communication texts."""

    @staticmethod
    def extract_signals(incident_id: str, text: str) -> List[EvidenceSignal]:
        signals: List[EvidenceSignal] = []
        lower_text = text.lower()

        # 1. Detect Urgency & Coercive Pressure
        urgency_matches = []
        for pat in URGENCY_PATTERNS:
            found = re.findall(pat, lower_text)
            if found:
                urgency_matches.extend(found)

        if urgency_matches:
            signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    dimension=SignalDimension.SEMANTIC,
                    signal_type="URGENCY_PRESSURE_DETECTED",
                    severity=SignalSeverity.HIGH,
                    confidence=0.88,
                    weight=1.5,
                    description=f"Message uses high-urgency psychological coercion: '{urgency_matches[0]}'",
                    provenance=ProvenanceRecord(
                        source_service="services/pattern-engine",
                        detector_name="SemanticSignalExtractor",
                        target_artifact=text[:100],
                        raw_evidence={"matched_tokens": urgency_matches[:5]},
                    ),
                )
            )

        # 2. Detect Official Impersonation
        impersonation_matches = []
        for pat in IMPERSONATION_PATTERNS:
            found = re.findall(pat, lower_text)
            if found:
                impersonation_matches.extend(found)

        if impersonation_matches:
            signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    dimension=SignalDimension.SEMANTIC,
                    signal_type="OFFICIAL_ENTITY_IMPERSONATION",
                    severity=SignalSeverity.HIGH,
                    confidence=0.91,
                    weight=1.8,
                    description=f"Sender purports to represent an official or utility entity: '{impersonation_matches[0]}'",
                    provenance=ProvenanceRecord(
                        source_service="services/pattern-engine",
                        detector_name="SemanticSignalExtractor",
                        target_artifact=text[:100],
                        raw_evidence={"claimed_entities": impersonation_matches[:3]},
                    ),
                )
            )

        # 3. Detect Task / Work-From-Home Scam Lures
        job_matches = []
        for pat in JOB_LURE_PATTERNS:
            found = re.findall(pat, lower_text)
            if found:
                job_matches.extend(found)

        if job_matches:
            signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    dimension=SignalDimension.SEMANTIC,
                    signal_type="UNSOLICITED_TASK_JOB_LURE",
                    severity=SignalSeverity.MEDIUM,
                    confidence=0.86,
                    weight=1.4,
                    description="Message offers high-yield / low-effort daily earnings or Telegram review tasks.",
                    provenance=ProvenanceRecord(
                        source_service="services/pattern-engine",
                        detector_name="SemanticSignalExtractor",
                        target_artifact=text[:100],
                        raw_evidence={"matched_lures": job_matches[:3]},
                    ),
                )
            )

        return signals
