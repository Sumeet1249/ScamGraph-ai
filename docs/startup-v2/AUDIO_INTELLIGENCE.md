# Audio & Voice Intelligence Specification

## 1. Core Mission: Behavioral Understanding Over Deepfake Hype
The primary objective of ScamGraph Audio Intelligence is:
**UNDERSTAND WHAT THE CALLER IS DOING AND ASKING THE USER TO DO.**

Deepfake detection alone is insufficient: real humans perpetrate high-loss digital arrest and task scams, and benign synthetic voices exist in customer service. ScamGraph focuses on behavioral manipulation tactics and requested action analysis.

## 2. Pipeline Execution
1. **Audio Validation**: Security checks on container (`audio/mpeg`, `audio/wav`, `audio/ogg`, `audio/mp4`), file size ($\le 50$ MB), and format integrity.
2. **Speech-to-Text**: Segmented transcription with millisecond timestamps (`start_ms`, `end_ms`), speaker tags (`SPEAKER_A`, `SPEAKER_B`), and confidence scores.
3. **Indic & Multilingual Analysis**: Integration with Prompt 17 for Hindi, Hinglish code-mixed, and Bengali speech.
4. **Tactic Timeline**: Pinpointing exact timestamps where authority claims, secrecy demands, legal threats, or payment pressure occur.
5. **Requested Actions & Negation Protection**: Extracting actions (`SEND_PAYMENT`, `SHARE_OTP`, `DO_NOT_DISCONNECT`, `KEEP_SECRET`) with strict negation checking.
6. **Bounded Synthetic Signal**: Providing a calibrated `SyntheticMediaSignal` (`NO_STRONG_SIGNAL`, `POSSIBLE_SYNTHETIC`, `NOT_ANALYZED`) with safe-action verification guidance rather than speculative verdicts.
