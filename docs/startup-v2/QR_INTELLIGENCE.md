# QR Code Intelligence Specification

## 1. Role in Fraud & Safe Extraction
QR codes are heavily leveraged in payment scams (fake courier delivery fees, task job deposits, OLX advance payments, electricity bill reconnect fees).

### Absolute Safety Rules:
1. **Never Auto-Execute**: Decoded UPI URIs (`upi://pay`) and web URLs are strictly parsed into structured data. No automatic payment intents or browser redirects are ever triggered.
2. **Safe UPI Parsing**:
   - `pa`: Payee VPA / address (canonical payment entity)
   - `pn`: Payee display name (treated as an unverified CLAIM, never trusted identity)
   - `am`: Encoded amount (parsed if explicitly set)
   - `cu`: Currency (typically INR)
   - `tn`: Transaction note / memo
   - `mc`: Merchant category code
   - `tr`: Transaction reference
3. **Reputation & Graph Feed**: The extracted UPI VPA feeds canonical `EntityIntelligenceService` and `GraphEdge` resolution. No disjoint QR blacklist is constructed; it shares the single ScamGraph entity graph.
