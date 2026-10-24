# Rescue Case Package & Export Architecture (Phase 5B)

## Package Specification
The `RescueCasePackage` structures all incident observations into a standardized technical format ready for submission to 1930, the National Cyber Crime Reporting Portal (NCRP), and commercial banks.

### Key Sections:
1. **Case Summary & IDs**: Stable incident ID, generation timestamp, engine version.
2. **User-Reported Facts**: Explicitly delineated from automated inferences.
3. **Loss Summary**: Itemized payment table with UTR, method, and amounts.
4. **Timeline**: Chronological sequence of encounter, payment, and response events.
5. **Suspect Identifiers**: Contact phone numbers, URLs, Telegram handles, and claimed organizations.
6. **ScamGraph Analysis**: Inferred scam typology, psychological manipulation tactics, and correlated campaign signals.
7. **Evidence Manifest**: Table of preserved files with SHA-256 hashes.
8. **Copyable Summary**: One-click formatted text block designed to paste directly into official reporting forms.
9. **Legal Disclaimer**:
   > "This document is a technical Incident Information Package prepared based on user-provided statements and ScamGraph AI automated analysis. It does NOT constitute an official Police FIR, Government Cybercrime Registration, or guarantee of fund recovery. It is designed to assist victims in filing accurate, structured reports with verified authorities and banking institutions."
