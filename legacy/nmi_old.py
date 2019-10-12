def calc_nmi(l1, l2):
    """
    Function to calculate NMI
    :param l1: List of group labels, ordered by node label
    :param l2: List of group labels, ordered by node label
    :return: Normalized mutual information (https://arxiv.org/pdf/0709.2108.pdf)
    """

    # Helper function to get intersection
    #  of nodes in two groups
    #  e.g. which nodes are in both groups
    def get_n_xx(g1, g2):
        n_xx = set()
        for i in range(num_nodes):
            if l1[i] == g1 and l2[i] == g2:
                n_xx.add(i)
        return len(n_xx)

    num_nodes = len(l1)
    s1 = set(l1)
    s2 = set(l2)

    s = 0
    # Iterate over all pairs of groups
    #  in both groupings
    for x in s1:
        for y in s2:
            # Calculate P(x), P(y), P(xy)
            num_nodes_in_x = sum([1 if i == x else 0
                                  for i in l1])
            p_x = num_nodes_in_x / num_nodes
            num_nodes_in_y = sum([1 if i == y else 0
                                  for i in l2])
            p_y = num_nodes_in_y / num_nodes
            p_xy = get_n_xx(x, y) / num_nodes

            # Increment sum
            # If statement to avoid log(0)
            if p_xy != 0:
                s += p_xy * np.log2(p_xy / (p_x * p_y))

    # Calculate H(x), H(y)
    h_x = 0
    for x in s1:
        p_x = sum([1 if i == x else 0 for i in l1]) / num_nodes
        h_x += -1 * p_x * np.log2(p_x)
    h_y = 0
    for y in s2:
        p_y = sum([1 if i == y else 0 for i in l2]) / num_nodes
        h_y += -1 * p_y * np.log2(p_y)

    # Put it all together
    #  to get NMI
    res = (2 * s) / (h_x + h_y)
    return res
