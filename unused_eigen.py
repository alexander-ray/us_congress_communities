import numpy as np

def create_expected_matrix(G, degrees):
    P = np.zeros(G.shape)
    # "m is the total weight of the edges in the network"
    two_m = np.sum(G)
    for i in range(G[0].size):
        for j in range(G[0].size):
            P[i, j] = (degrees[i]*degrees[j])/two_m
    return P


def create_modularity_matrix(G, P):
    return np.subtract(G, P)


P = create_expected_matrix(G_arr, degrees)

M = create_modularity_matrix(G_arr, P)

# https://docs.scipy.org/doc/numpy/reference/generated/numpy.linalg.eig.html
eigenvalues, eigenvectors = np.linalg.eig(M)

# https://stackoverflow.com/questions/5469286/how-to-get-the-index-of-a-maximum-element-in-a-numpy-array-along-one-axis
# Get max eigenvalue
max_eigenval_index = eigenvalues.argmax()
max_eigenval = eigenvalues[max_eigenval_index]

# Retrieve corresponding eigenvector
x = eigenvectors[:, max_eigenval_index]

# https://stackoverflow.com/questions/35215161/
# Generating group matrix with eigenvector
g = lambda x: 1 if x >= 0 else -1
s = np.array([g(xi) for xi in x])