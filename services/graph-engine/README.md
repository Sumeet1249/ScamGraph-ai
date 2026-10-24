# services/graph-engine — Neo4j Graph & Journey Traversal Engine

## Overview
Graph intelligence service interfacing with Neo4j:
- **Journey Construction**: Chronological linking of user interaction steps (`:JourneyStep -[:NEXT]-> :JourneyStep`).
- **Entity Resolution**: Linking senders, phone numbers, URLs, domains, IPs, and payment handles (VPAs, bank accounts).
- **Incident Fusion**: Identifying shared infrastructure, identical campaign signatures, or reused UPI VPAs across distinct incidents.
- **Topology Extraction**: Exporting clean, format-ready subgraphs for Cytoscape.js visualization in the web application.
