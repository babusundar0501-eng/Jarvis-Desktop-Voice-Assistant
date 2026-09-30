# ULTRON 2.0 — Windows AI Assistant

A modular desktop voice assistant built from the existing Jarvis foundation.

## Current core
- Wake word: ULTRON
- Speech recognition
- Natural-language Gemini fallback
- Text-to-speech
- Open websites / web search
- Date and time
- Windows Calculator
- Screenshots
- Environment-variable secrets (never commit your API key)

## Quick start (Windows)
1. Install Python 3.11+.
2. Create a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   py -m pip install -r requirements-ultron.txt
   ```
3. Copy `.env.example` to `.env` and set `GEMINI_API_KEY`.
4. Run `py ultron.py`.
5. Say **ULTRON open YouTube**, **ULTRON what time is it**, or ask a general question.

## Roadmap
- Live HUD dashboard
- Push-to-talk and wake-word modes
- Computer vision and gesture controls
- Safe computer-control tools with confirmations
- Smart-home integrations
- Phone/SMS provider adapters
- LiveKit real-time voice mode
- Plugin architecture
- Persistent local memory
- GitHub Actions tests and packaging

Security: never put API keys, phone credentials, or device tokens into source code. Use environment variables or a secrets manager.
