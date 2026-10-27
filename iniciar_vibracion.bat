@echo off
rem Vibracion realista URSA MINOR (joystick + acelerador). Cerrar esta ventana apaga los motores.
cd /d "%~dp0"
title Vibracion URSA - cerrar esta ventana para apagar
if not exist venv\Scripts\python.exe (echo Primero corre instalar.bat & pause & exit /b 1)
venv\Scripts\python.exe vibracion.py
pause
