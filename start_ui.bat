@echo off
echo Starting Argus MVP UI...
set PYTHONPATH=%~dp0src
cd /d "%~dp0"
streamlit run src/ui/app.py --server.address=0.0.0.0 --server.port=8501
pause
