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
echo Chat AI: http://localhost:8000/api/v1/chat/query
echo Ollama Status: http://localhost:8000/api/v1/chat/ollama/status
echo Monitoring: http://localhost:8000/api/v1/monitoring/stats
echo Log files: logs/ directory
echo ========================================
echo.
echo Note: Make sure Ollama is running (ollama serve)
echo Default model: gemma2:2b
echo.

python run.py
