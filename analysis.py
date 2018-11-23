from data_parser import generate_graph, generate_digraph, generate_bipartite_graph
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


def update_nodes_to_numeric(G):
    return nx.convert_node_labels_to_integers(G, label_attribute='bioguide')


def create_expected_matrix(G, degrees):
    P = np.zeros(G.shape)
    # "m is the total weight of the edges in the network"
    two_m = np.sum(G)
    for i in range(G[0].size):
        for j in range(G[0].size):
            P[i, j] = (degrees[i]*degrees[j])/two_m
    return P


def create_modularity_matrix(G, P):
    return np.subtract(G, P)


def calculate_modularity(G, degrees, s):
    #two_m = 2*np.sum(np.triu(G))
    two_m = np.sum(degrees)
    num_nodes = degrees.size
    #num_nodes = len(degrees)
    acc = 0
    for i in range(num_nodes):
        for j in range(num_nodes):
            expected = (degrees[i] * degrees[j])/two_m
            acc += (G[i, j] - expected)*(s[i] == s[j])
    return (1/two_m)*acc

'''
def calculate_modularity(G):
    degrees = [degree[1] for degree in G.degree]
    two_m = 2*np.sum(degrees)
    acc = 0
    for i in G.nodes:
        for j in G.adj[i]:
            expected = (G.degree[i] * G.degree[j]) / two_m
            acc += (G[i][j]['weight'] - expected) * (G.nodes[i]['party'] == G.nodes[j]['party'])
    return (1 / two_m) * acc
'''
mod_arr = []
for senate in range(96, 97):
    G = generate_digraph('/Users/alexray/Documents/data/', senate, ['s', 'sconres', 'sjres', 'sres', 'samendments'])
    print(len(G))
    avg_degree = np.mean([deg[1] for deg in G.in_degree])
    print(avg_degree)
    print(nx.average_shortest_path_length(G))

    G_bipartite = generate_bipartite_graph('/Users/alexray/Documents/data/', senate, ['s', 'sconres', 'sjres', 'sres', 'samendments'])
    print(len(G_bipartite))
    legislators = [node for node in G_bipartite.nodes if G_bipartite.nodes[node]['type'] == 'legislator']
    G_proj = nx.bipartite.weighted_projected_graph(G_bipartite, legislators)
    print(len(G))
    for node in G_proj.nodes:
        G_proj.add_edge(node, node, weight=G_bipartite.degree[node])
    G_arr = nx.to_numpy_array(G_proj, nodelist=G_proj.nodes)
    #G = nx.bipartite.biadjacency_matrix(G, G.nodes)
    #print(G)


    s = []
    #for i in range(len(G)):
    for i in G_proj.nodes:
        party = G_proj.nodes[i]['party']
        if 'Byrd, Harry F.,  Jr.' in G_proj.nodes[i]['name']:
            party = 'Independent'
        if party == 'Democrat':
            s.append('D')
        else:
            s.append('R')
    '''
    counter = 0
    for i in G.nodes:
        print(G.nodes[i]['name'] + '  ' + G.nodes[i]['party'] + '  ' + s[counter])
        counter += 1
    # Convert to adjacency matrix representation
    #G_arr = nx.to_numpy_array(G, nodelist=list(range(len(G))))
    '''
    #G_arr = nx.to_numpy_array(G, nodelist=G.nodes)

    print(G_arr)
    degrees = np.sum(G_arr, axis=1)
    s = np.random.permutation(s)
    mod = calculate_modularity(G_arr, degrees, s)
    print(mod)
    mod_arr.append(mod)
    '''
    P = create_expected_matrix(G_arr, degrees)
    
    M = create_modularity_matrix(G_arr, P)
    
    # https://docs.scipy.org/doc/numpy/reference/generated/numpy.linalg.eig.html
    eigenvalues, eigenvectors = np.linalg.eig(M)
    
    # https://stackoverflow.com/questions/5469286/how-to-get-the-index-of-a-maximum-element-in-a-numpy-array-along-one-axis
    # Get max eigenvalue
    max_eigenval_index = eigenvalues.argmax()
    max_eigenval = eigenvalues[max_eigenval_index]
    
    # Retrieve corresponding eigenvector
    x = eigenvectors[:, max_eigenval_index]
    
    # https://stackoverflow.com/questions/35215161/
    # Generating group matrix with eigenvector
    g = lambda x: 1 if x >= 0 else -1
    s = np.array([g(xi) for xi in x])
    '''
    #s = np.random.permutation(s)

    G = generate_graph('/Users/alexray/Documents/data/', senate, ['s', 'sconres', 'sjres', 'sres', 'samendments'])
    G_arr = nx.to_numpy_array(G, nodelist=G.nodes)
    s = []
    # for i in range(len(G)):
    for i in legislators:
        party = G.nodes[i]['party']
        if 'Byrd, Harry F.,  Jr.' in G.nodes[i]['name']:
            party = 'Independent'
        if party == 'Democrat':
            s.append('D')
        else:
            s.append('R')
    #G = update_nodes_to_numeric(G)
    print(G_arr)
    degrees = np.sum(G_arr, axis=1)
    mod = calculate_modularity(G_arr, degrees, s)
    print(mod)
    mod_arr.append(mod)


#plt.plot(list(range(96, 99)), mod_arr)
#plt.show()