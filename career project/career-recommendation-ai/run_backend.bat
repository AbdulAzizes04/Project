@echo off
echo ============================================================
echo Starting Career AI Recommendation Backend (FastAPI on :8000)
echo ============================================================
set PYTHONPATH=%~dp0;%~dp0backend;%~dp0ml;%PYTHONPATH%
cd /d "%~dp0backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
