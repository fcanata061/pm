from core import database, sandbox, logger, hooks, dependency

def install(pkg):
    logger.info(f"Instalando {pkg}...")
    recipe = database.get_recipe(pkg)
    if not recipe:
        logger.warn(f"Receita de {pkg} não encontrada!")
        return

    deps = recipe.get("dependencias_build", []) + recipe.get("dependencias_runtime", [])
    ordered = dependency.topological_sort(deps + [pkg])
    logger.debug(f"Ordem de instalação: {ordered}")

    for p in ordered:
        rec = database.get_recipe(p)
        if not rec:
            logger.warn(f"Receita de {p} não encontrada! Pulando...")
            continue
        sandbox.run_build(rec)
        database.add(p)

def remove(pkg):
    logger.warn(f"Removendo {pkg}...")
    hooks.run("pre_remove", pkg)
    database.remove(pkg)
    hooks.run("post_remove", pkg)

def rebuild_system():
    logger.info("Reconstruindo todo o sistema (@world)...")
    world = database.list_installed()
    ordered = dependency.topological_sort(world)
    logger.debug(f"Ordem de compilação: {ordered}")
    for pkg in ordered:
        rebuild_package(pkg)

def rebuild_package(pkg):
    logger.info(f"Recompilando {pkg}...")
    recipe = database.get_recipe(pkg)
    if recipe:
        sandbox.run_build(recipe, rebuild=True)
        database.add(pkg)

def remove_orphans():
    logger.info("Removendo pacotes órfãos...")
    orphans = database.find_orphans()
    for pkg in orphans:
        remove(pkg)
