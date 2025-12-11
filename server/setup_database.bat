@echo off
echo === Deep-Shiva Database Setup ===
echo.

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Initializing database...
python init_db.py

echo.
echo Setup complete! You can now start the server with:
echo python run.py
echo.
echo Or check database status with:
echo python db_utils.py

pause