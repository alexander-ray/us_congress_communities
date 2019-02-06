from data_parser import generate_digraph, generate_bipartite_graph
import numpy as np
import networkx as nx
import csv
import igraph
from sklearn.metrics import adjusted_mutual_info_score
from NMI import calc_nmi
import math
#import graph_tool.all as gt
import sys
import json
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

def create_bipartite(filepath, congress, bill_types, threshold=None):
    """
    Wrapper for generate_bipartite_graph

    :param filepath: Path to type directories
    :param congress: Numerical congress number
    :param bill_types: List of types of bills to include
    :param threshold: Threshold to remove high-sponsor bills
    :return: Bipartite nx graph
    """
    if chamber == 'house':
        G_bipartite = generate_bipartite_graph(filepath, congress, bill_types)
    else:
        G_bipartite = generate_bipartite_graph(filepath, congress, bill_types)
    # G_bipartite= update_nodes_to_numeric(G_bipartite)
    legislators = [node for node in G_bipartite.nodes if G_bipartite.nodes[node]['type'] == 'legislator']
    if threshold is not None:
        G_bipartite = apply_threshold(G_bipartite, len(legislators), threshold)
    return G_bipartite

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

def gt_graph_from_networkx_bipartite(G_bipartite):
    """
    Helper function to convert nx bipartite to graph-tool. Stores weights in 'weight' e

    :param G_bipartite:
    :return:
    """
    G_bipartite = nx.convert_node_labels_to_integers(G_bipartite)
    A = nx.to_numpy_array(G_bipartite, nodelist=G_bipartite.nodes)

    edges = np.zeros((np.count_nonzero(A), 3), dtype='uint16')
    edges[:, 0:2] = np.transpose(np.nonzero(A))
    for e in range(edges.shape[0]):
        edges[e, 2] = A[edges[e, 0], edges[e, 1]]
    #g = gt.Graph(directed=False)
    # https: // stackoverflow.com / questions / 45821741 /
    weight = g.new_edge_property('int')
    eprops = [weight]
    g.ep['weight'] = weight
    g.add_edge_list(edges, eprops=eprops)

    type_vprop = g.new_vertex_property('string')
    g.vertex_properties['type'] = type_vprop
    for v in g.vertices():
        if G_bipartite.nodes[v]['type'] == 'legislator':
            g.vp.type[v] = 0
        else:
            g.vp.type[v] = 1

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


        '''
        # GRAPH-TOOL CODE
        G_bipartite = nx.convert_node_labels_to_integers(G_bipartite)
        g = gt_graph_from_networkx_bipartite(G_bipartite)
        # https://github.com/martingerlach/hSBM_Topicmodel/blob/master/sbmtm.py#L139
        clabel = g.vp['type']
        state_args = {'clabel': clabel, 'pclabel': clabel}
        state_args['eweight'] = g.ep.weight
        mdl = np.inf
        for i in range(5):
            state_tmp = gt.minimize_nested_blockmodel_dl(g, deg_corr=True,
                                                         overlap=None,
                                                         state_args=state_args,
                                                         B_min=2)
            mdl_tmp = state_tmp.entropy()
            print(mdl_tmp)
            if mdl_tmp < mdl:
                mdl = 1.0 * mdl_tmp
                state = state_tmp.copy()

        print('Final:')
        print(state)
        print(state.entropy())

        # Generate json files with all nested group memberships
        first_level_partition = state.levels[0].get_blocks()
        group_dict = {}
        for v in g.get_vertices():
            if G_bipartite.nodes[v]['type'] == 'legislator':
                if first_level_partition[v] not in group_dict:
                    group_dict[first_level_partition[v]] = []
                group_dict[first_level_partition[v]].append((G_bipartite.nodes[v]['name'], G_bipartite.nodes[v]['party']))
        with open('./data/sbm/114_senate_groups_nested_level_1.json', 'w') as f:
            f.write(json.dumps(group_dict, indent=4, sort_keys=True))

        # http://main-discussion-list-for-the-graph-tool-project.982480.n3.nabble.com/About-the-blocks-from-the-minimize-nested-blockmodel-dl-td4026580.html
        partitions = state.levels[1:]
        prev_par = group_dict
        level_counter = 1
        for partition in partitions:
            level_counter += 1
            tmp = {}
            curr_par = partition.get_blocks()
            for k,v in prev_par.items():
                if curr_par[k] not in tmp:
                    tmp[curr_par[k]] = []
                for i in v:
                    tmp[curr_par[k]].append(i)
            with open('./data/sbm/114_senate_groups_nested_level_' + str(level_counter) + '.json', 'w') as f:
                f.write(json.dumps(tmp, indent=4, sort_keys=True))
            prev_par = tmp
        '''
        #gt.draw_hierarchy(state, output="114_senate.pdf", layout='bipartite')
