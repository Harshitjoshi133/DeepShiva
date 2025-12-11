@echo off
echo ========================================
echo Starting Deep-Shiva Backend Server
echo ========================================
echo.

cd server

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

@REM echo Installing dependencies...
@REM pip install -r requirements.txt

echo.
echo ========================================
echo Backend server starting on port 8000
echo API Docs: http://localhost:8000/docs
echo Monitoring: http://localhost:8000/api/v1/monitoring/stats
echo Log files: logs/ directory
echo ========================================
echo.

python run.py
