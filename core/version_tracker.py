from core import database, logger

# Pacotes críticos (não atualizados automaticamente, apenas aviso)
CRITICAL_PACKAGES = ["gcc", "glibc", "linux-kernel", "xorg-server"]

def get_installed_versions():
    """
    Retorna um dicionário {nome_pacote: versão_instalada} de todos os pacotes instalados.
    """
    installed = database.get_installed_packages()
    return {pkg["nome"]: pkg["versao"] for pkg in installed}

def get_latest_versions():
    """
    Retorna um dicionário {nome_pacote: versão_mais_recente} de todas as receitas.
    """
    all_recipes = database.get_all_packages()
    return {pkg["nome"]: pkg.get("versao", "N/A") for pkg in all_recipes}

def check_for_updates():
    """
    Compara versões instaladas com as mais recentes e retorna pacotes que precisam de atualização.
    """
    installed = get_installed_versions()
    latest = get_latest_versions()

    updates = []
    for name, version in installed.items():
        latest_version = latest.get(name)
        if latest_version and latest_version != version:
            updates.append((name, version, latest_version))
    return updates

def display_updates():
    """
    Mostra no terminal quais pacotes têm nova versão.
    """
    updates = check_for_updates()
    if not updates:
        logger.info("✅ Todos os pacotes estão atualizados.")
        return

    for name, current, latest in updates:
        if name in CRITICAL_PACKAGES:
            logger.warn(f"⚠ Pacote crítico {name} tem nova versão: {current} → {latest} (não será atualizado automaticamente)")
        else:
            logger.info(f"🔄 Pacote opcional {name} pode ser atualizado: {current} → {latest}")

def update_package(name):
    """
    Atualiza um pacote específico se não for crítico.
    """
    if name in CRITICAL_PACKAGES:
        logger.warn(f"⚠ Pacote crítico {name} não será atualizado automaticamente")
        return

    latest_version = get_latest_versions().get(name)
    installed_version = get_installed_versions().get(name)

    if not latest_version:
        logger.warn(f"Receita de {name} não encontrada")
        return

    if latest_version == installed_version:
        logger.info(f"{name} já está atualizado ({installed_version})")
        return

    recipe = database.find_recipe(name)
    if recipe:
        from core import install
        logger.info(f"🔄 Atualizando {name}: {installed_version} → {latest_version}")
        install.install(recipe)
    else:
        logger.warn(f"Receita de {name} não encontrada, atualização abortada")
