from __future__ import print_function
import numpy as np
import ROOT

#hf = ROOT.TFile("Fits/Bkgfits_flat_regionlimit.root","READ")
hf = ROOT.TFile("Fits/CMS_h4g_sgbg_shapes.root","READ")
#print(hf.ls())
hnames = list(hf.GetListOfKeys())
hnames = [h.GetName() for h in hnames]
#print(hnames)

bg = 'bkg'

hbg = {}
for k in hnames:
    if bg in k:
        hbg[k] = hf.Get(k)
        #print(k, hbg[k].GetNbinsX())
# bg
nbg = {}
systbg = [k.split('_')[-1] for k in hbg.keys() if bg != k]
systbg = np.unique([syst.replace('Up','').replace('Down','') for syst in systbg])
#print(systbg)

for k in hbg:
    #if k != bg: continue
    #print(k)
    nbg[k] = np.zeros(hbg[k].GetNbinsX())
    count = 0
    for ib in range(1, hbg[k].GetNbinsX()+1):
        nbg[k][ib-1] = hbg[k].GetBinContent(ib)
        #print(ib-1, nbg[k][ib-1])
        count += 1
    #print(k, count)
    #break

for syst in systbg:
    #continue
    #rup = np.abs(nbg[bg])
    #rup = np.abs(nbg[bg+'_'+syst+'Up']/nbg[bg] - 1.)
    #rdn = np.abs(nbg[bg+'_'+syst+'Down']/nbg[bg] - 1.)
    rup = np.abs(nbg[bg+'_CMS_h4g_'+syst+'Up']/nbg[bg] - 1.)
    rdn = np.abs(nbg[bg+'_CMS_h4g_'+syst+'Down']/nbg[bg] - 1.)
    rmax = [up if up > dn else dn for up,dn in zip(rup, rdn)]
    rmin = [dn if up > dn else up for up,dn in zip(rup, rdn)]
    for i,r in enumerate(rmax):
        pass
        #print(i, r)
        #if syst == 'flo':
        #    print(i, rdn[i], nbg[bg][i], rup[i])
    print('%s: (fmin, fmax): %.1f %%, %.1f %%'%(syst, 1.e2*np.min(rmin), 1.e2*np.max(rmax)))
    #break

errbg = np.zeros(hbg[bg].GetNbinsX())
for ib in range(1, hbg[bg].GetNbinsX()+1):
    errbg[ib-1] = hbg[bg].GetBinError(ib)/hbg[bg].GetBinContent(ib)
    #print(ib, hbg[bg].GetBinContent(ib), errbg[ib-1])
#print('stat', errbg.min(), errbg.max())
print('stat: (fmin, fmax): %.1f %%, %.1f %%'%(errbg.min()*1.e2, errbg.max()*1.e2))

#'''
# sg

#sg = 'h4g_100MeV'
#sg = 'h4g_400MeV'
#sg = 'h4g_1GeV'
#sgs = ['h4g_100MeV', 'h4g_400MeV', 'h4g_1GeV']
yr = '2018'
yr = 'Run2'
sgs = ['h4g_0p1', 'h4g_0p4', 'h4g_1p0']
#sgs = ['h4g_0p4']
sgs = [s+'_'+yr for s in sgs]
#sgs = ['h4g_0p4_2018']

for sg in sgs:

    print('>> Doing:',sg)

    hsg = {}
    for k in hnames:
        if sg in k:
            hsg[k] = hf.Get(k)
            #print(k, hsg[k].GetNbinsX())

    #systsg = [k.split('_')[-1] for k in hsg.keys() if sg != k]
    systsg = ['_'.join(k.split('_')[5:]) for k in hsg.keys() if sg != k]
    systsg = np.unique([syst.replace('Up','').replace('Down','') for syst in systsg])
    #print(systsg)

# Initialize dicts for min,max frac errs
syst_mins = {}
syst_maxs = {}
for syst in systsg:
    syst_mins[syst] = []
    syst_maxs[syst] = []

syst_mins['stat'] = []
syst_maxs['stat'] = []

for sg in sgs:

    hsg = {}
    for k in hnames:
        if sg in k:
            hsg[k] = hf.Get(k)
            #print(k, hsg[k].GetNbinsX())

    nsg = {}

    for k in hsg:
        #if k != sg: continue
        #if k != 'h4g_100MeV_scaleUp': continue
        #if k != 'h4g_100MeV_smearUp': continue
        #print(k)
        nsg[k] = np.zeros(hsg[k].GetNbinsX())
        count = 0
        for ib in range(1, hsg[k].GetNbinsX()+1):
            binc = hsg[k].GetBinContent(ib)
            nsg[k][ib-1] = binc
            #if binc >= halfmax:
            #    nsg[k][ib-1] = binc
            #    #print(ib-1, nsg[k][ib-1])
            #    #valid_idxs.append(ib-1)
            count += 1
        #print(k, count, len(valid_idxs))
        #break
    halfmax = hsg[sg].GetMaximum()/2.
    #print(sg,'max: %f, halfmax: %f'%(hsg[sg].GetMaximum(), halfmax))
    valid_idxs = (nsg[sg] > halfmax)
    #print('.. N_elements > halfmax:',len(nsg[sg][valid_idxs]))
    assert np.all(nsg[sg][valid_idxs] > 0.)

    #print(nsg.keys())
    for syst in systsg:
        #print('   >> Doing syst:',syst)
        #continue
        #rup = np.abs(nsg[sg])
        #rup = np.nan_to_num(np.abs(nsg[sg+'_'+syst+'Up']/nsg[sg] - 1.))
        #rdn = np.nan_to_num(np.abs(nsg[sg+'_'+syst+'Down']/nsg[sg] - 1.))
        #rmax = np.array([up if up > dn else dn for up,dn in zip(rup, rdn)])
        #rmin = np.array([dn if (up > dn and dn > 0.) else up for up,dn in zip(rup, rdn)])
        #rup = np.abs(nsg[sg+'_'+syst+'Up'][valid_idxs]/nsg[sg][valid_idxs] - 1.)
        #rdn = np.abs(nsg[sg+'_'+syst+'Down'][valid_idxs]/nsg[sg][valid_idxs] - 1.)
        rup = np.abs(nsg[sg+'_CMS_h4g_'+syst+'Up'][valid_idxs]/nsg[sg][valid_idxs] - 1.)
        rdn = np.abs(nsg[sg+'_CMS_h4g_'+syst+'Down'][valid_idxs]/nsg[sg][valid_idxs] - 1.)
        rmax = np.array([up if up > dn else dn for up,dn in zip(rup, rdn)])
        rmin = np.array([dn if (up > dn and dn > 0.) else up for up,dn in zip(rup, rdn)])
        for i,r in enumerate(rmin):
            pass
            #print(i, r)
        #print(syst, np.min(rmin[rmin>0.]), np.max(rmax))
        syst_mins[syst].append(np.min(rmin[rmin>0.]))
        syst_maxs[syst].append(np.max(rmax))
        #break

#'''
    errsg = np.zeros(hsg[sg].GetNbinsX())
    for ib in range(1, hsg[sg].GetNbinsX()+1):
        binc = hsg[sg].GetBinContent(ib)
        #if binc >= halfmax:
        #    errsg[ib-1] = hsg[sg].GetBinError(ib)/binc
        #errsg[ib-1] = hsg[sg].GetBinError(ib)/binc
        errsg[ib-1] = hsg[sg].GetBinError(ib)
    assert len(errsg) == len(nsg[sg])
    fracerrs = errsg[valid_idxs]/nsg[sg][valid_idxs]
    #print('stat', errsg[errsg>0.].min(), errsg.max())
    #print('stat', fracerrs.min(), fracerrs.max())
    print('stat: (fmin, fmax): %.1f %%, %.1f %%'%(fracerrs.min()*1.e2, fracerrs.max()*1.e2))
    syst_mins['stat'].append(fracerrs.min())
    syst_maxs['stat'].append(fracerrs.max())
#'''

print('Global min,max')
for k in syst_mins:
    #syst_mins = np.array(syst_mins[k])
    #print(k, np.min(syst_mins[k]), np.max(syst_maxs[k]))
    print('%s: (fmin, fmax): %.1f %%, %.1f %%'%(k, 1.e2*np.min(syst_mins[k]), 1.e2*np.max(syst_maxs[k])))
