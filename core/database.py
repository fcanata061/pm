import os
import sqlite3
from core import logger

DB_PATH = "/var/lib/pm/packages.db"

def init():
    """Inicializa o banco de dados se não existir"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS packages (
        name TEXT NOT NULL,
        version TEXT NOT NULL,
        description TEXT,
        bin_path TEXT,
        build_deps TEXT,
        run_deps TEXT,
        PRIMARY KEY (name)
    )
    """)
    conn.commit()
    conn.close()

def add_package(recipe: dict):
    """Adiciona um pacote ao banco"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO packages (name, version, description, bin_path, build_deps, run_deps)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        recipe["nome"],
        recipe["versao"],
        recipe.get("descricao", ""),
        ",".join(recipe.get("bin_path", [])),
        ",".join(recipe.get("dependencias_build", [])),
        ",".join(recipe.get("dependencias_runtime", []))
    ))
    conn.commit()
    conn.close()
    logger.info(f"Pacote {recipe['nome']} registrado no database.")

def remove_package(name: str):
    """Remove pacote do banco"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM packages WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    logger.info(f"Pacote {name} removido do database.")

def get_package(name: str):
    """Retorna informações de um pacote"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM packages WHERE name = ?", (name,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            "nome": row[0],
            "versao": row[1],
            "descricao": row[2],
            "bin_path": row[3].split(",") if row[3] else [],
            "dependencias_build": row[4].split(",") if row[4] else [],
            "dependencias_runtime": row[5].split(",") if row[5] else [],
        }
    return None

def list_installed():
    """Lista todos os pacotes instalados"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name, version FROM packages ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return [{"nome": r[0], "versao": r[1]} for r in rows]

def is_installed(name: str) -> bool:
    """Checa se pacote está instalado"""
    return get_package(name) is not None
