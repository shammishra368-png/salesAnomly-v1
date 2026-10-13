@echo off
title Actual Live Data Viewer - Retail Detection Engine
color 0a
cd /d "%~dp0"

set "PY_EXE=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
if not exist "%PY_EXE%" set "PY_EXE=python"

:top
cls
"%PY_EXE%" show_actual_live_data.py --limit 20

echo.
echo =====================================================================
echo  Export file: %~dp0data_export\actual_live_data.csv
echo  Press any key to refresh with latest incoming records (Ctrl+C to exit)
echo =====================================================================
pause >nul
goto top
