@echo off
echo.
echo  ==========================================
echo    AI Career Assistant Bot - Starting...
echo  ==========================================
echo.

cd /d "%~dp0"

call venv\Scripts\activate

echo  [OK] Virtual environment activated.
echo  [OK] Starting bot... Press Ctrl+C to stop.
echo.

python bot.py

echo.
echo  Bot stopped. Press any key to exit.
pause >nul
