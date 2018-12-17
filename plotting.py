import matplotlib.pyplot as plt
import plotting_setup
import numpy as np

chamber = 'senate'
xlabel = 'Senate'
ylabel = 'Party Modularity'
title = 'Modularity of bills passing chamber'


congress_mask = set(range(97, 116))
data = []

modularities = []

# thresholds = {0.6: [], 0.7: [], 0.8: [], 0.9: [], 1.0: []}
congress = list(range(97, 116))

files = ['senate_bills_all.csv', 'senate_bills_passed.csv', 'house_bills_all.csv', 'house_bills_passed.csv']

with open(files[0], 'r') as f:
    for line in f:
        line = line.strip().split(',')
        if line[0] == '':
            continue
        else:
            modularities.append(float(line[3]))
            # print ('chamber: ', line[0],'\tCongress: ',line[1],'\tModularity: ', line[2],'\tmax mod: ', line[3])
plt.plot(congress, modularities, label='All Bills')

modularities = []
with open(files[1], 'r') as f:
    for line in f:
        line = line.strip().split(',')
        if line[0] == '':
            continue
        else:
            modularities.append(float(line[3]))
plt.plot(congress, modularities, label='Bills Passing Chamber')

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
