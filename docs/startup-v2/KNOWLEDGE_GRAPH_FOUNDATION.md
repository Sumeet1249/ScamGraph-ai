# ScamGraph AI — India Scam Knowledge Graph Foundation

> **Document Version**: 2.0.0  
> **Status**: APPROVED  
> **Phase**: 1A — Graph Architecture & Relationship Topology  

---

## 1. Hybrid Storage Architecture

ScamGraph avoids the fatal anti-pattern of using Neo4j as the sole database for all tabular records, or using a relational database for 5-hop path traversals.

```
+-----------------------------------------------------------------------------------+
| POSTGRESQL (Relational Source of Truth)                                            |
| - Canonical entity records, masked display values, canonical hashes               |
| - Incident states, chronological interaction events, raw encrypted artifacts       |
| - Audit logs, merge/split records, dispute states, authoritative verifications    |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼ (Async / Event Sync)
+-----------------------------------------------------------------------------------+
| NEO4J & IN-MEMORY TOPOLOGY (Graph Traversal & Campaign Discovery)                 |
| - Nodes: (Entity), (Incident), (Brand), (Evidence), (Campaign)                    |
| - Edges: [:APPEARED_WITH], [:HOSTED_ON], [:REQUESTED_PAYMENT_TO], etc.            |
| - Graph algorithms: Community detection, multi-hop shortest paths, centrality     |
+-----------------------------------------------------------------------------------+
```

---

## 2. Graph Node & Edge Contracts

### Node Taxonomy
- `(:Incident {id, risk, scam_family, created_at})`
- `(:Entity {id, entity_type, masked_value, canonical_hash, verification_state})`
- `(:Brand {id, canonical_name, ticker, category})`
- `(:Organization {id, official_name, category})`
- `(:Evidence {id, polarity, confidence, created_at})`
- `(:Campaign {id, name, velocity, status})`

### Relationship Edge Taxonomy
1. `(e1:Entity)-[:APPEARED_WITH {incident_id, confidence}]->(e2:Entity)`
2. `(u:URL)-[:HOSTED_ON]->(d:Domain)`
3. `(i:Incident)-[:REQUESTED_PAYMENT_TO]->(p:Entity {type: "UPI_VPA"})`
4. `(m:Entity)-[:CLAIMS_TO_REPRESENT]->(b:Brand)`
5. `(m:Entity)-[:IMPERSONATES]->(o:Organization)`
6. `(e1:Entity)-[:SHARES_INFRASTRUCTURE {shared_type}]->(e2:Entity)`
7. `(ev:Evidence)-[:SUPPORTS | :CONTRADICTS]->(clm:Claim)`

> [!WARNING]
> **Constitutional Attribution Safeguard**: The graph topology may establish `[:SHARES_INFRASTRUCTURE]` or `[:APPEARED_WITH]`. It must **NEVER** assert a `[:SAME_CRIMINAL]` relationship without authorized judicial evidence.

---

## 3. Graceful Fallback (`DEGRADED_GRAPH_MODE`)

In development, unit testing, and environments without an active Neo4j cluster:
- ScamGraph's `EntityRelationshipManager` operates seamlessly in-memory using bidirectional adjacency indexes.
- All correlation queries, multi-hop traversals, and incident relationship searches function identically.
- Graph responses emit metadata: `"graph_mode": "DEGRADED_GRAPH_MODE"` to truthfully indicate that multi-million node distributed clustering is running on local in-memory adjacency sets.
