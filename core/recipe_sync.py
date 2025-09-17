import os
import subprocess
from core import database, logger

def fetch_git_version(repo_url, branch="main"):
    """
    Obtém a última versão de um repositório Git.
    Retorna a tag mais recente ou commit hash.
    """
    try:
        cmd = ["git", "ls-remote", "--tags", repo_url]
        output = subprocess.check_output(cmd, universal_newlines=True)
        tags = []
        for line in output.splitlines():
            ref = line.split("\t")[1]
            if "refs/tags/" in ref:
                tags.append(ref.replace("refs/tags/", ""))
        if tags:
            # Ordena tags numericamente se possível
            tags.sort(key=lambda x: [int(p) if p.isdigit() else p for p in x.split(".")])
            return tags[-1]
        else:
            # Nenhuma tag → retornar commit hash do branch
            cmd_branch = ["git", "ls-remote", repo_url, branch]
            branch_hash = subprocess.check_output(cmd_branch, universal_newlines=True)
            return branch_hash.split()[0]
    except Exception as e:
        logger.error(f"Erro ao obter versão do git {repo_url}: {e}")
        return None

def fetch_https_version(url):
    """
    Obtém a versão mais recente de um tarball ou página de release.
    Para simplificação, apenas pega a versão do arquivo.
    """
    import re
    import requests

    try:
        response = requests.get(url)
        response.raise_for_status()
        # Extrai versão do arquivo via regex
        matches = re.findall(r"\d+\.\d+(\.\d+)?", url)
        if matches:
            return matches[-1]
    except Exception as e:
        logger.error(f"Erro ao obter versão via HTTPS {url}: {e}")
    return None

def sync_recipe(recipe):
    """
    Sincroniza a receita para a versão mais nova.
    Atualiza o database se encontrar nova versão.
    """
    name = recipe["nome"]
    current_version = recipe["versao"]
    latest_version = None

    urls = recipe.get("urls", {})
    if "git" in urls:
        latest_version = fetch_git_version(urls["git"])
    elif "tarball" in urls:
        latest_version = fetch_https_version(urls["tarball"])

    if latest_version and latest_version != current_version:
        logger.info(f"🆕 Nova versão encontrada para {name}: {current_version} → {latest_version}")
        # Atualiza o database
        database.update_package_version(name, latest_version)
        return True
    else:
        logger.info(f"{name} já está na versão mais recente ({current_version})")
        return False

def sync_all(recipes=None):
    """
    Sincroniza todas as receitas ou uma lista específica.
    """
    recipes = recipes or database.get_all_packages()
    updated_packages = []

    for recipe in recipes:
        if sync_recipe(recipe):
            updated_packages.append(recipe["nome"])

    if updated_packages:
        logger.info(f"📦 Pacotes atualizados no database: {', '.join(updated_packages)}")
    else:
        logger.info("✅ Todas as receitas estão atualizadas")
