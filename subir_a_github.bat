@echo off
chcp 65001 > nul
title Subir Smart Irrigation Copilot a GitHub
echo ========================================================
echo   💧 SUBIENDO SMART IRRIGATION COPILOT A GITHUB
echo   Repositorio: crisgonzalezhWineMaker/smart-irrigation-copilot
echo ========================================================
cd /d "%~dp0"

echo.
echo Verificando autenticación con GitHub...
gh auth status > nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Es necesario autenticar tu cuenta una sola vez en el navegador:
    gh auth login --web -h github.com -p https
    gh auth setup-git
)

echo.
echo Subiendo código al repositorio remoto...
git push -u origin main

echo.
if %errorlevel% equ 0 (
    echo ========================================================
    echo   🎉 ¡PROYECTO SUBIDO CON ÉXITO A GITHUB!
    echo   Visítalo en:
    echo   https://github.com/crisgonzalezhWineMaker/smart-irrigation-copilot
    echo ========================================================
) else (
    echo.
    echo [X] Ocurrió un inconveniente al subir el repositorio.
)
pause
