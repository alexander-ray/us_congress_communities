from data_parser import generate_graph, generate_digraph, generate_bipartite_graph
from analysis import generate_membership_list, update_nodes_to_numeric, apply_threshold
import numpy as np
import networkx as nx
import csv
import igraph
from NMI import calc_nmi
import pandas as pd
import math

def generate_attribute_dict(G, attribute_name):
    inv_attribute_dict = nx.get_node_attributes(G, attribute_name)
    attribute_dict = {}
    for k, v in inv_attribute_dict.items():
        attribute_dict.setdefault(v, []).append(k)

    return attribute_dict

def calculate_weighted_modularity(G):
        A = nx.to_numpy_array(G, nodelist=G.nodes)
        s = generate_membership_list(G.nodes)

        # Networkx to igraph: https://stackoverflow.com/questions/29655111/
        g = igraph.Graph.Adjacency((A > 0).tolist())
        g.es['weight'] = A[A.nonzero()]
        g.vs['label'] = list(G.nodes)
        mod = g.modularity(membership=s, weights='weight')
        eig_result = g.community_leading_eigenvector(clusters=None, weights='weight')
        max_mod = eig_result.modularity

        return mod, max_mod

def perform_projection(G_bipartite, projected_node_type, threshold=None):
    G_bipartite= update_nodes_to_numeric(G_bipartite)
    legislators = [node for node in G_bipartite.nodes if G_bipartite.nodes[node]['type'] == projected_node_type]
    if threshold is not None:
        G_bipartite = apply_threshold(G_bipartite, len(legislators), threshold)

    return nx.bipartite.weighted_projected_graph(G_bipartite, legislators)

def analyze_graph(G_bipartite):
    subject_modularities = {}
    bill_types = generate_attribute_dict(G_bipartite, 'subject')
    node_types = generate_attribute_dict(G_bipartite, 'type')
    legislators = node_types['legislator']

    for subject, valid_bills in bill_types.items():
        G_filtered = G_bipartite.subgraph(legislators + valid_bills)
        G_proj = perform_projection(G_filtered, 'legislator')
        mod, _ = calculate_weighted_modularity(G_proj)
        subject_modularities[subject] = mod
    
    return subject_modularities

def chamber_analysis(congresses, file_names):
    df = pd.DataFrame(columns=['CONGRESS'])

    for congress in congresses:
        G_bipartite = generate_bipartite_graph('/home/eitri/git/us_congress_communities/data/', congress, file_names)
        congress_data = analyze_graph(G_bipartite)
        congress_data['CONGRESS'] = congress
        df_congress_data = pd.DataFrame(congress_data, index=[0])
        df = pd.concat([df, df_congress_data], axis=0, sort=True)
    
    return df


def congress_analysis():
    house_names = ['hr']
    senate_names = ['s']
    congresses = list(range(96, 116))

    df = chamber_analysis(congresses, house_names)
    df.to_csv('/home/eitri/Documents/house_output.csv', encoding='utf-8')

    df = chamber_analysis(congresses, senate_names)
    df.to_csv('/home/eitri/Documents/senate_output.csv', encoding='utf-8')

congress_analysis()