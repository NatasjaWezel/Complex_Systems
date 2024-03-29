import networkx as nx

import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx

from networkx import DiGraph

import pickle

import os
import time

# Create number for each group to allow use of colormap
from itertools import count

def visualize_graph(G):
    fig = plt.figure()
    nodes_dict = dict(G.nodes(data=True))

    # Get unique groups
    groups = set([nodes_dict[method_node]['data']['class'].name for method_node in G.__iter__()])
    mapping = dict(zip(sorted(groups), count()))

    # Color is dependent on which class the node is in
    colors = [mapping[nodes_dict[node]['data']['class'].name] for node in G.__iter__()]

    # Node size gets bigger if the node has more edges going in
    node_sizes = [in_degree * 3 + 5 for node, in_degree in G.in_degree()]

    # Use a spring layout for the network
    pos = nx.layout.spring_layout(G)

    # Draw the nodes and edges separately so we can set their properties
    nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=colors, cmap=plt.cm.jet)
    edges = nx.draw_networkx_edges(G, pos, node_size=node_sizes, arrowstyle='->',
                                   arrowsize=5, edge_color='grey',
                                   width=1)
    timer = time.time()

    ax = plt.gca()
    ax.set_axis_off()
    # plt.title("Reference graph simulated Java methods")

    os.makedirs('./web_output', exist_ok=True)
    plt.savefig("./web_output/network.png", dpi=500)
    plt.close()
