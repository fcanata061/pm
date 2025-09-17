from core import database, logger

def search(query: str = "", group: str = None):
    """
    Busca pacotes pelo nome ou grupo.
    :param query: string a buscar
    :param group: nome do grupo para filtrar
    """
    results = []

    # Buscar todos os pacotes disponíveis
    if group:
        pkgs = database.get_group_packages(group)
    else:
        pkgs = database.get_all_packages()

    for pkg in pkgs:
        name = pkg.get("nome")
        version = pkg.get("versao", "N/A")
        desc = pkg.get("descricao", "")
        installed = database.is_installed(name)
        mark = "[✔]" if installed else "[ ]"

        if query.lower() in name.lower():
            results.append(f"{mark} {name}-{version}: {desc}")

    if results:
        logger.info("🔍 Resultados da busca:")
        for r in results:
            print(r)
    else:
        logger.warn("Nenhum pacote encontrado para sua busca.")
