@echo off
REM
REM

setlocal ENABLEDELAYEDEXPANSION
set TARGET=%1
if "%TARGET%"=="" (
    echo Available targets:
    echo   install           - Install dependencies from requirements.txt
    echo   init-db           - Initialize demo database
    echo   run               - Run Text-to-SQL demo query
    echo   benchmark-compare - Run benchmark on all providers
    echo   clean             - Remove cache files and artifacts
    echo   help              - Show this help message
    goto :eof
)

if /I "%TARGET%"=="install" (
    echo Installing dependencies...
    python -m pip install -r requirements.txt
    goto :eof
)

if /I "%TARGET%"=="init-db" (
    echo Initializing demo database...
    python scripts\init_demo_db.py
    goto :eof
)

if /I "%TARGET%"=="run" (
    echo Running Text-to-SQL demo query...
    python -m src.cli "How many tracks are there?" --provider naive
    goto :eof
)

if /I "%TARGET%"=="benchmark-compare" (
    echo Running benchmark on all providers...
    python -m scripts.benchmark_compare eval\spider_sample.json --db data\demo_music.sqlite --providers naive openai ollama --output-md docs\benchmark_results.md --output-csv eval\results.csv
    goto :eof
)

if /I "%TARGET%"=="clean" (
    echo Cleaning cache and artifacts...
    for /r %%i in (__pycache__) do if exist "%%i" rmdir /s /q "%%i"
    for /r %%i in (*.pyc) do del /f /q "%%i"
    for /r %%i in (*.pyo) do del /f /q "%%i"
    del /f /q .pytest_cache .coverage htmlcov 2>nul
    goto :eof
)

if /I "%TARGET%"=="help" (
    echo Available targets:
    echo   install           - Install dependencies from requirements.txt
    echo   init-db           - Initialize demo database
    echo   run               - Run Text-to-SQL demo query
    echo   benchmark-compare - Run benchmark on all providers
    echo   clean             - Remove cache files and artifacts
    echo   help              - Show this help message
    goto :eof
)

echo Unknown target: %TARGET%
echo Run without arguments to see available targets.