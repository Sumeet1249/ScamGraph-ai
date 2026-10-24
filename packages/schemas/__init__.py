"""ScamGraph AI Canonical Schemas Package."""

from packages.schemas.common import (
    generate_id,
    RiskLevelV2,
    ConfidenceLevelV2,
    UrgencyLevelV2,
    PrivacyClassification,
)
from packages.schemas.artifact import (
    ArtifactType,
    Artifact,
)
from packages.schemas.entity import (
    EntityType,
    EntityVerificationState,
    Entity,
)
from packages.schemas.incident import (
    IncidentStatus,
    Incident,
)
from packages.schemas.provenance import (
    SourceProvenanceType,
    AnnotationType,
    AnnotationRecord,
    SourceProvenanceRecord,
    ModelExecutionRecord,
    DatasetLineageRecord,
)
from packages.schemas.dataset import (
    SplitType,
    LanguageMetadata,
    QualityMetadata,
    SplitMetadata,
    ScamGraphRecordV2,
)
from packages.schemas.conversation import (
    SpeakerRole,
    ConversationMessage,
    Conversation,
)
from packages.schemas.tactics import (
    TacticType,
    ActionRequestedType,
    ManipulationSignal,
)
from packages.schemas.payment_context import (
    ClaimedPaymentReason,
    PaymentContextRecord,
)
from packages.schemas.journey_corpus import (
    JourneyOutcome,
    ScamJourneyRecord,
)
from packages.schemas.evidence_record import (
    EvidencePolarity,
    ClaimEvidenceRecord,
)
from packages.schemas.campaign_foundation import (
    CampaignVelocity,
    CampaignRecord,
)
from packages.schemas.review_queue import (
    ReviewReason,
    ReviewStatus,
    UserFeedbackType,
    ReviewItem,
    UserFeedbackRecord,
)
from packages.schemas.product_events import (
    ProductEventType,
    ProductEvent,
)
from packages.schemas.events import (
    ChannelType,
    EventType,
    ActorRole,
    MessagePayload,
    UrlPayload,
    PaymentPayload,
    Event,
)
from packages.schemas.signals import (
    SignalDimension,
    SignalSeverity,
    ProvenanceRecord,
    EvidenceSignal,
)
from packages.schemas.journey import (
    JourneyStage,
    JourneyStep,
    NextStepPrediction,
    ScamJourney,
)
from packages.schemas.assessment import (
    RiskLevel,
    EvidenceConfidence,
    EmergingStatus,
    InterventionAction,
    AdaptiveIntervention,
    ExplainabilityReport,
    AssessmentResult,
)
from packages.schemas.fingerprint import (
    ScamFingerprint,
    ScamFingerprintV2,
    FingerprintSimilarityResult,
)
from packages.schemas.graph import (
    GraphNodeType,
    CytoscapeNodeData,
    CytoscapeEdgeData,
    CytoscapeNode,
    CytoscapeEdge,
    CytoscapeGraph,
)
from packages.schemas.registry import (
    IdentifierType,
    ReportStatus,
    MatchType,
    AuditAction,
    TypedIdentifier,
    CanonicalFingerprint,
    CreateReportRequest,
    RegistryReport,
    ScreenRequest,
    ScreeningMatch,
    ScreenResponse,
    SubmitDisputeRequest,
    ResolveDisputeRequest,
    DisputeRecord,
    SubmitRevocationRequest,
    RevocationRecord,
    RegistryFeedbackRequest,
    AuditEvent,
)
from packages.schemas.mule import (
    TransactionDirection,
    TransactionChannel,
    TransactionOutcome,
    MuleRiskBand,
    MuleAction,
    TransactionRecord,
    MuleFeatureVector,
    MuleRuleHit,
    MuleEvaluationRequest,
    MuleEvaluationResponse,
    BatchMuleEvaluationRequest,
    BatchMuleEvaluationResponse,
)

__all__ = [
    # Common & V2 Primitives
    "generate_id",
    "RiskLevelV2",
    "ConfidenceLevelV2",
    "UrgencyLevelV2",
    "PrivacyClassification",
    # Artifact V2
    "ArtifactType",
    "Artifact",
    # Entity V2
    "EntityType",
    "EntityVerificationState",
    "Entity",
    # Incident V2
    "IncidentStatus",
    "Incident",
    # Provenance & Lineage V2
    "SourceProvenanceType",
    "AnnotationType",
    "AnnotationRecord",
    "SourceProvenanceRecord",
    "ModelExecutionRecord",
    "DatasetLineageRecord",
    # Dataset & ScamGraphRecordV2
    "SplitType",
    "LanguageMetadata",
    "QualityMetadata",
    "SplitMetadata",
    "ScamGraphRecordV2",
    # Conversation Corpus
    "SpeakerRole",
    "ConversationMessage",
    "Conversation",
    # Tactics & Manipulation
    "TacticType",
    "ActionRequestedType",
    "ManipulationSignal",
    # Payment Context Guard
    "ClaimedPaymentReason",
    "PaymentContextRecord",
    # Journey Corpus
    "JourneyOutcome",
    "ScamJourneyRecord",
    # Evidence (Supports & Contradicts)
    "EvidencePolarity",
    "ClaimEvidenceRecord",
    # Campaign Foundation
    "CampaignVelocity",
    "CampaignRecord",
    # Review Queue & Feedback
    "ReviewReason",
    "ReviewStatus",
    "UserFeedbackType",
    "ReviewItem",
    "UserFeedbackRecord",
    # Product Telemetry
    "ProductEventType",
    "ProductEvent",
    # Events
    "ChannelType",
    "EventType",
    "ActorRole",
    "MessagePayload",
    "UrlPayload",
    "PaymentPayload",
    "Event",
    # Signals
    "SignalDimension",
    "SignalSeverity",
    "ProvenanceRecord",
    "EvidenceSignal",
    # Journey
    "JourneyStage",
    "JourneyStep",
    "NextStepPrediction",
    "ScamJourney",
    # Assessment
    "RiskLevel",
    "EvidenceConfidence",
    "EmergingStatus",
    "InterventionAction",
    "AdaptiveIntervention",
    "ExplainabilityReport",
    "AssessmentResult",
    # Fingerprint
    "ScamFingerprint",
    "ScamFingerprintV2",
    "FingerprintSimilarityResult",
    # Graph
    "GraphNodeType",
    "CytoscapeNodeData",
    "CytoscapeEdgeData",
    "CytoscapeNode",
    "CytoscapeEdge",
    "CytoscapeGraph",
    # Smart Registry
    "IdentifierType",
    "ReportStatus",
    "MatchType",
    "AuditAction",
    "TypedIdentifier",
    "CanonicalFingerprint",
    "CreateReportRequest",
    "RegistryReport",
    "ScreenRequest",
    "ScreeningMatch",
    "ScreenResponse",
    "SubmitDisputeRequest",
    "ResolveDisputeRequest",
    "DisputeRecord",
    "SubmitRevocationRequest",
    "RevocationRecord",
    "RegistryFeedbackRequest",
    "AuditEvent",
    # Mule Intelligence
    "TransactionDirection",
    "TransactionChannel",
    "TransactionOutcome",
    "MuleRiskBand",
    "MuleAction",
    "TransactionRecord",
    "MuleFeatureVector",
    "MuleRuleHit",
    "MuleEvaluationRequest",
    "MuleEvaluationResponse",
    "BatchMuleEvaluationRequest",
    "BatchMuleEvaluationResponse",
]
