"""Incident Ingestion, Multi-Signal Evidence Extraction, and Journey Endpoints."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field

from packages.schemas import (
    Event,
    EventType,
    EvidenceSignal,
    SignalDimension,
    SignalSeverity,
    ProvenanceRecord,
    ScamJourney,
    JourneyStep,
    JourneyStage,
    NextStepPrediction,
    AssessmentResult,
    RiskLevel,
    EvidenceConfidence,
    EmergingStatus,
    InterventionAction,
    AdaptiveIntervention,
    ExplainabilityReport,
    CytoscapeGraph,
    CytoscapeNode,
    CytoscapeNodeData,
    CytoscapeEdge,
    CytoscapeEdgeData,
    GraphNodeType,
)
from services.investigation.url_analysis.safety import URLAnalyzer
from services.pattern_engine.semantic.nlp import SemanticSignalExtractor
from services.pattern_engine.matcher.fusion import EvidenceFusionEngine
from services.api.app.repository import get_incident_repository, IncidentRepository
from services.journey_engine.service import JourneyEngineService
from packages.schemas.journey import JourneyEvent
from packages.schemas.dna import ScamDNA, ConsumerDNAView
from services.dna_engine.service import ScamDNAService
from packages.schemas.correlation import (
    ConsumerNetworkSignal,
    IncidentCorrelation,
    CandidateIncident,
    AnalystCorrelationView,
)
from services.correlation_engine.service import correlation_service

from datetime import datetime, timezone
from uuid import uuid4

router = APIRouter()

# In-memory storage for active sessions / timeline signals
_INCIDENT_EVENTS: Dict[str, List[Event]] = {}
_INCIDENT_SIGNALS: Dict[str, List[EvidenceSignal]] = {}
_INCIDENTS_METADATA: Dict[str, Dict[str, Any]] = {}


def _extract_signals_for_event(incident_id: str, event: Any) -> List[EvidenceSignal]:
    """Extracts specialized signals for an event across semantic, URL, and payment extractors."""
    new_signals: List[EvidenceSignal] = []
    ev_type = getattr(event, "event_type", None)
    payload = getattr(event, "payload", {})
    if hasattr(payload, "model_dump"):
        payload = payload.model_dump()
    elif not isinstance(payload, dict):
        payload = {}

    if ev_type == EventType.MESSAGE_RECEIVED:
        text = payload.get("text", "")
        if text:
            new_signals = SemanticSignalExtractor.extract_signals(incident_id, text)
    elif ev_type == EventType.LINK_CLICKED:
        raw_url = payload.get("raw_url", "")
        if raw_url:
            res = URLAnalyzer.analyze_lexical_risk(incident_id, raw_url)
            new_signals = res.get("signals", [])
    elif ev_type in (EventType.COLLECT_REQUEST_RECEIVED, EventType.PAYMENT_INTENT_INITIATED):
        vpa = payload.get("vpa", "")
        claimed_payee = payload.get("claimed_payee_name", "")
        if vpa and any(psb in vpa for psb in ["@oksbi", "@paytm", "@ybl", "@axl", "@ibl"]):
            new_signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    event_id=getattr(event, "event_id", getattr(event, "id", str(uuid4()))),
                    dimension=SignalDimension.PAYMENT,
                    signal_type="INDIVIDUAL_VPA_PAYMENT_TARGETED",
                    severity=SignalSeverity.MEDIUM,
                    confidence=0.85,
                    weight=1.5,
                    description=f"Transaction targets an individual personal VPA handle: {vpa}",
                    provenance=ProvenanceRecord(
                        source_service="services/api",
                        detector_name="PaymentContextExtractor",
                        target_artifact=vpa,
                        raw_evidence={"vpa": vpa, "claimed_payee": claimed_payee},
                    ),
                )
            )
    return new_signals


class CreateIncidentRequest(BaseModel):
    user_identifier_hash: str = Field(..., description="Pseudonymized user ID")
    channel: str = Field(default="SMS", description="Initial contact channel (SMS, WhatsApp, Web, etc.)")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IncidentRecord(BaseModel):
    id: str
    user_identifier_hash: Optional[str] = "anon"
    channel: str
    status: str = "ACTIVE"
    events_count: int = 0
    created_at: datetime


class AddEventRequest(BaseModel):
    event_type: EventType
    sequence_number: Optional[int] = None
    timestamp: Optional[datetime] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TimelineEventItem(BaseModel):
    sequence_number: int
    event_type: str
    timestamp: datetime
    time_delta_seconds: Optional[int]
    payload: Dict[str, Any]


class TimelineResponse(BaseModel):
    incident_id: str
    total_events: int
    events: List[TimelineEventItem]


class IngestResponse(BaseModel):
    status: str = "received"
    event_id: str
    incident_id: str
    sequence_number: int
    current_stage: JourneyStage
    active_signals_count: int


@router.post("", response_model=IncidentRecord, status_code=status.HTTP_201_CREATED)
async def create_incident(
    req: CreateIncidentRequest,
    repo: IncidentRepository = Depends(get_incident_repository)
):
    """Step 11: Create a new incident session via repository."""
    from services.api.app.domain import Incident
    
    inc_id = f"inc_{uuid4().hex[:12]}"
    now = datetime.now(timezone.utc)
    
    incident = Incident(
        id=inc_id,
        created_at=now,
        updated_at=now,
        title=f"Incident: {req.channel} - {now.isoformat()}",
        source=req.channel,
        metadata={
            "user_identifier_hash": req.user_identifier_hash,
            "channel": req.channel,
            **req.metadata
        }
    )
    
    await repo.create_incident(incident)
    _INCIDENTS_METADATA[inc_id] = req.metadata or {}
    _INCIDENT_EVENTS[inc_id] = []
    
    return IncidentRecord(
        id=inc_id,
        user_identifier_hash=req.user_identifier_hash,
        channel=req.channel,
        status="ACTIVE",
        events_count=0,
        created_at=now,
    )


@router.get("", response_model=List[IncidentRecord])
async def list_all_incidents(
    repo: IncidentRepository = Depends(get_incident_repository)
):
    """Retrieve all incident records."""
    incidents = await repo.list_incidents()
    records = []
    for inc in incidents:
        events = await repo.get_events(inc.id)
        records.append(
            IncidentRecord(
                id=inc.id,
                user_identifier_hash=inc.metadata.get("user_identifier_hash") if inc.metadata else None,
                channel=inc.source or "WEB",
                status="ACTIVE",
                events_count=len(events) if events else 0,
                created_at=inc.created_at,
            )
        )
    return records


@router.get("/{incident_id}", response_model=IncidentRecord)
async def get_incident(
    incident_id: str,
    repo: IncidentRepository = Depends(get_incident_repository)
):
    """Step 11: Retrieve incident session details."""
    incident = await repo.get_incident(incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found."
        )
    
    events = await repo.get_events(incident_id)
    
    return IncidentRecord(
        id=incident.id,
        user_identifier_hash=incident.metadata.get("user_identifier_hash", "anonymous"),
        channel=incident.metadata.get("channel", "unknown"),
        status="ACTIVE" if incident.status.value == "OPEN" else incident.status.value,
        events_count=len(events) if events else 0,
        created_at=incident.created_at,
    )


@router.post("/{incident_id}/events", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def add_incident_event(
    incident_id: str,
    req: AddEventRequest,
    repo: IncidentRepository = Depends(get_incident_repository)
):
    """Step 11: Add an event to an existing incident session via repository."""
    # Auto-create incident if needed
    incident = await repo.get_incident(incident_id)
    if not incident:
        now = datetime.now(timezone.utc)
        incident = Incident(
            id=incident_id,
            created_at=now,
            updated_at=now,
            title=f"Auto-created incident: {incident_id}",
            source="API",
            metadata={"channel": "API"}
        )
        await repo.create_incident(incident)

    seq = req.sequence_number or ((await repo.get_events(incident_id) or []).__len__() + 1)
    ev = Event(
        incident_id=incident_id,
        sequence_number=seq,
        event_type=req.event_type,
        timestamp=req.timestamp or datetime.now(timezone.utc),
        source="USER_INPUT",
        payload=req.payload,
    )
    await repo.add_event(incident_id, ev)
    _INCIDENT_EVENTS.setdefault(incident_id, []).append(ev)
    
    # Extract signals via specialized intelligence engines
    new_signals = _extract_signals_for_event(incident_id, ev)
    _INCIDENT_SIGNALS.setdefault(incident_id, []).extend(new_signals)

    stage_map = {
        EventType.MESSAGE_RECEIVED: JourneyStage.INITIAL_CONTACT,
        EventType.LINK_CLICKED: JourneyStage.SUSPICIOUS_LINK,
        EventType.OTP_REQUESTED: JourneyStage.CREDENTIAL_OTP_HARVEST,
        EventType.COLLECT_REQUEST_RECEIVED: JourneyStage.PAYMENT_REQUEST,
        EventType.PAYMENT_INTENT_INITIATED: JourneyStage.PAYMENT_INTENT,
    }
    current_stage = stage_map.get(req.event_type, JourneyStage.UNKNOWN)

    return IngestResponse(
        status="received",
        event_id=getattr(ev, "event_id", getattr(ev, "id", str(uuid4()))),
        incident_id=incident_id,
        sequence_number=seq,
        current_stage=current_stage,
        active_signals_count=len(_INCIDENT_SIGNALS.get(incident_id, [])),
    )


@router.get("/{incident_id}/timeline", response_model=TimelineResponse)
async def get_incident_timeline(incident_id: str):
    """Step 11: Retrieve pure ordered event timeline without AI interpretation."""
    events = _INCIDENT_EVENTS.get(incident_id)
    if not events:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident {incident_id} not found.")

    items: List[TimelineEventItem] = []
    prev_time = None
    for ev in events:
        delta = None
        if prev_time:
            delta = int((ev.timestamp - prev_time).total_seconds())
        prev_time = ev.timestamp

        raw_payload = ev.payload.model_dump() if hasattr(ev.payload, "model_dump") else (ev.payload if isinstance(ev.payload, dict) else {})
        items.append(
            TimelineEventItem(
                sequence_number=ev.sequence_number,
                event_type=ev.event_type.value,
                timestamp=ev.timestamp,
                time_delta_seconds=delta,
                payload=raw_payload,
            )
        )

    return TimelineResponse(
        incident_id=incident_id,
        total_events=len(items),
        events=items,
    )


@router.get("/{incident_id}/events")
async def get_incident_events(incident_id: str):
    """Retrieve all raw events for an incident session."""
    if incident_id not in _INCIDENT_EVENTS and incident_id not in _INCIDENTS_METADATA:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident {incident_id} not found.")
    events = _INCIDENT_EVENTS.get(incident_id, [])
    return [ev.model_dump() if hasattr(ev, "model_dump") else ev for ev in events]


@router.post("/{incident_id}/evidence", status_code=status.HTTP_201_CREATED)
async def add_incident_evidence(
    incident_id: str,
    payload: Dict[str, Any],
    repo: IncidentRepository = Depends(get_incident_repository),
):
    """Attach canonical Evidence observation to an incident."""
    if incident_id not in _INCIDENT_EVENTS and incident_id not in _INCIDENTS_METADATA:
        inc_obj = await repo.get_incident(incident_id)
        if not inc_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident {incident_id} not found.")
        _INCIDENTS_METADATA[incident_id] = inc_obj.metadata or {}
        _INCIDENT_EVENTS[incident_id] = []

    from services.api.app.domain import Evidence
    from pydantic import ValidationError

    try:
        if "incident_id" not in payload:
            payload["incident_id"] = incident_id
        ev = Evidence(**payload)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors())

    # Store in session state
    if incident_id not in _INCIDENT_SIGNALS:
        _INCIDENT_SIGNALS[incident_id] = []
    
    # Store evidence representation
    _INCIDENTS_METADATA.setdefault(incident_id, {}).setdefault("evidence", []).append(ev.model_dump())
    return ev.model_dump()


@router.get("/{incident_id}/evidence")
async def get_incident_evidence(incident_id: str):
    """Retrieve all evidence observations attached to an incident."""
    if incident_id not in _INCIDENT_EVENTS and incident_id not in _INCIDENTS_METADATA:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident {incident_id} not found.")

    inc = _INCIDENTS_METADATA.get(incident_id, {})
    return inc.get("evidence", [])



@router.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_event(event: Event):
    """Ingest a multi-channel user communication, URL click, or payment request event."""
    if not event.incident_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="incident_id is required for session correlation.",
        )

    if event.incident_id not in _INCIDENT_EVENTS:
        _INCIDENT_EVENTS[event.incident_id] = []
        _INCIDENT_SIGNALS[event.incident_id] = []

    _INCIDENT_EVENTS[event.incident_id].append(event)

    # 1. Specialized Intelligence: Extract Signals based on Event Type
    new_signals: List[EvidenceSignal] = []

    if event.event_type == EventType.MESSAGE_RECEIVED:
        text = getattr(event.payload, "text", "") if hasattr(event.payload, "text") else event.payload.get("text", "")
        if text:
            new_signals = SemanticSignalExtractor.extract_signals(event.incident_id, text)

    elif event.event_type == EventType.LINK_CLICKED:
        raw_url = getattr(event.payload, "raw_url", "") if hasattr(event.payload, "raw_url") else event.payload.get("raw_url", "")
        if raw_url:
            res = URLAnalyzer.analyze_lexical_risk(event.incident_id, raw_url)
            new_signals = res.get("signals", [])

    elif event.event_type in (EventType.COLLECT_REQUEST_RECEIVED, EventType.PAYMENT_INTENT_INITIATED):
        vpa = getattr(event.payload, "vpa", "") if hasattr(event.payload, "vpa") else event.payload.get("vpa", "")
        claimed_payee = getattr(event.payload, "claimed_payee_name", "") if hasattr(event.payload, "claimed_payee_name") else event.payload.get("claimed_payee_name", "")

        # Detect personal handle claiming to be institutional
        if vpa and any(psb in vpa for psb in ["@oksbi", "@paytm", "@ybl", "@axl", "@ibl"]):
            new_signals.append(
                EvidenceSignal(
                    incident_id=event.incident_id,
                    event_id=event.event_id,
                    dimension=SignalDimension.PAYMENT,
                    signal_type="INDIVIDUAL_VPA_PAYMENT_TARGETED",
                    severity=SignalSeverity.MEDIUM,
                    confidence=0.85,
                    weight=1.5,
                    description=f"Transaction targets an individual personal VPA handle: {vpa}",
                    provenance=ProvenanceRecord(
                        source_service="services/api",
                        detector_name="PaymentContextExtractor",
                        target_artifact=vpa,
                        raw_evidence={"vpa": vpa, "claimed_payee": claimed_payee},
                    ),
                )
            )

    # Store newly extracted signals
    _INCIDENT_SIGNALS[event.incident_id].extend(new_signals)

    # Determine current stage from event type
    stage_map = {
        EventType.MESSAGE_RECEIVED: JourneyStage.INITIAL_CONTACT,
        EventType.LINK_CLICKED: JourneyStage.SUSPICIOUS_LINK,
        EventType.OTP_REQUESTED: JourneyStage.CREDENTIAL_OTP_HARVEST,
        EventType.COLLECT_REQUEST_RECEIVED: JourneyStage.PAYMENT_REQUEST,
        EventType.PAYMENT_INTENT_INITIATED: JourneyStage.PAYMENT_INTENT,
    }
    current_stage = stage_map.get(event.event_type, JourneyStage.UNKNOWN)

    return IngestResponse(
        status="received",
        event_id=event.event_id,
        incident_id=event.incident_id,
        sequence_number=event.sequence_number,
        current_stage=current_stage,
        active_signals_count=len(_INCIDENT_SIGNALS[event.incident_id]),
    )


_journey_service = JourneyEngineService()


def _reconstruct_v2_journey(incident_id: str) -> ScamJourney:
    events = _INCIDENT_EVENTS.get(incident_id)
    if not events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No journey events found for incident: {incident_id}",
        )

    all_signals = _INCIDENT_SIGNALS.get(incident_id, [])
    signals_by_event: Dict[str, List[EvidenceSignal]] = {}
    for s in all_signals:
        if s.event_id:
            signals_by_event.setdefault(s.event_id, []).append(s)

    jrev_list: List[JourneyEvent] = []
    steps: List[JourneyStep] = []
    prev_time = None
    stage_map = {
        EventType.MESSAGE_RECEIVED: JourneyStage.INITIAL_CONTACT,
        EventType.LINK_CLICKED: JourneyStage.SUSPICIOUS_LINK,
        EventType.OTP_REQUESTED: JourneyStage.CREDENTIAL_OTP_HARVEST,
        EventType.COLLECT_REQUEST_RECEIVED: JourneyStage.PAYMENT_REQUEST,
        EventType.PAYMENT_INTENT_INITIATED: JourneyStage.PAYMENT_INTENT,
    }

    for idx, ev in enumerate(events, start=1):
        delta = None
        if prev_time:
            delta = int((ev.timestamp - prev_time).total_seconds())
        prev_time = ev.timestamp

        stage = stage_map.get(ev.event_type, JourneyStage.UNKNOWN)
        step_signals = signals_by_event.get(ev.event_id, [])

        steps.append(
            JourneyStep(
                incident_id=incident_id,
                sequence=idx,
                stage=stage,
                title=f"Step {idx}: {ev.event_type.value}",
                description=f"Observed event of type {ev.event_type.value}",
                timestamp=ev.timestamp,
                time_delta_seconds=delta,
                associated_signals=step_signals,
            )
        )

        tactics_list = []
        for s in step_signals:
            sig_dim = getattr(s, "dimension", None) or getattr(s, "signal_dimension", None)
            rid = getattr(s, "rule_id", None) or getattr(s, "signal_type", None)
            if (sig_dim == SignalDimension.SEMANTIC or str(sig_dim) == "PSYCHOLOGICAL_TACTIC") and rid:
                tactics_list.append(str(rid))

        jrev_list.append(
            JourneyEvent(
                event_id=ev.event_id,
                timestamp=ev.timestamp,
                sequence_number=idx - 1,
                event_type=ev.event_type.value if hasattr(ev.event_type, "value") else str(ev.event_type),
                tactics=tactics_list,
                evidence_ids=[s.signal_id for s in step_signals],
            )
        )

    journey = _journey_service.create_journey(incident_id, jrev_list)
    journey.steps = steps

    last_stage = steps[-1].stage if steps else JourneyStage.INITIAL_CONTACT
    next_stage_map = {
        JourneyStage.INITIAL_CONTACT: JourneyStage.SUSPICIOUS_LINK,
        JourneyStage.IMPERSONATION: JourneyStage.SUSPICIOUS_LINK,
        JourneyStage.URGENCY_PRESSURE: JourneyStage.SUSPICIOUS_LINK,
        JourneyStage.SUSPICIOUS_LINK: JourneyStage.CREDENTIAL_OTP_HARVEST,
        JourneyStage.CREDENTIAL_OTP_HARVEST: JourneyStage.PAYMENT_REQUEST,
        JourneyStage.PAYMENT_REQUEST: JourneyStage.PAYMENT_INTENT,
    }
    predicted_next = next_stage_map.get(last_stage, JourneyStage.UNKNOWN)
    journey.prediction = NextStepPrediction(
        current_stage=last_stage,
        predicted_next_stage=predicted_next,
        rationale=f"Historical scam progression follows {last_stage.value} -> {predicted_next.value}",
        recommended_preventive_action="Verify entity via official phone book before continuing.",
    )
    return journey


@router.get("/{incident_id}/journey", response_model=ScamJourney)
async def get_journey(incident_id: str):
    """Retrieve the reconstructed sequential scam journey for an incident."""
    return _reconstruct_v2_journey(incident_id)


@router.get("/{incident_id}/journey/timeline")
async def get_journey_timeline(incident_id: str):
    """Retrieve forensic timeline of stages and events."""
    journey = _reconstruct_v2_journey(incident_id)
    return _journey_service.serialize_analyst_view(journey)


@router.get("/{incident_id}/journey/progress")
async def get_journey_progress(incident_id: str):
    """Retrieve consumer-friendly progress meter representation."""
    journey = _reconstruct_v2_journey(incident_id)
    return _journey_service.serialize_consumer_view(journey)


@router.get("/{incident_id}/journey/warnings")
async def get_journey_warnings(incident_id: str):
    """Retrieve proactive pre-loss early warning candidates."""
    journey = _reconstruct_v2_journey(incident_id)
    return {
        "incident_id": incident_id,
        "early_warnings": [w.dict() for w in journey.early_warnings],
        "monetization_boundary_event_id": journey.monetization_boundary_event_id,
        "pre_loss_warning_issued": journey.pre_loss_warning_issued,
        "warning_lead_time_seconds": journey.warning_lead_time_seconds,
    }


@router.post("/{incident_id}/journey/recompute", response_model=ScamJourney)
async def recompute_journey(incident_id: str):
    """Recomputes scam journey state across all accumulated events."""
    journey = _reconstruct_v2_journey(incident_id)
    return _journey_service.recompute_journey(journey)


_dna_service = ScamDNAService()


def _reconstruct_or_get_dna(incident_id: str) -> ScamDNA:
    existing = _dna_service.get_dna_by_incident(incident_id)
    if existing:
        return existing
    try:
        journey = _reconstruct_v2_journey(incident_id)
    except HTTPException:
        journey = None

    events = _INCIDENT_EVENTS.get(incident_id, [])
    summary_text = ""
    for ev in events:
        if hasattr(ev, "payload") and isinstance(ev.payload, dict) and "text" in ev.payload:
            summary_text += " " + ev.payload["text"]

    all_signals = _INCIDENT_SIGNALS.get(incident_id, [])
    tactics = [s.rule_id for s in all_signals if s.signal_dimension == SignalDimension.PSYCHOLOGICAL_TACTIC and s.rule_id]
    
    return _dna_service.create_or_update_dna(
        incident_id=incident_id,
        journey=journey,
        tactics=tactics,
        message_text=summary_text.strip(),
        message_summary=summary_text.strip()[:100] if summary_text else None,
        family_hypotheses=journey.family_hypotheses if journey else {"UNKNOWN": 1.0},
        evidence_ids=[s.signal_id for s in all_signals],
    )


@router.get("/{incident_id}/dna", response_model=ScamDNA)
async def get_incident_dna(incident_id: str):
    """Retrieve canonical ScamDNA V3 behavioral fingerprint for an incident."""
    return _reconstruct_or_get_dna(incident_id)


@router.post("/{incident_id}/dna/rebuild", response_model=ScamDNA)
async def rebuild_incident_dna(incident_id: str):
    """Rebuilds and indexes ScamDNA V3 for an incident."""
    try:
        journey = _reconstruct_v2_journey(incident_id)
    except HTTPException:
        journey = None

    events = _INCIDENT_EVENTS.get(incident_id, [])
    summary_text = ""
    for ev in events:
        if hasattr(ev, "payload") and isinstance(ev.payload, dict) and "text" in ev.payload:
            summary_text += " " + ev.payload["text"]

    all_signals = _INCIDENT_SIGNALS.get(incident_id, [])
    tactics = [s.rule_id for s in all_signals if s.signal_dimension == SignalDimension.PSYCHOLOGICAL_TACTIC and s.rule_id]

    return _dna_service.create_or_update_dna(
        incident_id=incident_id,
        journey=journey,
        tactics=tactics,
        message_text=summary_text.strip(),
        message_summary=summary_text.strip()[:100] if summary_text else None,
        family_hypotheses=journey.family_hypotheses if journey else {"UNKNOWN": 1.0},
        evidence_ids=[s.signal_id for s in all_signals],
    )


@router.get("/{incident_id}/dna/similar")
async def get_similar_dna_patterns(incident_id: str, top_k: int = 5):
    """Retrieve most similar known scam patterns and variants using 2-stage DNA matching."""
    _reconstruct_or_get_dna(incident_id)
    matches = _dna_service.find_similar_patterns(incident_id, top_k=top_k)
    return [m.dict() for m in matches]


@router.get("/{incident_id}/dna/consumer", response_model=ConsumerDNAView)
async def get_consumer_dna_view(incident_id: str):
    """Retrieve plain-language consumer explanation of behavioral DNA match."""
    view = _dna_service.serialize_consumer_view(incident_id)
    if not view:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No DNA available for incident {incident_id}")
    return view


# -----------------------------------------------------------------------------
# Correlation & Network Intelligence Endpoints (Phase 3B)
# -----------------------------------------------------------------------------

@router.get("/{incident_id}/network-signal", response_model=ConsumerNetworkSignal)
async def get_incident_network_signal(incident_id: str):
    """Retrieve privacy-safe collective network signal for an incident (No victim PII)."""
    return correlation_service.get_network_signal(incident_id)


@router.get("/{incident_id}/related")
async def get_incident_related(
    incident_id: str,
    access_tier: str = Query("CONSUMER", pattern="^(CONSUMER|ANALYST)$"),
):
    """Retrieve related incidents.
    - If CONSUMER: Returns privacy-safe aggregated summary without foreign incident IDs.
    - If ANALYST: Returns detailed multi-signal correlations and graph paths.
    """
    if access_tier == "CONSUMER":
        return correlation_service.get_network_signal(incident_id)
    correlations = correlation_service.get_related_incidents(incident_id)
    return [c.model_dump() for c in correlations]


@router.get("/{incident_id}/correlation-candidates", response_model=List[CandidateIncident])
async def get_incident_correlation_candidates(incident_id: str):
    """Stage 1: Multi-source candidate retrieval for cross-incident analysis."""
    return correlation_service.find_candidates(incident_id)


@router.post("/{incident_id}/correlate")
async def run_incident_correlation(incident_id: str, top_k: int = 10):
    """Runs candidate retrieval and detailed correlation for an incident."""
    correlations = correlation_service.correlate_incident(incident_id, top_k=top_k)
    return [c.model_dump() for c in correlations]


@router.get("/{source_id}/correlations/{target_id}", response_model=AnalystCorrelationView)
async def get_pair_correlation_view(source_id: str, target_id: str):
    """Retrieve deep analyst correlation telemetry for a specific incident pair."""
    return correlation_service.get_analyst_view(source_id, target_id)


@router.get("/{incident_id}/assessment", response_model=AssessmentResult)
async def get_assessment(incident_id: str):
    """Retrieve the dual-axis Risk and Evidence Confidence assessment.

    Uses EvidenceFusionEngine to fuse multi-dimensional signals.
    Strict Rule: If insufficient data exists, returns INSUFFICIENT_EVIDENCE.
    """
    events = _INCIDENT_EVENTS.get(incident_id)
    if not events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found.",
        )

    signals = _INCIDENT_SIGNALS.get(incident_id, [])

    # Check if a payment request or payment intent is present in the journey
    has_payment = any(
        ev.event_type in (EventType.COLLECT_REQUEST_RECEIVED, EventType.PAYMENT_INTENT_INITIATED)
        for ev in events
    )

    # Multi-signal evidence fusion
    return EvidenceFusionEngine.evaluate(
        incident_id=incident_id,
        signals=signals,
        payment_proximate=has_payment,
        is_simulated=False,
    )


@router.get("/{incident_id}/graph", response_model=CytoscapeGraph)
async def get_cytoscape_graph(incident_id: str):
    """Retrieve Cytoscape.js directed graph format for frontend canvas rendering."""
    events = _INCIDENT_EVENTS.get(incident_id)
    if not events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found.",
        )

    all_signals = _INCIDENT_SIGNALS.get(incident_id, [])
    signals_by_event: Dict[str, List[EvidenceSignal]] = {}
    for s in all_signals:
        if s.event_id:
            signals_by_event.setdefault(s.event_id, []).append(s)

    nodes: List[CytoscapeNode] = [
        CytoscapeNode(
            data=CytoscapeNodeData(
                id=incident_id,
                label=f"Incident: {incident_id[:8]}",
                node_type=GraphNodeType.INCIDENT,
            )
        )
    ]
    edges: List[CytoscapeEdge] = []

    prev_node_id = None
    for idx, ev in enumerate(events, start=1):
        node_id = f"{incident_id}_step_{idx}"
        step_signals = signals_by_event.get(ev.event_id, [])
        highest_severity = "INFO"
        if step_signals:
            highest_severity = max(s.severity.value for s in step_signals)

        nodes.append(
            CytoscapeNode(
                data=CytoscapeNodeData(
                    id=node_id,
                    label=f"Step {idx}: {ev.event_type.value}",
                    node_type=GraphNodeType.JOURNEY_STEP,
                    severity=highest_severity,
                    subtext=ev.timestamp.strftime("%H:%M:%S UTC"),
                    properties={"signals_count": len(step_signals)},
                )
            )
        )
        # Link to root incident
        edges.append(
            CytoscapeEdge(
                data=CytoscapeEdgeData(
                    id=f"e_inc_{node_id}",
                    source=incident_id,
                    target=node_id,
                    label="CONTAINS_STEP",
                    relationship_type="CONTAINS_STEP",
                )
            )
        )
        # Sequential temporal edge
        if prev_node_id:
            edges.append(
                CytoscapeEdge(
                    data=CytoscapeEdgeData(
                        id=f"e_seq_{prev_node_id}_{node_id}",
                        source=prev_node_id,
                        target=node_id,
                        label="FOLLOWED_BY",
                        relationship_type="FOLLOWED_BY",
                    )
                )
            )
        prev_node_id = node_id

    return CytoscapeGraph(nodes=nodes, edges=edges)


@router.post("/{incident_id}/assess")
async def assess_incident_endpoint(incident_id: str):
    """Step 18: Unified incident assessment pipeline executing URL safety,
    TinyFish observation, pattern matching, risk indexing, and adaptive intervention.
    """
    from services.investigation.orchestrator import investigation_orchestrator
    try:
        assessment = await investigation_orchestrator.assess_incident(incident_id)
        return assessment
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Investigation assessment failed: {str(e)}",
        )
