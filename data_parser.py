import glob
import json
import networkx as nx


def generate_graph(congress, origin):
    """

    :param congress: integer between 93 and 115
    :param origin: 's' or 'hr' indicating senate or house
    :return:
    """
    assert 93 <= congress < 116, 'Not a valid congress'
    assert origin == 's' or origin == 'hr', 'Not a valid bill origin'

    G = nx.DiGraph()

    with open('./legislators/bioguide_lookup', 'r') as f:
        bioguide_lookup = json.load(f)

    def get_bioguide(d):
        if 'bioguide_id' in d:
            return d['bioguide_id']
        return bioguide_lookup[d['thomas_id']]

    # Assumes dir structure of ./data/congress_num/bills/origin_indicator/*/data.json
    dir_path = './data/' + str(congress) + '/bills/' + origin + '/*/data.json'
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


def generate_bioguide_lookup():
    """
    Generate lookup tables for bioguide and thomas ids
    """
    thomas_lookup = {}
    bioguide_lookup = {}

    def load_data(f):
        data = json.load(f)
        for entry in data:
            if 'bioguide' in entry['id'] and 'thomas' in entry['id']:
                thomas_lookup[entry['id']['bioguide']] = entry['id']['thomas']
                bioguide_lookup[entry['id']['thomas']] = entry['id']['bioguide']

    with open('./legislators/legislators-current.json', 'r') as f:
        load_data(f)
    with open('./legislators/legislators-historical.json', 'r') as f:
        load_data(f)

    with open('./legislators/thomas_lookup', 'w') as fout:
        fout.write(json.dumps(thomas_lookup))
    with open('./legislators/bioguide_lookup', 'w') as fout:
        fout.write(json.dumps(bioguide_lookup))


generate_bioguide_lookup()
G = generate_graph(93, 's')
