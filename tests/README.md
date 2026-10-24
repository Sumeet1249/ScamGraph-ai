# tests — Test Suite

## Overview
Comprehensive test suite for ScamGraph AI:
- `unit/`: Unit tests for feature extraction, signal definitions, and Pydantic schema validation.
- `integration/`: Integration tests validating:
  - Neo4j graph traversal and entity fusion.
  - pgvector cosine similarity search.
  - TinyFish API mock client responses.
- `e2e/`: End-to-end journey ingestion, multi-signal correlation, dual-axis risk/confidence calibration, and `INSUFFICIENT_EVIDENCE` validation.
