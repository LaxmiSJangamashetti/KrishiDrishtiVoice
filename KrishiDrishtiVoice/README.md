# KrishiDrishti Voice

Prototype multilingual voice assistant for Indian farmers, built for the Gnani AI Great Indian AI Internship Challenge 2026.

## Current status

The app includes Gnani Prisma v2.5 speech-to-text and a local, deterministic, source-attributed tomato knowledge base for Karnataka-focused triage. It distinguishes symptoms from diagnoses and does not provide pesticide doses.

## Run

```powershell
& "D:\AI-Projects\Python-Environments\KrishiDrishtiVoice\Scripts\Activate.ps1"
streamlit run app.py
```

Initial UI languages are English and Kannada. Audio recording/upload controls are available when supported by the installed Streamlit runtime.

The tomato knowledge engine normalizes English and Kannada text, ranks transparent keyword matches, asks follow-up questions, and returns source references. Kannada descriptions are left pending review where verified translations are not available.

## Safety

This prototype does not provide confirmed diagnoses, pesticide doses, guaranteed yield predictions, or full offline voice functionality. API credentials belong in `.env`, which is ignored by Git.
