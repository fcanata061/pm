from core import database, sandbox, logger, hooks

def install(pkg):
    logger.info(f"Instalando {pkg}...")
    recipe = database.get_recipe(pkg)
    sandbox.run_build(recipe)
    database.add(pkg)

def remove(pkg):
    logger.warn(f"Removendo {pkg}...")
    hooks.run("pre_remove", pkg)
    database.remove(pkg)
    hooks.run("post_remove", pkg)

def rebuild_system():
    logger.info("Reconstruindo todo o sistema (@world)...")
    world = database.list_installed()
    ordered = resolve_dependencies(world)
    for pkg in ordered:
        rebuild_package(pkg)

def rebuild_package(pkg):
    logger.info(f"Recompilando {pkg}...")
    recipe = database.get_recipe(pkg)
    sandbox.run_build(recipe, rebuild=True)

def remove_orphans():
    logger.info("Removendo pacotes órfãos...")
    orphans = database.find_orphans()
    for pkg in orphans:
        remove(pkg)

def resolve_dependencies(pkg_list):
    logger.debug("Resolvendo dependências topológicas...")
    return pkg_list  # placeholder
