# graph_visualizer.py
import networkx as nx
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output

def create_visualization():
    # Graph setup
    G = nx.DiGraph()
    top_nodes = [str(i) for i in range(1, 7)]
    bottom_nodes = list('ABCDEFG')
    G.add_nodes_from(top_nodes, layer=0)
    G.add_nodes_from(bottom_nodes, layer=1)

    connections = [
        ('1', 'A'), ('1', 'B'),
        ('2', 'B'), ('2', 'C'),
        ('3', 'C'), ('3', 'D'),
        ('4', 'D'), ('4', 'E'),
        ('5', 'E'), ('5', 'F'),
        ('6', 'F'), ('6', 'G'),
    ]
    G.add_edges_from(connections)

    # Position setup
    pos = {}
    for i, node in enumerate(top_nodes):
        pos[node] = (i - len(top_nodes)/2 + 0.5, 1)
    for i, node in enumerate(bottom_nodes):
        pos[node] = (i - len(bottom_nodes)/2 + 0.5, -1)

    # Highlight configuration
    highlight_dict = {
        0: (['3'], []),
        1: (['3'], ['C', 'D']),
        2: (['2', '3', '4'], ['C', 'D']),
        3: (['2', '3', '4'], ['B', 'C', 'D', 'E']),
        4: (['1', '2', '3', '4', '5'], ['B', 'C', 'D', 'E']),
        5: (['1', '2', '3', '4', '5'], ['A', 'B', 'C', 'D', 'E', 'F'])
    }

    # Update function
    def update_graph(iteration):
        clear_output(wait=True)
        highlight_top, highlight_bottom = highlight_dict[iteration]
        
        plt.figure(figsize=(12, 6))
        plt.title("Propagation of Qubit 3's Initial Beliefs", fontsize=14, pad=20)
        
        # Draw check qubits (top row)
        nx.draw_networkx_nodes(
            G, pos, nodelist=top_nodes,
            node_color=['red' if n in highlight_top else 'purple' for n in top_nodes],
            node_size=2000
        )
        
        # Draw data qubits (bottom row)
        nx.draw_networkx_nodes(
            G, pos, nodelist=bottom_nodes,
            node_color=['red' if n in highlight_bottom else '#76B900' for n in bottom_nodes],  # NVIDIA Green
            node_size=2000
        )
        
        nx.draw_networkx_edges(G, pos, edgelist=G.edges(), arrowstyle='-|>', arrowsize=20)
        nx.draw_networkx_labels(G, pos, font_size=16, font_weight='bold')
        
        # Add row labels
        plt.text(-3.5, 1, "Check Qubits", fontsize=12, weight='bold', ha='right')
        plt.text(-3.5, -1, "Data Qubits", fontsize=12, weight='bold', ha='right')
        
        plt.axis('off')
        plt.show()

    # Create and return widget
    slider = widgets.IntSlider(
        value=0,
        min=0,
        max=5,
        step=1,
        description='Iteration:',
        continuous_update=False
    )
    
    return widgets.interactive(update_graph, iteration=slider)

