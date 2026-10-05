@echo off
title Smart Irrigation Copilot - Visual Cockpit
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================================
echo   💧 Iniciando Visual Cockpit · Smart Irrigation Copilot
echo ========================================================
echo Abriendo en tu navegador predeterminado...
echo Localhost: http://localhost:8060/index.html
echo.

python "dashboard\server.py"
pause
