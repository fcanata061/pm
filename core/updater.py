from core import database, install, logger

# Pacotes críticos que apenas avisam quando há nova versão
CRITICAL_PACKAGES = ["gcc", "glibc", "linux-kernel", "xorg-server"]

def check_updates():
    """
    Verifica atualizações para todos os pacotes instalados.
    """
    installed = database.get_installed_packages()
    updates_available = []

    for pkg in installed:
        latest_version = database.get_latest_version(pkg["nome"])
        if latest_version and latest_version != pkg["versao"]:
            updates_available.append((pkg["nome"], pkg["versao"], latest_version))

    if not updates_available:
        logger.info("✅ Todos os pacotes estão atualizados.")
        return

    for name, current, latest in updates_available:
        if name in CRITICAL_PACKAGES:
            logger.warn(f"⚠ Pacote crítico {name} tem nova versão: {current} → {latest} (não será atualizado automaticamente)")
        else:
            logger.info(f"🔄 Atualizando {name}: {current} → {latest}")
            recipe = database.find_recipe(name)
            if recipe:
                install.install(recipe)
            else:
                logger.warn(f"Receita de {name} não encontrada, pulando atualização.")

def update_group(group_name: str):
    """
    Atualiza todos os pacotes de um grupo.
    """
    pkgs = database.get_group_packages(group_name)
    if not pkgs:
        logger.warn(f"Grupo {group_name} não encontrado ou vazio")
        return

    for pkg in pkgs:
        latest_version = database.get_latest_version(pkg["nome"])
        if latest_version and latest_version != pkg["versao"]:
            logger.info(f"🔄 Atualizando {pkg['nome']}: {pkg['versao']} → {latest_version}")
            recipe = database.find_recipe(pkg["nome"])
            if recipe:
                install.install(recipe)
            else:
                logger.warn(f"Receita de {pkg['nome']} não encontrada, pulando atualização.")
