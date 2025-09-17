import subprocess
from core import database, logger, hooks, dependency

def remove(pkg_name: str, remove_orphans: bool = True):
    """
    Remove um pacote do sistema e atualiza o banco de dados.
    """

    if not database.is_installed(pkg_name):
        logger.warn(f"Pacote {pkg_name} não está instalado.")
        return

    # --- 1. Carregar receita ---
    recipe = database.get_package(pkg_name)
    if not recipe:
        logger.error(f"Receita de {pkg_name} não encontrada!")
        return

    # --- 2. Hooks pré-removal ---
    for cmd in recipe.get("hooks", {}).get("pre_remove", []):
        logger.info(f"🔧 Executando hook pre_remove: {cmd}")
        subprocess.run(cmd, shell=True, check=True)

    # --- 3. Remover arquivos ---
    # Exemplo genérico: se houver "install_path" na receita
    install_paths = recipe.get("install_path", [])
    for path in install_paths:
        logger.info(f"🗑 Removendo {path}...")
        subprocess.run(f"rm -rf {path}", shell=True, check=True)

    # --- 4. Remover do banco de dados ---
    database.remove_package(pkg_name)
    logger.success(f"✅ Pacote {pkg_name} removido do database.")

    # --- 5. Hooks pós-removal ---
    for cmd in recipe.get("hooks", {}).get("post_remove", []):
        logger.info(f"🔧 Executando hook post_remove: {cmd}")
        subprocess.run(cmd, shell=True, check=True)

    # --- 6. Detectar e remover órfãos ---
    if remove_orphans:
        logger.info("🔎 Verificando pacotes órfãos...")
        orphans = database.find_orphans()
        if orphans:
            logger.info(f"Pacotes órfãos detectados: {orphans}")
            for orphan in orphans:
                remove(orphan, remove_orphans=False)
        else:
            logger.info("Nenhum pacote órfão detectado.")
