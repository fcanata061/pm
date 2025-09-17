from collections import defaultdict, deque
from core import database, logger

def build_dependency_graph(pkg_list):
    graph = defaultdict(list)
    indegree = defaultdict(int)

    for pkg in pkg_list:
        recipe = database.get_recipe(pkg)
        if not recipe:
            continue
        deps = recipe.get("dependencias_build", []) + recipe.get("dependencias_runtime", [])
        for dep in deps:
            graph[dep].append(pkg)
            indegree[pkg] += 1
            indegree.setdefault(dep, 0)
        indegree.setdefault(pkg, 0)

    return graph, indegree

def topological_sort(pkg_list):
    graph, indegree = build_dependency_graph(pkg_list)
    queue = deque([node for node in indegree if indegree[node] == 0])
    ordered = []

    while queue:
        node = queue.popleft()
        if node in pkg_list:  # só mantemos pacotes que pedimos
            ordered.append(node)
        for neighbor in graph[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    if len(ordered) != len(set(pkg_list)):
        logger.warn("Ciclo detectado nas dependências!")
    return ordered
