"""City diagram with Matplotlib, shared by main.py and report.py."""

from matplotlib.figure import Figure

# Same layout as the figure in the assignment PDF
POSITIONS = {
    "A": (0, 0),
    "B": (2, 1),
    "C": (5, 1),
    "D": (3, 0),
    "E": (2, -1),
    "F": (5, -1),
    "G": (7, 0),
}


def draw_graph(edges, path=None, disabled=()):
    """Figure with weights on streets, path in red and disabled streets dashed.

    edges: every street as (u, v, w); disabled: set of frozenset({u, v}).
    """
    path = path or []
    path_edges = {frozenset(pair) for pair in zip(path, path[1:])}
    fig = Figure(figsize=(9, 4.5))
    ax = fig.subplots()

    for u, v, w in edges:
        (x1, y1), (x2, y2) = POSITIONS[u], POSITIONS[v]
        key = frozenset((u, v))
        if key in path_edges:
            style = {"color": "#d62728", "linewidth": 4, "zorder": 2}
        elif key in disabled:
            style = {"color": "#bbbbbb", "linewidth": 1.5, "linestyle": "--", "zorder": 1}
        else:
            style = {"color": "#555555", "linewidth": 1.5, "zorder": 1}
        ax.plot([x1, x2], [y1, y2], **style)
        ax.text(
            (x1 + x2) / 2, (y1 + y2) / 2, f"{w:g}",
            ha="center", va="center", fontsize=11, zorder=4,
            bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "none"},
        )

    for node, (x, y) in POSITIONS.items():
        color = "#d62728" if node in path else "#1f77b4"
        ax.scatter(x, y, s=900, color=color, zorder=3)
        ax.text(x, y, node, ha="center", va="center", color="white",
                fontsize=13, fontweight="bold", zorder=5)

    ax.set_aspect("equal")
    ax.margins(0.08)
    ax.axis("off")
    fig.tight_layout()
    return fig
