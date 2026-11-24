# Frontend–Backend Integration Report

Status: `TESTED_WITH_MOCKS`

## Integrated paths

- Existing Farmer experience remains connected to Conversation Manager, LU, safety, retrieval, guidance, and optional Gnani TTS.
- New Farmer profile workspace loads `farmer_profile.ui` and initializes the local repository.
- Profile, farms, crops, consultations, notifications, and settings use the repository module rather than hardcoded sample data.
- Profile language and voice settings are available in the imported UI; the existing advisory language controls remain unchanged.

## Verification

- Farmer profile repository tests passed.
- Streamlit AppTest rendered the default app without exception.
- Streamlit AppTest rendered the Farmer profile workspace without exception and exposed farm/crop actions.
- Streamlit HTTP smoke test passed with HTTP 200.
