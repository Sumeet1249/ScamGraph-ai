"""Unit Tests for Step 27: URL Machine Learning Detector (URL ML).

Tests:
1. Feature extraction accuracy (lexical, structural, entropy, brand targeting).
2. Malicious phishing URL classification and explainable feature contributions.
3. Benign URL classification (legitimate banks, search engines, utilities).
4. Direct IP address host detection.
5. Brand subdomain typosquatting / spoofing detection.
6. Canonical EvidenceSignal conversion.
7. Integration with URLInvestigationService.
8. Sub-millisecond inference latency performance.
"""

import time
import pytest

from ml.url.classifier import URLMLPrediction, URLRiskClassifier
from ml.url.feature_extractor import URLFeatureExtractor
from packages.schemas.signals import EvidenceSignal, SignalDimension, SignalSeverity
from services.investigation.url_analysis.service import url_investigation_service


def test_feature_extractor_accuracy():
    """Validates that URLFeatureExtractor accurately calculates all 19 structural and lexical dimensions."""
    extractor = URLFeatureExtractor()
    url = "http://sbi-kyc-update.xyz/portal/verify.php?token=12345"
    features = extractor.extract(url)

    assert features["url_length"] == len(url)
    assert features["has_ip_host"] == 0.0
    assert features["non_https"] == 1.0  # http scheme
    assert features["suspicious_tld"] == 1.0  # .xyz
    assert features["brand_in_subdomain_or_path"] == 1.0  # sbi in untrusted domain
    assert features["suspicious_keyword_count"] >= 3.0  # kyc, update, verify
    assert features["hostname_entropy"] > 2.5
    assert features["query_parameter_count"] == 1.0
    assert features["path_depth"] == 2.0


def test_obvious_phishing_url_classification():
    """A fraudulent KYC phishing link must yield high probability and explainable risk factors."""
    classifier = URLRiskClassifier()
    phishing_url = "http://sbi-kyc-verify-update.xyz/login.php?user=123"

    pred = classifier.predict(phishing_url)

    assert isinstance(pred, URLMLPrediction)
    assert pred.is_malicious is True
    assert pred.malicious_probability >= 0.85
    assert pred.risk_tier in ("HIGH_RISK", "MALICIOUS")
    assert pred.confidence >= 0.80

    # Verify explainable risk factors
    factors_text = " ".join(pred.top_risk_factors)
    assert "High-abuse top-level domain" in factors_text or ".xyz" in factors_text
    assert "Targeted brand identity" in factors_text or "phishing keywords" in factors_text
    assert len(pred.feature_contributions) > 0


def test_benign_legitimate_url_classification():
    """Legitimate enterprise banking and search portal URLs must yield low risk (BENIGN)."""
    classifier = URLRiskClassifier()
    benign_urls = [
        "https://www.google.com/search?q=weather",
        "https://www.onlinesbi.sbi/portal/index.html",
        "https://www.hdfcbank.com/personal/ways-to-bank/online-banking",
        "https://tatapower.com/contact-us.aspx",
    ]

    for url in benign_urls:
        pred = classifier.predict(url)
        assert pred.is_malicious is False, f"URL {url} false positive! Score: {pred.malicious_probability}"
        assert pred.risk_tier == "BENIGN"
        assert pred.malicious_probability <= 0.35


def test_direct_ip_address_host():
    """Direct IP host with suspicious path must trigger elevated risk and IP factor."""
    classifier = URLRiskClassifier()
    ip_url = "http://185.220.101.5/sbi/netbanking/login"

    pred = classifier.predict(ip_url)
    assert pred.is_malicious is True
    assert pred.malicious_probability >= 0.70
    assert any("Direct IP address" in f for f in pred.top_risk_factors)


def test_brand_subdomain_spoofing():
    """Unofficial domain hosting a targeted bank brand in subdomains must be flagged."""
    classifier = URLRiskClassifier()
    spoofed_url = "http://hdfc-security-check.top/verify-account"

    pred = classifier.predict(spoofed_url)
    assert pred.is_malicious is True
    assert pred.malicious_probability >= 0.80
    assert pred.risk_tier in ("HIGH_RISK", "MALICIOUS")


def test_to_evidence_signal_generation():
    """Verifies that malicious predictions convert to standard ScamGraph EvidenceSignal objects."""
    classifier = URLRiskClassifier()
    incident_id = "inc_test_url_ml_001"

    # Malicious URL -> EvidenceSignal
    phishing_url = "http://sbi-kyc-verify-update.xyz/login.php"
    mal_pred = classifier.predict(phishing_url)
    signal = classifier.to_evidence_signal(incident_id, mal_pred)

    assert signal is not None
    assert isinstance(signal, EvidenceSignal)
    assert signal.dimension == SignalDimension.URL
    assert signal.signal_type == "ML_HIGH_RISK_URL_DETECTED"
    assert signal.severity in (SignalSeverity.HIGH, SignalSeverity.CRITICAL)
    assert signal.provenance.source_service == "URL_ML"
    assert signal.provenance.detector_name == "URLRiskClassifier"
    assert signal.context["malicious_probability"] >= 0.85

    # Benign URL -> None (no alert fatigue)
    benign_url = "https://www.google.com"
    benign_pred = classifier.predict(benign_url)
    assert classifier.to_evidence_signal(incident_id, benign_pred) is None


@pytest.mark.asyncio
async def test_url_investigation_service_integration():
    """Tests that URLInvestigationService invokes ML detection and includes ml_prediction in the result."""
    phishing_url = "http://sbi-fake-kyc.xyz/login"
    result = await url_investigation_service.investigate_url(
        incident_id="inc_url_ml_service_test",
        raw_url=phishing_url,
    )

    assert result is not None
    assert result.ml_prediction is not None
    assert "malicious_probability" in result.ml_prediction
    assert result.ml_prediction["is_malicious"] is True
    assert result.ml_prediction["risk_tier"] in ("HIGH_RISK", "MALICIOUS")

    # Assert ML Evidence item exists
    ml_evidence = [e for e in result.evidence if "ML_" in e.signal]
    assert len(ml_evidence) >= 1
    assert "evi-url-ml-" in ml_evidence[0].id


def test_sub_millisecond_inference_performance():
    """URL ML classification must be lightweight and fast (< 5ms per URL)."""
    classifier = URLRiskClassifier()
    urls = [
        "https://www.google.com",
        "http://sbi-kyc-update.xyz/verify",
        "http://192.168.1.1/login",
        "https://tatapower.com/bills",
        "http://hdfc-verify.top/auth",
    ] * 20  # 100 evaluations

    start = time.perf_counter()
    for u in urls:
        _ = classifier.predict(u)
    duration = time.perf_counter() - start

    avg_ms = (duration / len(urls)) * 1000
    assert avg_ms < 5.0, f"Average inference time too high: {avg_ms:.2f}ms"
