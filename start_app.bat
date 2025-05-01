@echo off
setlocal enabledelayedexpansion

echo Creating venv (if needed)...
if not exist venv (
    python -m venv venv
)

echo Activating venv...
call venv\Scripts\activate

echo Launching Video Splitter Pro...
python video_splitter.py

pause
