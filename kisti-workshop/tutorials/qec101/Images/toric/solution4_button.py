# reveal_cudaq.py
import ipywidgets as widgets
from IPython.display import display, Markdown
import runpy, tempfile, os

_NV_GREEN = "#76b900"


# your example as a raw‐string
_CODE = """\
import networkx as nx
import matplotlib.pyplot as plt

def toric_distance(u, v, L):

    dx = abs(u[0] - v[0])
    dx = min(dx, L - dx)
    dy = abs(u[1] - v[1])
    dy = min(dy, L - dy)
    return dx + dy

def mwpm_decoder_toric(flagged_stabilizers, L):

    G = nx.Graph()
    # Add each flagged stabilizer as a node
    for i, coord in enumerate(flagged_stabilizers):
        G.add_node(i, pos=coord)

    # Add edges with wrapped Manhattan distance as weight
    for i in range(len(flagged_stabilizers)):
        for j in range(i + 1, len(flagged_stabilizers)):
            dist = toric_distance(flagged_stabilizers[i], flagged_stabilizers[j], L)
            G.add_edge(i, j, weight=dist)

    # Draw the graph
    pos = {node: G.nodes[node]['pos'] for node in G.nodes}
    nx.draw(G, pos, with_labels=True, node_size=500, font_weight='bold')
    # Add edge labels (i.e., distances)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.title("Toric Code Graph (Distances on Edges)")
    plt.show()

    #Performs MWPM
    matching_indices = nx.min_weight_matching(G)

    # Convert node indices back to stabilizer coordinates for clarity
    matching_solution = []
    for i, j in matching_indices:
        matching_solution.append((G.nodes[i]['pos'], G.nodes[j]['pos']))
    return matching_solution

flagged_1 = [(2, 1), (1, 3), (2, 4), (1, 6), (4,5), (5,2)]
flagged_2 = [(1, 0), (1, 6), (2, 1), (3, 4), (5,3), (4,6)]
L = 7

print("MWPM solution 1:",mwpm_decoder_toric(flagged_1, L))
print("MWPM solution 2:", mwpm_decoder_toric(flagged_2, L))
"""


_ANSWER_TEXT_1 = """\
**Answer:**  

A logical error occurs

<img src="Images/toric/mwpmsolution1.png"  title="Landscape Image" width="600">
"""

_ANSWER_TEXT_2 = """\
**Answer:**  

A logical error does not occur

<img src="Images/toric/mwpmsolution2.png"  title="Landscape Image" width="600">
"""

def show_cudaq_solution():
    """
    Returns a Reveal‐Answer widget that displays the CUDA‑Q code
    and then runs it, showing its printed output.
    """
    btn = widgets.Button(
        description="Reveal Answer",
        style={"button_color": _NV_GREEN, "font_weight": "bold"},
        layout=widgets.Layout(width="180px")
    )
    out = widgets.Output()

    def _on_click(_):
        out.clear_output()
        with out:
            # 1) show the source
            display(Markdown("```python\n" + _CODE + "\n```"))
            # 2) write to a temp .py file so inspect.getsource will succeed
            fd, path = tempfile.mkstemp(suffix=".py")
            with os.fdopen(fd, "w") as f:
                f.write(_CODE)
            try:
                # 3) execute that file as __main__
                runpy.run_path(path, run_name="__main__")
            finally:
                os.remove(path)
            display(Markdown(_ANSWER_TEXT_1))
            display(Markdown(_ANSWER_TEXT_2))

    btn.on_click(_on_click)
    return widgets.VBox([btn, out])
