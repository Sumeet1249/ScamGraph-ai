"""Semantic Vector Encoder (Step 15 & Step 20).

Re-exports the canonical SemanticEncoder interface and singleton from ml.embeddings.encoder
for full backwards compatibility with VECTPHISH and Pattern Engine components.
"""

import numpy as np
from ml.embeddings.encoder import SemanticEncoder, semantic_encoder, EmbeddingCache

__all__ = ["SemanticEncoder", "semantic_encoder", "EmbeddingCache", "np"]
