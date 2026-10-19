"""City graph data, shortest path algorithm and route explanations. No Streamlit or Matplotlib here."""

import heapq

NODES = {
    "A": "Depósito",
    "B": "Cruzamento B",
    "C": "Cruzamento C",
    "D": "Cruzamento D",
    "E": "Cruzamento E",
    "F": "Cruzamento F",
    "G": "Cliente",
}

# Two-way streets: (from, to, distance in km)
EDGES = [
    ("A", "B", 4),
    ("A", "D", 2),
    ("A", "E", 7),
    ("B", "C", 3),
    ("B", "D", 1),
    ("C", "D", 6),
    ("C", "G", 5),
    ("D", "E", 4),
    ("D", "F", 2),
    ("D", "G", 3),
    ("E", "F", 3),
    ("F", "G", 2),
]


def create_graph(edges):
    """Adjacency list {node: [(neighbor, weight), ...]}, each street stored both ways."""
    graph = {node: [] for node in NODES}
    for u, v, w in edges:
        graph[u].append((v, w))
        graph[v].append((u, w))
    return graph


def dijkstra(graph, origin, target):
    """Return (dist, prev): shortest known distance and predecessor of each node."""
    dist = {node: float("inf") for node in graph}
    prev = {node: None for node in graph}
    dist[origin] = 0
    heap = [(0, origin)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue  # stale entry, u was already reached by a shorter path
        if u == target:
            break  # target distance is final once popped
        for v, w in graph[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                prev[v] = u
                heapq.heappush(heap, (dist[v], v))
    return dist, prev


def rebuild_path(prev, origin, target):
    """Walk predecessors back from target. None when target is unreachable."""
    path = [target]
    while path[-1] != origin:
        node = prev[path[-1]]
        if node is None:
            return None
        path.append(node)
    return path[::-1]


def shortest_route(edges, origin, target):
    """(path, distance) from origin to target, or (None, inf) when there is no path."""
    dist, prev = dijkstra(create_graph(edges), origin, target)
    return rebuild_path(prev, origin, target), dist[target]


def simple_paths(graph, origin, target, path=None):
    """Brute force: yield every (path, cost) without repeated nodes. Used to prove minimality."""
    path = path or [origin]
    if path[-1] == target:
        yield path, 0
        return
    for v, w in graph[path[-1]]:
        if v not in path:
            for rest, cost in simple_paths(graph, origin, target, path + [v]):
                yield rest, cost + w


ORIGINAL_WEIGHTS = {frozenset((u, v)): w for u, v, w in EDGES}


def format_route(path):
    return " → ".join(path)


def explain_change(original_path, original_distance, path, distance, weights, disabled):
    """Text comparing the route on the original map with the route after edits."""
    if path == original_path:
        return (f"A rota não mudou: {format_route(path)} continua sendo a menor "
                f"(antes {original_distance:g} km, agora {distance:g} km).")

    changes = []
    for u, v in zip(original_path, original_path[1:]):
        key = frozenset((u, v))
        if key in disabled:
            changes.append(f"a rua {u}-{v} foi desativada")
        elif weights[key] != ORIGINAL_WEIGHTS[key]:
            changes.append(f"a rua {u}-{v} mudou de {ORIGINAL_WEIGHTS[key]:g} para {weights[key]:g} km")

    text = f"Rota original: {format_route(original_path)} ({original_distance:g} km). "
    if not changes:
        return text + ("Nenhuma rua do caminho original mudou, mas outra rua ficou mais "
                       f"curta e criou um caminho melhor: {format_route(path)} ({distance:g} km).")
    text += "No caminho original, " + "; ".join(changes) + ". "
    if any(frozenset(pair) in disabled for pair in zip(original_path, original_path[1:])):
        text += "Esse caminho deixou de existir"
    else:
        old_cost = sum(weights[frozenset(pair)] for pair in zip(original_path, original_path[1:]))
        text += f"Esse caminho agora custaria {old_cost:g} km"
    return text + f", então o Dijkstra escolheu {format_route(path)} ({distance:g} km)."
