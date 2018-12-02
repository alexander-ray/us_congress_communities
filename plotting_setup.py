# Figure setup
import matplotlib as mpl

black = '#2d2d2d'
white = '#f5f5f5'
# Trying to make plots look OK

# Avoid cutting off labels
mpl.rcParams['figure.autolayout'] = True
# Fonts
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = ['Helvetica']
mpl.rcParams['font.size'] = 16
# Setting normal framing colors to off-black
mpl.rcParams['text.color'] = black
mpl.rcParams['axes.labelcolor'] = black
mpl.rcParams['axes.edgecolor'] = black
mpl.rcParams['xtick.color'] = black
mpl.rcParams['ytick.color'] = black
# Background to off-white
mpl.rcParams['figure.facecolor'] = white
# Legend
mpl.rcParams['legend.framealpha'] = 0
mpl.rcParams['legend.borderpad'] = 0
mpl.rcParams['legend.markerscale'] = 0.05
mpl.rcParams['legend.handlelength'] = 0.8
mpl.rcParams['legend.frameon'] = False
mpl.rcParams['legend.handletextpad'] = 0.2
# Grid
mpl.rcParams['grid.color'] = 'k'
mpl.rcParams['grid.linestyle'] = ':'
mpl.rcParams['grid.linewidth'] = 0.5