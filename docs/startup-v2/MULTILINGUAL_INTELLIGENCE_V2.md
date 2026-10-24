# ScamGraph AI — India Multilingual Intelligence V2

## Executive Summary & Product Architecture (Prompt 17 / Phase 5C)

In India's digital payments and messaging ecosystem, fraud campaigns operate seamlessly across languages, scripts, and colloquial mixtures. A digital-arrest or task scam campaign does not change its manipulative essence merely because one message is typed in English, another in Devanagari Hindi, another in Roman-script Hinglish, and another in Bengali.

**ScamGraph AI V2** rejects naive translation or siloed per-language classifiers in favor of an **invariant behavioral architecture**:
```
RAW USER MESSAGE
       │
       ▼
Deterministic Script Detection (Latin, Devanagari, Bengali, Mixed)
       │
       ▼
Language & Code-Mixing Profiler (Hinglish, Hindi, English, Bengali)
       │
       ▼
Indic Text Normalization (Unicode NFKC, zero-width stripping, elongation collapse, currency & security preservation)
       │
       ▼
Protective Negation Guard (Mandatory distinction: demand vs. legitimate advisory)
       │
       ▼
Derived Transliteration & Lexicon-Guided Supporting Translation
       │
       ▼
Language-Independent Behavioral Features (Tactics, Requested Actions, Entities, Amounts)
       │
       ▼
Multi-Turn Scam Journey Engine (Single coherent journey across language switches)
       │
       ▼
ScamDNA V3 Behavioral Fingerprinting (Cross-language similarity invariance)
       │
       ▼
Cross-Incident Correlation & Multi-Language Campaign Clustering
       │
       ▼
Unified Risk Assessment & Localized Consumer Interventions (Protect / Guard / Rescue)
```

---

## 1. Core Operating Principles

1. **Language $\neq$ Script $\neq$ Locale**:
   - Latin script is NOT assumed to be English (it can be Roman Hindi / Hinglish or Roman Bengali).
   - Devanagari script is NOT assumed to be pure standard Hindi.
   - Code-mixing (e.g. *"Sir verification complete karne ke liye abhi 5000 pay karo"*) is treated as a first-class language profile (`hinglish` with an interpretable `code_mix_score`), never forcibly collapsed into English or rejected as corrupted text.
2. **Immutability of Original Evidence**:
   - `original_text` is permanently preserved unaltered in forensic storage.
   - Derived forms (`normalized_text`, `transliterated_text`, `translated_text`, `semantic_input_text`) are stored alongside in `MultilingualTextRepresentation`.
   - Never replace `artifact.text = translated_text`.
3. **Mandatory Negation Distinction**:
   - Fraud demand: *"Share your OTP right now"* / *"अभी अपना ओटीपी बताएं"* $\to$ `ActionRequestedType.SHARE_OTP` + `TacticType.CREDENTIAL_PRESSURE`.
   - Legitimate bank advisory: *"SBI never asks for your OTP. Do not disclose PIN to anyone."* / *"अपना OTP किसी के साथ साझा न करें"* $\to$ `is_protective_advisory = True` $\to$ credential pressure suppressed, false positive avoided.
4. **Language Is Not Risk**:
   - Being written in Hindi, Hinglish, or Bengali never increases or decreases the scam risk score.
   - Language support level affects **analysis confidence** and **completeness**, never risk probability.

---

## 2. Integrated Multilingual Components

| Component | Location | Role |
| :--- | :--- | :--- |
| `ScriptDetector` | `services/language_intelligence/script_detector.py` | Deterministic Unicode block identification (`LATIN`, `DEVANAGARI`, `BENGALI`, `MIXED`). |
| `IndicTextNormalizer` | `services/language_intelligence/normalizer.py` | NFKC normalization, zero-width stripping, elongation collapse, currency normalization (`500 rs`, `५०० रुपये` $\to$ `₹500`), security token preservation (UPI, URLs, handles, phones). |
| `LanguageIntelligenceDetector` | `services/language_intelligence/detector.py` | Multi-script token analysis, Hinglish Roman Hindi classification, code-mix index calculation. |
| `ProtectiveNegationEngine` | `services/language_intelligence/negation.py` | Explicit recognition of warnings against credential disclosure across English, Hindi, Hinglish, and Bengali. |
| `TransliterationAdapter` | `services/language_intelligence/transliteration.py` | Non-destructive Devanagari $\leftrightarrow$ Roman candidate generation for semantic embedding alignment. |
| `TranslationAdapter` | `services/language_intelligence/translation.py` | Supporting domain-preserving translation (protects `OTP`, `UPI`, `KYC`, `digital arrest`, `task`). |
| `LanguageIntelligenceService` | `services/language_intelligence/service.py` | Orchestrates analysis and outputs language-independent `BehavioralFeatureSet`. |

---

## 3. Runtime Verification & Test Coverage

All 15 comprehensive unit and regression tests in `tests/unit/test_multilingual_intelligence_step17.py` passed with 100% green status:
- **Test 1**: Deterministic script detection across Devanagari, Bengali, Latin, and Mixed scripts.
- **Test 2**: Language and code-mixing detection (Hindi, English, Hinglish, Bengali).
- **Test 3**: Indic text normalization preserving raw UPI IDs, URLs, and handles.
- **Test 4**: Amount normalization across `₹500`, `500 rs`, `500 rupees`, `500 rupaye`, `५०० रुपये`.
- **Test 5**: Mandatory negation distinction between fraudulent demands and protective advisories.
- **Test 6**: Legitimate bank security advisory collision avoidance (SBI OTP warning $\neq$ scam).
- **Test 7**: Non-destructive transliteration candidate generation.
- **Test 8**: Multi-turn cross-language conversation (English $\to$ Hinglish $\to$ Hindi $\to$ Hinglish) unified into a single coherent `ScamJourney`.
- **Test 9**: Cross-language `ScamDNA` behavioral similarity invariance ($>0.70$ similarity).
- **Test 10**: Cross-language campaign continuity (aggregating English, Hindi, and Hinglish incidents into one cluster).
- **Test 11**: Language-only negative test (unrelated Hindi electricity scam and matrimonial scam do NOT correlate on language alone).
- **Test 12**: Digital arrest behavioral feature extraction in Hindi/Hinglish (`AUTHORITY`, `ISOLATION`, `SECRECY`, `DO_NOT_DISCONNECT`).
- **Test 13**: Rescue triage in Hindi retaining exact `1930` emergency dialer and prioritized steps.
- **Test 14**: Graceful degradation on unsupported foreign languages with `PARTIAL_ANALYSIS`.
- **Test 15**: Unicode homoglyph, confusable, and zero-width character evasion resistance.
