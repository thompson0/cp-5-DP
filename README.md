# Grupo
- RM 563126 Gabriel Thompson Freitas  
- RM 561503 Enzo Quarelo  
- RM 563186 Jose Otavio Kaneto  
- RM 563245 Nicolas Baradel
- RM 562499 
# Rota mínima com Dijkstra

Aplicação em Python + Streamlit que encontra a menor rota entre dois pontos de uma
cidade fictícia. A cidade é um grafo ponderado (pontos = vértices, ruas de mão dupla =
arestas, peso = distância em km) e o caminho é calculado com o algoritmo de Dijkstra,
implementado sem bibliotecas prontas de caminho mínimo.

Atividade prática "Grafos e Caminho Mínimo com Dijkstra" (`cp 5 - Dynamic Programming.pdf`).

## Funcionalidades

- Escolha de origem e destino por menus e botão **Calcular rota**.
- Sequência de pontos do caminho e distância total.
- Diagrama da cidade com pesos nas ruas e caminho mínimo destacado em vermelho.
- Aviso quando origem e destino são iguais e quando não existe caminho.
- **Desafio opcional:** tabela para alterar a distância das ruas ou desativá-las; o app
  recalcula a rota e explica por que ela mudou (ou não).

## Mapa

| Código | Local | | Rua | km | | Rua | km |
|---|---|---|---|---|---|---|---|
| A | Depósito | | A-B | 4 | | C-G | 5 |
| B | Cruzamento B | | A-D | 2 | | D-E | 4 |
| C | Cruzamento C | | A-E | 7 | | D-F | 2 |
| D | Cruzamento D | | B-C | 3 | | D-G | 3 |
| E | Cruzamento E | | B-D | 1 | | E-F | 3 |
| F | Cruzamento F | | C-D | 6 | | F-G | 2 |
| G | Cliente | | | | | | |

## Como rodar

Requer Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py                   # abre em http://localhost:8501
```

`streamlit run main.py` também funciona.

## Testes

```bash
python test_graph.py
```

Cobre a representação do grafo (12 ruas nos dois sentidos), os casos da atividade,
troca de origem e destino, rua alterada/desativada e ausência de caminho. Também compara
o Dijkstra com uma busca por força bruta em todos os pares de pontos.

| Origem → Destino | Caminho | km |
|---|---|---|
| A → G | A → D → G | 5 |
| G → A | G → D → A | 5 |
| A → C | A → D → B → C | 6 |
| E → C | E → D → B → C | 8 |
| E → G | E → F → G | 5 |

## Relatório

```bash
python report.py
```

Gera `report.pdf` com a modelagem, a explicação do algoritmo, os testes (com prova de
minimalidade por força bruta), os cenários do desafio e as capturas de tela salvas em
`screenshots/`.

## Estrutura

```
graph.py          dados do mapa, lista de adjacência e algoritmo de Dijkstra
draw.py           desenho do grafo com Matplotlib
main.py           interface Streamlit
test_graph.py     testes
report.py         gerador do relatório em PDF
screenshots/      capturas de tela usadas no relatório
SPEC.md           especificação da implementação
```

## Como o Dijkstra funciona aqui

1. Distância da origem = 0; dos demais pontos = infinito.
2. Uma fila de prioridade (`heapq`) retira sempre o ponto com menor distância.
3. Para cada vizinho, se `distância(atual) + peso` for menor que a distância conhecida,
   ela é atualizada e o ponto atual vira o **predecessor** do vizinho.
4. Ao retirar o destino da fila, sua distância é definitiva.
5. O caminho é reconstruído seguindo os predecessores do destino até a origem.
