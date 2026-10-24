# services/investigation — External Investigation Service

## Overview
Investigation service responsible for external web and infrastructure enrichment:
- **TinyFish API**: URL risk analysis, domain age, registrar reputation, IP/ASN lookup, and redirect-chain tracking.
- URL normalization, unshortening, and canonicalization.
- Response caching to minimize latency and redundant external API calls.
- Emits structured web evidence signals into the correlation pipeline.
