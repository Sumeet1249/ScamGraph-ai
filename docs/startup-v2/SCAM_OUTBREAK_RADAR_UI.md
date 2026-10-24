# Scam Outbreak Radar UI Specification

## 1. Outbreak Radar Integrity: No Fake Animated Dots
The Scam Outbreak Radar (`/radar`) is ScamGraph's flagship visual intelligence surface. Every visual element on the Radar is strictly bound to backend intelligence models:
- **Campaign Node**: Derived from `ScamCampaign` in `services.campaign_engine`.
- **Radial Distance & Ring**: Geometric mapping where Ring 1 (`CRITICAL`) represents outbreak states ($>400\%$ velocity increase), Ring 2 (`SURGING`) represents rapid acceleration ($>100\%$), and Ring 3 (`EMERGING`) tracks newly candidate clusters.
- **Blip Size**: Encodes aggregate victim impact and reporting volume.
- **Pulse Speed**: Directly represents real-time velocity (incidents per hour relative to campaign historical baseline).
- **Multimodal & Language Markers**: Indicates primary observed channels (`PHONE_CALL`, `WHATSAPP_SCREENSHOT`, `UPI_QR`) and linguistic profile (`Hindi`, `Hinglish`, `Bengali`).

## 2. Interactive Side Panel & Progressive Disclosure
Selecting any campaign node on the Radar immediately populates the context inspector:
- Lifecycle state (`EMERGING`, `ACTIVE`, `SURGING`, `OUTBREAK`, `RESURGING`)
- First seen and last updated timestamps
- Dominant Scam Journey flow
- 8-dimension ScamDNA profile
- Direct deep-links to `/campaigns/[id]` and the interactive Knowledge Graph.
