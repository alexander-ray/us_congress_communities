import pandas as pd

from graph_generator import GraphGenerator
from graph_manipulator import GraphManipulator
from helper import Helper

def analyze_graph(G_bipartite):
    subject_modularities = {}
    bill_types = Helper.generate_attribute_dict(G_bipartite, 'subject')
    node_types = Helper.generate_attribute_dict(G_bipartite, 'type')
    legislators = node_types['legislator']

    for subject, valid_bills in bill_types.items():
        G_filtered = G_bipartite.subgraph(legislators + valid_bills)
        G_proj = GraphManipulator.one_mode_projection_from_bipartite(G_filtered, 'legislator')
        mod, _ = Helper.calculate_weighted_modularities(G_proj)
        subject_modularities[subject] = mod
    
    return subject_modularities

def analyze_graph_no_filter(G_bipartite):
    G_proj = GraphManipulator.one_mode_projection_from_bipartite(G_bipartite, 'legislator')
    mod, _ = Helper.calculate_weighted_modularities(G_proj)
    
    return mod

def chamber_analysis(congresses, file_names):
    df = pd.DataFrame(columns=['CONGRESS'])

    for congress in congresses:
        G_bipartite = graph_gen.generate_bipartite_graph('/home/eitri/git/us_congress_communities/data/', congress, file_names)
        congress_data = analyze_graph(G_bipartite)
        congress_data['CONGRESS'] = congress
        df_congress_data = pd.DataFrame(congress_data, index=[0])
        df = pd.concat([df, df_congress_data], axis=0, sort=True)
    
    return df

def total_modularity_analysis(congresses, file_names):
    df = pd.DataFrame(columns=['CONGRESS', 'MODULARITY'])

    for congress in congresses:
        G_bipartite = graph_gen.generate_bipartite_graph('/home/eitri/git/us_congress_communities/data/', congress, file_names)
        congress_mod = analyze_graph_no_filter(G_bipartite)
        df.loc[-1] = [congress, congress_mod]
        df.index = df.index + 1
        df.sort_index()
    return df

def total_congress_analysis():
    house_names = ['hr']
    senate_names = ['s']
    congresses = list(range(96, 116))

    df = total_modularity_analysis(congresses, house_names)
    df.to_csv('/home/eitri/Documents/house_modularities.csv', encoding='utf-8')

    df = total_modularity_analysis(congresses, senate_names)
    df.to_csv('/home/eitri/Documents/senate_modularities.csv', encoding='utf-8')

def congress_analysis():
    house_names = ['hr']
    senate_names = ['s']
    congresses = list(range(96, 116))

    df = chamber_analysis(congresses, house_names)
    df.to_csv('/home/eitri/Documents/house_output.csv', encoding='utf-8')

    df = chamber_analysis(congresses, senate_names)
    df.to_csv('/home/eitri/Documents/senate_output.csv', encoding='utf-8')

base_path = '/Users/alexray/Documents/data/'
bioguide_path = base_path + 'legislators/bioguide_lookup'
party_lookup_path = base_path + 'legislators/party_lookup'
secondary_party_lookup_path = base_path + 'legislators/legislators-current-test.json'

graph_gen = GraphGenerator(bioguide_path, party_lookup_path, secondary_party_lookup_path)
# congress_analysis()
total_congress_analysis()