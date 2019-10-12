import csv
import sys

from sklearn.metrics import adjusted_mutual_info_score

from graph_generator import GraphGenerator
from graph_manipulator import GraphManipulator
from helper import Helper

sys.path.append('/Users/alexray/Dropbox/Fall2018CU/thesis/')

base_path = '/Users/alexray/Documents/data/'
bioguide_path = base_path + 'legislators/bioguide_lookup'
party_lookup_path = base_path + 'legislators/party_lookup'
secondary_party_lookup_path = base_path + 'legislators/legislators-current-test.json'

graph_gen = GraphGenerator(bioguide_path, party_lookup_path, secondary_party_lookup_path)

house_names = ['hr', 'hconres', 'hjres', 'hres', 'hamendments']
senate_names = ['s', 'sconres', 'sjres', 'sres', 'samendments']
chamber = 'house'
include_self_loops = False
#thresholds = [0.6, 0.7, 0.8, 0.9, 1.0]
thresholds = [None]

mod_arr = []
congresses = list(range(96, 116))
for threshold in thresholds:
    for congress in congresses:
        if chamber == 'house':
            G_bipartite = graph_gen.generate_bipartite_graph(base_path=base_path,
                                                             congress=congress,
                                                             origins=house_names)
        else:
            G_bipartite = graph_gen.generate_bipartite_graph(base_path=base_path,
                                                             congress=congress,
                                                             origins=senate_names)

        G_proj = GraphManipulator.one_mode_projection_from_bipartite(G_bipartite, include_self_loops)

        s = Helper.generate_membership_list_from_party(G_proj.nodes)

        g = GraphManipulator.igraph_from_networkx_one_mode(G_proj)
        mod = g.modularity(membership=s, weights='weight')
        eig_s = Helper.generate_max_modularity_membership(g)
        
        # Uncomment to write results to csv for later use
        with open('./data/' + chamber + '_ami_no_self.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([congress, adjusted_mutual_info_score(s, eig_s)])
