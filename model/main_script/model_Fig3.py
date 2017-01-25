from __future__ import division
import statsmodels.tsa.stattools as sta
from math import isnan
from scipy import stats
import numpy as np
from numpy import sin, pi, mean
import sys
import os
import time

mydir = os.path.expanduser("~/")
sys.path.append(mydir + "GitHub/residence-time/model/metrics")
import metrics
sys.path.append(mydir + "GitHub/residence-time/model/LBM")
import LBM
sys.path.append(mydir + "GitHub/residence-time/model/bide")
import bide_Fig3 as bide
sys.path.append(mydir + "GitHub/residence-time/model/randparams")
import randparams_Fig3 as rp
sys.path.append(mydir + "GitHub/residence-time/model/spatial")
import spatial


""" To generate movies:
1.) uncomment line 'ani.save' on or near line 364
2.) adjust the frames variable on or near line 364, to change movie length
3.) change plot_system = 'no' to 'yes' on or near line 66

Because generating animations requires computing time and memory, doing so can
be computationally demanding. To quicken the process, use plot_system = 'no' on
or near line 66.
"""

# https://www.quantstart.com/articles/Basics-of-Statistical-Mean-Reversion-Testing
# http://statsmodels.sourceforge.net/0.5.0/generated/statsmodels.tsa.stattools.adfuller.html


GenPath = mydir + 'GitHub/residence-time/results/simulated_data/'

OUT1 = open(GenPath + 'SimData_Fig3.csv','w')
print>>OUT1, 'RowID,motion,dormancy,ind.production,biomass.prod.N,biomass.prod.P,biomass.prod.C,res.inflow,N.types,P.types,C.types,max.res.val,max.growth.rate,max.met.maint,max.active.dispersal,barriers,logseries.a,starting.seed,flow.rate,width,height,viscosity,total.abundance,immigration.rate,resource.tau,particle.tau,individual.tau,resource.concentration,shannons.resource.diversity,resource.richness,species.richness,simpson.e,e.var,berger.parker,inv.simp.D,N.max,skew,tracer.particles,resource.particles,speciation,Whittakers.turnover,Jaccards.dissimilarity,Sorensens.dissimilarity,avg.per.capita.growth,avg.per.capita.maint,avg.per.capita.N.efficiency,avg.per.capita.P.efficiency,avg.per.capita.C.efficiency,avg.per.capita.active.dispersal,amplitude,flux,frequency,phase,disturbance,spec.growth,spec.disp,spec.maint,avg.dist,dorm.freq,avg.per.capita.RPF,avg.per.capita.MF,spec.RPF,spec.MF'
OUT1.close()

def nextgen():

    """ Function called for each successive animation frame; arg is the frame number """

    global mmax, pmax, ADs, ADList, AVG_DIST, SpecDisp, SpecMaint, SpecGrowth
    global fixed, p, BurnIn, t, num_sims, width, height, Rates, u0, rho, ux, uy
    global n0, nN, nS, nE, nW, nNE, nNW, nSE, nSW, SpColorDict, GrowthDict, N_RD
    global P_RD, C_RD, DispDict, MaintDict, one9th, four9ths, one36th, barrier
    global gmax, dmax, maintmax, IndIDs, Qs, IndID, IndTimeIn, IndExitAge, IndX
    global IndY,  Ind_scatImage, SpeciesIDs, EnvD, TY, tracer_scatImage, TTimeIn
    global TIDs, TExitAge, TX, RTypes, RX, RY, RID, RIDs, RVals, RTimeIn, RExitAge
    global resource_scatImage, bN, bS, bE, bW, bNE, bNW, bSE, bSW, ct1, Mu, Maint
    global motion, reproduction, speciation, seedCom, m, r, nNi, nP, nC, rmax, sim
    global RAD, splist, N, ct, splist2, WTs, Jcs, Sos, RDens, RDiv, RRich, S, ES
    global Ev, BP, SD, Nm, sk, T, R, prod_i, prod_q, viscosity, alpha, dorm, imm
    global Ts, Rs, PRODIs, Ns, TTAUs, INDTAUs, RDENs, RDIVs, RRICHs, Ss, ESs, EVs
    global BPs, SDs, NMAXs, SKs, MUs, MAINTs, PRODNs, PRODPs, PRODCs, lefts, bottoms
    global Gs, Ms, NRs, PRs, CRs, Ds, RTAUs, GrowthList, MaintList, N_RList, P_RList
    global C_RList, DispList, amp, freq, flux, pulse, phase, disturb, envgrads
    global barriers, MainFactorDict, RPFDict, RPFList, MFList, SpecRPF, SpecMF

    ct = 0
    while ct >= 0:
        ct += 1
        # fluctuate flow according to amplitude, frequency, & phase
        u1 = u0 + u0*(amp * sin(2*pi * ct * freq + phase))
    
        # Fluid dynamics
        nN, nS, nE, nW, nNE, nNW, nSE, nSW, barrier = LBM.stream([nN, nS, nE, nW, nNE, nNW, nSE, nSW, barrier])
        rho, ux, uy, n0, nN, nS, nE, nW, nNE, nNW, nSE, nSW = LBM.collide(viscosity, rho, ux, uy, n0, nN, nS, nE, nW, nNE, nNW, nSE, nSW, u0)
    
        # Inflow of tracers
        if ct == 1:
            TIDs, TTimeIn, TX, TY = bide.NewTracers(motion,TIDs, TX, TY, TTimeIn, width, height, u0, ct)
    
        # moving tracer particles
        if len(TIDs) > 0:
            if motion == 'fluid':
                TIDs, TX, TY, TExitAge, TTimeIn = bide.fluid_movement('tracer', TIDs, TTimeIn, TExitAge, TX, TY, ux, uy, width, height, u0)
            else:
                TIDs, TX, TY, TExitAge, TTimeIn = bide.nonfluid_movement('tracer', motion, TIDs, TTimeIn, TExitAge, TX, TY, ux, uy, width, height, u0)
    
    
        # Inflow of resources
        RTypes, RVals, RX, RY,  RIDs, RID, RTimeIn = bide.ResIn(motion, RTypes, RVals, RX, RY,  RID, RIDs, RTimeIn, r, rmax, nNi, nP, nC, width, height, u1)
    
        # Resource flow
        Lists = [RTypes, RIDs, RID, RVals]
        if len(RTypes) > 0:
            if motion == 'fluid':
                RTypes, RX, RY,  RExitAge, RIDs, RID, RTimeIn, RVals = bide.fluid_movement('resource', Lists, RTimeIn, RExitAge, RX, RY,  ux, uy, width, height, u0)
            else:
                RTypes, RX, RY,  RExitAge, RIDs, RID, RTimeIn, RVals = bide.nonfluid_movement('resource', motion, Lists, RTimeIn, RExitAge, RX, RY,  ux, uy, width, height, u0)
    
        # Inflow of individuals (immigration)
        if ct == 1:
            SpeciesIDs, IndX, IndY,  MaintDict, MainFactorDict, RPFDict, EnvD, GrowthDict, DispDict, SpColorDict, IndIDs, IndID, IndTimeIn, Qs, N_RD, P_RD, C_RD, GrowthList, MaintList, N_RList, P_RList, C_RList, DispList, ADList = bide.immigration(mmax, pmax, dmax, gmax, maintmax, motion, seedCom, 1, SpeciesIDs, IndX, IndY,  width, height, MaintDict, MainFactorDict, RPFDict, EnvD, envgrads, GrowthDict, DispDict, SpColorDict, IndIDs, IndID, IndTimeIn, Qs, N_RD, P_RD, C_RD, nNi, nP, nC, u1, alpha, GrowthList, MaintList, N_RList, P_RList, C_RList, DispList, ADList)
        elif imm == 'yes':
            SpeciesIDs, IndX, IndY,  MaintDict, MainFactorDict, RPFDict, EnvD, GrowthDict, DispDict, SpColorDict, IndIDs, IndID, IndTimeIn, Qs, N_RD, P_RD, C_RD, GrowthList, MaintList, N_RList, P_RList, C_RList, DispList, ADList = bide.immigration(mmax, pmax, dmax, gmax, maintmax, motion, 1, m, SpeciesIDs, IndX, IndY,  width, height, MaintDict, MainFactorDict, RPFDict, EnvD, envgrads, GrowthDict, DispDict, SpColorDict, IndIDs, IndID, IndTimeIn, Qs, N_RD, P_RD, C_RD, nNi, nP, nC, u1, alpha, GrowthList, MaintList, N_RList, P_RList, C_RList, DispList, ADList)
    
    
        # dispersal
        Lists = [SpeciesIDs, IndIDs, IndID, Qs, DispDict, GrowthList, MaintList, N_RList, P_RList, C_RList, DispList, ADList]
        if len(SpeciesIDs) > 0:
            if motion == 'fluid':
                #sys.exit()
                SpeciesIDs, IndX, IndY, IndExitAge, IndIDs, IndID, IndTimeIn, Qs, GrowthList, MaintList, N_RList, P_RList, C_RList, DispList, ADList = bide.fluid_movement('individual', Lists, IndTimeIn, IndExitAge, IndX, IndY,  ux, uy, width, height, u0)
            else:
                SpeciesIDs, IndX, IndY, IndExitAge, IndIDs, IndID, IndTimeIn, Qs, GrowthList, MaintList, N_RList, P_RList, C_RList, DispList, ADList = bide.nonfluid_movement('individual', motion, Lists, IndTimeIn, IndExitAge, IndX, IndY,  ux, uy, width, height, u0)
    
        # Forage
        if len(SpeciesIDs) > 0:
            SpeciesIDs, Qs, IndIDs, ID, TimeIn, X, Y, GrowthDict, DispDict, GrowthList, MaintList, N_RList, P_RList, C_RList, DispList, ADList = bide.nearest_forage(RVals, RX, RY, reproduction, speciation, SpeciesIDs, Qs, IndIDs, IndID, IndTimeIn, IndX, IndY,  width, height, GrowthDict, DispDict, SpColorDict, N_RD, P_RD, C_RD, MaintDict, MainFactorDict, RPFDict, EnvD, envgrads, nNi, nP, nC, GrowthList, MaintList, N_RList, P_RList, C_RList, DispList, ADList)
    
        PRODI, PRODN, PRODC, PRODP = 0, 0, 0, 0
        p1, TNQ1, TPQ1, TCQ1 = metrics.getprod(Qs)
    
        # Consume
        if len(SpeciesIDs) > 0:
            RTypes, RVals, RIDs, RID, RTimeIn, RExitAge, RX, RY,  SpeciesIDs, Qs, IndIDs, IndID, IndTimeIn, IndX, IndY, GrowthList, MaintList, N_RList, P_RList, C_RList, DispList, ADList = bide.consume(RPFDict, RTypes, RVals, RIDs, RID, RX, RY,  RTimeIn, RExitAge, SpeciesIDs, Qs, IndIDs, IndID, IndTimeIn, IndX, IndY,  width, height, GrowthDict, N_RD, P_RD, C_RD, DispDict, GrowthList, MaintList, MainFactorDict, N_RList, P_RList, C_RList, DispList, ADList)
    
        # transition to or from dormancy
        if dorm == 'yes':
            if len(SpeciesIDs) > 0:
                Sp_IDs, IDs, Qs, GrowthList, MaintList, ADList = bide.transition(SpeciesIDs, IndIDs, Qs, GrowthList, MaintList, MainFactorDict, RPFDict,  ADList)
    
        # maintenance
        if len(SpeciesIDs) > 0:
            SpeciesIDs, X, Y, IndExitAge, IndIDs, IndTimeIn, Qs, GrowthList, MaintList, N_RList, P_RList, C_RList, DispList, ADList = bide.maintenance(SpeciesIDs, IndX, IndY,  IndExitAge, SpColorDict, MaintDict, MainFactorDict, RPFDict, EnvD, IndIDs, IndTimeIn, Qs, GrowthList, MaintList, N_RList, P_RList, C_RList, DispList, ADList)
    
        # Reproduction
        if len(SpeciesIDs) > 0:
            SpeciesIDs, Qs, IndIDs, ID, TimeIn, X, Y, GrowthDict, DispDict, GrowthList, MaintList, N_RList, P_RList, C_RList, DispList, ADList, MainFactorDict, RPFDict = bide.reproduce(reproduction, speciation, SpeciesIDs, Qs, IndIDs, IndID, IndTimeIn, IndX, IndY,  width, height, GrowthDict, DispDict, SpColorDict, N_RD, P_RD, C_RD, MaintDict, MainFactorDict, RPFDict, EnvD, envgrads, nNi, nP, nC, GrowthList, MaintList, N_RList, P_RList, C_RList, DispList, ADList)
    
    
        p2, TNQ2, TPQ2, TCQ2 = metrics.getprod(Qs)
    
        PRODI = p2 - p1
        PRODN = TNQ2 - TNQ1
        PRODP = TPQ2 - TPQ1
        PRODC = TCQ2 - TCQ1
    
        # disturbance
        minN = 10000
        if len(IndIDs) > minN:
            SpeciesIDs, X, Y, IndExitAge, IndIDs, IndTimeIn, Qs, GrowthList, MaintList, N_RList, P_RList, C_RList, DispList, ADList = bide.decimate(SpeciesIDs, IndX, IndY,  IndExitAge, SpColorDict, MaintDict, MainFactorDict, RPFDict, EnvD, IndIDs, IndTimeIn, Qs, GrowthList, MaintList, N_RList, P_RList, C_RList, DispList, ADList, minN)
    
        if len(SpeciesIDs) >= 1:  RAD, splist = bide.GetRAD(SpeciesIDs)
        else: RAD, splist, N, S = [], [], 0, 0
    
        N, S, tt, rr = sum(RAD), len(RAD), len(TIDs), len(RIDs)
        numD = ADList.count('d')
        Ns.append(N)
        
        if u0 > 0.5: lim = 100
        elif u0 > 0.1: lim = 100
        elif u0 > 0.01: lim = 100
        elif u0 > 0.001: lim = 100
        else: lim = 200
        
        if len(Ns) >= lim:
    
            if BurnIn == 'not done':
                AugmentedDickeyFuller = sta.adfuller(Ns)
                val, p = AugmentedDickeyFuller[0:2]
    
                if p >= 0.05:
                    Ns.pop(0)
    
                elif p < 0.05 or isnan(p) == True:
                    BurnIn = 'done'
                    Ns = [Ns[-1]] # only keep the most recent N value
    
        if BurnIn == 'done':
    
            PRODIs.append(PRODI)
            PRODNs.append(PRODN)
            PRODPs.append(PRODP)
            PRODCs.append(PRODC)
    
            if len(RExitAge) > 0:
                RTAUs.append(mean(RExitAge))
            if len(IndExitAge) > 0:
                INDTAUs.append(mean(IndExitAge))
            if len(TExitAge) > 0:
                TTAUs.append(mean(TExitAge))
    
            # Examining the resource RAD
            if len(RTypes) > 0:
                RRAD, Rlist = bide.GetRAD(RTypes)
                RDens = len(RTypes)/(height*width)
                RDiv = float(metrics.Shannons_H(RRAD))
                RRich = len(Rlist)
    
            RDENs.append(RDens)
            RDIVs.append(RDiv)
            RRICHs.append(RRich)
    
            # Number of tracers, resource particles, and individuals
            T, R, N = len(TIDs), len(RIDs), len(SpeciesIDs)
    
            Ts.append(T)
            Rs.append(R)
            Ss.append(S)
    
    
            if N >= 1:
    
                if R >= 1:
                    q = min([10, R])
                    avg_dist = spatial.avg_dist(IndX, RX, IndY, RY, q)
                    avg_dist = spatial.nearest_neighbor(IndX, RX, IndY, RY, q)
                    AVG_DIST.append(avg_dist)
    
                spD = DispDict.values()
                spM = MaintDict.values()
                spMF = MainFactorDict.values()
                spRPF = RPFDict.values()
                spG = GrowthDict.values()
    
                if len(spD)   > 0: SpecDisp.append(mean(spD))
                if len(spM)   > 0: SpecMaint.append(mean(spM))
                if len(spG)   > 0: SpecGrowth.append(mean(spG))
                if len(spRPF) > 0: SpecRPF.append(mean(spRPF))
                if len(spMF)  > 0: SpecMF.append(mean(spMF))
    
    
                RAD, splist = bide.GetRAD(SpeciesIDs)
                RAD, splist = zip(*sorted(zip(RAD, splist), reverse=True))
                RAD = list(RAD)
    
                avgRPF = 0
                avgMF = 0
                for index, sp in enumerate(splist):
                    avgRPF += RPFDict[sp] * RAD[index]
                    avgMF += MainFactorDict[sp] * RAD[index]
    
                avgRPF = avgRPF/sum(RAD)
                avgMF = avgMF/sum(RAD)
    
                RPFList.append(avgRPF)
                MFList.append(avgMF)
    
    
                if len(RAD) > S + 5:
                    print 'Large increase in S'
                    sys.exit()
    
                S = len(RAD)
                Ss.append(S)
                # Evenness, Dominance, and Rarity measures
                Ev = metrics.e_var(RAD)
                EVs.append(Ev)
                ES = metrics.e_simpson(RAD)
                ESs.append(ES)
    
                if len(Ns) == 1:
                    splist2 = list(splist)
    
                if len(Ns) > 1:
                    wt = metrics.WhittakersTurnover(splist, splist2)
                    jc = metrics.jaccard(splist, splist2)
                    so = metrics.sorensen(splist, splist2)
                    splist2 = list(splist)
                    WTs.append(wt)
                    Jcs.append(jc)
                    Sos.append(so)
    
                Nm, BP = [max(RAD), Nm/N]
                NMAXs.append(Nm)
                BPs.append(BP)
    
                SD = metrics.simpsons_dom(RAD)
                SDs.append(SD)
                sk = stats.skew(RAD)
                SKs.append(sk)
    
                if len(GrowthList) > 0: Gs.append(mean(GrowthList))
                if len(MaintList) > 0:  Ms.append(mean(MaintList))
                if len(DispList) > 0:   Ds.append(mean(DispList))
    
                numD = ADList.count('d')
                ADs.append(numD/len(ADList))
    
                Nmeans = [np.var(x) for x in zip(*N_RList)]
                if len(Nmeans) > 0: NRs.append(mean(Nmeans))
    
                Pmeans = [np.var(x) for x in zip(*P_RList)]
                if len(Pmeans) > 0: PRs.append(mean(Pmeans))
    
                Cmeans = [np.var(x) for x in zip(*C_RList)]
                if len(Cmeans) > 0: CRs.append(mean(Cmeans))
    
    
            if len(Ns) > 50:
    
                if int(round(mean(Ns))) >= 0:
    
                    print '%3s' % sim,'  flow:', '%6s' % round(u0,5),' |  N:', '%4s' % int(round(mean(Ns))),\
                    ' S:', '%3s' % int(round(mean(Ss))),' WT:', '%5s' % round(mean(WTs),3), ' Ev:', '%5s' % \
                    round(mean(ESs),2), ' |  MaintMax:', '%5s' % maintmax,' ResInflow:', '%3s' % \
                    r, ' GrowthMax:', '%3s' % gmax, ' DispMax:', '%3s' % dmax
    
                if int(round(mean(Ns))) >= 0:
    
                    OUT1 = open(GenPath + '/SimData_Fig3.csv', 'a')
                    outlist = [sim,motion,dorm,mean(PRODIs),mean(PRODNs),mean(PRODPs),mean(PRODCs),r,nNi,nP,nC,rmax,gmax,maintmax,dmax,barriers,alpha,seedCom,u0,width-0.2,height,viscosity,N,m,mean(RTAUs), mean(TExitAge) ,mean(INDTAUs),mean(RDENs),mean(RDIVs),mean(RRICHs),mean(Ss),mean(ESs),mean(EVs),mean(BPs),mean(SDs),mean(NMAXs),mean(SKs),T,R,speciation,mean(WTs),mean(Jcs),mean(Sos),mean(Gs),mean(Ms),mean(NRs),mean(PRs),mean(CRs),mean(Ds),amp,flux,freq,phase,disturb, mean(SpecGrowth), mean(SpecDisp), mean(SpecMaint), mean(AVG_DIST), mean(ADs), mean(RPFList), mean(MFList), mean(SpecRPF), mean(SpecMF)]
                    outlist = str(outlist).strip('[]')
                    outlist = str(outlist).strip(' ')
                    print>>OUT1, outlist
                    OUT1.close()
    
                ct1 += 1
                ct = 0
    
                Rates = np.roll(Rates, -1, axis=0)
                u0 = Rates[0]
    
                n0, nN, nS, nE, nW, nNE, nNW, nSE, nSW, barrier, rho, ux, uy, bN, bS, bE, bW, bNE, bNW, bSE, bSW = LBM.SetLattice(u0, viscosity, width, height, lefts, bottoms, barriers)
                u1 = u0 + u0*(amp * sin(2*pi * ct * freq + phase))
    
                RDens, RDiv, RRich, S, ES, Ev, BP, SD, Nm, sk, Mu, Maint, ct, IndID, RID, N, ct1, T, R, PRODI, PRODQ = [0]*21
                ADList, ADs, AVG_DIST, SpecDisp, SpecMaint, SpecGrowth, SpColorList, GrowthList, MaintList, N_RList, P_RList, C_RList, RColorList, DispList, RPFList, MFList, SpecRPF, SpecMF = [list([]) for _ in xrange(18)]
                RAD, splist, IndTimeIn, SpeciesIDs, IndX, IndY,  IndIDs, Qs, IndExitAge, TX, TY, TExitAge, TIDs, TTimeIn, RX, RY,  RIDs, RTypes, RExitAge, RTimeIn, RVals, Gs, Ms, NRs, PRs, CRs, Ds, Ts, Rs, PRODIs, PRODNs, PRODPs, PRODCs, Ns, RTAUs, TTAUs, INDTAUs, RDENs, RDIVs, RRICHs, Ss, ESs, EVs,BPs, SDs, NMAXs, SKs, MUs, MAINTs, WTs, Jcs, Sos, splist2 = [list([]) for _ in xrange(53)]
    
                p = 0
                BurnIn = 'not done'    
                if u0 == max(Rates):    
                    print '\n'
                    sim += 1
                    return
    




###############  SIMULATION VARIABLES, DIMENSIONAL & MODEL CONSTANTS  ##########

r_list = [600, 20]
gmax_list = [0.001, 0.999]
dmax_list = [0.01, 0.7]
maintmax_list = [0.0001, 0.001]

r_list = [600]
gmax_list = [0.999, 0.001, 0.0001]
dmax_list = [0.0001]
maintmax_list = [0.00001]


sim = 1
for r in r_list:
    for gmax in gmax_list:
        for dmax in dmax_list:
            for maintmax in maintmax_list:
                
                
                ################ DIMENSIONAL & MODEL CONSTANTS ##################################
                width, height, alpha, motion, reproduction, speciation, seedCom, m, nNi, nP, nC, rmax, amp, freq, flux, pulse, phase, disturb, envgrads, barriers, Rates, pmax, mmax, dorm, imm = rp.get_rand_params()
                lefts, bottoms = [], []
                
                for b in range(barriers):
                    lefts.append(np.random.uniform(0.3, .7))
                    bottoms.append(np.random.uniform(0.1, 0.8))
                
                #######################  Ind COMMUNITY PARAMETERS  #########################
                RDens, RDiv, RRich, S, ES, Ev, BP, SD, Nm, sk, Mu, Maint, ct, IndID, RID, N, ct1, T, R, PRODI, PRODQ = [0]*21
                RAD, splist, IndTimeIn, SpeciesIDs, IndX, IndY,  IndIDs, Qs, IndExitAge, TX, TY, TExitAge, TIDs, TTimeIn, RX, RY,  RIDs, RTypes, RExitAge, RTimeIn, RVals, Gs, Ms, NRs, PRs, CRs, Ds, Ts, Rs, PRODIs, PRODNs, PRODPs, PRODCs, Ns, RTAUs, TTAUs, INDTAUs, RDENs, RDIVs, RRICHs, Ss, ESs, EVs,BPs, SDs, NMAXs, SKs, MUs, MAINTs, WTs, Jcs, Sos, splist2 = [list([]) for _ in xrange(53)]
                SpColorDict, GrowthDict, MaintDict, MainFactorDict, RPFDict, EnvD, N_RD, P_RD, C_RD, RColorDict, DispDict, EnvD = {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}
                ADList, ADs, AVG_DIST, SpecDisp, SpecMaint, SpecGrowth, SpColorList, GrowthList, MaintList, N_RList, P_RList, C_RList, RColorList, DispList, RPFList, MFList, SpecRPF, SpecMF= [list([]) for _ in xrange(18)]

                viscosity = 10 # unitless but required by an LBM model
                u0 = Rates[0]
                
                ############### INITIALIZE GRAPHICS ############################################
                #####################  Lattice Boltzmann PARAMETERS  ###################
                n0, nN, nS, nE, nW, nNE, nNW, nSE, nSW, barrier, rho, ux, uy, bN, bS, bE, bW, bNE, bNW, bSE, bSW = LBM.SetLattice(u0, viscosity, width, height, lefts, bottoms, barriers)
                
                t = time.clock()
                Ns = []
                BurnIn = 'not done'
                p = 0.0
                
                nextgen()
                
                