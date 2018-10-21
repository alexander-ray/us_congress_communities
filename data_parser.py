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

    # Assumes dir structure of ./data/congress_num/bills/origin_indicator/*/data.json
    dir_path = './data/' + str(congress) + '/bills/' + origin + '/*/data.json'
    data_files = glob.glob(dir_path)
    for file in data_files:
        with open(file, 'r') as f:
            data = json.load(f)
            sponsor_id = data['sponsor']['bioguide_id']
            G.add_node(sponsor_id)
            G.nodes[sponsor_id]['name'] = data['sponsor']['name']
            G.nodes[sponsor_id]['state'] = data['sponsor']['state']

            for cosponsor in data['cosponsors']:
                G.add_edge(cosponsor['bioguide_id'], sponsor_id)

    return G

G = generate_graph(15, 's')
