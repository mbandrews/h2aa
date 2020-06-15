from __future__ import print_function
import numpy as np
np.random.seed(0)
import os, glob
import time
import argparse

#'''
import torch
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import *
import torch.nn as nn
#os.environ["CUDA_VISIBLE_DEVICES"]=str(0)
#'''

import ROOT
from array import array


# Register command line options
parser = argparse.ArgumentParser(description='Run STEALTH selection.')
parser.add_argument('-s', '--sample', default='test', type=str, help='Sample name.')
#parser.add_argument('-i', '--img_inputs', default=['test.root'], nargs='+', type=str, help='Input IMG files.')
parser.add_argument('-i', '--img_inputs', default='img_inputs.txt', type=str, help='List file of img inputs.')
parser.add_argument('-g', '--gg_inputs', default=['h24gntuple_n631.root'], nargs='+', type=str, help='Input GG files.')
#parser.add_argument('-t', '--gg_treename', default='', type=str, help='GG TTree name prefix.')
parser.add_argument('-o', '--outdir', default='MAntuples', type=str, help='Output directory.')
args = parser.parse_args()

# Crop out EB shower from full EB image
def crop_EBshower(imgEB, ieta, iphi, window=32):

    # NOTE: image window here should correspond to the one used in RHAnalyzer
    off = window//2
    ieta = int(ieta[0])+1 # seed positioned at [15,15]
    iphi = int(iphi[0])+1 # seed positioned at [15,15]

    # Wrap-around on left side
    if iphi < off:
        diff = off-iphi
        img_crop = np.concatenate((imgEB[:,ieta-off:ieta+off,-diff:],
                                   imgEB[:,ieta-off:ieta+off,:iphi+off]), axis=-1)
    # Wrap-around on right side
    elif 360-iphi < off:
        diff = off - (360-iphi)
        img_crop = np.concatenate((imgEB[:,ieta-off:ieta+off,iphi-off:],
                                   imgEB[:,ieta-off:ieta+off,:diff]), axis=-1)
    # Nominal case
    else:
        img_crop = imgEB[:,ieta-off:ieta+off,iphi-off:iphi+off]

    return img_crop

# Create an event list containing run:lumi:event:idx IDs for some input `tree`
# Defaults to GG ntuple (friend) so events can be skipped if
# not present here.
# NOTE: event id conventions for the ntuples are as follows:
# IMG -> runId:lumiId:eventId
# GG -> run:lumis:event
def get_evtlist(tree, ish24g=True):
    nEvts = tree.GetEntries()
    idxs = []
    for iEvt in range(nEvts):
        # Initialize event
        tree.GetEntry(iEvt)
        if iEvt%100e3==0: print(iEvt,'/',nEvts)
        if ish24g:
            eventId = [tree.run, tree.lumis, tree.event, iEvt]
        else:
            eventId = [tree.runId, tree.lumiId, tree.eventId, iEvt]
        idxs.append(eventId)
    # Array index on 1st element should be 0, and nEvts-1 on last element
    idxs = np.array(idxs)
    assert idxs[0,-1] == 0 and idxs[-1,-1] == nEvts-1
    return idxs

# Returns the index in the IMG ntuple (main)
# corresponding to the same event index in the GG ntuple (friend)
# If not found, defaults to -1
#def idx_where_eventId(idxs, run, lumi, event):
def idx_where_eventId(evtlistf, tree):

    if evtlistf.shape[-1] > 3:
        evtlistf = evtlistf[:,:3]
    assert evtlistf.shape[-1] == 3

    #eventId = np.array([run, lumi, event])
    # Get target event ID from IMG ntuple (main)
    eventId = np.array([tree.runId, tree.lumiId, tree.eventId])
    #print(evtlistf == eventId)
    #print(np.array_equal(evtlistf, eventId))
    #print(evtlistf.shape)
    # Look for this event in the GG ntuple (friend)
    idx = np.argwhere(np.all(evtlistf == eventId, axis=-1))
    #print(idx)
    #print(len(idx))
    if len(idx) == 1:
        return idx.flatten()[0]
    else:
        return -1

# Return the array index in `evtlistf` corresponding to event loaded in `tree`
# Each event uniquely identified by run, lumi, event no.
# Filter first by run then lumi before looking for event no.
# If evt not found, returns `-1` to trigger TTree event status == bad
def idxf_where_run_lumi_evt(tree, evtlistf):

    # `eventlistf` must have shape (nevts,4) where
    # [:,0]: run
    # [:,1]: lumi
    # [:,2]: event
    # [:,3]: idx
    assert evtlistf.shape[-1] == 4

    # This is the target event ID from the main IMG TTree
    evtid = np.array([tree.runId, tree.lumiId, tree.eventId])

    # Find the index in the friend tree corresponding to target event
    # Filter by run
    iruns = np.argwhere(evtlistf[:,0] == evtid[0]).flatten()
    evtlistf = evtlistf[iruns]
    if len(evtlistf) == 0:
        return -1
    # Filter by lumi
    ilumis = np.argwhere(evtlistf[:,1] == evtid[1]).flatten()
    evtlistf = evtlistf[ilumis]
    if len(evtlistf) == 0:
        return -1
    # Filter by event
    ievts = np.argwhere(evtlistf[:,2] == evtid[2]).flatten()
    evtlistf = evtlistf[ievts]

    assert len(evtlistf) <= 1, 'More than one evt match found!'

    if len(evtlistf) == 0:
        return -1
    else:
        return evtlistf.flatten()[-1]


# Load IMG ntuples as main TTree
img_inputs = []
print('Opening img input list:',args.img_inputs)
with open(args.img_inputs, 'r') as img_file:
    for img_input in img_file:
        img_inputs.append(img_input[:-1])
print(img_inputs[0])
print('len(img_inputs):',len(img_inputs))
assert len(img_inputs) > 0

print('Setting IMG as main TTree')
print('N IMG files:',len(img_inputs))
print('IMG file[0]:',img_inputs[0])
tree = ROOT.TChain("fevt/RHTree")
for fi in img_inputs:
    tree.Add(fi)
    #break
nEvts = tree.GetEntries()
print('N evts in IMG ntuple:',nEvts)
#tree_idxs = idxs_by_eventId(tree, False)
#print(tree_idxs.shape)

# Load GG ntuples as TTree friend
print('Setting GG as TTree friend')
print('N GG files:',len(args.gg_inputs))
print('GG file[0]:',args.gg_inputs[0])
#treef = ROOT.TChain("ggCandidateDumper/trees/%s_13TeV_2photons"%args.gg_treename)
treef = ROOT.TChain('ggNtuplizer/EventTree')
#for fh in args.gg_inputs:
for i,fh in enumerate(args.gg_inputs):
    treef.Add(fh)
    #if i > 10: break
nEvtsf = treef.GetEntries()
print('N evts in GG ntuple:',nEvtsf)
# Make this a friend of the IMG ntuple:
# This allows event variables from both ntuples to be accessible
# from the main TTree, the IMG ntuple
#tree.AddFriend(treef)
# Keep an index of eventIds in TTree friend
# Since the IMG ntuple controls the main event loop
# want to later skip events not in GG ntuple
print('Collecting event indices from GG ntuple...')
evtlistf = get_evtlist(treef)
#print(evtlistf)
print('...done')

#'''
# Initialize output ntuple
# Merges GG variables + regressed m_a
if not os.path.isdir(args.outdir):
    os.makedirs(args.outdir)
file_out = ROOT.TFile("%s/%s_mantuple.root"%(args.outdir, args.sample), "RECREATE")
file_out.mkdir("ggNtuplizer")
file_out.cd("ggNtuplizer")
# Clone TTree structure of GG ntuple
tree_out = treef.CloneTree(0)
#print(list(tree_out.GetListOfBranches()))

# Initialize branches for the m_as as single floats
# [PyROOT boilerplate for single float branches]
ma0 = np.zeros(1, dtype='float32')
ma1 = np.zeros(1, dtype='float32')
tree_out.Branch('ma0', ma0, 'ma0/F')
tree_out.Branch('ma1', ma1, 'ma1/F')
#sc0 = np.zeros(1024, dtype='float32')
#sc1 = np.zeros(1024, dtype='float32')
#tree_out.Branch('sc0', sc0, 'sc0/F')
#tree_out.Branch('sc1', sc1, 'sc1/F')
#'''

# Load mass regressor for inference
print('Loading regressor model')
import torch_resnet_concat as networks
#epoch = 80
#neg_mass = 300
## AOD
#model_file = glob.glob('../EB_Pi0_massreg_Pt20To100_2017PU_ext3_tzfixed_wrapfix/MODELS/DoublePi0Pt20To100_m0To1600_pythia8_PU2017_genDR10_aodDR16_nPhoN_PhoNeg%dTo0_wgts_EBtzo25_AOD_m0o1.6_ResNet_blocks3_seedPos_FC128x0_MAEloss_lr0.0005_epochs80_n778k_run0/model_epoch%d_*.pkl'%(neg_mass, epoch))
#assert len(model_file) == 1
#model_file = model_file[0]
#'''
model_file = 'Models/model_epoch80_mae0.1906.pkl'
resnet = networks.ResNet(2, 3, [16, 32], 128, 0).cuda()
resnet.load_state_dict(torch.load(model_file)['model'])
resnet.eval()
print(model_file)
#'''

eb_scale = 25.
m0_scale = 1.6
def transform_y(y):
    return y/m0_scale
def inv_transform(y):
    return y*m0_scale

#'''
c, h = {}, {}
wd, ht = int(440*1), int(400*1)

k = 'iphi'
#c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
h[k] = ROOT.TH1F(k, k, 360//5, 0., 360)
k = 'ieta'
#c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
h[k] = ROOT.TH1F(k, k, 170//5, 0., 170)

k = 'ma0'
c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
h[k] = ROOT.TH1F(k, k, 56, -0.2, 1.2)
#h[k] = ROOT.TH1F(k, k, 48, 0., 1.2)
k = 'ma1'
c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
h[k] = ROOT.TH1F(k, k, 56, -0.2, 1.2)
#h[k] = ROOT.TH1F(k, k, 48, 0., 1.2)

'''
k = 'ma0dn'
c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
h[k] = ROOT.TH1F(k, k, 56, -0.2, 1.2)
#h[k] = ROOT.TH1F(k, k, 48, 0., 1.2)
k = 'ma1dn'
c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
h[k] = ROOT.TH1F(k, k, 56, -0.2, 1.2)
#h[k] = ROOT.TH1F(k, k, 48, 0., 1.2)

k = 'ma0up'
c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
h[k] = ROOT.TH1F(k, k, 56, -0.2, 1.2)
#h[k] = ROOT.TH1F(k, k, 48, 0., 1.2)
k = 'ma1up'
c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
h[k] = ROOT.TH1F(k, k, 56, -0.2, 1.2)
#h[k] = ROOT.TH1F(k, k, 48, 0., 1.2)
'''

k = 'ma0vma1'
#c[k] = ROOT.TCanvas("c","c",wd,ht)
h[k] = ROOT.TH2F(k, k, 48, 0., 1.2, 48, 0., 1.2)
#'''

# Event range to process
iEvtStart = 0
iEvtEnd   = nEvts
#iEvtEnd   = 10#50000#10
print(">> Processing entries: [",iEvtStart,"->",iEvtEnd,")")

def shapeEB(eb):
    return np.array(eb).reshape(1,170,360)

nWrite = 0
sw = ROOT.TStopwatch()
sw.Start()
for iEvt in range(iEvtStart,iEvtEnd):

    # Initialize event
    if iEvt%10e3==0: print(iEvt,'/',iEvtEnd-iEvtStart)
    evt_status = tree.GetEntry(iEvt)
    if evt_status <= 0: continue
    #evt_idx = idx_where_eventId(evtlistf, tree)
    #print('evt_idx',evt_idx)
    #evt_statusf = treef.GetEntry(evt_idx)
    evt_statusf = treef.GetEntry(idxf_where_run_lumi_evt(tree, evtlistf))
    #evt_statusf = treef.GetEntry(idx_where_eventId(evtlistf, tree))
    #if evt_status <= 0 or evt_statusf <= 0: continue
    if evt_statusf <= 0: continue
    #print('evt_status:',evt_status, 'evt_statusf:', evt_statusf)

    # Event ID
    #eventId = '%d:%d:%d'%(tree.runId, tree.lumiId, tree.eventId)
    #print(eventId)
    #eventIdf = '%d:%d:%d'%(tree.run, tree.lumi, tree.event)
    #print(eventIdf)
    assert((treef.run == tree.runId) & (treef.lumis == tree.lumiId) & (treef.event == tree.eventId))
    #print('runId:',tree.runId)
    #print('run:',treef.run)
    #eventVs = '%d:%d:%d vs. %d:%d:%d'%(tree.runId, tree.lumiId, tree.eventId, treef.run, treef.lumi, treef.event)
    #print(eventVs)
    #print(iEvt,'/',nEvts)

    #if treef.pho12_m < 90.: continue
    if treef.mgg < 100. or treef.mgg > 180.: continue

    # Only keep events with photons within ieta image window
    #npho_roi = sum([0 if (tree.SC_ieta[i] < 15) or (tree.SC_ieta[i]+16 > 169) else 1 for i in range(2)])
    #if npho_roi != 2: continue

    #'''
    #print(treef.phoSeedPos1_z, treef.phoSeedPos1_row, treef.phoSeedPos1_col) # z,ieta,iphi
    #print(treef.phoSeedPos2_z, treef.phoSeedPos2_row, treef.phoSeedPos2_col) # z,ieta,iphi
    #assert(ieta bounds)
    p4 = {}
    pho_idx = {}
    #pho_idx[0], pho_idx[1] = treef.phoPreselIdxs[0], treef.phoPreselIdxs[1]
    #print('%d:%d:%d'%(tree.runId, tree.lumiId, tree.eventId))
    #print('presel idxs:',list(treef.phoPreselIdxs))
    #print(list(treef.phoPreselIdxs))
    #print(len(treef.phoEt))
    #print(list(treef.phoEt))
    #print('N imgs:',len(tree.SC_ieta))
    #print('ietas:',list(tree.SC_ieta))
    #print('iphis:',list(tree.SC_iphi))
    #print(list(tree.SC_ieta))
    #for i in range(2):
    for i in range(len(treef.phoPreselIdxs)):
        pho_idx[i] = treef.phoPreselIdxs[i]
        #p4 = ROOT.Math.PtEtaPhiEVector(treef.phoEt[pho_idx[i]], treef.phoEta[pho_idx[i]], treef.phoPhi[pho_idx[i]], treef.phoE[pho_idx[i]])
        # ggntuple photon vector
        p4['gg'] = ROOT.TVector3()
        p4['gg'].SetPtEtaPhi(treef.phoEt[pho_idx[i]], treef.phoEta[pho_idx[i]], treef.phoPhi[pho_idx[i]])
        # img ntuple photon vector
        p4['img'] = ROOT.TVector3()
        p4['img'].SetPtEtaPhi(tree.pho_pT[pho_idx[i]], tree.pho_eta[pho_idx[i]], tree.pho_phi[pho_idx[i]])
        # Ensure photons are alike
        dR = ROOT.Math.VectorUtil.DeltaR(p4['gg'], p4['img'])
        #print(dR)
        assert dR == 0.
        h['ieta'].Fill(tree.SC_ieta[pho_idx[i]])
        h['iphi'].Fill(tree.SC_iphi[pho_idx[i]])

    # Only keep events with photons within ieta image window
    npho_roi = sum([0 if (tree.SC_ieta[pho_idx[i]] < 15) or (tree.SC_ieta[pho_idx[i]]+16 > 169) else 1 for i in range(len(pho_idx))])
    if npho_roi != 2: continue

    # Only keep events with barrel photons
    #assert((treef.phoSeedPos1_z == 0.) & (treef.phoSeedPos1_z == 0.))
    #'''
    #break
    sc_cms = []
    ieta, iphi = [], []
    #X_EBt = np.array(tree.EB_energyT).reshape(1,170,360)
    #X_EBt = tree.EB_energyT
    #X_EBt = shapeEB(tree.EB_energyT)
    #print(type(tree.EB_energyT))
    #X_EBt = list(X_EBt)
    #del X_EBt
    #X_EBt = shapeEB(tree.EB_energyT)
    #X_EBz = shapeEB(tree.EB_energyZ)
    #'''
    X_EBt = np.array(tree.EB_energyT).reshape(1,170,360)
    X_EBz = np.array(tree.EB_energyZ).reshape(1,170,360)
    X_cms = np.concatenate([X_EBt, X_EBz], axis=0)
    #X_EBerr = np.array(tree.EB_energyErr).reshape(1,170,360)
    for i in range(npho_roi):
        #X_EB = np.array(tree.EB_energy).reshape(1,170,360)
        #print(X_cms.shape)
        #ieta.append([treef.phoSeedPos1_row if i == 0 else treef.phoSeedPos2_row])
        #iphi.append([treef.phoSeedPos1_col if i == 0 else treef.phoSeedPos2_col])
        ieta.append([tree.SC_ieta[pho_idx[i]]])
        iphi.append([tree.SC_iphi[pho_idx[i]]])
        #print(tree.SC_ieta[pho_idx[i]], ieta[-1])
        #print(tree.SC_iphi[pho_idx[i]], iphi[-1])
        #ieta.append([100])
        #iphi.append([100])
        #print('ieta:%.f, iphi:%.f'%(ieta[-1][0], iphi[-1][0]))
        #sc_cms.append(crop_EBshower(X_cms, ieta[-1], iphi[-1]))
        #print(crop_EBshower(X_cms, ieta[-1], iphi[-1]).shape)
        sc_cms_ = crop_EBshower(X_cms, ieta[-1], iphi[-1])
        sc_cms.append(sc_cms_)
        #print(sc_cms_.shape)
        '''
        # Calculate energy +/- err
        sc_err_ = crop_EBshower(X_EBerr, ieta[-1], iphi[-1])
        #print(sc_err_.shape)
        # Only have total energy err but need to decompose it into i = t,z components
        # to associate with Et and Ez layers. ith component is then
        # err_i = err * (\hat{E} dot \hat{E_i})
        #       = err * (E_i/E)
        sc_energy_ = np.sqrt(sc_cms_[:1]*sc_cms_[:1] + sc_cms_[1:]*sc_cms_[1:])# E = sqrt( Et^2 + Ez^2 )
        #print(sc_energy_.shape)
        # Avoid dividing by zero energy in empty hits
        zero_en = (sc_energy_ == 0.)
        zero_err = (sc_err_ == 0.)
        #assert np.array_equal(zero_en, zero_err), '%d vs. %d'%(len(sc_energy_[zero_en]), len(sc_err_[zero_err]))
        #sc_energy_[sc_energy_ == 0.] = 1. # value of 1 arbitrary but will result in 0 err anyway
        assert np.array_equal(len(sc_energy_[(zero_en | zero_err)]), len(sc_err_[zero_err])),\
                 '%d vs. %d'%(len(sc_energy_[(zero_en | zero_err)]), len(sc_err_[zero_err]))
        sc_energy_[sc_err_ == 0.] = 1. # value of 1 arbitrary but will result in 0 err anyway
        #print(sc_err_[0,15,15], sc_energy_[0,15,15], sc_cms_[:,15,15])
        #print((sc_err_[0,15,15]/sc_energy_[0,15,15])*sc_cms_[0,15,15], (sc_err_[0,15,15]/sc_energy_[0,15,15])*sc_cms_[1,15,15])
        sc_cms_err_ = (sc_err_/sc_energy_)*sc_cms_ # err/E will be broadcast: err_i = (err/E)*E_i
        #print(sc_cms_err_[:,15,15])
        # energy down
        mean_ferr = np.mean(sc_cms_err_[sc_cms_>0.]/sc_cms_[sc_cms_>0.])
        print(np.mean(sc_cms_err_[sc_cms_>0.]))
        print(np.mean(sc_cms_[sc_cms_>0.]))
        print(mean_ferr)
        ieta.append([tree.SC_ieta[pho_idx[i]]])
        iphi.append([tree.SC_iphi[pho_idx[i]]])
        #sc_cms.append(sc_cms_-sc_cms_err_)
        sc_cms.append(sc_cms_*(1.-mean_ferr))
        # energy up
        ieta.append([tree.SC_ieta[pho_idx[i]]])
        iphi.append([tree.SC_iphi[pho_idx[i]]])
        #sc_cms.append(sc_cms_+sc_cms_err_)
        sc_cms.append(sc_cms_*(1.+mean_ferr))
        #print(sc_cms_[:,15,15],sc_cms_err_[:,15,15])
        '''
    #print(np.array(sc_cms).shape)
    #print(np.array(iphi).shape)
    #print(np.array(ieta).shape)
    ma = inv_transform(resnet([torch.Tensor(sc_cms).cuda()/eb_scale,\
                               torch.Tensor(iphi).cuda()/360.,\
                               torch.Tensor(ieta).cuda()/170.
                              ])).tolist()
    #'''
    #print(np.array(ma).shape)
    #print(ma)
    #'''
    ma0_, ma1_ = ma[0][0], ma[1][0]
    #ma0_, ma0dn_, ma0up_, ma1_, ma1dn_, ma1up_ = np.array(ma)[:,0]
    #print(ma)
    #print(ma0_, ma1_)
    ma0[0] = ma0_
    ma1[0] = ma1_
    tree_out.Fill()
    h['ma0'].Fill(ma0_)
    h['ma1'].Fill(ma1_)
    h['ma0vma1'].Fill(ma0_, ma1_)

    #h['ma0dn'].Fill(ma0dn_)
    #h['ma1dn'].Fill(ma1dn_)
    #h['ma0up'].Fill(ma0up_)
    #h['ma1up'].Fill(ma1up_)
    #'''
    #break
    nWrite += 1

sw.Stop()
print(">> N events written: %d / %d"%(nWrite, iEvtEnd-iEvtStart))
print(">> Real time:",sw.RealTime()/60.,"minutes")
print(">> CPU time: ",sw.CpuTime() /60.,"minutes")

'''
# Histograms already get written to file_out during their init?
file_out.cd("ggCandidateDumper")
for k in h.keys():
    pass
    #h[k].Write()

'''


# In[9]:

'''
tree_test = ROOT.TChain("ggCandidateDumper/trees/_13TeV_2photons")
tree_test.Add('output.root')
nEvts_ = tree_test.GetEntries()
print(nEvts_)


# In[10]:


def plot_shower(img, fix_scale=True):
    plt.rcParams["figure.figsize"] = (5,5)
    #cmap_ = 'hot_r'
    cmap_ = 'jet'
    #img[img < 1.e-5] = 0.
    #print(img[img>0.].min(), img.max())
    if fix_scale:
        plt.imshow(img, cmap=cmap_, norm=LogNorm(), vmin=1.e-4, vmax=60.)
    else:
        plt.imshow(img, cmap=cmap_, norm=LogNorm(), vmin=1.e-5, vmax=100.)
    #ax = plt.axes()
    zoom = 0.
    zoom = 5.
    plt.xlim([0.+zoom, 31.-zoom])
    plt.ylim([0.+zoom, 31.-zoom])
    plt.xlabel(r"$\mathrm{i\varphi}'$", size=14)
    plt.ylabel(r"$\mathrm{i\eta}'$", size=14)
    plt.colorbar(fraction=0.0457, pad=0.04, label='Energy [GeV]')
    plt.show()

for a in sc:
    print(a)
    plot_shower(sc[a])
'''


# In[34]:


def set_hist(h, c, xtitle, ytitle, htitle):
    c.SetLeftMargin(0.16)
    c.SetRightMargin(0.15)
    c.SetBottomMargin(0.13)
    ROOT.gStyle.SetOptStat(0)

    h.GetXaxis().SetLabelSize(0.04)
    h.GetXaxis().SetLabelFont(62)
    h.GetXaxis().SetTitleOffset(1.1)
    h.GetXaxis().SetTitleSize(0.05)
    h.GetXaxis().SetTitleFont(62)
    h.GetXaxis().SetTitle(xtitle)

    h.GetYaxis().SetLabelSize(0.04)
    h.GetYaxis().SetLabelFont(62)
    h.GetYaxis().SetTitleOffset(1.5)
    h.GetYaxis().SetTitleSize(0.05)
    h.GetYaxis().SetTitleFont(62)
    h.GetYaxis().SetTitle(ytitle)

    h.SetTitleSize(0.04)
    h.SetTitleFont(62)
    h.SetTitle(htitle)
    h.SetTitleOffset(1.2)

    return h, c

mass_line = 0.

#######################################################
'''
#for shift in ['', 'dn', 'up']:
    k = 'ma0'+shift
    print(k, h.keys(), c.keys())
    assert k in h.keys()
    print(type(h[k]), type(c[k]))
    c[k].cd()
    h[k], c[k] = set_hist(h[k], c[k], "m_{a,pred} [GeV]", "N_{a}", "")
    h[k].SetLineColor(9)
    h[k].Draw("hist")
    k = 'ma1'+shift
    h[k].SetLineColor(2)
    h[k].Draw("hist SAME")

    ymax = 1.2*max(h['ma0'+shift].GetMaximum(), h['ma1'+shift].GetMaximum())
    h['ma0'+shift].GetYaxis().SetRangeUser(0., ymax)

    #l = ROOT.TLine(mass_line, 0., mass_line, ymax) # x0,y0, x1,y1
    #l.SetLineColor(14)
    #l.SetLineStyle(7)
    #l.Draw("same")
    hatch = ROOT.TGraph(2, array('d',[0.,0.]), array('d',[0.,ymax]));
    hatch.SetLineColor(14)
    hatch.SetLineWidth(2001)
    hatch.SetFillStyle(3004)
    hatch.SetFillColor(14)
    hatch.Draw("same")

    #c[k].SetGrid()
    c['ma0'+shift].Draw()
    c['ma0'+shift].Update()
    c['ma0'+shift].Print('Plots/h%s.eps'%k)
'''
'''
for im in ['ma0', 'ma1']:
    k = im
    c[k].cd()
    h[k], c[k] = set_hist(h[k], c[k], "m_{a,pred} [GeV]", "N_{a}", "")
    h[k].SetLineColor(1)
    h[k].Draw("hist")
    k = im+'dn'
    h[k].SetLineColor(2)
    h[k].Draw("hist SAME")
    k = im+'up'
    h[k].SetLineColor(9)
    h[k].Draw("hist SAME")

    ymax = 1.2*h[im].GetMaximum()
    h[im].GetYaxis().SetRangeUser(0., ymax)

    #l = ROOT.TLine(mass_line, 0., mass_line, ymax) # x0,y0, x1,y1
    #l.SetLineColor(14)
    #l.SetLineStyle(7)
    #l.Draw("same")
    hatch = ROOT.TGraph(2, array('d',[0.,0.]), array('d',[0.,ymax]));
    hatch.SetLineColor(14)
    hatch.SetLineWidth(2001)
    hatch.SetFillStyle(3004)
    hatch.SetFillColor(14)
    hatch.Draw("same")

    #c[k].SetGrid()
    c[im].Draw()
    c[im].Update()
    c[im].Print('Plots/h%s_%s_nomdnup.eps'%(args.sample, im))
'''
'''
##############################
k = 'iphi'
c[k].cd()
h[k], c[k] = set_hist(h[k], c[k], "i#varphi", "N_{a}", "i#varphi")
h[k].SetLineColor(9)
h[k].Draw("hist")
c[k].Draw()
##############################
k = 'ieta'
c[k].cd()
h[k], c[k] = set_hist(h[k], c[k], "i#eta", "N_{a}", "i#eta")
h[k].SetLineColor(9)
h[k].Draw("hist")
c[k].Draw()
##############################
k = 'ma0vma1'
c[k].cd()
h[k], c[k] = set_hist(h[k], c[k], "m_{a_{0},pred} [GeV]", "m_{a_{1},pred} [GeV]", "m_{a_{1},pred} vs. m_{a_{0},pred}")
ROOT.gPad.SetRightMargin(0.17)
ROOT.gStyle.SetPalette(55)#53
h[k].GetYaxis().SetTitleOffset(1.1)
h[k].GetZaxis().SetTitle("Events")
h[k].GetZaxis().SetTitleOffset(1.1)
h[k].GetZaxis().SetTitleSize(0.05)
h[k].GetZaxis().SetTitleFont(62)
h[k].GetZaxis().SetLabelSize(0.04)
h[k].GetZaxis().SetLabelFont(62)
h[k].Draw("COL Z")
#h[k].SetMaximum(150.) #2: 150, 3: 220
c[k].Draw()
palette = h[k].GetListOfFunctions().FindObject("palette")
palette.SetX1NDC(0.84)
palette.SetX2NDC(0.89)
palette.SetY1NDC(0.13)
'''
##############################

#blue: leading
#red: sub-leading

file_out.Write()
file_out.Close()
