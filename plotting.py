import matplotlib.pyplot as plt
import plotting_setup
import numpy as np
from scipy import stats
import pandas as pd
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker



"""
General helper functions
"""
def plot_data_at_index(ax, filename, x_idx, y_idx,
                       x_cast=int, y_cast=float, regression=False, ls='-',
                       label='', color='black', marker='x'):
    """
    Plot a "field" from a CSV. Assumes

    :param filename: Name of CSV
    :param x_idx: Index of x value
    :param y_idx: Index of y value
    :param ax: Matplotlib axis
    :param ls: Line style
    :param x_cast: Type to cast x values to
    :param y_cast: Type to cast y values to
    :param label: Label for line
    :param color: Color for line
    :param marker: Marker style for fitted scatter
    """
    x = []
    y = []
    with open(filename) as f:
        for line in f:
            line = line.strip().split(',')
            x.append(x_cast(line[x_idx]))
            y.append(y_cast(line[y_idx]))

    if regression:
        poly = np.polyfit(x, y, 1)
        ax.plot(x, np.poly1d(poly)(x), ls=ls, color=color)
        ax.scatter(x, y, alpha=0.3, color=color, marker=marker, label=label)
    else:
        ax.plot(x, y, ls=ls, label=label, color=color)


def get_max_mod_across_files(files):
    """
    Function to get maximum modularity values for plotting purposes

    :param files: Filename. Assumes 3 column CSV where indices 1 & 2 contain modularity values
    :return: Largest modularity value
    """
    curr_max = 0
    for file in files:
        with open(file, 'r') as f:
            for line in f:
                line = line.strip().split(',')
                if float(line[1]) > curr_max:
                    curr_max = float(line[1])
                if float(line[2]) > curr_max:
                    curr_max = float(line[2])
    return curr_max


def plot_color_bands(ax):
    """
    Function to plot hardcoded red and blue color bands on axis.

    :param ax: Matplotlib axis
    """
    ax.axvspan(ax.get_xlim()[0], 97, alpha=0.3, color='blue')  # Carter
    ax.axvspan(97, 103, alpha=0.3, color='red')  # Reagan and Bush Sr.
    ax.axvspan(103, 107, alpha=0.3, color='blue')  # Clinton
    ax.axvspan(107, 111, alpha=0.3, color='red')  # Bush Jr.
    ax.axvspan(111, ax.get_xlim()[1], alpha=0.3, color='blue')  # Obama


def plot_top_presidents(ax):
    """
    Function to plot hardcoded secondary x axis ticks for presidents.

    :param ax: Matplotlib axis
    """
    ax_top = ax.twiny()
    ax_top.set_xlim(ax.get_xlim())
    ax_top.set_xticks([97, 101, 103, 107, 111, 115])
    ax_top.set_xticklabels(['Reagan', 'H.W.Bush', 'Clinton', 'W. Bush', 'Obama', 'Trump'], rotation=45, fontsize=12)


"""
Specific functions to generate specific plots for the paper
"""
def plot_AMI():
    ax = plt.gca()
    ax.autoscale(enable=True, axis='x', tight=True)

    plot_data_at_index(ax=ax, filename='./data/house_ami_no_self.csv',
                       x_idx=0, y_idx=1, ls='-', label='House',
                       regression=True, marker='x')
    plot_data_at_index(ax=ax, filename='./data/senate_ami_no_self.csv',
                       x_idx=0, y_idx=1, ls='-', label='Senate',
                       regression=True, marker='o')

    plot_top_presidents(ax)
    plot_color_bands(ax)
    ax.legend()
    ax.set_xlabel('Congress')
    ax.set_ylabel('AMI')
    ax.set_ylim([0, 1])
    ax.grid()

    plt.minorticks_off()
    plt.savefig('./plots/main_ami_color_no_self', bbox_inches='tight', pad_inches=0.1)
    plt.show()


def plot_dual_panel_mod():
    fig = plt.figure(figsize=(12, 6))
    axes = np.empty(shape=(1, 2), dtype=object)
    gs = gridspec.GridSpec(1, 2)

    # Left
    ax = plt.Subplot(fig, gs[0, 0],
                     sharex=axes[0, 0], sharey=axes[0, 0])
    ax.grid()
    ax.autoscale(enable=True, axis='x', tight=True)
    ax.set_ylabel('Party Modularity')
    ax.set_xlabel('Congress')
    fig.add_subplot(ax)
    axes[0, 0] = ax
    # Right
    ax = plt.Subplot(fig, gs[0, 1],
                     sharex=axes[0, 0], sharey=axes[0, 0])
    ax.grid()
    plt.setp(ax.get_yticklabels(), visible=False)
    ax.autoscale(enable=True, axis='x', tight=True)
    ax.set_ylabel('Maximum Modularity')
    ax.set_xlabel('Congress')
    fig.add_subplot(ax)
    axes[0, 1] = ax

    ax = axes[0, 0]
    plot_data_at_index(ax=ax, filename='./data/house_party_mod_w_max_no_self.csv',
                       x_idx=0, y_idx=1, ls='-.', label='House')
    plot_data_at_index(ax=ax, filename='./data/senate_party_mod_w_max_no_self.csv',
                       x_idx=0, y_idx=1, ls=':', label='Senate')
    ax = axes[0, 1]
    plot_data_at_index(ax=ax, filename='./data/house_party_mod_w_max_no_self.csv',
                       x_idx=0, y_idx=2, ls='-.', label='House')
    plot_data_at_index(ax=ax, filename='./data/senate_party_mod_w_max_no_self.csv',
                       x_idx=0, y_idx=2, ls=':', label='Senate')

    max_y = get_max_mod_across_files(['./data/senate_party_mod_w_max_self.csv',
                                      './data/house_party_mod_w_max_self.csv'])
    axes[0, 0].set_ylim([0, max_y + 0.02])
    plot_top_presidents(axes[0, 0])
    plot_top_presidents(axes[0, 1])
    plot_color_bands(axes[0, 0])
    plot_color_bands(axes[0, 1])

    axes[0, 0].legend()
    axes[0, 1].legend()

    plt.tight_layout()
    plt.minorticks_off()
    plt.savefig('./plots/both_mod_color_no_self', bbox_inches='tight', pad_inches=0.1)
    plt.show()

"""
CALL FUNCTION HERE
"""
plot_dual_panel_mod()


"""
OUTDATED SPECIFIC PLOTTING FUNCTIONS
"""
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