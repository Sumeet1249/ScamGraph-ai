# Rescue Privacy, Security & IDOR Protections (Phase 5B)

## Data Sensitivity & Protections
Post-loss rescue data contains high-sensitivity PII: victim account numbers, payment receipts, screenshots of private chats, and Aadhaar/PAN references.

1. **Non-Enumerable Incident IDs**:
   - Incident IDs use cryptographic 16-character hex salts (`inc_...`) generated via CSPRNG.
   - Prevents sequential enumeration attacks (IDOR).
2. **Deterministic Masking**:
   - All exported case packages and client-facing API responses mask sensitive account and phone numbers.
   - Transaction references retain only last 4 digits (`UTR-****9012`).
3. **No Unauthenticated Public URLs**:
   - Case packages are generated dynamically for the current authenticated victim session.
   - No public link generation by default.
4. **Cross-Victim Privacy Barrier**:
   - Correlation engine projects suspect entities into the graph as cluster candidates, but strictly obscures any victim identity or other incident IDs from the user.
