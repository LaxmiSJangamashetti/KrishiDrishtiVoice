# Task 10 Offline Readiness Report

Status: `IMPLEMENTED_NOT_TESTED` for full offline operation.

## Works locally without network

- Farmer profile persistence through SQLite.
- Farm and crop records.
- Text input.
- Deterministic LU.
- Deterministic keyword retrieval.
- Existing source-backed guidance and safety checks.
- Conversation state and follow-up logic.

## Requires network/external service

- Gnani Prisma STT.
- Gnani Timbre TTS.
- Microphone/browser capture support remains device-dependent.

When Gnani is unavailable, text input remains the supported fallback. The project does not claim full offline voice functionality and no large offline speech model was added.
