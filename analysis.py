from data_parser import generate_graph, generate_digraph, generate_bipartite_graph
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import csv
import igraph


def update_nodes_to_numeric(G):
    return nx.convert_node_labels_to_integers(G, label_attribute='bioguide')


def calculate_modularity(G, degrees, s):
    two_m = np.sum(degrees)
    num_nodes = degrees.size
    acc = 0
    for i in range(num_nodes):
        for j in range(num_nodes):
            expected = (degrees[i] * degrees[j])/two_m
            acc += (G[i, j] - expected)*(s[i] == s[j])
    return (1/two_m)*acc


def generate_membership_list(nodes):
    s = []
    for i in nodes:
        party = nodes[i]['party']
        if 'Byrd, Harry F.,  Jr.' in nodes[i]['name']:
            party = 'Independent'
        if 'Democrat' in party:
            s.append(0)
        else:
            s.append(1)
    return s


house_names = ['hr', 'hconres', 'hjres', 'hres', 'hamendments']
senate_names = ['s', 'sconres', 'sjres', 'sres', 'samendments']

mod_arr = []
congresses = list(range(96, 116))
for senate in congresses:
    # Check against "truth" in https://www.sciencedirect.com/science/article/pii/S037843710701206X?via%3Dihub
    '''
    G = generate_digraph('/Users/alexray/Documents/data/', senate, senate_names)
    print(len(G))
    avg_degree = np.mean([deg[1] for deg in G.in_degree])
    print(avg_degree)
    print(nx.average_shortest_path_length(G))
    '''

    G_bipartite = generate_bipartite_graph('/Users/alexray/Documents/data/', senate, senate_names)
    G_bipartite= update_nodes_to_numeric(G_bipartite)
    legislators = [node for node in G_bipartite.nodes if G_bipartite.nodes[node]['type'] == 'legislator']
    G_proj = nx.bipartite.weighted_projected_graph(G_bipartite, legislators)
    #for node in G_proj.nodes:
    #    G_proj.add_edge(node, node, weight=G_bipartite.degree[node])
    A = nx.to_numpy_array(G_proj, nodelist=G_proj.nodes)

    s = generate_membership_list(G_proj.nodes)

    # Networkx to igraph: https://stackoverflow.com/questions/29655111/
    g = igraph.Graph.Adjacency((A > 0).tolist())
    g.es['weight'] = A[A.nonzero()]
    g.vs['label'] = list(G_proj.nodes)
    mod = g.modularity(membership=s, weights='weight')
    max_mod = g.community_leading_eigenvector(clusters=None, weights='weight').modularity

    with open('senate_party_mod_w_max_no_self.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([senate, mod, max_mod])
