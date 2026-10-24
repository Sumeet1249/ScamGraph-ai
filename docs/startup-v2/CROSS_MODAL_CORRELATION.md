# Cross-Modal Correlation Specification

## 1. Unified Network Correlation Across Modalities
Scam campaigns systematically transition across communication channels:
- Initial lure via SMS or telegram message
- High-pressure intimidation via Hindi voice call (digital arrest)
- Fake credentialing via court order screenshot
- Monetization via WhatsApp QR code or payment gateway

### Correlation Mechanics
The correlation engine (`services.correlation`) operates directly on canonical entities and ScamDNA profiles derived across all modalities:
1. **Shared Payment Entity**:
   - Incident A (Screenshot shows `fake.cbi@sbi`)
   - Incident B (QR decodes to `fake.cbi@sbi`)
   - Incident C (Call transcript mentions `fake.cbi@sbi`)
   - **Resolution**: All 3 incidents correlate onto the same payment destination node in the Knowledge Graph.
2. **Behavioral Continuity**: Even if payment identifiers rotate, matching ScamDNA profiles (tactic combination, journey transition pattern, linguistic profile) connect incidents to the active campaign cluster.
