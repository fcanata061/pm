from core import logger

def run_build(recipe, rebuild=False):
    logger.info(f"Sandbox: preparando ambiente para {recipe['nome']}...")
    # criar diretórios isolados, permissões, fakeroot
    # gerar dinamicamente mozconfig/Makefile se precisar
    # aplicar patches
    # compilar com paralelismo
    if rebuild:
        logger.debug("Rodando em modo REBUILD")
