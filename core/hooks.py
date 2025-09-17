import subprocess
from core import logger
import os

def run(hook_type: str, recipe: dict = None, group: list = None):
    """
    Executa hooks de acordo com o tipo.
    
    hook_type: pre_build, post_build, pre_install, post_install, pre_remove, post_remove
    recipe: dicionário da receita do pacote
    group: lista de pacotes em caso de grupo
    """

    if recipe:
        # Hooks definidos na receita
        cmds = recipe.get("hooks", {}).get(hook_type, [])
        for cmd in cmds:
            execute(cmd, f"{recipe.get('nome')}:{hook_type}")

    if group:
        # Hooks definidos no grupo, opcional
        for pkg in group:
            recipe_pkg = pkg if isinstance(pkg, dict) else None
            if recipe_pkg:
                cmds = recipe_pkg.get("hooks", {}).get(hook_type, [])
                for cmd in cmds:
                    execute(cmd, f"{pkg.get('nome')}:{hook_type}")

def execute(cmd: str, context: str = ""):
    """
    Executa um comando de hook e loga saída e erros.
    """
    logger.info(f"🔧 Executando hook [{context}]: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True)
        logger.success(f"✅ Hook [{context}] executado com sucesso")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Hook [{context}] falhou: {e}")
