#!/bin/bash

#interrompe lo script in caso di errori imprevisti
set -e

echo "   AVVIO APPLICAZIONE WEBCAM OPENCV  "

#cerca sistema operativo
#check della variabile interna $OSTYPE di Bash
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS_CORRENTE="Windows"
    CMD_PYTHON="python"
else
    OS_CORRENTE="Linux/Mac"
    CMD_PYTHON="python3"
fi

echo "-> Sistema operativo rilevato: $OS_CORRENTE"

#check se c'è python
if ! command -v $CMD_PYTHON &> /dev/null; then
    echo "Errore: Python ($CMD_PYTHON) non è installato o non è nel PATH."
    echo "Per favore, installa Python prima di procedere."
    exit 1
fi
#gestione venv separato per os
if [ "$OS_CORRENTE" == "Windows" ]; then
    NOME_VENV=".venv"
else
    NOME_VENV=".venv_linux"
fi

if [ ! -d "$NOME_VENV" ]; then
    echo "-> Configurazione iniziale: Creazione ambiente virtuale ($NOME_VENV)..."
    $CMD_PYTHON -m venv $NOME_VENV
fi

#attivazione venv
if [ "$OS_CORRENTE" == "Windows" ]; then
    source .venv/Scripts/activate
else
    source .venv_linux/bin/activate
fi

echo "-> Ambiente virtuale ($NOME_VENV) attivato con successo."

#verifica e aggiornamento dipendenze
if [ -f "requirements.txt" ]; then
    echo "-> Verifica e installazione delle librerie da requirements.txt..."
    $CMD_PYTHON -m pip install --upgrade pip --disable-pip-version-check || echo "Avviso: Aggiornamento pip saltato..."
    $CMD_PYTHON -m pip install -r requirements.txt
else
    echo "⚠️ Avviso: 'requirements.txt' non trovato!"
    $CMD_PYTHON -m pip install opencv-python numpy
fi

#esegue
echo "-> Lancio di main.py in corso..."
$CMD_PYTHON main.py


#chiusura
deactivate
echo "Applicazione chiusa correttamente."