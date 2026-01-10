@echo off
echo Starting Argus MVP Development Environment...
echo.
echo 1. Starting API Server...
start "Argus API" cmd /k "cd /d %~dp0 && start_api.bat"
timeout /t 3 /nobreak >nul
echo.
echo 2. Starting Streamlit UI...
start "Argus UI" cmd /k "cd /d %~dp0 && start_ui.bat"
echo.
echo 3. Opening browser...
timeout /t 5 /nobreak >nul
start http://localhost:8501
echo.
echo Argus MVP is starting...
echo API: http://localhost:8000
echo UI:  http://localhost:8501
echo API Docs: http://localhost:8000/docs
echo.
pause
