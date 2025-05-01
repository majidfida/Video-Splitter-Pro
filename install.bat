@echo off
setlocal enabledelayedexpansion

echo Creating venv...
python -m venv venv
call venv\Scripts\activate

echo Installing Python deps...
pip install --upgrade pip
pip install gradio torch torchvision ffmpeg-python

:: Bundle FFmpeg if not on PATH
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo Downloading FFmpeg...
    powershell -Command "Invoke-WebRequest -Uri https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip -OutFile ffmpeg.zip"
    powershell -Command "Expand-Archive ffmpeg.zip -DestinationPath .\ffmpeg"
)

echo Done. Run with: call venv\Scripts\activate && python video_splitter.py
pause