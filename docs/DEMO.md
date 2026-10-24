# Hackathon Demonstration Guide

## 1. Demo Objectives

The ScamGraph AI demonstration illustrates how the system:

1. Reconstructs the complete scam journey from the initial message to payment intent.
2. Correlates signals across multiple independent dimensions.
3. Refrains from declaring fraud on any single model's signal.
4. Correctly assigns dual-axis **Risk** and **Evidence Confidence** scores.
5. Reliably returns __`INSUFFICIENT_EVIDENCE`__ on benign or ambiguous interactions.
6. Renders the interactive directed Scam Journey Graph using Cytoscape.js.

---

## 2. Pre-Loaded Scenarios for Demo

### Scenario 1: Electricity Bill Disconnection Scam (High Risk, High Confidence)

- **Step 1 (SMS)**: Urgent disconnection alert from an unknown 10-digit number claiming to be "Electricity Officer".
- **Step 2 (URL Click)**: User clicks bit.ly shortened link resolving to brand new domain `mahavitaran-billupdate.info` (age: 1 day, flagged by TinyFish API).
- **Step 3 (Payment)**: Page instructs user to pay ₹10 update fee via UPI collect request from `billpay.officer@oksbi` (individual VPA, not corporate).
- **Outcome**: `Risk: HIGH`, `Evidence Confidence: HIGH`. System recommends Transaction Delay & Step-up confirmation.

### Scenario 2: Benign Customer Notification (Insufficient Evidence)

- **Step 1 (SMS)**: "Your electricity bill for Oct is generated. Pay before 28th to avoid late fees. Visit official portal."
- **Step 2 (URL Click)**: Official portal domain `mahadiscom.in` (age: 15 years, verified SSL).
- __Outcome__: `Risk: LOW`, `Evidence Confidence: LOW` / `INSUFFICIENT_EVIDENCE`. System triggers __ALLOW_SILENT__ (zero alert fatigue).

### Scenario 3: Novel Variant / Emerging Campaign

- **Step 1 (WhatsApp)**: Unsolicited task-based earnings invitation in Hinglish.
- **Step 2 (Telegram Redirect)**: Link to Telegram channel for "Crypto Task Verification".
- **Step 3 (Payment)**: Collect request for "refundable deposit".
- **Outcome**: Matches campaign cluster via pgvector embedding similarity (> 0.88).

---

## 3. Demo Walkthrough Steps

```bash {"metadata":"[object Object]"}
# 1. Start backend dependencies
docker compose up -d postgres neo4j

# 2. Run API service
cd services/api
uvicorn app.main:app --reload --port 8000

# 3. Start Next.js Frontend
cd apps/web
npm run dev

# 4. Open browser at http://localhost:3000
# - Navigate to /investigate to run a simulated journey
# - Explore the Cytoscape Scam Journey Graph
# - Inspect signal evidence breakdown in the Evidence drawer


```
