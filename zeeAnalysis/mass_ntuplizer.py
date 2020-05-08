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
parser.add_argument('-j', '--job', default=None, type=int, help='Output directory.')
parser.add_argument('-n', '--njobs', default=None, type=int, help='Output directory.')
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
    #nEvts = 5000
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

def is_barrel_ieta(ieta, window=32):
    off = window//2
    if ieta == -1:
        return False
    elif (ieta+1 < off) or (ieta+1 > 170-off): # seed at idx=15
        return False
    else:
        return True

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
imgtree = ROOT.TChain("fevt/RHTree")
for fi in img_inputs:
    imgtree.Add(fi)
    #break
nEvts = imgtree.GetEntries()
print('N evts in IMG ntuple:',nEvts)
#tree_idxs = idxs_by_eventId(tree, False)
#print(tree_idxs.shape)
#print(list(imgtree.GetListOfBranches()))

# Load GG ntuples as TTree friend
print('Setting GG as TTree friend')
print('N GG files:',len(args.gg_inputs))
print('GG file[0]:',args.gg_inputs[0])
#ggtree = ROOT.TChain("ggCandidateDumper/trees/%s_13TeV_2photons"%args.gg_treename)
ggtree = ROOT.TChain('ggNtuplizer/EventTree')
#for fh in args.gg_inputs:
for i,fh in enumerate(args.gg_inputs):
    ggtree.Add(fh)
    #if i > 10: break
nEvtsf = ggtree.GetEntries()
print('N evts in GG ntuple:',nEvtsf)
# Make this a friend of the IMG ntuple:
# This allows event variables from both ntuples to be accessible
# from the main TTree, the IMG ntuple
#imgtree.AddFriend(ggtree)
# Keep an index of eventIds in TTree friend
# Since the IMG ntuple controls the main event loop
# want to later skip events not in GG ntuple
print('Collecting event indices from GG ntuple...')
evtlistf = get_evtlist(ggtree)
print('len(evtlistf):',len(evtlistf))
print('...done')

#'''
# Initialize output ntuple
# Merges GG variables + regressed m_a
if not os.path.isdir(args.outdir):
    os.makedirs(args.outdir)
if args.njobs is None:
    file_out = ROOT.TFile("%s/%s_mantuple.root"%(args.outdir, args.sample), "RECREATE")
else:
    file_out = ROOT.TFile("%s/%s%d_mantuple.root"%(args.outdir, args.sample, args.job), "RECREATE")
file_out.mkdir("ggNtuplizer")
file_out.cd("ggNtuplizer")
# Clone TTree structure of GG ntuple
tree_out = ggtree.CloneTree(0)
#print(list(tree_out.GetListOfBranches()))

# Initialize add-on `ma` branch:
# In PyROOT, to declare a branch `ma` with variable size nPho(evt_i),
# need to declare a separate branch `nPho` whose value at fill time
# is the desired (variable) size of `ma`. The cloned ggNtuple already
# has such a branch `nPho` (otherwise would need to be created explicitly).
# !! NOTE: at fill time, need to check that ggtree.nPho corresponds to
# no. of presumed photon objects to be regressed, i.e.:
# ggtree.nPho == len(imgtree.SC_ieta) or len(imgtree.SC_iphi)
# The `ma` branch still needs to be initialized with an array of some
# arbitrarily large allocation `nPhoMax` which then gets reduced at fill time.
nPhoMax = 20
#ma = array('f', nPhoMax*[0.])
ma = np.zeros(nPhoMax, dtype='float32')
tree_out.Branch('ma', ma, 'ma[nPho]/F')
#'''

# Load mass regressor for inference
print('Loading regressor model')
import torch_resnet_concat as networks
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

k = 'ma'
#c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
h[k] = ROOT.TH1F(k, k, 56, -0.2, 1.2)
#h[k] = ROOT.TH1F(k, k, 48, 0., 1.2)

nEvtsJob = nEvts//args.njobs
# Event range to process
#iEvtStart = 0
#iEvtEnd   = nEvts
iEvtStart = args.job*nEvtsJob
iEvtEnd = (args.job+1)*nEvtsJob if args.job+1 < args.njobs else nEvts
#iEvtEnd   = 10000#50000#10
#iEvtEnd   = len(evtlistf)
print(">> Processing entries: [",iEvtStart,"->",iEvtEnd,")")

def shapeEB(eb):
    return np.array(eb).reshape(1,170,360)

nWrite = 0
sw = ROOT.TStopwatch()
sw.Start()
# Main event loop follows imgtree
for iEvt in range(iEvtStart,iEvtEnd):

    # Initialize event
    if iEvt%10e3==0: print(iEvt,'/',iEvtEnd-iEvtStart)
    # Get imgtree entry
    evt_status = imgtree.GetEntry(iEvt)
    if evt_status <= 0: continue
    # Get matching ggtree entry
    evt_statusf = ggtree.GetEntry(idxf_where_run_lumi_evt(imgtree, evtlistf))
    if evt_statusf <= 0: continue
    #print('evt_status:',evt_status, 'evt_statusf:', evt_statusf)

    # Verify event ID match
    assert((ggtree.run == imgtree.runId) & (ggtree.lumis == imgtree.lumiId) & (ggtree.event == imgtree.eventId))

    # Ensure that photons in ggtree are same ones as in imgtree
    #print(len(ggtree.phoEt))
    #print(list(ggtree.phoEt))
    #print('N imgs:',len(imgtree.SC_ieta))
    #print('ietas:',list(imgtree.SC_ieta))
    #print('iphis:',list(imgtree.SC_iphi))
    #print('img ntuple:',list(imgtree.pho_pT))
    assert ggtree.nPho == len(imgtree.SC_ieta)
    assert list(ggtree.phoEt) == list(imgtree.pho_pT)
    assert list(ggtree.phoEta) == list(imgtree.pho_eta)
    assert list(ggtree.phoPhi) == list(imgtree.pho_phi)

    # Initialize a separate array `ma_` that will be used to fill
    # tree branch `ma` (faster than initializing `ma` by element)
    assert ggtree.nPho <= nPhoMax
    ma_ = -1.*np.ones(ggtree.nPho) # default value = -1.
    # Regress only photons within ROI
    idxs_roi = [i for i,ieta in enumerate(imgtree.SC_ieta) if is_barrel_ieta(ieta)]
    #print(idxs_roi)
    #idxs_roi_iphi = [i for i,iphi in enumerate(imgtree.SC_iphi) if iphi != -1]
    #print(idxs_roi_iphi)
    #idxs_roi_np = np.argwhere(np.array(imgtree.SC_ieta) == -1)
    #print(idxs_roi_np)
    if len(idxs_roi) > 0:

        X_EBt = np.array(imgtree.EB_energyT).reshape(1,170,360)
        X_EBz = np.array(imgtree.EB_energyZ).reshape(1,170,360)
        X_cms = np.concatenate([X_EBt, X_EBz], axis=0)

        sc_cms, ieta, iphi = [], [], []
        for idx in idxs_roi:
            ieta.append([imgtree.SC_ieta[idx]])
            iphi.append([imgtree.SC_iphi[idx]])
            #print(imgtree.SC_ieta[idx], ieta[-1])
            #print(imgtree.SC_iphi[idx], iphi[-1])
            sc_cms.append(crop_EBshower(X_cms, ieta[-1], iphi[-1]))
            #print(crop_EBshower(X_cms, ieta[-1], iphi[-1]).shape)
        #print(np.array(sc_cms).shape)
        #print(np.array(iphi).shape)
        #print(np.array(ieta).shape)
        #'''
        ma_roi = inv_transform(resnet([torch.Tensor(sc_cms).cuda()/eb_scale,\
                                   torch.Tensor(iphi).cuda()/360.,\
                                   torch.Tensor(ieta).cuda()/170.
                                  ])).tolist()
        #print(np.array(ma_roi).shape)
        #print(ma_roi)
        # Overwrite default values at ROI indices
        for i,idx_roi in enumerate(idxs_roi):
            ma_[idx_roi] = ma_roi[i][0]

    #print(ma_)
    # Fill output branch and histograms
    for i in range(ggtree.nPho):
        ma[i] = ma_[i]
        h['ma'].Fill(ma_[i])
        h['ieta'].Fill(imgtree.SC_ieta[i])
        h['iphi'].Fill(imgtree.SC_iphi[i])

    #print(ma)
    tree_out.Fill()
    nWrite += 1
    #if nWrite > 10: break

sw.Stop()
print(">> N events written: %d / %d"%(nWrite, iEvtEnd-iEvtStart))
print(">> Real time:",sw.RealTime()/60.,"minutes")
print(">> CPU time: ",sw.CpuTime() /60.,"minutes")

'''
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
'''

#blue: leading
#red: sub-leading

file_out.Write()
file_out.Close()
