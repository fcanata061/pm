from core import install, remove, database, logger, dependency

GROUPS = {
    "base": ["gcc", "binutils", "glibc", "linux-kernel"],
    "xorg": ["xorg-server", "xorg-apps", "mesa"],
    "dev": ["vim", "git", "python3", "rust"],
}

def install_group(group_name: str):
    """Instala todos os pacotes de um grupo"""
    if group_name not in GROUPS:
        logger.error(f"Grupo {group_name} não encontrado!")
        return

    logger.info(f"📦 Instalando grupo '{group_name}'")
    pkgs = GROUPS[group_name]

    # Resolver dependências topológicas do grupo
    ordered = dependency.topological_sort(pkgs)

    for pkg in ordered:
        recipe_path = database.find_recipe(pkg)
        if recipe_path:
            install.install(recipe_path)
        else:
            logger.warn(f"Receita de {pkg} não encontrada, pulando...")

    logger.success(f"✅ Grupo '{group_name}' instalado com sucesso!")

def remove_group(group_name: str, remove_orphans: bool = True):
    """Remove todos os pacotes de um grupo"""
    if group_name not in GROUPS:
        logger.error(f"Grupo {group_name} não encontrado!")
        return

    logger.info(f"🗑 Removendo grupo '{group_name}'")
    pkgs = GROUPS[group_name]

    # Remover na ordem inversa para não quebrar dependências
    ordered = dependency.topological_sort(pkgs)
    ordered.reverse()

    for pkg in ordered:
        remove.remove(pkg, remove_orphans=remove_orphans)

    logger.success(f"✅ Grupo '{group_name}' removido com sucesso!")
