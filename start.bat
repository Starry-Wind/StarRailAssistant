@echo off
poetry -V >nul 2>nul
if errorlevel 9009 (
    echo Poetry is not installed. Please install Poetry first.
    pause
    exit /b
)
echo Installing dependencies using Poetry...
poetry install
echo Running the python script...
.venv\Scripts\python.exe Honkai_Star_Rail.py
