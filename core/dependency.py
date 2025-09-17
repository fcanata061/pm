from collections import defaultdict, deque
from core import database, logger

def get_dependencies(pkg_name: str, build: bool = True, use_flags: list = None):
    """
    Retorna a lista de dependências de um pacote considerando USE flags.
    :param pkg_name: nome do pacote
    :param build: se True considera dependências de build, senão runtime
    :param use_flags: lista de flags USE ativas
    """
    recipe = database.find_recipe(pkg_name)
    if not recipe:
        return []

    deps = []
    if build:
        deps.extend(recipe.get("dependencias_build", []))
    else:
        deps.extend(recipe.get("dependencias_runtime", []))

    # Adicionar dependências opcionais baseadas nas flags USE
    use_flags = use_flags or []
    for flag in recipe.get("flags_USE", []):
        if flag in use_flags:
            optional_deps = recipe.get("dependencias_opcionais", {}).get(flag, [])
            deps.extend(optional_deps)

    return list(set(deps))  # remover duplicatas


def topological_sort(pkg_names: list, use_flags: dict = None):
    """
    Ordena os pacotes em ordem de build considerando dependências.
    :param pkg_names: lista de nomes de pacotes
    :param use_flags: dict {pkg_name: [flags]} para dependências opcionais
    """
    use_flags = use_flags or {}
    graph = defaultdict(list)
    indegree = defaultdict(int)

    # Construir grafo
    for pkg in pkg_names:
        deps = get_dependencies(pkg, build=True, use_flags=use_flags.get(pkg, []))
        for dep in deps:
            graph[dep].append(pkg)
            indegree[pkg] += 1
        if pkg not in indegree:
            indegree[pkg] = indegree.get(pkg, 0)

    # Kahn's algorithm
    queue = deque([n for n in indegree if indegree[n] == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(indegree):
        raise RuntimeError("Ciclo detectado nas dependências!")

    return order


def revdep(pkg_name: str):
    """
    Retorna a lista de pacotes que dependem do pacote fornecido.
    """
    all_pkgs = database.get_all_packages()
    dependents = []

    for pkg in all_pkgs:
        deps = get_dependencies(pkg["nome"], build=True)
        deps += get_dependencies(pkg["nome"], build=False)
        if pkg_name in deps:
            dependents.append(pkg["nome"])

    return dependents


def find_orphans():
    """
    Retorna pacotes instalados que não são dependência de nenhum outro pacote.
    """
    installed = database.get_installed_packages()
    installed_names = [pkg["nome"] for pkg in installed]
    orphans = []

    for pkg in installed:
        dependents = revdep(pkg["nome"])
        if not dependents:
            orphans.append(pkg["nome"])

    return orphans
