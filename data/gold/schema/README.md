# Gold Set Schema Guidelines

Defines canonical schema contracts for records eligible to enter the ScamGraph India Gold Standard Set.

## Verification Requirements
Every sample entering the Gold Standard Set must satisfy:
1. **Multi-Reviewer Consensus**: `annotation_type: HUMAN_MULTI_REVIEW` or `HUMAN_VERIFIED`.
2. **Template Independence**: Must not share a template signature (`extract_template_signature`) with any record in training datasets.
3. **No Synthetic Artifacts**: Synthetic records generated from prompts are strictly prohibited.
4. **PII Masking**: All victim phones, VPAs, and personal names must be replaced with masked presentations and canonical hashes.
