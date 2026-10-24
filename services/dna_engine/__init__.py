"""ScamDNA V3 Behavioral Fingerprinting Engine.

Multi-dimensional behavioral fingerprinting, variant matching, and explainable
scam signatures across 8 decoupled dimensions.
"""

from services.dna_engine.adapter import ScamFingerprintV2Adapter
from services.dna_engine.builder import ScamDNABuilder
from services.dna_engine.retrieval import DNACandidateIndex
from services.dna_engine.serializer import DNASerializer
from services.dna_engine.service import ScamDNAService, scam_dna_service
from services.dna_engine.similarity import ScamDNASimilarityEngine

__all__ = [
    "ScamDNABuilder",
    "ScamDNASimilarityEngine",
    "ScamFingerprintV2Adapter",
    "DNACandidateIndex",
    "DNASerializer",
    "ScamDNAService",
    "scam_dna_service",
]
