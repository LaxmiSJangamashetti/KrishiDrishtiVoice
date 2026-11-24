# Frontend Integration Audit

Status: `TESTED_WITH_MOCKS`

## Existing application

The project is a Streamlit application rooted at `app.py`. It already owns the working LU, Conversation Manager, agricultural retrieval, safety, Gnani STT/TTS, and farmer-facing testing dashboard.

## Supplied ZIP

The ZIP contains a Streamlit-compatible `farmer_profile` package with:

- `repository.py`: SQLite-backed farmer, farm, crop, consultation, notification, and profile operations.
- `ui.py`: bilingual dashboard, farmer profile, farms, crops, assistant, voice assistant, consultation history, notifications, settings, and help views.
- Repository tests and `.streamlit/config.toml`.

It is not a separate frontend framework or standalone build. The safest integration was to add the package and route it through the existing Streamlit sidebar, preserving the current voice-assistant dashboard and backend.

## Risks handled

- No `.env`, Gnani service, knowledge base, or existing app architecture was replaced.
- Profile data is stored locally in `data/krishidrishti_profiles.sqlite3`, now excluded by `.gitignore`.
- ZIP UI functions are routed only through the new Farmer profile workspace.
- Live voice behavior remains unvalidated by policy.
