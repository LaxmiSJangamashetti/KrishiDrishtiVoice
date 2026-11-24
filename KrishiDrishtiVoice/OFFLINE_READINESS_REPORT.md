# Offline Readiness Report

## Works without network access

- SQLite profile, farm, crop, consultation, and notification storage.
- Deterministic text parsing, conversation state, safety validation, and tomato knowledge retrieval.
- Farmer dashboard rendering after local dependencies are installed.
- Image-result schema validation.

## Requires external service or human verification

- Gnani Prisma STT.
- Gnani Timbre TTS.
- Actual voice capture/transcription/audio playback validation.
- Any future model download, image inference, synchronization, or cloud backup.

Gnani failure must remain a recoverable farmer-facing error; text consultation is the offline fallback. The project does not provide full offline voice functionality.

## Next offline work

Benchmark a local STT/TTS option on target budget Android hardware only after an explicit model and licensing decision. Do not present it as operational before device testing.
