@echo off
rem Crea el entorno de Python e instala las dependencias. Correr una sola vez.
cd /d "%~dp0"
where py >nul 2>nul || (echo Falta Python 3.11 o superior: https://www.python.org/downloads/ & pause & exit /b 1)
if not exist venv\Scripts\python.exe (
  py -3 -m venv venv || (echo No pude crear el entorno. & pause & exit /b 1)
)
venv\Scripts\python.exe -m pip install --upgrade pip >nul
venv\Scripts\python.exe -m pip install -r requirements.txt || (echo Fallo la instalacion. & pause & exit /b 1)
if not exist SimConnect.dll if not exist SimConnect2024.dll (
  echo.
  echo Falta SimConnect.dll: copiala del SDK de MSFS 2024 ^(SimConnect SDK\lib\SimConnect.dll^) a esta carpeta.
)
echo.
echo Listo. Para usarlo: doble click en iniciar_vibracion.bat
pause
