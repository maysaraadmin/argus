@echo off
echo Starting Argus MVP API...
set PYTHONPATH=%~dp0src
cd /d "%~dp0"
python -m src.api.server
pause
