from __future__ import division
import  matplotlib.pyplot as plt
import statsmodels.api as sm
import pandas as pd
import numpy as np
import os
import sys

mydir = os.path.expanduser('~/GitHub/residence-time/Emergence')
sys.path.append(mydir+'/tools')
mydir2 = os.path.expanduser("~/")

def figplot(x, y, xlab, ylab, fig, n):
    fig.add_subplot(2, 2, n)
    #plt.scatter(x, y, lw=0.5, color='0.2', s = 4)
    plt.scatter(x, y, s = sz, color='0.7', linewidths=0.1, edgecolor='w')
    lowess = sm.nonparametric.lowess(y, x, frac=fr)
    x, y = lowess[:, 0], lowess[:, 1]
    plt.plot(x, y, lw=_lw, color='k')
    plt.tick_params(axis='both', labelsize=6)
    plt.xlabel(xlab, fontsize=9)
    plt.ylabel(ylab, fontsize=9)
    return fig

p, fr, _lw, w, sz, fs = 2, 0.2, 2, 1, 5, 6

df = pd.read_csv(mydir + '/results/simulated_data/SimData.csv')

df2 = pd.DataFrame({'length' : df['length'].groupby(df['sim']).mean()})
df2['flow'] = df['flow.rate'].groupby(df['sim']).mean()
df2['tau'] = np.log10((df2['length']**p)/df2['flow'])
df2['R'] = np.log10(df['resource.particles'].groupby(df['sim']).mean())
df2['RDens'] = df['resource.concentration'].groupby(df['sim']).mean()

#df2 = df2[df2['RDens'] > 0]
#df2 = df2[df2['R'] > 0]
#### plot figure ###############################################################
xlab = r"$log_{10}$"+'(' + r"$\tau$" +')'
fig = plt.figure()

ylab = r"$log_{10}$"+ '(' + r"$R$" + ')'
fig = figplot(df2['tau'], df2['R'], xlab, ylab, fig, 1)

ylab = r"$RDens$"
fig = figplot(df2['tau'], df2['RDens'], xlab, ylab, fig, 2)

#### Final Format and Save #####################################################
plt.subplots_adjust(wspace=0.4, hspace=0.4)
plt.savefig(mydir + '/results/figures/resources_tau.png', dpi=600, bbox_inches = "tight")
plt.close()
