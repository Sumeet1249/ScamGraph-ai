"""ScamGraph AI Data Platform Package."""

from packages.data_platform.adapters import (
    HinglishScamAdapter,
    ICFD31kAdapter,
    ScamHamIndiaAdapter,
)
from packages.data_platform.auditor import DatasetQualityAuditor
from packages.data_platform.base_adapter import DatasetAdapter

__all__ = [
    "DatasetAdapter",
    "ScamHamIndiaAdapter",
    "ICFD31kAdapter",
    "HinglishScamAdapter",
    "DatasetQualityAuditor",
]
