def gt_graph_from_networkx_bipartite(G_bipartite):
    """
    Helper function to convert nx bipartite to graph-tool. Stores weights in 'weight' e

    :param G_bipartite:
    :return:
    """
    G_bipartite = nx.convert_node_labels_to_integers(G_bipartite)
    A = nx.to_numpy_array(G_bipartite, nodelist=G_bipartite.nodes)

    edges = np.zeros((np.count_nonzero(A), 3), dtype='uint16')
    edges[:, 0:2] = np.transpose(np.nonzero(A))
    for e in range(edges.shape[0]):
        edges[e, 2] = A[edges[e, 0], edges[e, 1]]
    #g = gt.Graph(directed=False)
    # https: // stackoverflow.com / questions / 45821741 /
    weight = g.new_edge_property('int')
    eprops = [weight]
    g.ep['weight'] = weight
    g.add_edge_list(edges, eprops=eprops)

    type_vprop = g.new_vertex_property('string')
    g.vertex_properties['type'] = type_vprop
    for v in g.vertices():
        if G_bipartite.nodes[v]['type'] == 'legislator':
            g.vp.type[v] = 0
        else:
            g.vp.type[v] = 1

    return g


g = gt.Graph()

# GRAPH-TOOL CODE
G_bipartite = nx.convert_node_labels_to_integers(G_bipartite)
g = gt_graph_from_networkx_bipartite(G_bipartite)
# https://github.com/martingerlach/hSBM_Topicmodel/blob/master/sbmtm.py#L139
clabel = g.vp['type']
state_args = {'clabel': clabel, 'pclabel': clabel}
state_args['eweight'] = g.ep.weight
mdl = np.inf
for i in range(5):
    state_tmp = gt.minimize_nested_blockmodel_dl(g, deg_corr=True,
                                                 overlap=None,
                                                 state_args=state_args,
                                                 B_min=2)
    mdl_tmp = state_tmp.entropy()
    print(mdl_tmp)
    if mdl_tmp < mdl:
        mdl = 1.0 * mdl_tmp
        state = state_tmp.copy()

print('Final:')
print(state)
print(state.entropy())

# Generate json files with all nested group memberships
first_level_partition = state.levels[0].get_blocks()
group_dict = {}
for v in g.get_vertices():
    if G_bipartite.nodes[v]['type'] == 'legislator':
        if first_level_partition[v] not in group_dict:
            group_dict[first_level_partition[v]] = []
        group_dict[first_level_partition[v]].append((G_bipartite.nodes[v]['name'], G_bipartite.nodes[v]['party']))
with open('./data/sbm/114_senate_groups_nested_level_1.json', 'w') as f:
    f.write(json.dumps(group_dict, indent=4, sort_keys=True))

# http://main-discussion-list-for-the-graph-tool-project.982480.n3.nabble.com/About-the-blocks-from-the-minimize-nested-blockmodel-dl-td4026580.html
partitions = state.levels[1:]
prev_par = group_dict
level_counter = 1
for partition in partitions:
    level_counter += 1
    tmp = {}
    curr_par = partition.get_blocks()
    for k, v in prev_par.items():
        if curr_par[k] not in tmp:
            tmp[curr_par[k]] = []
        for i in v:
            tmp[curr_par[k]].append(i)
    with open('./data/sbm/114_senate_groups_nested_level_' + str(level_counter) + '.json', 'w') as f:
        f.write(json.dumps(tmp, indent=4, sort_keys=True))
    prev_par = tmp

    # gt.draw_hierarchy(state, output="114_senate.pdf", layout='bipartite')