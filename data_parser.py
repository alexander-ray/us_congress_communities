import glob
import json
import networkx as nx


class GraphGenerator:
    DIRECTORY_FORMAT_STRING = '{}/bills/{}/{}/*/data.json'
    def __init__(self, bioguide_path, party_lookup_path, secondary_party_lookup_path):
        with open(bioguide_path, 'r') as f:
            self.bioguide_lookup = json.load(f)
        with open(party_lookup_path, 'r') as f:
            self.party_lookup = json.load(f)
        with open(secondary_party_lookup_path, 'r') as f:
            self.secondary_party_lookup = json.load(f)

    def generate_bipartite_graph(self, base_path, congress, origins):
        """
        Method to generate a bipartite legislator-legislation graph for a given congress

        :param path: Absolute path to data files
        :param congress: Numerical congress number
        :param origins: List of types of legislation to include
        :return: nx bipartite graph
        """
        assert 93 <= congress < 116, 'Not a valid congress'

        G = nx.Graph()

        bill_id_counter = 1
        for origin in origins:
            dir_path = base_path + 'bills/' + str(congress) + '/' + origin + '/*/data.json'
            data_files = glob.glob(dir_path)
            for file in data_files:
                with open(file, 'r') as f:
                    data = json.load(f)

                    # Check if sponsor data included
                    # e.x. /98/hjres/hjres308 doesn't have sponsor
                    if data['sponsor'] is None:
                        continue

                    sponsors = []
                    sponsor_id = self._get_bioguide(data['sponsor'])
                    self._add_legislator_node(G, sponsor_id, data)
                    sponsors.append(sponsor_id)
                    for cosponsor in data['cosponsors']:
                        cosponsor_id = self._get_bioguide(cosponsor)
                        self._add_legislator_node(G, cosponsor_id, data)
                        sponsors.append(cosponsor_id)

                    bill_id = str(bill_id_counter)
                    bill_id_counter += 1
                    if bill_id not in G:
                        G.add_node(bill_id)
                        G.nodes[bill_id]['type'] = 'bill'

                    for sponsor in sponsors:
                        # for u, v in itertools.combinations(sponsors, r=2):
                        # Add new edge if it doesn't exist
                        if not G.has_edge(bill_id, sponsor):
                            G.add_edge(bill_id, sponsor, weight=1)
        return G

    def generate_digraph(self, path, congress, origins):
        """
        Generate directed graph in the form of
        https://www.sciencedirect.com/science/article/pii/S037843710701206X?via%3Dihub

        Used for checking data collection process

        :param path: file path to directory containing data and legislators directories
        :param congress: integer between 93 and 115
        :param origins: iterable of origins
        :return:
        """
        assert 93 <= congress < 116, 'Not a valid congress'

        G = nx.DiGraph()

        for origin in origins:
            # Assumes dir structure of ./data/congress_num/bills/origin_indicator/*/data.json
            dir_path = path + 'bills/' + str(congress) + '/' + origin + '/*/data.json'
            data_files = glob.glob(dir_path)
            for file in data_files:
                with open(file, 'r') as f:
                    data = json.load(f)

                    # Check if sponsor data included
                    # e.x. /98/hjres/hjres308 doesn't have sponsor
                    if data['sponsor'] == None:
                        continue
                    sponsor_id = self._get_bioguide(data['sponsor'])
                    self._add_legislator_node(G, sponsor_id, data)

                    if not G.has_edge(sponsor_id, sponsor_id):
                        G.add_edge(sponsor_id, sponsor_id, weight=1)
                    else:
                        G[sponsor_id][sponsor_id]['weight'] += 1

                    for cosponsor in data['cosponsors']:
                        cosponsor_id = self._get_bioguide(cosponsor)
                        self._add_legislator_node(G, cosponsor_id, cosponsor)

                        if not G.has_edge(cosponsor_id, sponsor_id):
                            G.add_edge(cosponsor_id, sponsor_id, weight=1)
                        else:
                            G[cosponsor_id][sponsor_id]['weight'] += 1
        return G

    def _get_bioguide(self, d):
        if 'bioguide_id' in d:
            return d['bioguide_id']
        return self.bioguide_lookup[d['thomas_id']]

    def _get_party(self, bioguide):
        if bioguide in self.party_lookup:
            return self.party_lookup[bioguide]['party']
        # https://theunitedstates.io/congress-legislators/ for more current data
        else:
            for e in self.secondary_party_lookup:
                if e['id']['bioguide'] == bioguide:
                    return e['terms'][0]['party']

    def _add_legislator_node(self, G, bioguide_id, data):
        if bioguide_id not in G:
            G.add_node(bioguide_id)
            G.nodes[bioguide_id]['name'] = data['sponsor']['name']
            G.nodes[bioguide_id]['state'] = data['sponsor']['state']
            G.nodes[bioguide_id]['party'] = self._get_party(bioguide_id)
            G.nodes[bioguide_id]['type'] = 'legislator'

    # DANGEROUS
    # USE WITH CAUTION
    # SOME ARE HAND-CURATED
    '''
    def generate_bioguide_lookup(path):
        """
        Generate lookup tables for bioguide and thomas ids
    
        :param path: file path to legislators directory
        """
        thomas_lookup = {}
        bioguide_lookup = {}
        party_lookup = {}
        def load_data(f):
            data = json.load(f)
            for entry in data:
                if 'bioguide' in entry['id'] and 'thomas' in entry['id']:
                    thomas_lookup[entry['id']['bioguide']] = entry['id']['thomas']
                    bioguide_lookup[entry['id']['thomas']] = entry['id']['bioguide']
                    party_lookup[entry['id']['bioguide']] = {
                        'party': entry['terms'][0]['party'],
                        'name': entry['name']['first'] + ' ' + entry['name']['last'],
                        'state': entry['terms'][0]['state']
                    }
    
        with open(path+'legislators-current.json', 'r') as f:
            load_data(f)
        with open(path+'legislators-historical.json', 'r') as f:
            load_data(f)
    
        with open(path+'thomas_lookup', 'w') as fout:
            fout.write(json.dumps(thomas_lookup))
        with open(path+'bioguide_lookup', 'w') as fout:
            fout.write(json.dumps(bioguide_lookup))
        with open(path+'party_lookup', 'w') as fout:
            fout.write(json.dumps(party_lookup))
    '''
