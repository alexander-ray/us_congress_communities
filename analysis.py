from data_parser import generate_graph, generate_digraph, generate_bipartite_graph
import numpy as np
import networkx as nx
import csv
import igraph
from NMI import calc_nmi
import math

def update_nodes_to_numeric(G):
    """
    Converts networkx nodes to numeric, setting 'bioguide' to be old node label

    :param G: nx.Graph
    :return: nx.Graph
    """
    return nx.convert_node_labels_to_integers(G, label_attribute='bioguide')


def calculate_modularity(G, degrees, s):
    """
    Helper function to calculate weighted modularity. Same result as iGraph, but slower

    :param G: np array adjacency matrix
    :param degrees: ordered list of degrees
    :param s: ordered list of group labels
    :return: modularity score Q
    """
    two_m = np.sum(degrees)
    num_nodes = degrees.size
    acc = 0
    for i in range(num_nodes):
        for j in range(num_nodes):
            expected = (degrees[i] * degrees[j])/two_m
            acc += (G[i, j] - expected)*(s[i] == s[j])
    return (1/two_m)*acc


def generate_membership_list(nodes):
    """
    Helper function to generate ordered list of group labels from Networkx nodeset

    :param nodes: Networkx nodes
    :return: ordered list of group labels
    """
    s = []
    for i in nodes:
        party = nodes[i]['party']
        # Zhang et al. assigns non-democrats to the the republican group
        if 'Democrat' in party:
            s.append(0)
        else:
            s.append(1)
    return s


def apply_threshold(G, num_legislators, threshold):
    """
    Apply threshold to bills in bipartite network. Keep bills with sub-threshold sponsorship

    :param G: Bipartite nx.Graph
    :param num_legislators: Number of legislators in this chamber & congress
    :param threshold: Threshold to apply
    :return: nx.Graph
    """
    threshold = math.ceil(threshold * num_legislators)
    nodes_to_remove = []
    s = 0
    c = 0
    for node in G.nodes:
        c += 1
        s += G.degree[node]
        if G.nodes[node]['type'] == 'bill' and G.degree[node] > threshold:
            nodes_to_remove.append(node)
    G.remove_nodes_from(nodes_to_remove)
    return G

path = 'C:/Users/David Crosswy/Documents/New folder/updated-data/data/'

house_names = ['hr', 'hconres', 'hjres', 'hres', 'hamendments']
#senate_names = ['s', 'sconres', 'sjres', 'sres', 'samendments']
senate_names = ['s']
chamber = 'senate'
#thresholds = [0.6, 0.7, 0.8, 0.9, 1.0]
thresholds = [0.6, 0.7, 0.8, 0.9, 1.0]

mod_arr = []
congresses = list(range(96, 116))
for threshold in thresholds:
    print(threshold)
    for congress in congresses:
        # Check against "truth" in https://www.sciencedirect.com/science/article/pii/S037843710701206X?via%3Dihub
        '''
        G = generate_digraph('/Users/alexray/Documents/data/', senate, senate_names)
        print(len(G))
        avg_degree = np.mean([deg[1] for deg in G.in_degree])
        print(avg_degree)
        print(nx.average_shortest_path_length(G))
        '''
        if chamber == 'house':
            G_bipartite = generate_bipartite_graph(path, congress, house_names)
        else:
            G_bipartite = generate_bipartite_graph(path, congress, senate_names)
        G_bipartite= update_nodes_to_numeric(G_bipartite)
        legislators = [node for node in G_bipartite.nodes if G_bipartite.nodes[node]['type'] == 'legislator']
        if threshold is not None:
            G_bipartite = apply_threshold(G_bipartite, len(legislators), threshold)
        G_proj = nx.bipartite.weighted_projected_graph(G_bipartite, legislators)
        # Uncomment to include self-loops
        #for node in G_proj.nodes:
        #    G_proj.add_edge(node, node, weight=G_bipartite.degree[node])

        A = nx.to_numpy_array(G_proj, nodelist=G_proj.nodes)

        s = generate_membership_list(G_proj.nodes)

        # Networkx to igraph: https://stackoverflow.com/questions/29655111/
        g = igraph.Graph.Adjacency((A > 0).tolist())
        g.es['weight'] = A[A.nonzero()]
        g.vs['label'] = list(G_proj.nodes)
        mod = g.modularity(membership=s, weights='weight')
        eig_result = g.community_leading_eigenvector(clusters=None, weights='weight')
        max_mod = eig_result.modularity

        eig_s = []
        for i in range(len(G_proj)):
            j = 0
            for group in eig_result:
                if i in group:
                    eig_s.append(j)
                    break
                j += 1
    print ("Results")
    print ("Threshold: ", threshold,"\tModularity: ", mod, "\tMax Modularity: ", max_mod)

        # Uncomment to write results to csv for later use
        # with open('./data/senate_thresholds_no_self_bills.csv', 'a') as f:
        #     writer = csv.writer(f)
        #     writer.writerow([threshold, congress, mod, max_mod])
