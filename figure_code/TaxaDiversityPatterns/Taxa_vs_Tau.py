from __future__ import division
import  matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import statsmodels.api as sm


mydir = os.path.expanduser('~/GitHub/residence-time/Emergence')
tools = os.path.expanduser(mydir + "/tools")

df1 = pd.read_csv(mydir + '/results/simulated_data/Mason-SimData.csv')
df2 = pd.read_csv(mydir + '/results/simulated_data/Karst-SimData.csv')
df3 = pd.read_csv(mydir + '/results/simulated_data/BigRed2-SimData.csv')

frames = [df1, df2, df3]
df = pd.concat(frames)


def assigncolor(xs):
    cDict = {}
    clrs = []
    for x in xs:
        if x not in cDict:
            if x < 10: c = 'r'
            elif x < 20: c = 'OrangeRed'
            elif x < 30: c = 'Orange'
            elif x < 40: c = 'Gold'
            elif x < 50: c = 'Lime'
            elif x < 60: c = 'Green'
            elif x < 70: c = 'Cyan'
            elif x < 80: c = 'Blue'
            elif x < 90: c = 'Plum'
            else: c = 'Darkviolet'
            cDict[x] = c

        clrs.append(cDict[x])
    return clrs



def figplot(clrs, x, y, xlab, ylab, fig, n):
    fig.add_subplot(3, 3, n)
    plt.scatter(x, y, lw=0.5, color=clrs, s=sz, linewidths=0.0, edgecolor=None)
    #plt.scatter(x, y, lw=0.5, color=clrs, s=sz, linewidths=0.01, edgecolor='w')
    lowess = sm.nonparametric.lowess(y, x, frac=fr)
    x, y = lowess[:, 0], lowess[:, 1]
    plt.plot(x, y, lw=_lw, color='k')
    plt.tick_params(axis='both', labelsize=6)
    plt.xlabel(xlab, fontsize=9)
    plt.ylabel(ylab, fontsize=9)
    if n == 1: plt.ylim(0.0, 5.2)
    if n == 2: plt.ylim(0.0, 5)
    elif n == 4: plt.ylim(0.0, 3)
    elif n == 5: plt.ylim(0.0, 1.1)
    elif n == 8: plt.ylim(0, 110)
    elif n == 7: plt.ylim(0, 2.1)
    return fig


p, fr, _lw, w, sz, fs = 2, 0.2, 1.5, 1, 1, 6

mydir = os.path.expanduser('~/GitHub/residence-time/')

df2 = pd.DataFrame({'area' : df['area'].groupby(df['sim']).mean()})
df2['sim'] = df['sim'].groupby(df['sim']).mean()
df2['flow'] = df['flow.rate'].groupby(df['sim']).mean()
df2['tau'] = np.log10(df2['area']/df2['flow'])

df2['N'] = np.log10(df['total.abundance'].groupby(df['sim']).max())
df2['Prod'] = np.log10(df['ind.production'].groupby(df['sim']).max())
df2['S'] = np.log10(df['species.richness'].groupby(df['sim']).max())
df2['E'] = df['simpson.e'].groupby(df['sim']).mean()
df2['W'] = df['whittakers.turnover'].groupby(df['sim']).mean()
df2['Dorm'] = 100*df['percent.dormant'].groupby(df['sim']).mean()

df2 = df2.replace([np.inf, -np.inf], np.nan).dropna()

clrs = assigncolor(df2['area'])
df2['clrs'] = clrs

fig = plt.figure()
xlab = r"$log_{10}$"+'(' + r"$\tau$" +')'

fig = figplot(df2['clrs'], df2['tau'], df2['N'], xlab, r"$log_{10}$"+'(' + r"$N$" +')', fig, 1)
fig = figplot(df2['clrs'], df2['tau'], df2['Prod'], xlab, r"$log_{10}$"+'(' + r"$P$" +')', fig, 2)
fig = figplot(df2['clrs'], df2['tau'], df2['S'], xlab, r"$log_{10}$"+'(' + r"$S$" +')', fig, 4)
fig = figplot(df2['clrs'], df2['tau'], df2['E'], xlab, 'Evenness', fig, 5)
ylab = r"$log_{10}$"+'(' + r"$\beta$" +')'
fig = figplot(df2['clrs'], df2['tau'], df2['W'], xlab, ylab, fig, 7)
fig = figplot(df2['clrs'], df2['tau'], df2['Dorm'], xlab, '%Dormant', fig, 8)

plt.subplots_adjust(wspace=0.5, hspace=0.45)
plt.savefig(mydir + 'Emergence/results/figures/Taxa_vs_Tau.png', dpi=200, bbox_inches = "tight")
plt.close()
