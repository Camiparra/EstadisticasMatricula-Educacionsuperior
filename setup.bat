@echo off
setlocal EnableDelayedExpansion

echo ================================================
echo  Estadisticas Matricula - Educacion Superior
echo  Setup local (Windows)
echo ================================================
echo.

:: --- Verificar Python ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    echo         Descargalo en https://www.python.org/downloads/
    echo         Marca "Add Python to PATH" al instalar.
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo [OK] Python %PY_VER% detectado.

:: --- Crear entorno virtual si no existe ---
if not exist "venv\" (
    echo.
    echo [1/3] Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo [OK] Entorno virtual creado en .\venv\
) else (
    echo [OK] Entorno virtual ya existe, se reutiliza.
)

:: --- Activar e instalar dependencias ---
echo.
echo [2/3] Instalando dependencias desde requirements.txt...
call venv\Scripts\activate.bat
pip install --upgrade pip --quiet
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Fallo la instalacion de dependencias.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.

:: --- Iniciar la aplicacion ---
echo.
echo [3/3] Iniciando la aplicacion Flask...
echo.
echo  URL local: http://127.0.0.1:5000
echo  Presiona Ctrl+C para detener el servidor.
echo.
python app.py

endlocal
