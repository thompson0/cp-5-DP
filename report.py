"""Build report.pdf from the real algorithm output. Run with: python report.py"""

import io
from pathlib import Path

from fpdf import FPDF

from draw import draw_graph
from graph import EDGES, NODES, create_graph, explain_change, shortest_route, simple_paths

HERE = Path(__file__).parent
CASES = [("A", "G"), ("G", "A"), ("A", "C"), ("E", "C"), ("E", "G")]
# (title, origin, target, changed weights, disabled streets)
SCENARIOS = [
    ("Trânsito: rua D-G passa de 3 para 6 km", "A", "G", {frozenset("DG"): 6}, set()),
    ("Obra: rua D-G desativada", "A", "G", {}, {frozenset("DG")}),
    ("Rua fora da rota: C-G passa de 5 para 50 km", "A", "G", {frozenset("CG"): 50}, set()),
    ("A isolado: ruas A-B, A-D e A-E desativadas", "A", "G", {},
     {frozenset("AB"), frozenset("AD"), frozenset("AE")}),
]


def latin1(text):
    """Built-in PDF fonts only cover Latin-1."""
    return text.replace("→", "->").replace("—", "-")


class Report(FPDF):
    def keep_together(self, height=100):
        """Start a new page so a heading is not split from its figure."""
        if self.get_y() + height > self.page_break_trigger:
            self.add_page()

    def heading(self, text):
        self.set_font("Helvetica", "B", 13)
        self.ln(3)
        self.cell(0, 8, latin1(text), new_x="LMARGIN", new_y="NEXT")

    def paragraph(self, text):
        self.set_font("Helvetica", size=10)
        self.multi_cell(0, 5.5, latin1(text), markdown=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def grid(self, rows, col_widths):
        self.set_font("Helvetica", size=9)
        with self.table(width=sum(col_widths), col_widths=col_widths, align="LEFT",
                        text_align="LEFT", line_height=5.5) as table:
            for row in rows:
                table.row([latin1(str(cell)) for cell in row])
        self.ln(2)

    def screenshot_grid(self, shots, box_h=118):
        """Two screenshots per row, each scaled to fit its box, so captions stay with images."""
        gap = 6
        box_w = (self.epw - gap) / 2
        for i, shot in enumerate(shots):
            col = i % 2
            if col == 0:
                if self.get_y() + box_h + 8 > self.page_break_trigger:
                    self.add_page()
                top = self.get_y()
            x = self.l_margin + col * (box_w + gap)
            self.set_font("Helvetica", "B", 9)
            self.set_xy(x, top)
            self.cell(box_w, 5, latin1(shot.stem))
            self.image(str(shot), x=x, y=top + 6, w=box_w, h=box_h, keep_aspect_ratio=True)
            if col == 1 or i == len(shots) - 1:
                self.set_xy(self.l_margin, top + box_h + 10)

    def figure(self, fig):
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", dpi=150)
        self.image(buffer, w=self.epw * 0.85, x=self.l_margin + self.epw * 0.075)
        self.ln(2)


def justification(origin, target, distance):
    """Brute force over every simple path: proves the Dijkstra distance is the minimum."""
    paths = sorted(simple_paths(create_graph(EDGES), origin, target), key=lambda item: item[1])
    best = ", ".join(f"{'-'.join(path)} ({cost:g} km)" for path, cost in paths[:3])
    assert paths[0][1] == distance
    return f"{len(paths)} caminhos possíveis sem repetir pontos. Os 3 menores: {best}."


def build():
    pdf = Report()
    pdf.set_auto_page_break(True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Grafos e Caminho Mínimo com Dijkstra", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "I", 11)
    pdf.cell(0, 7, latin1("Trânsito entre pontos de uma cidade — relatório de testes"),
             new_x="LMARGIN", new_y="NEXT", align="C")

    pdf.heading("1. Problema e modelagem")
    pdf.paragraph(
        "Uma empresa de entregas precisa da menor rota entre dois pontos da cidade. A cidade é um "
        "grafo ponderado: vértices são locais, arestas são ruas de mão dupla e o peso é a distância "
        "em km. O grafo é guardado como **lista de adjacência** (dicionário ponto -> [(vizinho, km)]); "
        "cada rua é inserida nos dois sentidos, resultando em 24 entradas para 12 ruas."
    )
    pdf.grid([("Código", "Descrição")] + list(NODES.items()), (20, 60))
    pdf.grid([("Origem", "Destino", "Distância (km)")] + EDGES, (30, 30, 30))
    pdf.figure(draw_graph(EDGES))

    pdf.heading("2. Algoritmo de Dijkstra")
    pdf.paragraph(
        "1. A distância da origem começa em 0 e a de todos os outros pontos em infinito.\n"
        "2. Uma fila de prioridade (heapq) sempre retira o ponto com a menor distância ainda não fechada.\n"
        "3. Para cada vizinho, se distância(atual) + peso for menor que a distância conhecida do vizinho, "
        "ela é atualizada e o atual vira o **predecessor** do vizinho.\n"
        "4. Quando o destino sai da fila, sua distância é definitiva.\n"
        "5. O caminho é reconstruído seguindo os predecessores do destino até a origem e invertendo a lista. "
        "Se o destino não tem predecessor, não existe caminho."
    )
    pdf.paragraph(
        "O algoritmo fica em graph.py, separado da interface (main.py) e do desenho (draw.py). "
        "Nenhuma função pronta de caminho mínimo foi usada."
    )

    pdf.heading("3. Testes")
    pdf.paragraph(
        "Cada caso foi calculado pelo Dijkstra e conferido por força bruta: todos os caminhos possíveis "
        "sem repetir pontos foram enumerados e o menor deles bate com o resultado. O teste 2 troca "
        "origem e destino do teste 1."
    )
    rows = [("#", "Origem", "Destino", "Caminho", "km")]
    results = []
    for number, (origin, target) in enumerate(CASES, 1):
        path, distance = shortest_route(EDGES, origin, target)
        rows.append((number, origin, target, " -> ".join(path), f"{distance:g}"))
        results.append((number, origin, target, path, distance))
    pdf.grid(rows, (10, 20, 20, 60, 15))
    for number, origin, target, path, distance in results:
        pdf.keep_together()
        pdf.heading(f"Teste {number}: {origin} -> {target} = {distance:g} km")
        pdf.paragraph(f"Caminho: **{' -> '.join(path)}**. {justification(origin, target, distance)}")
        if (origin, target) == ("G", "A"):
            pdf.paragraph("Mesmo caminho do teste 1 invertido e mesma distância: as ruas são de mão dupla.")
        pdf.figure(draw_graph(EDGES, path))

    pdf.add_page()
    pdf.heading("4. Desafio: alterar e desativar ruas")
    pdf.paragraph(
        "O Dijkstra só enxerga os pesos. Se uma rua do caminho mínimo fica mais longa ou fecha, outra soma "
        "pode ficar menor e a rota muda. Se a rua alterada não está no caminho, nada muda."
    )
    original_path, original_distance = shortest_route(EDGES, "A", "G")
    for title, origin, target, changed, disabled in SCENARIOS:
        all_edges = [(u, v, changed.get(frozenset((u, v)), w)) for u, v, w in EDGES]
        active = [edge for edge in all_edges if frozenset(edge[:2]) not in disabled]
        path, distance = shortest_route(active, origin, target)
        pdf.keep_together()
        pdf.heading(title)
        if path is None:
            pdf.paragraph(f"Não existe caminho entre {origin} e {target}: a aplicação mostra uma mensagem de erro.")
        else:
            weights = {frozenset((u, v)): w for u, v, w in all_edges}
            pdf.paragraph(explain_change(original_path, original_distance, path, distance, weights, disabled))
        pdf.figure(draw_graph(all_edges, path, disabled))

    screenshots = sorted(HERE.glob("screenshots/*.png")) + sorted(HERE.glob("screenshots/*.jp*g"))
    pdf.add_page()
    pdf.heading("5. Capturas de tela da interface")
    if not screenshots:
        pdf.paragraph("Nenhuma captura encontrada em screenshots/.")
    pdf.screenshot_grid(screenshots)

    pdf.heading("6. Como executar")
    pdf.paragraph(
        "pip install -r requirements.txt\n"
        "python main.py (abre em http://localhost:8501)\n"
        "python test_graph.py (testes automáticos)\n"
        "python report.py (gera este relatório)"
    )

    pdf.output(HERE / "report.pdf")
    print("report.pdf gerado com", len(screenshots), "capturas de tela")


if __name__ == "__main__":
    build()
