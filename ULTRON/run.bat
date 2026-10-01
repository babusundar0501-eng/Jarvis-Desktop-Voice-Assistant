@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3.11 -m venv .venv
  if errorlevel 1 (
    echo Python 3.11 is required. Install Python 3.11 and run this again.
    pause
    exit /b 1
  )
)
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
if not exist ".env" copy ".env.example" ".env"
python -m pip install -r requirements.txt
python ultron.py
pause
