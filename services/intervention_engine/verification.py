"""Independent Verification Recommendation Engine (Phase 4B / Prompt 14).

Generates actionable, safe verification plans ensuring the victim never relies
on contact numbers, links, or identities supplied by the suspicious party.
"""

from typing import List, Optional
from packages.schemas.contextual_intervention import VerificationPlan


class VerificationRecommendationEngine:
    """Creates safe independent verification plans tailored to claimed organizational identities."""

    @staticmethod
    def generate_plan(
        claimed_type: str,
        claimed_entity_name: Optional[str] = None,
        suspect_url: Optional[str] = None,
        suspect_phone: Optional[str] = None,
    ) -> VerificationPlan:
        """Constructs an anti-loophole verification plan."""
        normalized_type = (claimed_type or "GENERAL").upper()

        if "BANK" in normalized_type or "KYC" in normalized_type:
            org = claimed_entity_name or "Your Bank"
            return VerificationPlan(
                verification_type="BANK_DIRECT",
                target_type="FINANCIAL_INSTITUTION",
                trusted_source_required="Official Bank Mobile Banking App, debit card backside toll-free number, or physical branch",
                steps=[
                    f"Open the official {org} mobile application directly from your home screen (do not click any message link).",
                    f"Check the account status, KYC notifications, or pending alerts inside the official app.",
                    "If still concerned, call the toll-free number printed directly on the back of your debit card.",
                    "Never call phone numbers sent via SMS or WhatsApp claiming to be 'helpline agents'.",
                ],
                reason=f"Financial institutions maintain secure in-app message centres. Verifying via official app bypasses spoofed SMS sender headers.",
                confidence=0.95,
                metadata={"category": "BANKING", "institution": org},
            )

        if (
            "POLICE" in normalized_type
            or "CBI" in normalized_type
            or "ARREST" in normalized_type
            or "CUSTOMS" in normalized_type
            or "AUTHORITY" in normalized_type
            or "GOVERNMENT" in normalized_type
        ):
            agency = claimed_entity_name or "Law Enforcement / Police"
            return VerificationPlan(
                verification_type="GOVERNMENT_PORTAL",
                target_type="GOVERNMENT_AGENCY",
                trusted_source_required="National Cybercrime Portal (1930 / cybercrime.gov.in) or local police station in person",
                steps=[
                    "Disconnect any active video call or audio session immediately.",
                    "Dial 1930 directly (Ministry of Home Affairs National Cybercrime Helpline).",
                    "Visit your nearest local police station in person and show the summons/notice.",
                    "Remember: Indian law enforcement agencies NEVER conduct arrests, trials, or fines via Skype or WhatsApp video.",
                ],
                reason="Indian police and courts issue physical summons or judicial notices; they never demand money transfers or video isolation.",
                confidence=0.98,
                metadata={"category": "LAW_ENFORCEMENT", "agency": agency},
            )

        if (
            "JOB" in normalized_type
            or "TASK" in normalized_type
            or "RECRUITMENT" in normalized_type
            or "REWARD" in normalized_type
            or "FAKE_REWARD" in normalized_type
        ):
            company = claimed_entity_name or "Claimed Employer"
            return VerificationPlan(
                verification_type="EMPLOYER_HR",
                target_type="EMPLOYER",
                trusted_source_required="Official corporate career portal (e.g., https://company.com/careers) and verified corporate LinkedIn",
                steps=[
                    f"Visit the official website of {company} by typing the domain name manually in your browser.",
                    "Check the Careers or Job Openings section for matching requisition IDs.",
                    "Verify recruiter authenticity by writing directly to official corporate email addresses (@company.com, not @gmail.com).",
                    "Never pay fees for 'interview security', 'task enrollment', or 'prepaid VIP deposits'.",
                ],
                reason="Legitimate multi-national corporations operate institutional recruiting portals and never hire or pay through Telegram groups.",
                confidence=0.92,
                metadata={"category": "EMPLOYMENT", "company": company},
            )

        if "COURIER" in normalized_type or "PARCEL" in normalized_type or "DELIVERY" in normalized_type:
            courier = claimed_entity_name or "Logistics / Postal Service"
            return VerificationPlan(
                verification_type="COURIER_DIRECT",
                target_type="MARKETPLACE",
                trusted_source_required="Official logistics tracking portal (e.g., indiapost.gov.in, bluedart.com) using your known tracking ID",
                steps=[
                    f"Manually open the official website or app of {courier}.",
                    "Type your known consignment tracking number directly into the official tracker.",
                    "Never click SMS links claiming 'address update failed' or 'pay ₹5 fee to deliver'.",
                ],
                reason="Parcel delivery scams use address update phishing forms to harvest banking credentials or induce small fee transfers.",
                confidence=0.90,
                metadata={"category": "LOGISTICS", "provider": courier},
            )

        # Default General Verification Plan
        return VerificationPlan(
            verification_type="GENERAL_INDEPENDENT",
            target_type="ORGANIZATION",
            trusted_source_required="Official domain manually typed into browser or verified search directory",
            steps=[
                "Do not use any phone numbers, email addresses, or links contained in the message.",
                "Search for the organization's verified official portal on the web manually.",
                "Contact customer service using only the contact information published on their official domain.",
                "Consult a trusted family member or peer before transferring funds or entering credentials.",
            ],
            reason="Independent verification breaks the attacker's communication loop and exposes impersonation.",
            confidence=0.85,
            metadata={"category": "GENERAL"},
        )


verification_recommendation_engine = VerificationRecommendationEngine()
