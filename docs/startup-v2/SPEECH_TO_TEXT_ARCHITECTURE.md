# Speech-to-Text Architecture Specification

## 1. Provider Abstraction
ScamGraph abstracts speech-to-text processing via `SpeechToTextProvider`:
- `LocalSpeechToTextAdapter`: Lightweight local simulation and whisper-style adapter with time-segmented outputs.
- `CloudSTTProvider`: Production plug-in for scalable multilingual ASR (Whisper large-v3, IndicASR, Sarvam, Azure Speech).

## 2. Transcript Artifact Contract
Every speech processing invocation produces a canonical `TranscriptArtifact`:
- `transcript_id`: Deterministic ID linked to source audio artifact.
- `full_transcript`: Complete unified transcript text.
- `segments`: List of `AudioTranscriptSegment` with `start_ms`, `end_ms`, `text`, `confidence`, and `speaker_tag`.
- `primary_language`: Detected language (ISO 639-1 e.g., `hi`, `en`).
- `overall_confidence`: Aggregate transcription confidence.
- `provider`: Identifying provider name and model version.

Original audio media remains the authoritative source of truth; transcripts are strictly derived evidence.
