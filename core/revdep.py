import os
import subprocess
from core import logger, database, build, dependency

LIB_DIRS = ["/usr/lib", "/usr/lib64", "/lib", "/lib64"]

def run():
    logger.info("Rodando revdep: verificando bibliotecas ausentes...")

    broken_bins = []

    # varrer todos os binários conhecidos
    for pkg in database.list_installed():
        recipe = database.get_recipe(pkg)
        if not recipe:
            continue
        bin_path = recipe.get("bin_path", [])
        for b in bin_path:
            if not os.path.exists(b):
                continue
            try:
                output = subprocess.check_output(["ldd", b], text=True)
                for line in output.splitlines():
                    if "not found" in line:
                        logger.warn(f"{b} (pacote {pkg}) depende de {line.strip()}")
                        broken_bins.append(pkg)
            except Exception as e:
                logger.debug(f"Erro ao checar {b}: {e}")

    broken_bins = list(set(broken_bins))
    if not broken_bins:
        logger.info("Nenhum problema encontrado! ✅")
        return

    logger.warn(f"Pacotes com dependências quebradas: {broken_bins}")

    # Resolver dependências e recompilar
    ordered = dependency.topological_sort(broken_bins)
    for pkg in ordered:
        logger.info(f"Recompilando {pkg} para corrigir dependências...")
        build.rebuild_package(pkg)
