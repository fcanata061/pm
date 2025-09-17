from core import logger

def run():
    logger.info("Rodando revdep para encontrar libs quebradas...")
    # detectar libs ausentes
    # recompilar pacotes que dependem delas
