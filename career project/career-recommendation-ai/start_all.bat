@echo off
echo ============================================================
echo Starting Full Explainable AI Career Recommendation System
echo ============================================================
echo.
echo Starting FastAPI Backend in new window...
start "Career AI Backend" cmd /k "run_backend.bat"

echo Waiting 3 seconds for backend initialization...
timeout /t 3 /nobreak >nul

echo Starting Next.js Frontend in new window...
start "Career AI Frontend" cmd /k "run_frontend.bat"

echo.
echo ============================================================
echo Application Launching!
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:3000
echo Swagger:  http://127.0.0.1:8000/docs
echo.
echo Demo Student: student@careerai.edu / Student@123
echo Demo Admin:   admin@careerai.edu   / Admin@123
echo ============================================================
pause
