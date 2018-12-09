import glob
import json
import networkx as nx
import itertools


def generate_bipartite_graph(path, congress, origins):
    assert 93 <= congress < 116, 'Not a valid congress'

    G = nx.Graph()

    with open(path + 'legislators/bioguide_lookup', 'r') as f:
        bioguide_lookup = json.load(f)
    with open(path + 'legislators/party_lookup', 'r') as f:
        party_lookup = json.load(f)
    with open(path + 'legislators/legislators-current-test.json', 'r') as f:
        secondary_party_lookup = json.load(f)

    def get_bioguide(d):
        if 'bioguide_id' in d:
            return d['bioguide_id']
        return bioguide_lookup[d['thomas_id']]

    def get_party(bioguide):
        found = False
        if bioguide in party_lookup:
            return party_lookup[bioguide]['party']
        # https://theunitedstates.io/congress-legislators/ for more current data
        else:
            for e in secondary_party_lookup:
                if e['id']['bioguide'] == bioguide:
                    found = True
                    return e['terms'][0]['party']

    counter = 0
    bill_id_counter = 1
    for origin in origins:
        # Assumes dir structure of ./data/bills/CONGRESS_NUM/bills/origin_indicator/*/data.json
        dir_path = path + 'bills/' + str(congress) + '/' + origin + '/*/data.json'
        data_files = glob.glob(dir_path)
        for file in data_files:
            with open(file, 'r') as f:
                data = json.load(f)

                # Check if sponsor data included
                # e.x. /98/hjres/hjres308 doesn't have sponsor
                if data['sponsor'] == None:
                    continue
                sponsors = []
                sponsor_id = get_bioguide(data['sponsor'])
                if sponsor_id not in G:
                    G.add_node(sponsor_id)
                    G.nodes[sponsor_id]['name'] = data['sponsor']['name']
                    G.nodes[sponsor_id]['state'] = data['sponsor']['state']
                    G.nodes[sponsor_id]['party'] = get_party(sponsor_id)
                    G.nodes[sponsor_id]['type'] = 'legislator'
                sponsors.append(sponsor_id)
                for cosponsor in data['cosponsors']:
                    cosponsor_id = get_bioguide(cosponsor)
                    if cosponsor_id not in G:
                        G.add_node(cosponsor_id)
                        G.nodes[cosponsor_id]['name'] = cosponsor['name']
                        G.nodes[cosponsor_id]['state'] = cosponsor['state']
                        G.nodes[cosponsor_id]['party'] = get_party(cosponsor_id)
                        G.nodes[cosponsor_id]['type'] = 'legislator'

                    sponsors.append(cosponsor_id)

                bill_id = str(bill_id_counter)
                bill_id_counter += 1
                if bill_id not in G:
                    G.add_node(bill_id)
                    G.nodes[bill_id]['type'] = 'bill'
                    G.nodes[bill_id]['subject'] = data['subjects_top_term']

                for sponsor in sponsors:
                    # for u, v in itertools.combinations(sponsors, r=2):
                    # Add new edge if it doesn't exist
                    if not G.has_edge(bill_id, sponsor):
                        G.add_edge(bill_id, sponsor, weight=1)
    return G


def generate_graph(path, congress, origins):
    assert 93 <= congress < 116, 'Not a valid congress'

    G = nx.Graph()

    with open(path+'legislators/bioguide_lookup', 'r') as f:
        bioguide_lookup = json.load(f)
    with open(path+'legislators/party_lookup', 'r') as f:
        party_lookup = json.load(f)

    def get_bioguide(d):
        if 'bioguide_id' in d:
            return d['bioguide_id']
        return bioguide_lookup[d['thomas_id']]

    def get_party(bioguide):
        return party_lookup[bioguide]

    counter = 0
    for origin in origins:
        # Assumes dir structure of ./data/bills/CONGRESS_NUM/bills/origin_indicator/*/data.json
        dir_path = path + 'bills/' + str(congress) + '/' + origin + '/*/data.json'
        data_files = glob.glob(dir_path)
        for file in data_files:
            with open(file, 'r') as f:
                data = json.load(f)

                # Check if sponsor data included
                # e.x. /98/hjres/hjres308 doesn't have sponsor
                # '01594' is problematic in house 106
                if data['sponsor'] == None:
                    continue
                sponsors = []
                sponsor_id = get_bioguide(data['sponsor'])
                if sponsor_id not in G:
                    G.add_node(sponsor_id)
                    G.nodes[sponsor_id]['name'] = data['sponsor']['name']
                    G.nodes[sponsor_id]['state'] = data['sponsor']['state']
                    G.nodes[sponsor_id]['party'] = party_lookup[sponsor_id]['party']
                sponsors.append(sponsor_id)
                for cosponsor in data['cosponsors']:
                    cosponsor_id = get_bioguide(cosponsor)
                    if cosponsor_id not in G:
                        G.add_node(cosponsor_id)
                        G.nodes[cosponsor_id]['name'] = cosponsor['name']
                        G.nodes[cosponsor_id]['state'] = cosponsor['state']
                        G.nodes[cosponsor_id]['party'] = party_lookup[cosponsor_id]['party']
                    sponsors.append(cosponsor_id)

                for u, v in itertools.combinations_with_replacement(sponsors, r=2):
                #for u, v in itertools.combinations(sponsors, r=2):
                    # Add new edge if it doesn't exist
                    if not G.has_edge(u, v):
                        G.add_edge(u, v, weight=1)
                    # Otherwise, update weight
                    else:
                        w = G[u][v]['weight']
                        G.add_edge(u, v, weight=w+1)
    return G


def generate_digraph(path, congress, origins):
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

    with open(path+'legislators/bioguide_lookup', 'r') as f:
        bioguide_lookup = json.load(f)
    with open(path+'legislators/party_lookup', 'r') as f:
        party_lookup = json.load(f)

    def get_bioguide(d):
        if 'bioguide_id' in d:
            return d['bioguide_id']
        return bioguide_lookup[d['thomas_id']]

    def get_party(bioguide):
        return party_lookup[bioguide]

    counter = 0
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
                sponsor_id = get_bioguide(data['sponsor'])
                counter += 1
                if sponsor_id not in G:
                    G.add_node(sponsor_id)
                    G.nodes[sponsor_id]['name'] = data['sponsor']['name']
                    G.nodes[sponsor_id]['state'] = data['sponsor']['state']
                    G.nodes[sponsor_id]['party'] = party_lookup[sponsor_id]['party']

                if not G.has_edge(sponsor_id, sponsor_id):
                    G.add_edge(sponsor_id, sponsor_id, weight=1)
                else:
                    G[sponsor_id][sponsor_id]['weight'] += 1

                for cosponsor in data['cosponsors']:
                    if get_bioguide(cosponsor) not in G:
                        cosponsor_id = get_bioguide(cosponsor)
                        G.add_node(cosponsor_id)
                        G.nodes[cosponsor_id]['name'] = data['sponsor']['name']
                        G.nodes[cosponsor_id]['state'] = data['sponsor']['state']
                        G.nodes[cosponsor_id]['party'] = party_lookup[cosponsor_id]
                    if not G.has_edge(get_bioguide(cosponsor), sponsor_id):
                        G.add_edge(get_bioguide(cosponsor), sponsor_id, weight=1)
                    else:
                        G[get_bioguide(cosponsor)][sponsor_id]['weight'] += 1

    print(counter)
    return G

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
#generate_bioguide_lookup('/Users/alexray/Documents/data/legislators/')
#generate_graph('/Users/alexray/Documents/data/', 100, ['s', 'sconres', 'sjres', 'sres', 'amendments'])
#generate_graph('/Users/alexray/Documents/data/', 98, ['hr', 'hconres', 'hjres', 'hres'])