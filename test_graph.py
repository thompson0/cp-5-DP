"""Run with: python test_graph.py"""

from graph import EDGES, NODES, create_graph, explain_change, shortest_route, simple_paths


def test_graph_representation():
    graph = create_graph(EDGES)
    assert set(graph) == set(NODES)
    assert sum(len(neighbors) for neighbors in graph.values()) == 24  # 12 streets x 2 ways
    for u, v, w in EDGES:
        assert (v, w) in graph[u] and (u, w) in graph[v]


def test_required_cases():
    cases = [
        ("A", "G", ["A", "D", "G"], 5),
        ("G", "A", ["G", "D", "A"], 5),  # swapped origin and target
        ("A", "C", ["A", "D", "B", "C"], 6),
        ("E", "C", ["E", "D", "B", "C"], 8),
        ("E", "G", ["E", "F", "G"], 5),
    ]
    for origin, target, path, distance in cases:
        assert shortest_route(EDGES, origin, target) == (path, distance), (origin, target)


def test_matches_brute_force_and_is_symmetric():
    graph = create_graph(EDGES)
    for origin in NODES:
        for target in NODES:
            _, distance = shortest_route(EDGES, origin, target)
            best = min(cost for _, cost in simple_paths(graph, origin, target))
            assert distance == best, (origin, target)
            assert distance == shortest_route(EDGES, target, origin)[1]


def test_same_origin_and_target():
    assert shortest_route(EDGES, "C", "C") == (["C"], 0)


def test_changed_weight_and_disabled_street():
    heavier = [(u, v, 6 if (u, v) == ("D", "G") else w) for u, v, w in EDGES]
    assert shortest_route(heavier, "A", "G") == (["A", "D", "F", "G"], 6)
    without_dg = [e for e in EDGES if e[:2] != ("D", "G")]
    assert shortest_route(without_dg, "A", "G") == (["A", "D", "F", "G"], 6)
    weights = {frozenset((u, v)): w for u, v, w in EDGES}
    text = explain_change(["A", "D", "G"], 5, ["A", "D", "F", "G"], 6, weights, {frozenset("DG")})
    assert "D-G foi desativada" in text


def test_no_path():
    isolated_a = [e for e in EDGES if "A" not in e[:2]]
    assert shortest_route(isolated_a, "A", "G") == (None, float("inf"))


if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_"):
            test()
            print("ok", name)
