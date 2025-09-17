import os
import subprocess
import tempfile
import yaml

from core import database, logger, utils, build, remove

def install(recipe_path: str, sandbox: str = "/tmp/pm_sandbox"):
    """
    Instala um pacote a partir de uma receita YAML.
    """
    logger.info(f"📦 Iniciando instalação usando {recipe_path}")

    # --- 1. Carregar receita ---
    with open(recipe_path, "r") as f:
        recipe = yaml.safe_load(f)

    nome = recipe["nome"]
    versao = recipe["versao"]

    if database.is_installed(nome):
        logger.warn(f"{nome}-{versao} já está instalado.")
        return

    # --- 2. Resolver dependências ---
    logger.info("🔗 Resolvendo dependências...")
    for dep in recipe.get("dependencias_build", []):
        if not database.is_installed(dep):
            dep_path = utils.find_recipe(dep)
            if dep_path:
                install(dep_path, sandbox=sandbox)
            else:
                logger.error(f"Dependência {dep} não encontrada!")
                return

    # --- 3. Hooks pre_install ---
    for cmd in recipe.get("hooks", {}).get("pre_install", []):
        logger.info(f"🔧 Executando hook pre_install: {cmd}")
        subprocess.run(cmd, shell=True, check=True)

    # --- 4. Construção do pacote ---
    logger.info("⚙️  Construindo pacote...")
    workdir = tempfile.mkdtemp(prefix=f"{nome}-build-", dir=sandbox)
    build.build(recipe, workdir)

    # --- 5. Instalação real ---
    logger.info("📥 Instalando no sistema...")
    # Exemplo simples: "make install DESTDIR=/"
    try:
        subprocess.run("make install", cwd=workdir, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro na instalação de {nome}: {e}")
        return

    # --- 6. Hooks post_install ---
    for cmd in recipe.get("hooks", {}).get("post_install", []):
        logger.info(f"🔧 Executando hook post_install: {cmd}")
        subprocess.run(cmd, shell=True, check=True)

    # --- 7. Registrar no database ---
    database.add_package(recipe)

    logger.success(f"✅ {nome}-{versao} instalado com sucesso!")
