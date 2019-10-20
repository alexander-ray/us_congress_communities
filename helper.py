import networkx as nx
from graph_manipulator import GraphManipulator

class Helper:
    @staticmethod
    def generate_membership_list_from_party(nodes):
        """
        Helper function to generate ordered list of group labels from Networkx nodeset

        :param nodes: Networkx nodes
        :return: ordered list of group labels
        """
        membership_dict = {}
        membership_count = 0
        s = []
        for i in nodes:
            party = nodes[i]['party']
            # note that Zhang et al. assigns non-democrats to the the republican group
            # We're going off real party
            if party in membership_dict:
                s.append(membership_dict[party])
            else:
                membership_dict[party] = membership_count
                s.append(membership_count)
                membership_count += 1
        return s

    @staticmethod
    def print_legislators(G, nodelist):
        for i in nodelist:
            print(f'{G.nodes[i]["name"]}  {G.nodes[i]["party"]}')

    @staticmethod
    def generate_max_modularity_membership(g):
        eig_result = g.community_leading_eigenvector(clusters=None, weights='weight')
        eig_s = []
        for i in range(g.vcount()):
            j = 0
            for group in eig_result:
                if i in group:
                    eig_s.append(j)
                    break
                j += 1
        return eig_s

    @staticmethod
    def generate_attribute_dict(G, attribute_name):
        inv_attribute_dict = nx.get_node_attributes(G, attribute_name)
        attribute_dict = {}
        for k, v in inv_attribute_dict.items():
            attribute_dict.setdefault(v, []).append(k)

        return attribute_dict

    @staticmethod
    def calculate_weighted_modularities(G):
        s = Helper.generate_membership_list_from_party(G.nodes)
        g = GraphManipulator.igraph_from_networkx_one_mode(G)
        mod = g.modularity(membership=s, weights='weight')
        eig_result = g.community_leading_eigenvector(clusters=None, weights='weight')
        max_mod = eig_result.modularity

        return mod, max_mod