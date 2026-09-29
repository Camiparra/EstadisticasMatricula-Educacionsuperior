#!/usr/bin/env bash
set -euo pipefail

echo "================================================"
echo " Estadisticas Matricula - Educacion Superior"
echo " Setup local (Linux / macOS)"
echo "================================================"
echo

# --- Verificar Python 3 ---
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] python3 no encontrado."
    echo "        Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "        macOS (Homebrew): brew install python"
    exit 1
fi

PY_VER=$(python3 --version 2>&1 | awk '{print $2}')
echo "[OK] Python $PY_VER detectado."

# --- Crear entorno virtual si no existe ---
if [ ! -d "venv" ]; then
    echo
    echo "[1/3] Creando entorno virtual..."
    python3 -m venv venv
    echo "[OK] Entorno virtual creado en ./venv/"
else
    echo "[OK] Entorno virtual ya existe, se reutiliza."
fi

# --- Activar e instalar dependencias ---
echo
echo "[2/3] Instalando dependencias desde requirements.txt..."
# shellcheck disable=SC1091
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt
echo "[OK] Dependencias instaladas."

# --- Iniciar la aplicacion ---
echo
echo "[3/3] Iniciando la aplicacion Flask..."
echo
echo "  URL local: http://127.0.0.1:5000"
echo "  Presiona Ctrl+C para detener el servidor."
echo
python app.py
