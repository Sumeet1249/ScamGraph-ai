# Enterprise Intelligence APIs: Guard, Entity, Network & Campaign

## 1. Pre-Payment Guard API (`POST /api/v1/guard/check`)
Targeted for low-latency UPI and banking apps prior to payment execution.
- Evaluates recipient VPA / phone / account token
- Emits calibrated friction level (0 to 5) and machine-readable `action`
- Guarantees fast-path SLA: avoids heavy LLM evaluation on latency-critical transactions

## 2. Entity Intelligence API (`POST /api/v1/entities/check`)
Safe identifier reputation queries without victim disclosure:
- Types supported: `PHONE`, `EMAIL`, `UPI_VPA`, `DOMAIN`, `URL`, `SOCIAL_ACCOUNT`
- Returns: `normalized_value`, `verification_state`, `network_reputation`, `incident_count_bracket` (e.g. "1-5", "6-20", "20+")
- **Anti-Enumeration Defense**: Thresholded results, query rate limits, and zero victim narrative disclosure.

## 3. Network Intelligence API (`POST /api/v1/network/check`)
Evaluates cross-incident infrastructure links:
- Semantics: `NO_NETWORK_SIGNAL`, `SIMILAR_PATTERN_OBSERVED`, `ENTITY_REPORTED_ELSEWHERE`, `MULTIPLE_RELATED_SIGNALS`, `EMERGING_PATTERN`
- **Strict Privacy Rule**: Never reveals "Customer A reported this VPA". Reports only aggregate cross-incident signals.
- **No Judicial Attribution**: Never claims `same_scammer=true`. Uses infrastructure correlation (`SHARES_INFRASTRUCTURE`, `APPEARED_WITH`).

## 4. Campaign Intelligence & Outbreak Feed (`GET /api/v1/outbreak/feed`)
Subscribers receive real-time intelligence on active and emerging syndicate waves:
- Lifecycle: `EMERGING`, `ACTIVE`, `DECLINING`, `DORMANT`, `RESURGING`, `ARCHIVED`
- Activity: `NORMAL`, `RISING`, `SURGING`, `OUTBREAK`
- Excludes: Analyst internal notes, raw graph embedding distances, and victim PII.
