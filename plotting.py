import matplotlib.pyplot as plt
import plotting_setup
import numpy as np

chamber = 'senate'
xlabel = 'Senate'
ylabel = 'Party Modularity'
title = 'Party modularity across different thresholds'


congress_mask = set(range(96, 116))
data = []
thresholds = {0.6: [], 0.7: [], 0.8: [], 0.9: [], 1.0: []}
congress = list(range(96, 116))
with open('./data/' + chamber + '_thresholds_no_self_bills.csv', 'r') as f:
    for line in f:
        line = line.strip().split(',')
        thres = float(line[0]); mod = float(line[2]); mod_max = float(line[3])
        thresholds[thres].append((mod, mod_max))

for thres in thresholds.keys():
    plt.plot(congress, [t[0] for t in thresholds[thres]], label=str(thres))

'''
with open('./data/' + chamber + '_senate_thresholds_no_self.csv', 'r') as f:
    for line in f:
        line = line.strip().split(',')
        #data.append((int(line[0]), float(line[1]), float(line[2])))
        data.append((int(line[0]), float(line[1])))

data = [d for d in data if d[0] in congress_mask]
congress = [d[0] for d in data]
nmi = [d[1] for d in data]
#max_mod = [d[2] for d in data]
poly = np.polyfit(congress, nmi, 1)
plt.plot(congress, np.poly1d(poly)(congress))
plt.scatter(congress, nmi)
#plt.plot(congress, max_mod, linestyle='--', label='Max Q')
'''

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