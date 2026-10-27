@echo off
rem Para desarrollo: crea el entorno de Python e instala las dependencias. Usuarios: bajar el .exe de Releases.
cd /d "%~dp0"
where py >nul 2>nul || (echo Falta Python 3.11 o superior: https://www.python.org/downloads/ & pause & exit /b 1)
if not exist venv\Scripts\python.exe (
  py -3 -m venv venv || (echo No pude crear el entorno. & pause & exit /b 1)
)
venv\Scripts\python.exe -m pip install --upgrade pip >nul
venv\Scripts\python.exe -m pip install -r requirements.txt || (echo Fallo la instalacion. & pause & exit /b 1)
echo.
echo Listo. Para usarlo desde el codigo: iniciar_vibracion.bat (consola) o venv\Scripts\pythonw.exe bandeja.py
pause
