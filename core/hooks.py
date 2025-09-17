from core import logger

def run(hook_type, pkg):
    logger.debug(f"Executando hook {hook_type} para {pkg}...")
    # hooks podem estar definidos na receita (inline ou externos)
