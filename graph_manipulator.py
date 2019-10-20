import networkx as nx
import igraph
import numpy as np
import math

class GraphManipulator:
    @staticmethod
    def update_nodes_to_numeric(G):
        """
        Converts networkx nodes to numeric, setting 'bioguide' to be old node label

        :param G: nx.Graph
        :return: nx.Graph
        """
        return nx.convert_node_labels_to_integers(G, label_attribute='bioguide')

    @staticmethod
    def calculate_modularity(G, degrees, s):
        """
        Helper function to calculate weighted modularity. Same result as iGraph, but slower

        :param G: np array adjacency matrix
        :param degrees: ordered list of degrees
        :param s: ordered list of group labels
        :return: modularity score Q
        """
        two_m = np.sum(degrees)
        # two_m = 2*np.sum(np.triu(G))
        num_nodes = degrees.size
        acc = 0
        for i in range(num_nodes):
            for j in range(num_nodes):
                expected = (degrees[i] * degrees[j]) / two_m
                acc += (G[i, j] - expected) * (s[i] == s[j])
        return (1 / two_m) * acc

    @staticmethod
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
        c = 0
        for node in G.nodes:
            c += 1
            if G.nodes[node]['type'] == 'bill' and G.degree[node] > threshold:
                nodes_to_remove.append(node)
        G.remove_nodes_from(nodes_to_remove)
        return G

    @staticmethod
    def one_mode_projection_from_bipartite(G_bipartite, projected_node_type='legislator'):
        """
        Create one-mode projection onto legislators from bipartite legislators-legislation network

        :param G_bipartite: Original bipartite network
        :param projected_node_type: string designating type of projected nodes
        :return: Projection with numerical node labels
        """
        legislators = [node for node in G_bipartite.nodes if G_bipartite.nodes[node]['type'] == projected_node_type]
        G_proj = nx.bipartite.weighted_projected_graph(G_bipartite, legislators)
        return G_proj

    @staticmethod
    def igraph_from_networkx_one_mode(G):
        """
        Helper function to convert nx one-mode projection to igraph
        Normally leave as directed, as that selection properly calculates modularity by our definition
            (even though the true network is undirected)

        :param G: One mode projection nx.graph
        :return: igraph graph
        """
        A = nx.to_numpy_array(G, nodelist=G.nodes)
        A = np.triu(A) + np.tril(A)
        # Networkx to igraph: https://stackoverflow.com/questions/29655111/
        g = igraph.Graph.Adjacency((A > 0).tolist())
        g.es['weight'] = A[A.nonzero()]
        g.vs['label'] = list(G.nodes)
        # Leaving as directed results in correct modularity for self and no self loops
        # g.to_undirected(combine_edges='max')
        return g

