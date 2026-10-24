# Adversarial Samples (`data/adversarial/`)

## Intended Purpose
Evasive variations of scam messages designed to bypass standard keyword filters and classical classifiers:
- Homoglyph and character substitutions (`13ank`, `K.Y.C`, `Aadh@ar`)
- Zero-width spaces and obfuscated phone/handle formats
- Phonetic Hindi/regional transliterations designed to slip past English dictionaries
- QR-bearing and image-embedded text variations

## Governance Rules
1. Kept for model robustness evaluation and adversarial benchmarking.
2. Must not be used as the sole basis for training without balanced representation.
