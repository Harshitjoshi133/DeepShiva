@echo off
echo ========================================
echo Starting Deep-Shiva Frontend
echo ========================================
echo.

cd client

if not exist node_modules (
    echo Installing dependencies...
    call npm install
)

echo.
echo ========================================
echo Frontend starting on port 5173
echo Open: http://localhost:5173
echo ========================================
echo.

call npm run dev
