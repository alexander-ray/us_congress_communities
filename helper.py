class Helper:

    @staticmethod
    def generate_membership_list_from_party(nodes):
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