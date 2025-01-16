@echo off
echo Activating virtual environment...
call .venv\Scripts\activate

echo Setting PYTHONPATH...
set PYTHONPATH=%PYTHONPATH%;%CD%

echo Starting the bot...
py src/bot/bot.py

pause