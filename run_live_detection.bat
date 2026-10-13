@echo off
title Retail Anomaly Engine -- Live Detection Server Launcher
color 0b
cd /d "%~dp0"

echo =====================================================================
echo       RETAIL SALES AND INVENTORY LIVE ANOMALY DETECTION ENGINE
echo         DUAL-ENGINE: SQL Z-SCORE + MACHINE LEARNING + WEBSOCKET
echo                  DEVELOPED BY: KRISHNA (B.TECH CSE)
echo =====================================================================
echo.

:: Detect Python executable
set PY_EXE=python
if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" (
    set PY_EXE="%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
)

:: Step 1: Ensure database exists
if not exist "retail.db" (
    echo [1/3] Generating initial retail database...
    %PY_EXE% generate_data.py
    %PY_EXE% setup_view.py
) else (
    echo [1/3] Checking SQLite database and SQL windowed views...
    %PY_EXE% setup_view.py
)

:: Step 2: Ensure dashboard.html is compiled and updated
echo [2/3] Building live-connected HTML dashboard...
%PY_EXE% build_html_dashboard.py
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Dashboard generation had warnings, proceeding...
)

:: Step 3: Launch Live Detection Engine Server and WebSockets
echo [3/3] Starting Live Detection Server on http://127.0.0.1:5000...
echo.
echo =====================================================================
echo   Live streaming active! Browser will open automatically.
echo   Press Ctrl+C in this console to stop the server at any time.
echo =====================================================================
echo.

%PY_EXE% live_detection_server.py --port 5000

pause
