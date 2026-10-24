# ScamGraph AI — Entity Resolution & Identity Governance

> **Document Version**: 2.0.0  
> **Status**: APPROVED  
> **Phase**: 1A — Entity Resolution & Lineage Preservation  

---

## 1. Resolution Principles

Entity resolution in fraud intelligence carries high stakes. In financial and cybersecurity investigations, **over-merging** falsely conflates innocent entities with malicious infrastructure, while **under-merging** blinds the network to campaign reuse.

ScamGraph adheres to three governing rules:
1. **Deterministic First**: Exact cryptographic hashes and verified alias trees resolve automatically.
2. **Never Auto-Merge Fuzzy Candidates**: High lexical similarity generates a `POSSIBLE_MATCH` and routes to `REQUIRES_REVIEW`. It is never merged without corroboration.
3. **Lineage Preservation**: Entities are never deleted on merge. History, previous entity IDs, and observations remain fully auditable and reversible.

---

## 2. Resolution Decision Matrix

| Match Type | Confidence | Decision | Action Taken |
| :--- | :---: | :--- | :--- |
| **`EXACT_MATCH`** | `1.00` | Automated Merge | Increments observation count; links observation to existing canonical entity |
| **`STRONG_MATCH`** | `0.95` | Automated Alias Resolution | Matches verified alias index; updates canonical entity timestamp |
| **`POSSIBLE_MATCH`** | `0.85 - 0.94` | **Hold for Review** | Creates new temporary entity candidate; flags `REQUIRES_REVIEW`; notifies analyst queue |
| **`CONFLICT`** | `0.50` | Escalate | Conflicting verification states detected (e.g. claimed brand matches official verified entity) |
| **`NO_MATCH`** | `1.00` | New Entity Creation | Generates new canonical entity ID (`ent_...`); indexes canonical hash |

---

## 3. Lineage-Preserving Consolidation (Merge Protocol)

When two entity candidates are confirmed by evidence or analyst review to represent the same underlying identifier, ScamGraph performs a non-destructive merge:

```
[Entity A: ent_101] (Canonical)  <=== MERGE ===  [Entity B: ent_102]
         │                                              │
         ├── observation_count: 5 + 3 = 8               ├── marked consolidated
         ├── incident_count: 2 + 1 = 3                  └── aliases pointer preserved
         ├── aliases: ["ent_102", "alias_val"]
         └── EntityMergeRecord generated
```

### The Merge Record (`EntityMergeRecord`)
Every merge produces an immutable audit record:
```json
{
  "merge_id": "mrg_9f81a7b2",
  "canonical_entity_id": "ent_101",
  "merged_entity_ids": ["ent_102"],
  "reason": "Confirmed shared telecom circle and identical secondary VPA registration",
  "evidence_ids": ["sig_4821a"],
  "merged_at": "2026-10-24T12:00:00Z",
  "can_split": true
}
```

---

## 4. Reversible Split Protocol (Error Correction)

If new evidence emerges indicating that two identifiers were incorrectly consolidated (e.g., a shared telecom pool number reassigned to a legitimate consumer), ScamGraph executes an instant split:
- Restores original target entity IDs.
- Removes target entity IDs from the canonical entity's alias list.
- Emits an `EntitySplitRecord` detailing the correction reason.
- Preserves full chronological audit history without destructive database mutations.
