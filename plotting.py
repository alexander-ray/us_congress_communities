import matplotlib.pyplot as plt
import plotting_setup

chamber = 'house'
xlabel = 'House'
ylabel = 'NMI'
title = ''


congress_mask = set(range(96, 116))
data = []
with open('./data/' + chamber + '_nmi_no_self.csv', 'r') as f:
    for line in f:
        line = line.strip().split(',')
        #data.append((int(line[0]), float(line[1]), float(line[2])))
        data.append((int(line[0]), float(line[1])))

data = [d for d in data if d[0] in congress_mask]
congress = [d[0] for d in data]
nmi = [d[1] for d in data]
#max_mod = [d[2] for d in data]
plt.scatter(congress, nmi)
#plt.plot(congress, max_mod, linestyle='--', label='Max Q')
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
