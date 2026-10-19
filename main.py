"""Streamlit interface. Run with: python main.py (or streamlit run main.py)"""

import sys

import streamlit as st
from streamlit import runtime

from draw import draw_graph
from graph import EDGES, NODES, explain_change, format_route, shortest_route

if not runtime.exists():  # started with plain python: relaunch through the Streamlit server
    from streamlit.web import cli
    sys.argv = ["streamlit", "run", __file__]
    sys.exit(cli.main())


def reset_streets():
    st.session_state.editor_version += 1  # new widget key discards the edits


st.set_page_config(page_title="Rota mínima — Dijkstra", page_icon="🗺️")
st.title("Rota mínima entre pontos da cidade")
st.caption("Algoritmo de Dijkstra sobre um grafo ponderado. Ruas de mão dupla, distâncias em km.")

labels = {node: f"{node} — {description}" for node, description in NODES.items()}
col_origin, col_target = st.columns(2)
origin = col_origin.selectbox("Origem", list(NODES), index=0, format_func=labels.get)
target = col_target.selectbox("Destino", list(NODES), index=len(NODES) - 1, format_func=labels.get)

st.session_state.setdefault("editor_version", 0)
with st.expander("Editar ruas (desafio opcional)"):
    st.write("Altere a distância ou desmarque **Ativa** para fechar uma rua, depois calcule de novo.")
    rows = st.data_editor(
        [{"Origem": u, "Destino": v, "Distância (km)": w, "Ativa": True} for u, v, w in EDGES],
        key=f"streets_{st.session_state.editor_version}",
        disabled=["Origem", "Destino"],
        column_config={"Distância (km)": st.column_config.NumberColumn(min_value=0, required=True)},
        hide_index=True,
        width="stretch",
    )
    st.button("Restaurar original", on_click=reset_streets)

if any(row["Distância (km)"] is None for row in rows):
    st.error("Preencha a distância de todas as ruas.")
    st.stop()

all_edges = [(row["Origem"], row["Destino"], row["Distância (km)"]) for row in rows]
active_edges = [edge for edge, row in zip(all_edges, rows) if row["Ativa"]]
disabled = {frozenset(edge[:2]) for edge, row in zip(all_edges, rows) if not row["Ativa"]}
weights = {frozenset((u, v)): w for u, v, w in all_edges}

path = None
if st.button("Calcular rota", type="primary"):
    if origin == target:
        st.warning("Origem e destino são o mesmo ponto. Escolha pontos diferentes.")
    else:
        path, distance = shortest_route(active_edges, origin, target)
        if path is None:
            st.error(f"Não existe caminho entre {origin} e {target} com as ruas ativas.")
        else:
            st.success(f"Caminho: {format_route(path)}")
            st.metric("Distância total", f"{distance:g} km")
            if active_edges != EDGES:
                original_path, original_distance = shortest_route(EDGES, origin, target)
                st.info(explain_change(original_path, original_distance, path, distance, weights, disabled))

st.pyplot(draw_graph(all_edges, path, disabled))
