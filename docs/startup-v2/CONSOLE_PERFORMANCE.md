# Console Performance & Scalability Protocols

## 1. Frontend Performance Budget
The Intelligence Console maintains strict operational responsiveness benchmarks:
- **Command Center Summary**: Load latency $< 350$ ms via consolidated API view models (`/api/v1/console/summary`).
- **Graph Explorer Traversal**: Bounded 2-hop radius with client-side progressive expansion and WebGL-accelerated Cytoscape rendering.
- **Outbreak Radar**: Renders active campaign nodes and blips using pure SVG/Canvas without blocking main thread interactions.
- **Table Pagination**: Server-side pagination with default limits ($\le 50$ items per page) to prevent DOM bloat on large incident datasets.
