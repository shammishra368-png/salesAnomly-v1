@echo off
title Retail Anomaly Engine -- System Verification Check
color 0a
cd /d "%~dp0"

echo =====================================================================
echo        RETAIL SALES AND INVENTORY LIVE ANOMALY ENGINE
echo               SYSTEM VERIFICATION AND HEALTH CHECK
echo                 DEVELOPED BY: KRISHNA (B.TECH CSE)
echo =====================================================================
echo.

:: Detect Python executable
set PY_EXE=python
if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" (
    set PY_EXE="%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
)

%PY_EXE% verify_live_detection.py

echo.
pause
