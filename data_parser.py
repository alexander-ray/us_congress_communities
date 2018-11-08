import glob
import json
import networkx as nx


def generate_graph(path, congress, origin):
    """
    :param path: file path to directory containing data and legislators directories
    :param congress: integer between 93 and 115
    :param origin: 's' or 'hr' indicating senate or house
    :return:
    """
    assert 93 <= congress < 116, 'Not a valid congress'
    assert origin == 's' or origin == 'hr', 'Not a valid bill origin'

    G = nx.DiGraph()

    with open(path+'legislators/bioguide_lookup', 'r') as f:
        bioguide_lookup = json.load(f)

    def get_bioguide(d):
        if 'bioguide_id' in d:
            return d['bioguide_id']
        return bioguide_lookup[d['thomas_id']]

    # Assumes dir structure of ./data/congress_num/bills/origin_indicator/*/data.json
    dir_path = path + 'bills/' + str(congress) + '/' + origin + '/*/data.json'
    data_files = glob.glob(dir_path)
    for file in data_files:
        with open(file, 'r') as f:
            data = json.load(f)
            sponsor_id = get_bioguide(data['sponsor'])
            G.add_node(sponsor_id)
            G.nodes[sponsor_id]['name'] = data['sponsor']['name']
            G.nodes[sponsor_id]['state'] = data['sponsor']['state']

            for cosponsor in data['cosponsors']:
                G.add_edge(get_bioguide(cosponsor), sponsor_id)

    return G


def generate_bioguide_lookup(path):
    """
    Generate lookup tables for bioguide and thomas ids

    :param path: file path to legislators directory
    """
    thomas_lookup = {}
    bioguide_lookup = {}

    def load_data(f):
        data = json.load(f)
        for entry in data:
            if 'bioguide' in entry['id'] and 'thomas' in entry['id']:
                thomas_lookup[entry['id']['bioguide']] = entry['id']['thomas']
                bioguide_lookup[entry['id']['thomas']] = entry['id']['bioguide']

    with open(path+'legislators-current.json', 'r') as f:
        load_data(f)
    with open(path+'legislators-historical.json', 'r') as f:
        load_data(f)

    with open(path+'thomas_lookup', 'w') as fout:
        fout.write(json.dumps(thomas_lookup))
    with open(path+'bioguide_lookup', 'w') as fout:
        fout.write(json.dumps(bioguide_lookup))


path = '/Users/alexray/Documents/data/'
generate_bioguide_lookup(path+'legislators/')
G = generate_graph(path, 115, 's')
print(len(G))
