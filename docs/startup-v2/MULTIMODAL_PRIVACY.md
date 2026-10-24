# Multimodal Privacy Boundaries & Principles

## 1. Strict Privacy Guardrails
Multimodal evidence contains exceptionally sensitive user data (family photos, private chat conversations, bank account statements, voice samples). ScamGraph enforces five non-negotiable privacy boundaries:

1. **Zero Biometric Facial Recognition**: Images and screenshots are parsed strictly for text, layout, logos, and QR codes. No biometric face embedding or facial identification model is ever invoked.
2. **Zero Biometric Voiceprinting**: Audio files are transcribed for speech content and tactic timing. No acoustic voiceprints or speaker biometric profiles are stored or matched.
3. **Contact Harvesting Prevention**: Unrelated personal contacts or background family chat logs visible in screenshots are isolated and ignored; only fraud-related tactics, entities, and URLs are promoted to intelligence.
4. **No Public Media URLs**: Original audio recordings and screenshot images are stored in protected object storage with short-lived pre-signed URLs accessible only to authorized analysts.
5. **Victim Anonymity**: Network graphs and public/outbreak radar views display privacy-safe synthetic incident keys (`inc_xxxx`) and aggregated campaign trends, never victim PII.
