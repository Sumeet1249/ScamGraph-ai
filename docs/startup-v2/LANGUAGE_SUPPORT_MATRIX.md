# ScamGraph AI — Language Support Matrix (Prompt 17 / Phase 5C)

## Canonical Support Tiers

| Tier | Definition | Operational SLA |
| :--- | :--- | :--- |
| **`PRODUCTION_VALIDATED`** | Gold set benchmarked, FPR $\le 0.5\%$, end-to-end regression verified, UI localization validated. | Full automated protection & emergency triage. |
| **`BETA`** | Script detection, Indic normalization, tactic rules, and semantic embeddings benchmarked. Evaluation data growing. | Full behavioral analysis with transparent confidence calibration. |
| **`EXPERIMENTAL`** | Lexicon heuristics and script mapping active; candidate transliteration available. | Monitored triage; analyst review flag recommended. |
| **`NORMALIZATION_ONLY`** | Deterministic Unicode NFKC, zero-width stripping, and entity token extraction supported. | Basic entity screening; higher behavioral confidence degraded. |
| **`UNSUPPORTED`** | Unrecognized character sets or non-Indic foreign languages. | Degrades to `PARTIAL_ANALYSIS`; NEVER returns false `SAFE`. |

---

## Language & Script Capabilities Matrix

| Dimension | English (`eng`) | Hindi (`hin`) | Hinglish (`hinglish`) | Bengali (`ben`) | Unsupported Foreign |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Support Tier** | `PRODUCTION_VALIDATED` | `PRODUCTION_VALIDATED` | `PRODUCTION_VALIDATED` | `BETA` | `UNSUPPORTED` |
| **Primary Script** | `LATIN` | `DEVANAGARI` | `LATIN` (+ mixed Devanagari) | `BENGALI` | Other / Non-Indic |
| **Code-Mixing Support** | Single-language | Code-mixed capable | First-class Code-Mix (Score $\ge 0.15$) | Code-mixed capable | N/A |
| **Input Understanding** | Direct & Presets | Direct & Presets | Direct & Presets | Direct & Presets | Fallback Tokenizer |
| **Script Detection** | Deterministic Unicode | Deterministic Unicode | Deterministic Mixed | Deterministic Unicode | Categorized `OTHER` |
| **Text Normalization** | ASCII / NFKC | NFKC, Elongation, Digits | Roman Hindi spelling, Slang collapse | NFKC, Bengali Digits, Spacing | Zero-width stripping only |
| **Amount Normalization** | `$`, `₹500`, `Rs 500` | `₹५००`, `५०० रुपये`, `५०० रुपया` | `500 rs`, `500 rupaye`, `500/-` | `৫০০ টাকা` $\to$ `₹500` | Preserved as raw string |
| **Security Token Preservation** | UPI, URLs, Phones, Handles | Preserved intact | Preserved intact | Preserved intact | RegEx extraction |
| **Protective Negation** | *"Never share OTP"* | *"अपना OTP साझा न करें"* | *"OTP kisi ko mat dena"* | *"OTP কাওকে দেবেন না"* | Degraded |
| **Tactic Ontology** | Universal (20 Tactics) | Universal (20 Tactics) | Universal (20 Tactics) | Universal (20 Tactics) | Conservative Rule Baseline |
| **Requested Actions** | Universal (16 Actions) | Universal (16 Actions) | Universal (16 Actions) | Universal (16 Actions) | Minimal Regex Baseline |
| **Journey Engine** | Full multi-turn | Full multi-turn | Full multi-turn | Full multi-turn | Degraded confidence |
| **Cross-Language Journey** | Seamless participant | Seamless participant | Seamless participant | Seamless participant | N/A |
| **ScamDNA Dimension Invariance** | Reference Baseline | High similarity ($>0.70$) | High similarity ($>0.75$) | Moderate similarity ($>0.65$) | Structural only |
| **Cross-Incident Correlation** | Entity + DNA + Journey | Entity + DNA + Journey | Entity + DNA + Journey | Entity + DNA + Journey | Entity overlap only |
| **Campaign Clustering** | Multi-Language Aware | Multi-Language Aware | Multi-Language Aware | Multi-Language Aware | Separate candidate |
| **Radar Representation** | Language mix breakdown | Language mix breakdown | Language mix breakdown | Language mix breakdown | Tagged `OTHER` |
| **Consumer Protect UI** | English localized | Hindi localized (`locales/hi`) | Selectable EN / HI guidance | Critical safety strings | Fallback English |
| **Rescue Emergency UI** | English localized | Hindi localized (`1930` exact) | English/Hindi selectable | Bengali emergency strings | Fallback English |
| **False Positive Rate (FPR)** | $\le 0.40\%$ | $\le 0.45\%$ | $\le 0.48\%$ | $\le 0.65\%$ (Beta) | N/A (Never False Safe) |
