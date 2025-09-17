import os
import shutil
import subprocess
import tempfile
from core import database, logger, hooks, dependency, utils

def build(recipe: dict, sandbox_dir: str = "/tmp/pm_sandbox", rebuild=False, parallel_jobs: int = 4):
    """
    Constrói um pacote dentro de um sandbox.
    """

    nome = recipe["nome"]
    versao = recipe["versao"]
    logger.info(f"⚙️  Iniciando build de {nome}-{versao}")

    # --- 1. Criar sandbox ---
    workdir = tempfile.mkdtemp(prefix=f"{nome}-build-", dir=sandbox_dir)
    logger.debug(f"📂 Sandbox criada em {workdir}")

    # --- 2. Hooks pré-build ---
    for cmd in recipe.get("hooks", {}).get("pre_build", []):
        logger.info(f"🔧 Executando hook pre_build: {cmd}")
        subprocess.run(cmd, shell=True, check=True, cwd=workdir)

    # --- 3. Download e extração ---
    tarball = recipe.get("urls", {}).get("tarball")
    if tarball:
        utils.download_and_extract(tarball, workdir)

    # --- 4. Aplicar patches se houver ---
    for patch in recipe.get("patches", []):
        patch_path = utils.find_patch(patch)
        if patch_path:
            logger.info(f"📌 Aplicando patch {patch}")
            subprocess.run(f"patch -p1 < {patch_path}", shell=True, cwd=workdir, check=True)

    # --- 5. Configuração / geração de arquivos build ---
    tipo_build = recipe.get("tipo_build", "autotools")
    if tipo_build == "mozconfig":
        mozconfig_content = utils.generate_mozconfig(recipe)
        with open(os.path.join(workdir, "mozconfig"), "w") as f:
            f.write(mozconfig_content)
    elif tipo_build == "autotools":
        configure_cmd = "./configure"
        logger.info(f"⚙️  Configurando com {configure_cmd}")
        subprocess.run(configure_cmd, shell=True, cwd=workdir, check=True)

    # --- 6. Compilação ---
    make_cmd = f"make -j{parallel_jobs}"
    logger.info(f"🏗 Compilando {nome} com '{make_cmd}'")
    subprocess.run(make_cmd, shell=True, cwd=workdir, check=True)

    # --- 7. Hooks pós-build ---
    for cmd in recipe.get("hooks", {}).get("post_build", []):
        logger.info(f"🔧 Executando hook post_build: {cmd}")
        subprocess.run(cmd, shell=True, check=True, cwd=workdir)

    # --- 8. Instalação dentro do sandbox (DESTDIR) ---
    destdir = recipe.get("destdir", "/")  # pode ser sandbox para testes
    logger.info(f"📥 Instalando temporariamente em {destdir}")
    subprocess.run(f"make install DESTDIR={destdir}", shell=True, cwd=workdir, check=True)

    # --- 9. Registrar no database ---
    if not rebuild:
        database.add_package(recipe)
        logger.success(f"✅ Pacote {nome}-{versao} registrado no database")

    # --- 10. Limpeza ---
    if recipe.get("clean_after_build", True):
        shutil.rmtree(workdir)
        logger.debug(f"🧹 Sandbox {workdir} removida")
