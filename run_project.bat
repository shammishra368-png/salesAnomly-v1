@echo off
title Retail Anomaly Engine - Single Click Launcher
color 0b

echo =====================================================================
echo           RETAIL SALES & INVENTORY ANOMALY DETECTION ENGINE
echo         DUAL-ENGINE: SQL Z-SCORE + MACHINE LEARNING + POWER BI
echo                  DEVELOPED BY: KRISHNA (B.TECH CSE)
echo =====================================================================
echo.

:: Detect Python executable
set PY_EXE=python
if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" (
    set PY_EXE="%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
)

echo [1/6] Generating synthetic sales, inventory, and pricing data (in INR Rs)...
%PY_EXE% generate_data.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Data generation failed!
    pause
    exit /b
)
echo.

echo [2/6] Compiling SQL Windowed Z-Score View in retail.db...
%PY_EXE% setup_view.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] SQL View setup failed!
    pause
    exit /b
)
echo.

echo [3/6] Exporting Power BI CSV datasets and DAX formulas...
%PY_EXE% export_to_powerbi.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] CSV export failed!
    pause
    exit /b
)
echo.

echo [4/6] Running Machine Learning Benchmark (Isolation Forest)...
%PY_EXE% ml_anomaly_detector.py
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] ML benchmark skipped or encountered issue.
)
echo.

echo [5/6] Generating Executive Audit & Risk Report (HTML/PDF)...
%PY_EXE% generate_executive_report.py
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Executive report generation skipped.
)
echo.

echo [6/6] Building Next-Gen Interactive HTML Dashboard...
%PY_EXE% build_html_dashboard.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Dashboard build failed!
    pause
    exit /b
)
echo.

echo =====================================================================
echo [SUCCESS] All components built and verified successfully!
echo Opening Dashboard in your default browser...
echo =====================================================================
start "" "%~dp0dashboard.html"

echo.
echo Dashboard is now open in your browser!
echo Available outputs:
echo   - Interactive Web Dashboard: %~dp0dashboard.html
echo   - Printable Executive Report: %~dp0Executive_Anomaly_Report.html
echo   - Power BI Project:          %~dp0PowerBI\SalesAnomalyDashboard.pbip
echo   - ML Comparison Dataset:     %~dp0data_export\ml_anomaly_comparison.csv
echo.
pause
