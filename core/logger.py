import sys
import datetime
import os

LOG_FILE = "/var/log/pm.log"

# Cores ANSI para terminal
COLORS = {
    "DEBUG": "\033[94m",    # Azul
    "INFO": "\033[97m",     # Branco
    "WARN": "\033[93m",     # Amarelo
    "ERROR": "\033[91m",    # Vermelho
    "SUCCESS": "\033[92m",  # Verde
    "ENDC": "\033[0m"       # Reset
}

def _log(level: str, msg: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    colored = f"{COLORS.get(level,'')}{level}{COLORS['ENDC']}"
    line = f"[{timestamp}] [{colored}] {msg}"
    print(line)
    # Append em arquivo de log
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] [{level}] {msg}\n")
    except Exception as e:
        print(f"[WARN] Não foi possível escrever no arquivo de log: {e}")

# Funções de log por nível
def debug(msg: str):
    _log("DEBUG", msg)

def info(msg: str):
    _log("INFO", msg)

def warn(msg: str):
    _log("WARN", msg)

def error(msg: str):
    _log("ERROR", msg)

def success(msg: str):
    _log("SUCCESS", msg)
