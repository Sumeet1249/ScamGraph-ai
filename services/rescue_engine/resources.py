"""Official Reporting Resources Registry for ScamGraph AI (India-First).

Provides verified, official, and tamper-proof contact channels for:
- 1930 National Cyber Financial Fraud Helpline (MHA / I4C)
- National Cyber Crime Reporting Portal (NCRP)
- 24/7 Bank Emergency Fraud Desks (SBI, HDFC, ICICI, Axis, PNB, etc.)
- UPI & Payment Providers (NPCI, PhonePe, Google Pay, Paytm)
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from packages.schemas.rescue import OfficialReportingResource, ReportingResourceType


OFFICIAL_INDIA_RESOURCES: List[OfficialReportingResource] = [
    # 1. 1930 National Cyber Financial Fraud Helpline
    OfficialReportingResource(
        resource_id="res_in_helpline_1930",
        resource_type=ReportingResourceType.NATIONAL_CYBER_FRAUD_HELP,
        jurisdiction="IN",
        organization="Ministry of Home Affairs (I4C)",
        display_name="1930 Citizen Financial Cyber Fraud Helpline",
        official_url="https://cybercrime.gov.in",
        official_phone="1930",
        verification_state="VERIFIED",
        source="MHA_I4C_OFFICIAL",
        last_verified_at=datetime(2026, 10, 1, 0, 0, tzinfo=timezone.utc),
        instructions=[
            "Call 1930 immediately (preferably within the 'Golden Hour' of transaction).",
            "Keep your Bank Name, Account Number, Transaction Date/Time, and UTR/Reference number ready.",
            "Explain that you are reporting an unauthorized/fraudulent payment.",
            "The 1930 system immediately alerts the nodal officers of source and destination banks to freeze the trail."
        ],
        metadata={
            "toll_free": True,
            "availability": "24x7",
            "coverage": "All Indian States & UTs"
        }
    ),
    # 2. National Cyber Crime Reporting Portal (NCRP)
    OfficialReportingResource(
        resource_id="res_in_ncrp_portal",
        resource_type=ReportingResourceType.CYBERCRIME_REPORTING,
        jurisdiction="IN",
        organization="National Cyber Crime Reporting Portal (I4C)",
        display_name="National Cyber Crime Reporting Portal (NCRP)",
        official_url="https://cybercrime.gov.in",
        official_phone=None,
        verification_state="VERIFIED",
        source="MHA_I4C_OFFICIAL",
        last_verified_at=datetime(2026, 10, 1, 0, 0, tzinfo=timezone.utc),
        instructions=[
            "Visit https://cybercrime.gov.in and click on 'Report Cyber Crime'.",
            "Select 'Financial Fraud' or 'Other Cyber Crime' depending on the incident type.",
            "Upload transaction receipts, chat screenshots, suspect phone numbers, and URLs.",
            "Note down the System Acknowledgement Number (Complaint ID) for reference."
        ],
        metadata={
            "portal": "NCRP",
            "official_domain": "gov.in"
        }
    ),
    # 3. State Bank of India (SBI)
    OfficialReportingResource(
        resource_id="res_in_bank_sbi",
        resource_type=ReportingResourceType.BANK_OR_PAYMENT_PROVIDER,
        jurisdiction="IN",
        organization="State Bank of India",
        display_name="SBI 24x7 Cyber Fraud Emergency Desk",
        official_url="https://bank.sbi",
        official_phone="1800111109",
        verification_state="VERIFIED",
        source="RBI_OFFICIAL_DIRECTORY",
        last_verified_at=datetime(2026, 10, 1, 0, 0, tzinfo=timezone.utc),
        instructions=[
            "Call 1800 11 1109 or 1800 1234 to block UPI, Netbanking, and Debit Card immediately.",
            "Provide Account Number and UTR number of the fraudulent debit.",
            "Request immediate flagging and stop-payment alert to the beneficiary bank."
        ],
        metadata={"short_code": "SBI", "alternate_phone": "18004253800"}
    ),
    # 4. HDFC Bank
    OfficialReportingResource(
        resource_id="res_in_bank_hdfc",
        resource_type=ReportingResourceType.BANK_OR_PAYMENT_PROVIDER,
        jurisdiction="IN",
        organization="HDFC Bank",
        display_name="HDFC Bank 24x7 Fraud Hotline",
        official_url="https://www.hdfcbank.com",
        official_phone="18002586161",
        verification_state="VERIFIED",
        source="RBI_OFFICIAL_DIRECTORY",
        last_verified_at=datetime(2026, 10, 1, 0, 0, tzinfo=timezone.utc),
        instructions=[
            "Call 1800 258 6161 immediately to report unauthorized digital transaction.",
            "Lock NetBanking access and block linked cards via phone banking or official app.",
            "Report the transaction reference number and beneficiary VPA/account."
        ],
        metadata={"short_code": "HDFC"}
    ),
    # 5. ICICI Bank
    OfficialReportingResource(
        resource_id="res_in_bank_icici",
        resource_type=ReportingResourceType.BANK_OR_PAYMENT_PROVIDER,
        jurisdiction="IN",
        organization="ICICI Bank",
        display_name="ICICI Bank Fraud Reporting Helpline",
        official_url="https://www.icicibank.com",
        official_phone="18001080",
        verification_state="VERIFIED",
        source="RBI_OFFICIAL_DIRECTORY",
        last_verified_at=datetime(2026, 10, 1, 0, 0, tzinfo=timezone.utc),
        instructions=[
            "Call 1800 1080 to lock iMobile and Netbanking credentials immediately.",
            "Dispute the fraudulent UPI/IMPS debit and note down the service request number."
        ],
        metadata={"short_code": "ICICI"}
    ),
    # 6. Axis Bank
    OfficialReportingResource(
        resource_id="res_in_bank_axis",
        resource_type=ReportingResourceType.BANK_OR_PAYMENT_PROVIDER,
        jurisdiction="IN",
        organization="Axis Bank",
        display_name="Axis Bank Fraud Reporting Desk",
        official_url="https://www.axisbank.com",
        official_phone="18004190068",
        verification_state="VERIFIED",
        source="RBI_OFFICIAL_DIRECTORY",
        last_verified_at=datetime(2026, 10, 1, 0, 0, tzinfo=timezone.utc),
        instructions=[
            "Call 1800 419 0068 to freeze accounts and debit cards against unauthorized transactions."
        ],
        metadata={"short_code": "AXIS"}
    ),
    # 7. Punjab National Bank (PNB)
    OfficialReportingResource(
        resource_id="res_in_bank_pnb",
        resource_type=ReportingResourceType.BANK_OR_PAYMENT_PROVIDER,
        jurisdiction="IN",
        organization="Punjab National Bank",
        display_name="PNB Cyber Fraud Emergency Desk",
        official_url="https://pnbindia.in",
        official_phone="18001802222",
        verification_state="VERIFIED",
        source="RBI_OFFICIAL_DIRECTORY",
        last_verified_at=datetime(2026, 10, 1, 0, 0, tzinfo=timezone.utc),
        instructions=[
            "Call 1800 180 2222 to block digital banking and debit card services."
        ],
        metadata={"short_code": "PNB"}
    ),
    # 8. NPCI UPI Dispute Redressal
    OfficialReportingResource(
        resource_id="res_in_upi_npci",
        resource_type=ReportingResourceType.UPI_PROVIDER,
        jurisdiction="IN",
        organization="National Payments Corporation of India (NPCI)",
        display_name="NPCI UPI Dispute Redressal Portal",
        official_url="https://www.npci.org.in/what-we-do/upi/dispute-redressal-mechanism",
        official_phone=None,
        verification_state="VERIFIED",
        source="NPCI_OFFICIAL",
        last_verified_at=datetime(2026, 10, 1, 0, 0, tzinfo=timezone.utc),
        instructions=[
            "Visit NPCI Dispute Redressal Mechanism portal.",
            "Select 'Transaction' and enter the 12-digit UPI Transaction ID (UTR).",
            "Select Issue: 'Fraudulent Transaction' and submit details."
        ],
        metadata={"network": "UPI"}
    ),
    # 9. PhonePe Fraud Reporting
    OfficialReportingResource(
        resource_id="res_in_upi_phonepe",
        resource_type=ReportingResourceType.UPI_PROVIDER,
        jurisdiction="IN",
        organization="PhonePe",
        display_name="PhonePe Fraud Support Helpline",
        official_url="https://www.phonepe.com/contact-us/",
        official_phone="080-68727374",
        verification_state="VERIFIED",
        source="PHONEPE_OFFICIAL",
        last_verified_at=datetime(2026, 10, 1, 0, 0, tzinfo=timezone.utc),
        instructions=[
            "Call PhonePe helpline at 080-68727374 or use the in-app 'Help' on the specific transaction.",
            "Report fraudulent beneficiary VPA and request transaction dispute."
        ],
        metadata={"short_code": "PHONEPE"}
    ),
    # 10. Google Pay India
    OfficialReportingResource(
        resource_id="res_in_upi_gpay",
        resource_type=ReportingResourceType.UPI_PROVIDER,
        jurisdiction="IN",
        organization="Google Pay India",
        display_name="Google Pay India Support Desk",
        official_url="https://support.google.com/pay/india",
        official_phone="18004190157",
        verification_state="VERIFIED",
        source="GOOGLE_OFFICIAL",
        last_verified_at=datetime(2026, 10, 1, 0, 0, tzinfo=timezone.utc),
        instructions=[
            "Call toll-free 1800 419 0157 or tap the transaction in Google Pay -> 'Having issues' -> 'Report fraud'."
        ],
        metadata={"short_code": "GPAY"}
    ),
    # 11. UIDAI Aadhaar Biometric Lock
    OfficialReportingResource(
        resource_id="res_in_uidai_lock",
        resource_type=ReportingResourceType.ACCOUNT_PROVIDER,
        jurisdiction="IN",
        organization="Unique Identification Authority of India (UIDAI)",
        display_name="UIDAI Aadhaar Biometric Lock / Masking Portal",
        official_url="https://myaadhaar.uidai.gov.in",
        official_phone="1947",
        verification_state="VERIFIED",
        source="UIDAI_OFFICIAL",
        last_verified_at=datetime(2026, 10, 1, 0, 0, tzinfo=timezone.utc),
        instructions=[
            "If Aadhaar image was shared with fraudsters, visit https://myaadhaar.uidai.gov.in.",
            "Log in via OTP and select 'Lock/Unlock Biometrics' to prevent AePS unauthorized withdrawals.",
            "Call 1947 for Aadhaar security assistance."
        ],
        metadata={"category": "IDENTITY_PROTECTION"}
    ),
]


class OfficialReportingResourceRegistry:
    """Registry maintaining verified official reporting channels."""

    def __init__(self, resources: Optional[List[OfficialReportingResource]] = None):
        self._resources: Dict[str, OfficialReportingResource] = {
            r.resource_id: r for r in (resources or OFFICIAL_INDIA_RESOURCES)
        }

    def get_by_id(self, resource_id: str) -> Optional[OfficialReportingResource]:
        return self._resources.get(resource_id)

    def list_all(self, jurisdiction: str = "IN") -> List[OfficialReportingResource]:
        return [r for r in self._resources.values() if r.jurisdiction == jurisdiction]

    def get_national_helpline(self, jurisdiction: str = "IN") -> Optional[OfficialReportingResource]:
        for r in self._resources.values():
            if r.jurisdiction == jurisdiction and r.resource_type == ReportingResourceType.NATIONAL_CYBER_FRAUD_HELP:
                return r
        return None

    def get_cybercrime_portal(self, jurisdiction: str = "IN") -> Optional[OfficialReportingResource]:
        for r in self._resources.values():
            if r.jurisdiction == jurisdiction and r.resource_type == ReportingResourceType.CYBERCRIME_REPORTING:
                return r
        return None

    def find_bank_resource(self, bank_hint: str) -> Optional[OfficialReportingResource]:
        hint = bank_hint.lower().strip()
        for r in self._resources.values():
            if r.resource_type in (ReportingResourceType.BANK_OR_PAYMENT_PROVIDER, ReportingResourceType.UPI_PROVIDER):
                if hint in r.organization.lower() or hint in r.display_name.lower():
                    return r
                short = r.metadata.get("short_code", "").lower()
                if short and short in hint:
                    return r
        return None


# Global singleton instance
official_resources_registry = OfficialReportingResourceRegistry()
