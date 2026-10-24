"""Investigation endpoint for ad-hoc analysis of Messages, URLs, and Payment/QR data."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status, Response
try:
    from services.api.app.core.config import settings
except ImportError:
    from app.core.config import settings
from pydantic import BaseModel, Field

from packages.schemas import (
    EvidenceSignal,
    SignalDimension,
    SignalSeverity,
    ProvenanceRecord,
    AssessmentResult,
    RiskLevel,
    EvidenceConfidence,
)
from services.investigation.url_analysis.safety import URLAnalyzer
from services.pattern_engine.semantic.nlp import SemanticSignalExtractor
from services.pattern_engine.patterns.scam_patterns import PatternMatcher
from services.pattern_engine.matcher.risk_engine import RiskEngine, RiskAssessment
from services.graph_engine.correlation.entity_service import EntityCorrelationService, EntityCorrelationReport

from datetime import datetime, timezone
from uuid import uuid4

router = APIRouter()


class InvestigateRequest(BaseModel):
    message_text: Optional[str] = Field(None, description="Raw SMS, WhatsApp, or email text")
    url: Optional[str] = Field(None, description="Suspicious URL or link")
    vpa: Optional[str] = Field(None, description="UPI VPA (e.g. merchant@upi or individual@okaxis)")
    qr_payload: Optional[str] = Field(None, description="Scanned UPI QR code data (upi://pay?...)")
    sender_phone: Optional[str] = Field(None, description="Sender phone number")


class InvestigateResponse(BaseModel):
    incident_id: str
    analyzed_at: datetime
    signals: List[EvidenceSignal]
    assessment: RiskAssessment
    pattern_match: Optional[Dict[str, Any]] = None
    graph_correlation: Optional[Dict[str, Any]] = None
    unified_assessment: Optional[Dict[str, Any]] = None
    tripartite_decision: Optional[Dict[str, Any]] = None
    contextual_intervention: Optional[Dict[str, Any]] = None
    multilingual_text: Optional[Dict[str, Any]] = None
    is_simulated: bool = False  # Set true if using DEMO_MODE or mock data



@router.post("", response_model=InvestigateResponse)
async def investigate_target(req: InvestigateRequest, response: Response):
    """Deep inspection of message content, web URL safety, and payment destination."""
    inc_id = f"inv_{uuid4().hex[:10]}"
    signals: List[EvidenceSignal] = []
    is_simulated = settings.DEMO_MODE
    multilingual_dict = None

    # Set X-Simulate header for client-side transparency
    if is_simulated:
        response.headers["X-Simulate"] = "true"

    # 1. Semantic Message Analysis & Multilingual Intelligence (Phase 5C)
    if req.message_text:
        try:
            from services.language_intelligence.service import language_intelligence_service
            multi_rep = language_intelligence_service.analyze_text(req.message_text)
            multilingual_dict = multi_rep.model_dump()
            feat = language_intelligence_service.extract_behavioral_features(req.message_text)

            if feat.protective_negation_present:
                signals.append(
                    EvidenceSignal(
                        incident_id=inc_id,
                        dimension=SignalDimension.TEXT,
                        signal_type="PROTECTIVE_SECURITY_ADVISORY",
                        severity=SignalSeverity.INFO,
                        confidence=0.98,
                        weight=-1.5,
                        description="Verified protective security notice: explicit advisory against disclosing credentials or passwords.",
                        provenance=ProvenanceRecord(
                            source_service="services/language_intelligence",
                            detector_name="ProtectiveNegationEngine",
                            target_artifact=req.message_text[:100],
                        ),
                    )
                )
        except Exception:
            pass

        text_signals = SemanticSignalExtractor.extract_signals(inc_id, req.message_text)
        signals.extend(text_signals)

    # 2. URL & Infrastructure Safety Analysis
    target_url = req.url
    if not target_url and req.qr_payload and ("http://" in req.qr_payload or "https://" in req.qr_payload):
        # Extract embedded URL from QR if present
        import re
        match = re.search(r"https?://[^\s&]+", req.qr_payload)
        if match:
            target_url = match.group(0)

    if target_url:
        url_res = URLAnalyzer.analyze_lexical_risk(inc_id, target_url)
        signals.extend(url_res.get("signals", []))

    # 3. Payment Context & QR Analysis
    target_vpa = req.vpa
    if not target_vpa and req.qr_payload and "pa=" in req.qr_payload:
        import urllib.parse
        parsed = urllib.parse.urlparse(req.qr_payload)
        params = urllib.parse.parse_qs(parsed.query)
        if "pa" in params:
            target_vpa = params["pa"][0]

    is_payment_proximate = False
    if target_vpa:
        is_payment_proximate = True
        # Check if individual VPA claiming institutional handle
        is_personal_psp = any(psp in target_vpa.lower() for psp in ["@oksbi", "@paytm", "@ybl", "@axl", "@ibl"])
        if is_personal_psp:
            signals.append(
                EvidenceSignal(
                    incident_id=inc_id,
                    dimension=SignalDimension.PAYMENT,
                    signal_type="INDIVIDUAL_VPA_PAYMENT_TARGETED",
                    severity=SignalSeverity.MEDIUM,
                    confidence=0.85,
                    weight=1.5,
                    description=f"Payment targets individual consumer VPA handle: {target_vpa}",
                    provenance=ProvenanceRecord(
                        source_service="services/investigation",
                        detector_name="PaymentVPAValidator",
                        target_artifact=target_vpa,
                    ),
                )
            )

    # 3.5. Smart Registry Real-Time Screening (DPIP Module A Integration)
    try:
        from packages.schemas.registry import IdentifierType, ScreenRequest, TypedIdentifier, ReportStatus
        from services.registry.service import get_smart_registry_service

        reg_idents = []
        if target_vpa:
            reg_idents.append(TypedIdentifier(identifier_type=IdentifierType.UPI_VPA, raw_value=target_vpa))
        if target_url:
            reg_idents.append(TypedIdentifier(identifier_type=IdentifierType.URL_DOMAIN, raw_value=target_url))
        if req.sender_phone:
            reg_idents.append(TypedIdentifier(identifier_type=IdentifierType.PHONE, raw_value=req.sender_phone))

        if reg_idents:
            reg_service = get_smart_registry_service()
            reg_res = await reg_service.screen_identifiers(
                ScreenRequest(caller_org="SCAMGRAPH_INVESTIGATE", identifiers=reg_idents, correlation_id=inc_id)
            )
            for m in reg_res.matches:
                if m.is_revoked:
                    continue
                
                dim = SignalDimension.PAYMENT if m.identifier_type in (IdentifierType.UPI_VPA, IdentifierType.BANK_ACCOUNT) else SignalDimension.NETWORK
                sev = SignalSeverity.CRITICAL if m.report_status == ReportStatus.CONFIRMED else SignalSeverity.MEDIUM
                signals.append(
                    EvidenceSignal(
                        incident_id=inc_id,
                        dimension=dim,
                        signal_type=m.reason_code,
                        severity=sev,
                        confidence=m.confidence,
                        weight=2.0 if sev == SignalSeverity.CRITICAL else 1.0,
                        description=f"DPIP Smart Suspect Registry match ({m.category}) reported by {m.reporting_source}. Status: {m.report_status.value}",
                        provenance=ProvenanceRecord(
                            source_service="services/registry",
                            detector_name="SmartRegistryMatcher",
                            target_artifact=m.matched_fingerprint,
                        ),
                    )
                )
    except Exception as reg_err:
        # Registry screening is non-fatal if optional
        pass

    # 4. Pattern Engine
    pattern_match = PatternMatcher.match(signals)
    pattern_dict = None
    if pattern_match and pattern_match.is_strong_match:
        pattern_dict = {
            "pattern_name": pattern_match.pattern_name,
            "match_score": pattern_match.match_score,
            "matched_required": pattern_match.matched_required,
            "matched_supporting": getattr(pattern_match, "matched_supporting", []),
            "missing_required": pattern_match.missing_required,
        }

    # 5. Graph Entity Correlation Check
    graph_report: Optional[EntityCorrelationReport] = None
    graph_dict = None
    if req.sender_phone or target_url or target_vpa:
        # Check for shared graph infrastructure
        # Note: correlate_incident is async and queries Neo4j for entities already stored
        # For now, we'll skip this if Neo4j is not populated
        try:
            graph_report = await EntityCorrelationService().correlate_incident(inc_id)
            if graph_report and graph_report.total_shared_entities > 0:
                graph_dict = {
                    "shared_phone_count": graph_report.shared_phone_count,
                    "shared_domain_count": graph_report.shared_domain_count,
                    "shared_payment_entity_count": graph_report.shared_payment_entity_count,
                    "related_incidents_count": len(graph_report.explanation_paths),
                    "explanation_paths": graph_report.explanation_paths,
                }
        except Exception:
            # Graph correlation is optional - if Neo4j isn't ready, skip
            pass

    # 6. Risk Engine Evaluation
    assessment = RiskEngine.evaluate(
        incident_id=inc_id,
        signals=signals,
        pattern_match=pattern_match,
        graph_correlation=graph_report,
        payment_proximate=is_payment_proximate,
    )

    # 7. Unified Multi-Signal Assessment (Module D)
    unified_dict = None
    try:
        from packages.schemas.unified_risk import UnifiedRiskRequest
        from services.risk_engine.unified_engine import get_unified_risk_engine

        unified_req = UnifiedRiskRequest(
            entity_id=inc_id,
            message_text=req.message_text,
            url=target_url,
            vpa=target_vpa,
            phone=req.sender_phone,
            caller_org="INVESTIGATE_UI",
        )
        unified_res = await get_unified_risk_engine().assess(unified_req)
        unified_dict = unified_res.model_dump()
    except Exception as e:
        pass

    # 7.5 Unified Decision Engine (Phase 4A Tripartite Decision)
    tripartite_dict = None
    try:
        from services.decision_engine.service import unified_decision_service
        stg = (
            pattern_dict.get("current_stage", "PAYMENT_REQUEST" if is_payment_proximate else "INITIAL_CONTACT")
            if pattern_dict
            else ("PAYMENT_REQUEST" if is_payment_proximate else "INITIAL_CONTACT")
        )
        tactics = [pattern_dict.get("pattern_id")] if pattern_dict and pattern_dict.get("pattern_id") else []
        tripartite_res = unified_decision_service.evaluate(
            incident_id=inc_id,
            message_text=req.message_text,
            url=target_url,
            vpa=target_vpa,
            phone=req.sender_phone,
            journey_stage=stg,
            tactics_observed=tactics,
        )
        tripartite_dict = tripartite_res.model_dump()
    except Exception as e:
        pass

    # 7.6 Contextual Intervention Engine (Phase 4B)
    contextual_dict = None
    try:
        from services.intervention_engine.service import contextual_intervention_service
        from packages.schemas.contextual_intervention import PaymentProximity
        intv_res = contextual_intervention_service.evaluate_from_signals(
            incident_id=inc_id,
            message_text=req.message_text,
            url=target_url,
            vpa=target_vpa,
            phone=req.sender_phone,
            journey_stage=stg,
            payment_proximity=PaymentProximity.REQUESTED if is_payment_proximate else PaymentProximity.NONE,
            tactics_observed=tactics,
        )
        contextual_dict = intv_res.model_dump()
    except Exception as e:
        pass

    # 8. Persist investigated incident to repository so it appears in the Incidents tab
    pattern_name = pattern_dict.get("pattern_name", "Unclassified") if pattern_dict else "Ad-hoc Investigation"
    risk_lvl_str = assessment.risk_level.value if hasattr(assessment.risk_level, "value") else str(assessment.risk_level)
    conf_str = assessment.evidence_confidence.value if hasattr(assessment.evidence_confidence, "value") else str(assessment.evidence_confidence)
    title_summary = req.url or target_url or req.vpa or target_vpa or (req.message_text[:40] + "..." if req.message_text else "Suspicious Activity")

    try:
        from services.api.app.domain import Incident
        from services.api.app.repository import get_incident_repository

        incident = Incident(
            id=inc_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            title=f"{pattern_name}: {title_summary}",
            source="INVESTIGATION",
            metadata={
                "user_identifier_hash": "analyst_session",
                "channel": "WEB",
                "pattern": pattern_name,
                "risk_score": int(round(assessment.risk_score * 100)) if assessment.risk_score <= 1.0 else int(round(assessment.risk_score)),
                "risk_level": risk_lvl_str,
                "confidence": conf_str,
                "current_stage": getattr(pattern_match, "current_stage", "INITIAL_CONTACT") if pattern_match else "INITIAL_CONTACT",
                "verdict": getattr(assessment, "verdict", "inconclusive"),
                "target_url": target_url,
                "target_vpa": target_vpa,
                "raw_text": req.message_text or "",
                "tripartite_action": tripartite_dict.get("action") if tripartite_dict else None,
            }
        )
        repo = get_incident_repository()
        await repo.create_incident(incident)
        if signals:
            await repo.add_signals(inc_id, signals)
    except Exception:
        pass

    return InvestigateResponse(
        incident_id=inc_id,
        analyzed_at=datetime.now(timezone.utc),
        signals=signals,
        assessment=assessment,
        pattern_match=pattern_dict,
        graph_correlation=graph_dict,
        unified_assessment=unified_dict,
        tripartite_decision=tripartite_dict,
        contextual_intervention=contextual_dict,
        multilingual_text=multilingual_dict,
        is_simulated=is_simulated,
    )

