@echo off
title Retail Anomaly Live Detection Launcher
color 0b
cd /d "%~dp0"

echo =====================================================================
echo    Starting Retail Anomaly Engine Live Dashboard...
echo =====================================================================
echo.

:: 1. Check if backend live server is already running
curl -s http://127.0.0.1:5000/api/status >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Starting Live Python Engine in background...
    wscript.exe "%~dp0start_server_background.vbs"
    timeout /t 2 /nobreak >nul
)

:: 2. Launch browser - prefers live server, falls back to direct html
curl -s http://127.0.0.1:5000/api/status >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Live Detection Server is ACTIVE on 127.0.0.1:5000
    start "" "http://127.0.0.1:5000/"
) else (
    echo [OK] Opening Standalone Dashboard locally...
    start "" "%~dp0dashboard.html"
)

echo.
echo =====================================================================
echo  [SUCCESS] Dashboard is now running in your browser!
echo =====================================================================
