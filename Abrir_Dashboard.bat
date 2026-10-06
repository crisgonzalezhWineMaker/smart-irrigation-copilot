@echo off
title Smart Irrigation Copilot - Visual Cockpit
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================================
echo   SMART IRRIGATION COPILOT - Visual Cockpit
echo   Iniciando servidor en http://localhost:8060
echo ========================================================
echo.
echo Presiona Ctrl+C para detener el servidor.
echo.

start "" http://localhost:8060/index.html
python "dashboard\server.py"
pause
