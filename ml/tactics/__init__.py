"""ScamGraph AI Psychological Manipulation & Tactic Intelligence Package."""

from ml.tactics.ontology import (
    TACTIC_SEVERITY,
    CRITICAL_SAFETY_TACTICS,
    TACTIC_DEFAULT_ACTIONS,
    CONSUMER_TACTIC_NAMES,
)
from ml.tactics.rules import (
    TacticRule,
    TACTIC_RULES,
    RuleBasedTacticEngine,
    is_global_advisory,
    is_routine_notification,
    is_quoted_inquiry,
)
from ml.tactics.semantic import (
    SemanticTacticMatcher,
    TACTIC_PROTOTYPES,
)
from ml.tactics.classifier import (
    MultiLabelTacticClassifier,
)

__all__ = [
    "TACTIC_SEVERITY",
    "CRITICAL_SAFETY_TACTICS",
    "TACTIC_DEFAULT_ACTIONS",
    "CONSUMER_TACTIC_NAMES",
    "TacticRule",
    "TACTIC_RULES",
    "RuleBasedTacticEngine",
    "is_global_advisory",
    "is_routine_notification",
    "is_quoted_inquiry",
    "SemanticTacticMatcher",
    "TACTIC_PROTOTYPES",
    "MultiLabelTacticClassifier",
]
