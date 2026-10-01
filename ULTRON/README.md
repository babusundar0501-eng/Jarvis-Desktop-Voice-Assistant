# ULTRON Desktop Assistant

A real Windows desktop ULTRON-style voice assistant.

## Features
- Futuristic red/black desktop HUD
- Wake word: Ultron
- Speech recognition
- Gemini AI brain
- Windows app and website launching
- Web search
- Local JSON memory
- Windows text-to-speech
- Phone identity: +65 8123 8904
- Windows tel: and sms: handoff
- No hand tracking
- No smart-device integrations
- No Home Assistant

## Run
Install Python 3.11 on Windows, then run ULTRON/run.bat.

On first run, the script creates a virtual environment, installs dependencies and creates ULTRON/.env from ULTRON/.env.example.

Put your Gemini API key into GEMINI_API_KEY in ULTRON/.env.

## Build the Windows app
Run ULTRON/build.bat to create ULTRON/dist/ULTRON.exe.

GitHub Actions also builds the Windows executable automatically when ULTRON files change. The artifact is named ULTRON-Windows.

## Phone
The configured phone identity is +65 8123 8904. Call and SMS buttons use Windows tel: and sms: links. Actual calling or messaging depends on a compatible communications app and connected phone service.

Optional SMSpva variables are included for future provider-specific integration. Do not commit API keys.

## Security
Never commit .env, API keys, access tokens or private credentials.