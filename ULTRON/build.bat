@echo off
cd /d "%~dp0"
call run.bat
.venv\Scripts\python.exe -m pip install pyinstaller
.venv\Scripts\pyinstaller.exe --noconfirm --clean --onefile --windowed --name ULTRON ultron.py
echo Built: ULTRON\dist\ULTRON.exe
pause
