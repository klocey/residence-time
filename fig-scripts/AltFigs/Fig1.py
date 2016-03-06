from __future__ import division
import  matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random
import os
import sys

import statsmodels.stats.api as sms
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.sandbox.regression.predstd import wls_prediction_std
from statsmodels.stats.outliers_influence import summary_table


mydir = os.path.expanduser('~/GitHub/ResTime')
sys.path.append(mydir+'/tools')
mydir2 = os.path.expanduser("~/")

dat = pd.read_csv(mydir + '/results/simulated_data/examples/2015_12_08/SimData.csv')

dat = dat[np.isfinite(dat['total.abundance'])]
dat = dat[np.isfinite(dat['species.richness'])]
dat = dat[np.isfinite(dat['simpson.e'])]
dat = dat[np.isfinite(dat['Whittakers.turnover'])]

dat = dat[dat['Whittakers.turnover'] > 0]
dat = dat[dat['total.abundance'] > 0]
dat = dat[dat['species.richness'] > 0]
dat = dat[dat['simpson.e'] > 0]

N = np.log10(dat['total.abundance']).tolist()
S = np.log10(dat['species.richness']).tolist()
W = np.log10(dat['Whittakers.turnover']).tolist()
E = dat['simpson.e']
motion = dat['motion']

disp = dat['max.active.dispersal']
colors = 1 - np.array(disp)

#disp = dat['res.inflow']
#colors = 0.001 * np.array(disp)

colors = colors.tolist()
colors = ['{:.4f}'.format(x) for x in colors]
#sys.exit()

tau = np.log10((dat['width']*dat['height'])/dat['flow.rate']).tolist()
dat['tau'] = list(tau)

d = pd.DataFrame({'N': list(N)})
d['tau'] = list(tau)
d['S'] = list(S)
d['E'] = list(E)
d['W'] = list(W)
d['motion'] = list(motion)
d['dispersal'] = list(disp)

#### plot figure ###############################################################
xlab = r"$log_{10}$"+'(' + r"$\tau$" +')'
fs = 8 # fontsize
fig = plt.figure()

#### N vs. Tau #################################################################
fig.add_subplot(2, 2, 1)

f2 = smf.ols('N ~ tau + I(tau ** 2.0)', d).fit()
print f2.summary()

a, b, c =  f2.params
p1, p2, p3 = f2.pvalues
r2 = round(f2.rsquared, 2)

st, data, ss2 = summary_table(f2, alpha=0.05)
fitted = data[:,2]
pred_mean_se = data[:,3]
pred_mean_ci_low, pred_mean_ci_upp = data[:,4:6].T
pred_ci_low, pred_ci_upp = data[:,6:8].T

tau2, fitted, pred_ci_low, pred_ci_upp, pred_mean_ci_low, pred_mean_ci_upp = zip(*sorted(zip(tau, fitted, pred_ci_low, pred_ci_upp, pred_mean_ci_low, pred_mean_ci_upp)))

plt.scatter(tau, N, color = colors , s = 10, linewidths=0.1, edgecolor='k')
#plt.fill_between(tau2, pred_ci_low, pred_ci_upp, color='r', lw=0.0, alpha=0.1)
#plt.fill_between(tau2, pred_mean_ci_low, pred_mean_ci_upp, color='r', lw=0.0, alpha=0.3)
plt.plot(tau2, fitted, color = 'r', ls='--', lw=1.5, alpha=0.9)

plt.ylabel(r"$log_{10}$"+'(' + r"$N$" +')', fontsize=fs+6)
plt.xlabel(xlab, fontsize=fs+6)
plt.tick_params(axis='both', which='major', labelsize=fs)
plt.ylim(-2, 5)
plt.text(2, -1,  r'$r^2$' + '=' +str(r2)+', '+r'$p$' + '=' +str(round(p2,4)), fontsize=fs+2, color='k')

#### S vs. Tau #################################################################
fig.add_subplot(2, 2, 2)
f2 = smf.ols('S ~ tau + I(tau ** 2.0)', d).fit()
#print f2.summary()
a, b, c =  f2.params
p1, p2, p3 = f2.pvalues
r2 = round(f2.rsquared, 2)

st, data, ss2 = summary_table(f2, alpha=0.05)
fitted = data[:,2]
pred_mean_se = data[:,3]
pred_mean_ci_low, pred_mean_ci_upp = data[:,4:6].T
pred_ci_low, pred_ci_upp = data[:,6:8].T

tau2, fitted, pred_ci_low, pred_ci_upp, pred_mean_ci_low, pred_mean_ci_upp = zip(*sorted(zip(tau, fitted, pred_ci_low, pred_ci_upp, pred_mean_ci_low, pred_mean_ci_upp)))

plt.scatter(tau, S, color = colors, s = 10, linewidths=0.1, edgecolor='k')
#plt.fill_between(tau2, pred_ci_low, pred_ci_upp, color='r', lw=0.0, alpha=0.1)
#plt.fill_between(tau2, pred_mean_ci_low, pred_mean_ci_upp, color='r', lw=0.0, alpha=0.3)
plt.plot(tau2, fitted, color = 'r', ls='--', lw=1.5, alpha=0.9)

plt.ylabel(r"$log_{10}$"+'(' + r"$S$" +')', fontsize=fs+6)
plt.xlabel(xlab, fontsize=fs+6)
plt.tick_params(axis='both', which='major', labelsize=fs)
plt.ylim(-2,3)

plt.text(2, -1.3,  r'$r^2$' + '=' +str(r2)+', '+r'$p$' + '=' +str(round(p2,4)), fontsize=fs+2, color='k')

#### E vs. Tau #################################################################
fig.add_subplot(2, 2, 3)
f2 = smf.ols('E ~ tau + I(tau ** 2.0)', d).fit()
#print f2.summary()
a, b, c =  f2.params
p1, p2, p3 = f2.pvalues
r2 = round(f2.rsquared, 2)

st, data, ss2 = summary_table(f2, alpha=0.05)
fitted = data[:,2]
pred_mean_se = data[:,3]
pred_mean_ci_low, pred_mean_ci_upp = data[:,4:6].T
pred_ci_low, pred_ci_upp = data[:,6:8].T

tau2, fitted, pred_ci_low, pred_ci_upp, pred_mean_ci_low, pred_mean_ci_upp = zip(*sorted(zip(tau, fitted, pred_ci_low, pred_ci_upp, pred_mean_ci_low, pred_mean_ci_upp)))

plt.scatter(tau, E, color = colors, s = 10, linewidths=0.1, edgecolor='k')
#plt.fill_between(tau2, pred_ci_low, pred_ci_upp, color='r', lw=0.0, alpha=0.1)
#plt.fill_between(tau2, pred_mean_ci_low, pred_mean_ci_upp, color='r', lw=0.0, alpha=0.3)
plt.plot(tau2, fitted, color = 'r', ls='--', lw=1.5, alpha=0.9)

plt.ylabel('Evenness', fontsize=fs+6)
plt.xlabel(xlab, fontsize=fs+6)
plt.ylim(-0.2, 1.1)
plt.tick_params(axis='both', which='major', labelsize=fs)

plt.text(5, -0.1,  r'$r^2$' + '=' +str(r2)+', '+r'$p$' + '=' +str(round(p2,4)), fontsize=fs+2, color='k')

#### W vs. Tau #################################################################
fig.add_subplot(2, 2, 4)
#d['tau'] = 10**np.array(tau)
#d['W'] = -1*np.array(d['W'])

f2 = smf.ols('W ~ tau + I(tau ** 2.0)', d).fit()
#print f2.summary()
a, b, c = f2.params
p1, p2, p3 = f2.pvalues
r2 = round(f2.rsquared, 2)

st, data, ss2 = summary_table(f2, alpha=0.05)
fitted = data[:,2]
pred_mean_se = data[:,3]
pred_mean_ci_low, pred_mean_ci_upp = data[:,4:6].T
pred_ci_low, pred_ci_upp = data[:,6:8].T

tau2, fitted, pred_ci_low, pred_ci_upp, pred_mean_ci_low, pred_mean_ci_upp = zip(*sorted(zip(tau, fitted, pred_ci_low, pred_ci_upp, pred_mean_ci_low, pred_mean_ci_upp)))

plt.scatter(tau, W, color = colors, s = 10, linewidths=0.1, edgecolor='k')
#plt.fill_between(tau2, pred_ci_low, pred_ci_upp, color='r', lw=0.0, alpha=0.1)
#plt.fill_between(tau2, pred_mean_ci_low, pred_mean_ci_upp, color='r', lw=0.0, alpha=0.3)
plt.plot(tau2, fitted, color = 'r', ls='--', lw=1.5, alpha=0.9)

plt.ylabel(r"$log_{10}$"+'(' + r"$\beta$" +')', fontsize=fs+6)
plt.xlabel(xlab, fontsize=fs+6)
plt.tick_params(axis='both', which='major', labelsize=fs)
plt.ylim(-3.5, 0.5)
plt.text(4, -0.25,  r'$r^2$' + '=' +str(r2)+', '+r'$p$' + '=' +str(round(p2,4)), fontsize=fs+2, color='k')

#### Final Format and Save #####################################################
plt.subplots_adjust(wspace=0.4, hspace=0.4)
#plt.savefig(mydir2 + 'Desktop/ResTime/figures/Fig3.png', dpi=600, bbox_inches = "tight")
plt.show()