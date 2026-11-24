# KrishiDrishti Voice

Prototype multilingual voice assistant for Indian farmers, built for the Gnani AI Great Indian AI Internship Challenge 2026.

## Current status

The app includes Gnani Prisma v2.5 speech-to-text, five-crop text guidance, experimental tomato/potato/maize image inference, Farm Monitoring, and Mandi Market Prices. It distinguishes symptoms from diagnoses and does not provide pesticide doses. Crop-only cultivation, productivity, irrigation, market and weather questions are separated from disease retrieval; missing verified coverage is reported rather than inferred.

## Run

```powershell
& "D:\AI-Projects\Python-Environments\KrishiDrishtiVoice\Scripts\python.exe" -m streamlit run "D:\AI-Projects\AI-Development\KrishiDrishtiVoice\app.py" --server.port 8501
```

Open `http://localhost:8501` or use `--server.port 8502` if needed. The health endpoint is `/_stcore/health`. The sidebar provides the Farmer experience, Farmer profile workspace, Farm Monitoring, and Mandi Market Prices. Farm coordinates are stored in SQLite when the database is writable.

Initial advisory languages are English and Kannada. The sidebar uses a visible radio language control so the selected value remains readable under theme/browser CSS. Audio recording/upload controls are available when supported by the installed Streamlit runtime. Hindi TTS configuration exists in the service layer but is not presented as fully live-validated.

The tomato knowledge engine normalizes English and Kannada text, ranks transparent keyword matches, asks follow-up questions, and returns source references. Kannada descriptions are left pending review where verified translations are not available.

## Safety

This prototype does not provide confirmed diagnoses, pesticide doses, guaranteed yield predictions, or full offline voice functionality. API credentials belong in `.env`, which is ignored by Git.

## Tests

```powershell
& "D:\AI-Projects\Python-Environments\KrishiDrishtiVoice\Scripts\python.exe" -B -m unittest discover -s tests -q
& "D:\AI-Projects\Python-Environments\KrishiDrishtiVoice\Scripts\python.exe" -B -m compileall -q .
```

Text understanding, profile storage, deterministic retrieval, safety, mocked voice services, conversation state, and Streamlit AppTest coverage are offline-testable. Gnani STT/TTS, microphone permissions, transcript accuracy, network latency, and audible playback require an authorized human-device test.
