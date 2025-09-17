from core import database

def run(query):
    installed = database.list_installed()
    # simulação: match simples
    for pkg in ["gcc", "glibc", "firefox"]:
        mark = "[✓]" if pkg in installed else "[ ]"
        if query in pkg:
            print(f"{mark} {pkg}")

def info(pkg):
    recipe = database.get_recipe(pkg)
    if recipe:
        print(f"Nome: {recipe['nome']}")
        print(f"Versão: {recipe['versao']}")
        print(f"Descrição: {recipe['descricao']}")
