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

# Defining functions to generate the Hamiltonian and Kernel for a given graph
# Necessary packages
import networkx as nx
from networkx import algorithms
from networkx.algorithms import community
import cudaq
from cudaq import spin
from cudaq.qis import *
import numpy as np
from typing import List, Tuple
from mpi4py import MPI

# Getting information about platform
cudaq.set_target("nvidia")
target = cudaq.get_target()

# Setting up MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
num_qpus = comm.Get_size()

#######################################################
# Step 1
####################################################### 
# Function to return a dictionary of subgraphs of the input graph 
# using the greedy modularity maximization algorithm

def subgraphpartition(G,n):
    """Divide the graph up into at most n subgraphs
    
    Parameters
    ----------
    G: networkX.Graph 
        Graph that we want to subdivdie
    n : int
        n is the maximum number of subgraphs in the partition
    Returns
    -------
    dict of str : networkX.Graph
        Dictionary of networkX graphs with a string as the key
    """
    greedy_partition = community.greedy_modularity_communities(G, weight=None, resolution=1.1, cutoff=1, best_n=n)
    number_of_subgraphs = len(greedy_partition)

    graph_dictionary = {}
    graph_names=[]
    for i in range(number_of_subgraphs):
        name='G'+str(i)
        graph_names.append(name)

    for i in range(number_of_subgraphs):
        nodelist = sorted(list(greedy_partition[i]))
        graph_dictionary[graph_names[i]] = nx.subgraph(G, nodelist)
     
    return(graph_dictionary) 


if rank ==0:
    # Defining the example graph
    # Random graph parameters
    n = 30  # numnber of nodes
    m = 70  # number of edges
    seed = 20160  # seed random number generators for reproducibility

    # Use seed for reproducibility
    sampleGraph2 = nx.gnm_random_graph(n, m, seed=seed)

    # Subdividing the graph
    num_subgraphs_limit = min(12, len(sampleGraph2.nodes())) # maximum number of subgraphs for the partition
    subgraph_dictionary = subgraphpartition(sampleGraph2,num_subgraphs_limit)

    # Assign the subgraphs to the QPUs
    number_of_subgraphs = len(sorted(subgraph_dictionary))
    number_of_subgraphs_per_qpu = int(np.ceil(number_of_subgraphs/num_qpus))

    keys_on_qpu ={}
    
    for q in range(num_qpus):
        keys_on_qpu[q]=[]
        for k in range(number_of_subgraphs_per_qpu):
            if (k*num_qpus+q < number_of_subgraphs):
                key = sorted(subgraph_dictionary)[k*num_qpus+q]
                keys_on_qpu[q].append(key)        
        print(keys_on_qpu[q],'=subgraph problems to be computed on processor',q)
        
    # Distribute the subgraph data to the QPUs
    for i in range(num_qpus):
        subgraph_to_qpu ={}
        for k in keys_on_qpu[i]:
            subgraph_to_qpu[k]= subgraph_dictionary[k]
        if i != 0:
            comm.send(subgraph_to_qpu, dest=i, tag=rank)
            print("{} sent by processor {}".format(subgraph_to_qpu, rank))
        else:
            assigned_subgraph_dictionary = subgraph_to_qpu
else:
    # Receive the subgraph data
    assigned_subgraph_dictionary= comm.recv(source=0, tag=0)
    print("Processor {} received {} from processor {}".format(rank,assigned_subgraph_dictionary, 0))


