import csv
import igraph
from sklearn.metrics import adjusted_mutual_info_score
import math
import sys

import networkx as nx
import numpy as np

from data_parser import generate_bipartite_graph

sys.path.append('/Users/alexray/Dropbox/Fall2018CU/thesis/')


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
    #two_m = 2*np.sum(np.triu(G))
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

def create_one_mode_projection(G_bipartite, include_self_loops):
    """
    Create one-mode projection onto legislators from bipartite legislators-legislation network

    :param G_bipartite: Original bipartite network
    :param include_self_loops: Boolean to indicate whether or not to add self loops to projection
    :return: Projection with numerical node labels
    """
    legislators = [node for node in G_bipartite.nodes
                   if G_bipartite.nodes[node]['type'] == 'legislator']
    G_proj = nx.bipartite.weighted_projected_graph(G_bipartite, legislators)

    if include_self_loops:
        for node in G_proj.nodes:
            G_proj.add_edge(node, node, weight=G_bipartite.degree[node])
    return update_nodes_to_numeric(G_proj)

def igraph_from_networkx_one_mode(A):
    """
    Helper function to convert nx one-mode projection to igraph
    Normally leave as directed, as that selection properly calculates modularity by our definition
        (even though the true network is undirected)

    :param A: np.ndarray weighted adjacency matrix
    :return: igraph graph
    """
    # Networkx to igraph: https://stackoverflow.com/questions/29655111/
    g = igraph.Graph.Adjacency((A > 0).tolist())
    g.es['weight'] = A[A.nonzero()]
    g.vs['label'] = list(G_proj.nodes)
    # Leaving as directed results in correct modularity for self and no self loops
    #g.to_undirected(combine_edges='max')
    return g

house_names = ['hr', 'hconres', 'hjres', 'hres', 'hamendments']
senate_names = ['s', 'sconres', 'sjres', 'sres', 'samendments']
#senate_names = ['s']
#house_names = ['hr']
chamber = 'house'
include_self_loops = False
#thresholds = [0.6, 0.7, 0.8, 0.9, 1.0]
thresholds = [None]

mod_arr = []
congresses = list(range(96, 116))
for threshold in thresholds:
    for congress in congresses:
        if chamber == 'house':
            G_bipartite = create_bipartite(filepath='/Users/alexray/Documents/data/',
                                                congress=congress,
                                                bill_types=house_names,
                                                threshold=threshold)
        else:
            G_bipartite = create_bipartite(filepath='/Users/alexray/Documents/data/',
                                                congress=congress,
                                                bill_types=senate_names,
                                                threshold=threshold)
        G_proj = create_one_mode_projection(G_bipartite, include_self_loops)
        A = nx.to_numpy_array(G_proj, nodelist=G_proj.nodes)
        A = np.triu(A) + np.tril(A)

        #print(A)
        s = generate_membership_list(G_proj.nodes)

        # Uncomment to print names and parties of specified nodes
        #for i in [5, 25, 30, 46, 103, 141, 152, 183, 202, 232, 235, 238, 244, 246, 260, 261,
        #          276, 281, 283, 287, 302, 305, 306, 308, 323, 378, 403, 421, 428]:
        #    print(G_proj.nodes[i]['name'] + '  ' + G_proj.nodes[i]['party'])
        #print(G_proj.nodes[447]['name'] + '  ' + G_proj.nodes[447]['party'])


        g = igraph_from_networkx_one_mode(A)
        mod = g.modularity(membership=s, weights='weight')
        eig_result = g.community_leading_eigenvector(clusters=None, weights='weight')
        max_mod = eig_result.modularity
        #print(np.asarray(g.get_adjacency(attribute='weight').data))
        #print(np.array_equal(np.asarray(g.get_adjacency(attribute='weight').data), A))
        eig_s = []
        for i in range(len(G_proj)):
            j = 0
            for group in eig_result:
                if i in group:
                    eig_s.append(j)
                    break
                j += 1
        print(mod)
        print(max_mod)
        
        # Uncomment to write results to csv for later use
        with open('./data/' + chamber + '_ami_no_self.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([congress, adjusted_mutual_info_score(s, eig_s)])
