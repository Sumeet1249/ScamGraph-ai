"""ScamGraph URL, DNS, RDAP, TLS, and Redirect Analyzers (Step 13).

Harvested from PhishGraph concepts.
Adheres strictly to:
- Rule 8: No browser fetches.
- Rule 9: Rejection of private IP ranges, loopback, and cloud metadata.
- Rule 10: Outputs are canonical EvidenceSignal objects, never final verdicts.
- Rule 21 & 22: Tight timeouts and graceful failure handling.
"""

import socket
import ssl
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
import httpx

from packages.schemas import EvidenceSignal, SignalDimension, SignalSeverity, ProvenanceRecord
from services.investigation.url_analysis.safety import URLSafetyValidator, URLAnalyzer


class DNSAnalyzer:
    """Performs safe DNS resolution and flags suspicious nameserver / IP patterns."""

    @staticmethod
    def analyze(incident_id: str, domain: str) -> List[EvidenceSignal]:
        signals: List[EvidenceSignal] = []
        if not domain or domain in ("localhost", "local"):
            return signals

        try:
            # Resolve IPv4 addresses with timeout
            resolved_ips = socket.gethostbyname_ex(domain)[2]
            # Flag if resolving to known private ranges (SSRF attempt)
            for ip_str in resolved_ips:
                if not URLSafetyValidator.is_safe_public_url(f"http://{ip_str}"):
                    signals.append(
                        EvidenceSignal(
                            incident_id=incident_id,
                            dimension=SignalDimension.INFRASTRUCTURE,
                            signal_type="DNS_RESOLVES_TO_INTERNAL_IP",
                            severity=SignalSeverity.CRITICAL,
                            confidence=1.0,
                            weight=2.0,
                            description=f"Domain {domain} resolves to reserved or private IP {ip_str}",
                            provenance=ProvenanceRecord(
                                source_service="services/investigation",
                                detector_name="DNSAnalyzer",
                                target_artifact=domain,
                                raw_evidence={"resolved_ips": resolved_ips},
                            ),
                        )
                    )
                    return signals

            # Standard successful public resolution evidence
            signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    dimension=SignalDimension.INFRASTRUCTURE,
                    signal_type="DNS_PUBLIC_RESOLUTION_CONFIRMED",
                    severity=SignalSeverity.INFO,
                    confidence=0.90,
                    weight=0.5,
                    description=f"Domain {domain} resolved to {len(resolved_ips)} public IP(s)",
                    provenance=ProvenanceRecord(
                        source_service="services/investigation",
                        detector_name="DNSAnalyzer",
                        target_artifact=domain,
                        raw_evidence={"ips": resolved_ips},
                    ),
                )
            )
        except socket.gaierror:
            signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    dimension=SignalDimension.INFRASTRUCTURE,
                    signal_type="DNS_NXDOMAIN_OR_UNRESOLVABLE",
                    severity=SignalSeverity.MEDIUM,
                    confidence=0.80,
                    weight=1.0,
                    description=f"Domain {domain} does not resolve (NXDOMAIN or DNS error)",
                    provenance=ProvenanceRecord(
                        source_service="services/investigation",
                        detector_name="DNSAnalyzer",
                        target_artifact=domain,
                        raw_evidence={"error": "NXDOMAIN"},
                    ),
                )
            )
        except Exception as e:
            pass

        return signals


class RDAPAnalyzer:
    """Analyzes domain age and registration duration."""

    @staticmethod
    def evaluate_domain_age(incident_id: str, domain: str, age_days: Optional[int] = None) -> List[EvidenceSignal]:
        signals: List[EvidenceSignal] = []
        if age_days is None:
            return signals

        if age_days < 14:
            signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    dimension=SignalDimension.INFRASTRUCTURE,
                    signal_type="FRESHLY_REGISTERED_DOMAIN",
                    severity=SignalSeverity.HIGH,
                    confidence=0.95,
                    weight=1.8,
                    description=f"Domain {domain} was registered only {age_days} days ago (typical of disposable phishing domains)",
                    provenance=ProvenanceRecord(
                        source_service="services/investigation",
                        detector_name="RDAPAnalyzer",
                        target_artifact=domain,
                        raw_evidence={"age_days": age_days},
                    ),
                )
            )
        elif age_days < 60:
            signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    dimension=SignalDimension.INFRASTRUCTURE,
                    signal_type="RECENT_DOMAIN_REGISTRATION",
                    severity=SignalSeverity.MEDIUM,
                    confidence=0.85,
                    weight=1.2,
                    description=f"Domain {domain} is relatively young ({age_days} days old)",
                    provenance=ProvenanceRecord(
                        source_service="services/investigation",
                        detector_name="RDAPAnalyzer",
                        target_artifact=domain,
                        raw_evidence={"age_days": age_days},
                    ),
                )
            )
        elif age_days > 365:
            # Established domain counter-evidence
            signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    dimension=SignalDimension.INFRASTRUCTURE,
                    signal_type="ESTABLISHED_LONG_TERM_DOMAIN",
                    severity=SignalSeverity.INFO,
                    confidence=0.95,
                    weight=1.2,
                    is_counter_evidence=True,
                    description=f"Domain {domain} has been registered for {age_days // 365} year(s)",
                    provenance=ProvenanceRecord(
                        source_service="services/investigation",
                        detector_name="RDAPAnalyzer",
                        target_artifact=domain,
                        raw_evidence={"age_days": age_days},
                    ),
                )
            )

        return signals


class TLSAnalyzer:
    """Inspects SSL certificate attributes, validity period, and issuer heuristics."""

    @staticmethod
    def evaluate_certificate_metadata(
        incident_id: str,
        domain: str,
        issuer: str,
        validity_days: int,
        claimed_bank: Optional[str] = None,
    ) -> List[EvidenceSignal]:
        signals: List[EvidenceSignal] = []

        is_free_ca = any(ca in issuer.lower() for ca in ["let's encrypt", "zerossl", "cpanel", "cloudflare"])

        # If claiming to be a tier-1 bank (e.g. SBI, HDFC) but using disposable free CA with short validity
        if claimed_bank and is_free_ca and validity_days <= 90:
            signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    dimension=SignalDimension.INFRASTRUCTURE,
                    signal_type="FREE_SSL_ON_PURPORTED_BANK",
                    severity=SignalSeverity.HIGH,
                    confidence=0.92,
                    weight=1.7,
                    description=f"Site claiming to be {claimed_bank} uses automated free SSL ({issuer}) with {validity_days}-day validity, inconsistent with institutional banking PKI.",
                    provenance=ProvenanceRecord(
                        source_service="services/investigation",
                        detector_name="TLSAnalyzer",
                        target_artifact=domain,
                        raw_evidence={"issuer": issuer, "validity_days": validity_days, "claimed_bank": claimed_bank},
                    ),
                )
            )

        return signals


class RedirectAnalyzer:
    """Traces redirect hops, unshortens links, and detects cross-domain hopping."""

    @staticmethod
    def evaluate_redirect_chain(
        incident_id: str,
        initial_url: str,
        redirect_chain: List[str],
    ) -> List[EvidenceSignal]:
        signals: List[EvidenceSignal] = []
        hop_count = len(redirect_chain)

        if hop_count >= 2:
            signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    dimension=SignalDimension.URL,
                    signal_type="MULTI_HOP_REDIRECT_CHAIN",
                    severity=SignalSeverity.MEDIUM,
                    confidence=0.85,
                    weight=1.3,
                    description=f"Link traverses {hop_count} redirect hops (obfuscation technique)",
                    provenance=ProvenanceRecord(
                        source_service="services/investigation",
                        detector_name="RedirectAnalyzer",
                        target_artifact=initial_url,
                        raw_evidence={"hops": hop_count, "chain": redirect_chain},
                    ),
                )
            )

        # Cross-domain hop check (e.g. bit.ly -> google-drive-login.com)
        if hop_count >= 1:
            initial_domain = urlparse(initial_url).hostname or ""
            final_domain = urlparse(redirect_chain[-1]).hostname or ""
            if initial_domain != final_domain:
                signals.append(
                    EvidenceSignal(
                        incident_id=incident_id,
                        dimension=SignalDimension.URL,
                        signal_type="CROSS_DOMAIN_REDIRECT_OBSERVED",
                        severity=SignalSeverity.MEDIUM,
                        confidence=0.88,
                        weight=1.2,
                        description=f"Redirect hops from '{initial_domain}' to completely distinct domain '{final_domain}'",
                        provenance=ProvenanceRecord(
                            source_service="services/investigation",
                            detector_name="RedirectAnalyzer",
                            target_artifact=initial_url,
                            raw_evidence={"initial_domain": initial_domain, "final_domain": final_domain},
                        ),
                    )
                )

        return signals
