@echo off
echo ==========================================
echo   TRENDSAGE AI STARTUP
echo ==========================================
echo.

echo [1/3] Checking dependencies...
python -m pip install -r requirements.txt

echo.
echo [2/3] Starting TrendSage Engine (API)...
echo Dashboard will be available at http://localhost:8001
echo.
echo Press Ctrl+C to stop the server.
echo.

python api.py
pause
