import matplotlib.pyplot as plt
import plotting_setup
import numpy as np
from scipy import stats
import pandas as pd

congress_mask = set(range(96, 116))


def plot_mod_and_max_mod(filename):
    congress = list(range(96, 116))
    data = []
    data2 = []
    with open(filename) as f:
        for line in f:
            line = line.strip().split(',')
            data.append((float(line[0]),float(line[1])))
            data2.append((float(line[0]),float(line[2])))
    congress = [c for c in congress if c in congress_mask]
    data = [d[1] for d in data if d[0] in congress_mask]
    data2 = [d[1] for d in data2 if d[0] in congress_mask]
    plt.plot(congress, data, label='Party Q')
    plt.plot(congress, data2, label='Max Q', ls='--')


def plot_thresholds(filename, max=False):
    data = []
    data2 = []
    data3 = []
    thresholds = {0.6: [], 0.7: [], 0.8: [], 0.9: [], 1.0: []}
    congress = list(range(96, 116))
    with open(filename) as f:
        for line in f:
            line = line.strip().split(',')
            if float(line[0]) not in thresholds.keys():
                continue
            if max:
                thresholds[float(line[0])].append(float(line[3]))
            else:
                thresholds[float(line[0])].append(float(line[2]))

    for threshold in thresholds.keys():
        plt.plot(congress, thresholds[threshold], label=threshold)


def plot_nmi(nmi_path):
    data = []
    for d in open(nmi_path, 'r'):
        d = d.strip().split(',')
        data.append(float(d[1]))

    congress = list(range(96, 116))
    slope, intercept, r_value, p_value, std_err = stats.linregress(congress, data)
    poly = np.polyfit(congress, data, 1)
    plt.plot(congress, np.poly1d(poly)(congress))
    plt.scatter(congress, data, alpha=0.3)


def plot_partisanship(mod_path, nmi_path):
    data = []
    data2 = []
    for d1, d2 in zip(open(mod_path, 'r'),
                      open(nmi_path, 'r')):
        d1 = d1.strip().split(',')
        d2 = d2.strip().split(',')

        data.append(float(d1[2]))
        data2.append(float(d2[1]))

    partisanship = [a * b for a, b in zip(data, data2)]
    congress = list(range(96, 116))
    slope, intercept, r_value, p_value, std_err = stats.linregress(congress, partisanship)
    poly = np.polyfit(congress, partisanship, 1)
    plt.plot(congress, np.poly1d(poly)(congress))
    plt.scatter(congress, partisanship, alpha=0.3)

chamber = 'senate'
xlabel = 'Senate'
ylabel = 'Modularity'
title = 'Senate Modularity w/ Self, Congress 96-115'

#plot_nmi('./data/' + chamber + '_nmi_no_self.csv')
#plot_partisanship('./data/' + chamber + '_party_mod_w_max_no_self_check.csv',
#                  './data/' + chamber + '_nmi_no_self.csv')
#plot_thresholds('./data/' + chamber + '_thresholds_no_self.csv', max=False)
plot_mod_and_max_mod('./data/' + chamber + '_party_mod_w_max_self.csv')

ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.xlabel(xlabel)
plt.ylabel(ylabel)
plt.title(title)
plt.legend(frameon=False)
plt.grid()
ax.margins(x=0)
plt.show()
