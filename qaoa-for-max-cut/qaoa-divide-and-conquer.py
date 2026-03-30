# SPDX-License-Identifier: Apache-2.0 AND CC-BY-NC-4.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import networkx as nx
from networkx.algorithms import community
import cudaq
from cudaq import spin
import cudaq_solvers as solvers
import numpy as np
from mpi4py import MPI
from typing import List


cudaq.set_target("nvidia")
target = cudaq.get_target()

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
num_qpus = comm.Get_size()


# ─── Graph utilities (from Lab 2) ──────────────────────────────────

def subgraph_of_vertex(graph_dictionary, vertex):
    """Return the key of the subgraph that contains *vertex*,
    or '' if the vertex is not found in any subgraph.

    Parameters
    ----------
    graph_dictionary : dict of networkX.Graph with str as keys
    vertex : int

    Returns
    -------
    str
    """
    location = ''
    for key in graph_dictionary:
        if vertex in graph_dictionary[key].nodes():
            location = key
    return location


def border(G, subgraph_dictionary):
    """Return the subgraph of G containing only edges that cross
    between distinct subgraphs.

    Parameters
    ----------
    G : networkX.Graph
    subgraph_dictionary : dict of networkX.Graph with str as keys

    Returns
    -------
    networkX.Graph
    """
    borderGraph = nx.Graph()
    for u, v in G.edges():
        is_border = True
        for key in subgraph_dictionary:
            SubG = subgraph_dictionary[key]
            if (u, v) in list(nx.edges(SubG)):
                is_border = False
        if is_border:
            borderGraph.add_edge(u, v)
    return borderGraph


def cutvalue(G):
    """Return the cut value of G based on the 'color' attribute of each node.

    Parameters
    ----------
    G : networkX.Graph

    Returns
    -------
    int
    """
    cut = 0
    for u, v in G.edges():
        if str(G.nodes[u]['color']) != str(G.nodes[v]['color']):
            cut += 1
    return cut


def subgraphpartition(G, n, name, globalGraph):
    """Divide G into at most *n* subgraphs using greedy modularity.

    Parameters
    ----------
    G : networkX.Graph
    n : int
    name : str
    globalGraph : networkX.Graph

    Returns
    -------
    dict of str : networkX.Graph
    """
    greedy_partition = community.greedy_modularity_communities(
        G, weight=None, resolution=1.1, cutoff=1, best_n=n)
    graph_dictionary = {}
    for i, part in enumerate(greedy_partition):
        subgraphname = f"{name}:{i}"
        nodelist = sorted(list(part))
        graph_dictionary[subgraphname] = nx.subgraph(globalGraph, nodelist)
    return graph_dictionary


# ─── Max-cut QAOA via solvers ───────────────────────────────────────

def qaoa_for_graph(G, layer_count, shots, seed):
    """Find an approximate max cut of G using ``solvers.qaoa()``.

    Parameters
    ----------
    G : networkX.Graph
    layer_count : int
    shots : int
        (Kept for API compatibility; solvers.qaoa handles sampling internally.)
    seed : int

    Returns
    -------
    str
        Binary string representing the max-cut colouring of the vertices.
    """
    if nx.number_of_nodes(G) == 1 or nx.number_of_edges(G) == 0:
        results = ''
        for u in list(nx.nodes(G)):
            np.random.seed(seed)
            results += str(np.random.randint(0, 1))
        return results

    # Remap to 0-indexed nodes so qubit indices match
    G_mapped = nx.convert_node_labels_to_integers(G, ordering='sorted')
    hamiltonian = solvers.get_maxcut_hamiltonian(G_mapped)
    parameter_count = solvers.get_num_qaoa_parameters(hamiltonian, layer_count)

    np.random.seed(seed)
    cudaq.set_random_seed(seed)
    initial_parameters = np.random.uniform(
        -np.pi, np.pi, parameter_count).tolist()

    optimal_value, optimal_parameters, sample_result = solvers.qaoa(
        hamiltonian, layer_count, initial_parameters)

    print("Optimal value =", optimal_value)
    print("most_probable outcome =", sample_result.most_probable())
    return str(sample_result.most_probable())


# ─── Merger graph construction and QAOA ─────────────────────────────

def createMergerGraph(border_graph, subgraphs):
    """Build a graph with one vertex per subgraph and edges where
    the corresponding subgraphs are connected by border edges.

    Parameters
    ----------
    border_graph : networkX.Graph
    subgraphs : dict of networkX.Graph with str as keys

    Returns
    -------
    networkX.Graph
    """
    M = nx.Graph()
    for u, v in border_graph.edges():
        su = subgraph_of_vertex(subgraphs, u)
        sv = subgraph_of_vertex(subgraphs, v)
        if su != sv:
            M.add_edge(su, sv)
    return M


def merger_graph_penalties(mergerGraph, subgraph_dictionary, G):
    """Compute penalty weights for each edge in the merger graph.

    Parameters
    ----------
    mergerGraph : networkX.Graph
    subgraph_dictionary : dict of networkX.Graph with str as keys
    G : networkX.Graph

    Returns
    -------
    networkX.Graph
    """
    nx.set_edge_attributes(mergerGraph, int(0), 'penalty')
    for i, j in mergerGraph.edges():
        penalty_ij = 0
        for u in nx.nodes(subgraph_dictionary[i]):
            for neighbor_u in nx.all_neighbors(G, u):
                if neighbor_u in nx.nodes(subgraph_dictionary[j]):
                    if str(G.nodes[u]['color']) != str(G.nodes[neighbor_u]['color']):
                        penalty_ij += 1
                    else:
                        penalty_ij -= 1
        mergerGraph[i][j]['penalty'] = penalty_ij
    return mergerGraph


def merger_hamiltonian(merger_edge_src, merger_edge_tgt, penalty):
    """Build the weighted ZZ Hamiltonian for the merger optimisation.

    This is *not* a standard max-cut Hamiltonian — the weights come
    from the penalty structure of the subgraph partition.

    Parameters
    ----------
    merger_edge_src : List[int]
    merger_edge_tgt : List[int]
    penalty : List[int]

    Returns
    -------
    cudaq.SpinOperator
    """
    H = 0
    for i in range(len(merger_edge_src)):
        H += -penalty[i] * spin.z(merger_edge_src[i]) * spin.z(merger_edge_tgt[i])
    return H


def merging(G, graph_dictionary, merger_graph):
    """Use ``solvers.qaoa()`` on the merger graph to determine which
    subgraphs should have their colours flipped.

    Parameters
    ----------
    G : networkX.Graph
    graph_dictionary : dict of networkX.Graph with str as keys
    merger_graph : networkX.Graph

    Returns
    -------
    str
        Binary string (one bit per subgraph); '1' means flip that subgraph.
    """
    mg = merger_graph_penalties(merger_graph, graph_dictionary, G)
    has_nontrivial = any(mg[u][v]['penalty'] != 0 for u, v in nx.edges(mg))

    if not has_nontrivial:
        print('Merging stage is trivial')
        return '0' * nx.number_of_nodes(merger_graph)

    merger_nodes = sorted(list(mg.nodes()))
    merger_edge_src = []
    merger_edge_tgt = []
    penalty = []
    for u, v in nx.edges(mg):
        merger_edge_src.append(merger_nodes.index(u))
        merger_edge_tgt.append(merger_nodes.index(v))
        penalty.append(mg[u][v]['penalty'])

    H = merger_hamiltonian(merger_edge_src, merger_edge_tgt, penalty)
    layer_count_merger = 3
    parameter_count = solvers.get_num_qaoa_parameters(H, layer_count_merger)

    cudaq.set_random_seed(12345)
    np.random.seed(4321)
    initial_parameters = np.random.uniform(
        -np.pi, np.pi, parameter_count).tolist()

    _, _, sample_result = solvers.qaoa(
        H, layer_count_merger, initial_parameters)

    return str(sample_result.most_probable())


# ─── Colouring utilities ────────────────────────────────────────────

def unaltered_colors(G, graph_dictionary, max_cuts):
    """Colour G's vertices based on per-subgraph max-cut results.

    Parameters
    ----------
    G : networkX.Graph
    graph_dictionary : dict of networkX.Graph with str as keys
    max_cuts : dict of str

    Returns
    -------
    networkX.Graph
    """
    for key in graph_dictionary:
        SubG = graph_dictionary[key]
        sorted_nodes = sorted(list(nx.nodes(SubG)))
        for v in sorted_nodes:
            G.nodes[v]['color'] = max_cuts[key][sorted_nodes.index(v)]
    return G


def new_colors(graph_dictionary, G, mergerGraph, flip_colors):
    """Flip subgraph colours according to the merger QAOA result.

    Parameters
    ----------
    graph_dictionary : dict of networkX.Graph with str as keys
    G : networkX.Graph
    mergerGraph : networkX.Graph
    flip_colors : str

    Returns
    -------
    (networkX.Graph, str)
    """
    mergerNodes = sorted(list(nx.nodes(mergerGraph)))
    flipGraphColors = {}
    for u in mergerNodes:
        flipGraphColors[u] = int(flip_colors[mergerNodes.index(u)])

    for key in graph_dictionary:
        if flipGraphColors[key] == 1:
            for u in graph_dictionary[key].nodes():
                G.nodes[u]['color'] = str(1 - int(G.nodes[u]['color']))

    revised_colors = ''
    for u in sorted(G.nodes()):
        revised_colors += str(G.nodes[u]['color'])
    return G, revised_colors


# ─── Recursive divide-and-conquer ───────────────────────────────────

def subgraph_solution(G, key, vertex_limit, subgraph_limit,
                      layer_count, global_graph, seed):
    """Recursively find max-cut approximations of the subgraphs.

    Parameters
    ----------
    G : networkX.Graph
    key : str
    vertex_limit : int
    subgraph_limit : int
    layer_count : int
    global_graph : networkX.Graph
    seed : int

    Returns
    -------
    str
    """
    results = {}
    seed = 123

    if nx.number_of_nodes(G) < vertex_limit + 1:
        print('Working on finding max cut approximations for', key)
        result = qaoa_for_graph(G, layer_count=layer_count,
                                shots=10000, seed=seed)
        results[key] = result
        nodes_of_G = sorted(list(G.nodes()))
        for u in G.nodes():
            global_graph.nodes[u]['color'] = results[key][nodes_of_G.index(u)]
        return result

    # Recursively apply the algorithm for large graphs
    subgraph_limit = min(subgraph_limit, nx.number_of_nodes(G))
    subgraph_dictionary = subgraphpartition(
        G, subgraph_limit, str(key), global_graph)

    for skey in subgraph_dictionary:
        results[skey] = subgraph_solution(
            subgraph_dictionary[skey], skey, vertex_limit,
            subgraph_limit, layer_count, global_graph, seed)

    print('Found max cut approximations for',
          list(subgraph_dictionary.keys()))

    G = unaltered_colors(G, subgraph_dictionary, results)
    unaltered_cut_value = cutvalue(G)
    print('prior to merging, the max cut value of', key, 'is',
          unaltered_cut_value)

    print('Merging these solutions together for a solution to', key)
    bordergraph = border(G, subgraph_dictionary)
    merger_graph = createMergerGraph(bordergraph, subgraph_dictionary)

    try:
        merger_results = merging(G, subgraph_dictionary, merger_graph)
    except Exception:
        merger_results = '0' * nx.number_of_nodes(merger_graph)
        print('Merging subroutine opted out with an error for', key)

    alteredG, new_color_list = new_colors(
        subgraph_dictionary, G, merger_graph, merger_results)
    newcut = cutvalue(alteredG)
    print('the merger algorithm produced a new coloring of', key,
          'with cut value,', newcut)

    return new_color_list


###########################################################################
# Main algorithm
###########################################################################

if rank == 0:
    n = 30
    m = 70
    seed = 20160
    sampleGraph3 = nx.gnm_random_graph(n, m, seed=seed)

    subgraph_dictionary = subgraphpartition(
        sampleGraph3, 12, 'Global', sampleGraph3)

    number_of_subgraphs = len(sorted(subgraph_dictionary))
    number_of_subgraphs_per_qpu = int(
        np.ceil(number_of_subgraphs / num_qpus))

    keys_on_qpu = {}
    for q in range(num_qpus):
        keys_on_qpu[q] = []
        for k in range(number_of_subgraphs_per_qpu):
            if k * num_qpus + q < number_of_subgraphs:
                key = sorted(subgraph_dictionary)[k * num_qpus + q]
                keys_on_qpu[q].append(key)

    print('Subgraph problems to be computed on each processor '
          'have been assigned')

    for i in range(num_qpus):
        subgraph_to_qpu = {k: subgraph_dictionary[k]
                           for k in keys_on_qpu[i]}
        if i != 0:
            comm.send(subgraph_to_qpu, dest=i, tag=rank)
        else:
            assigned_subgraph_dictionary = subgraph_to_qpu
else:
    assigned_subgraph_dictionary = comm.recv(source=0, tag=0)
    print(f"Processor {rank} received "
          f"{assigned_subgraph_dictionary} from processor 0")


###########################################################################
# Solve assigned subgraph problems
###########################################################################
num_subgraphs = 11
num_qubits = 9
layer_count = 2
results = {}

for key in assigned_subgraph_dictionary:
    G = assigned_subgraph_dictionary[key]
    newcoloring_of_G = subgraph_solution(
        G, key, num_subgraphs, num_qubits, layer_count, G, seed=13)
    results[key] = newcoloring_of_G


###########################################################################
# Gather results on rank 0
###########################################################################
if rank != 0:
    comm.send(results, dest=0, tag=0)
    print(f"{results} sent by processor {rank}")

else:
    for j in range(1, num_qpus):
        colors = comm.recv(source=j, tag=0)
        print(f"Received {colors} from processor {j}")
        for key in colors:
            results[key] = colors[key]
    print("The results dictionary on GPU 0 =", results)

    # Colour the full graph using subgraph solutions
    for key in subgraph_dictionary:
        SubG = subgraph_dictionary[key]
        color_list = [int(c) for c in results[key]]
        for v in sorted(list(nx.nodes(SubG))):
            idx = sorted(list(nx.nodes(SubG))).index(v)
            SubG.nodes[v]['color'] = color_list[idx]
            sampleGraph3.nodes[v]['color'] = SubG.nodes[v]['color']

    print('The divide-and-conquer QAOA unaltered cut approximation '
          'of the graph, prior to the final merge, is',
          cutvalue(sampleGraph3))

    # Final merger across all subgraphs
    borderGraph = border(sampleGraph3, subgraph_dictionary)
    mergerGraph = createMergerGraph(borderGraph, subgraph_dictionary)
    merger_results = merging(
        sampleGraph3, subgraph_dictionary, mergerGraph)
    maxcutSampleGraph3, G_colors_with_maxcut = new_colors(
        subgraph_dictionary, sampleGraph3, mergerGraph, merger_results)

    for node, attributes in maxcutSampleGraph3.nodes(data=True):
        print(f"Node: {node}, Attributes: {attributes}")

    print('The divide-and-conquer QAOA max cut approximation '
          'of the graph is', cutvalue(maxcutSampleGraph3))
    print('The divide and conquer max cut coloring is',
          G_colors_with_maxcut)

    # Compare with classical greedy approximation
    number_of_approx = 10
    randomlist = np.random.choice(3000, number_of_approx)
    minapprox = nx.algorithms.approximation.one_exchange(
        sampleGraph3, initial_cut=None, seed=int(randomlist[0]))[0]
    maxapprox = minapprox
    sum_of_approximations = 0
    for i in range(number_of_approx):
        seed = int(randomlist[i])
        ith_approximation = nx.algorithms.approximation.one_exchange(
            sampleGraph3, initial_cut=None, seed=seed)[0]
        if ith_approximation < minapprox:
            minapprox = ith_approximation
        if ith_approximation > maxapprox:
            maxapprox = ith_approximation
        sum_of_approximations += ith_approximation

    average_approx = sum_of_approximations / number_of_approx
    print('This compares to a few runs of the greedy modularity '
          'maximization algorithm gives an average approximate '
          'Max Cut value of', average_approx)
    print('with approximations ranging from', minapprox,
          'to', maxapprox)
