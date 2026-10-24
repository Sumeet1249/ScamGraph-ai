# Knowledge Graph Explorer UI Specification

## 1. Interactive Cytoscape Canvas & Bounded Traversal
The `/graph` surface visualizes bipartite relationships connecting incidents, campaigns, and canonical fraud entities:
- **Safety Limits**: Traversal depth is bounded ($\le 2$ hops) with progressive node expansion to prevent browser memory exhaustion.
- **Supernode Disambiguation**: High-degree nodes (e.g. genuine bank customer care numbers like 1800112211 or major platform domains) receive special visual styling to prevent false visual correlation.
- **Degraded Mode Resilience**: If the underlying Neo4j instance is temporarily unreachable, the frontend displays an explicit degraded mode banner while falling back to cached local incident representations.
