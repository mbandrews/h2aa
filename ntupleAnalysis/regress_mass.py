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
parser.add_argument('-t', '--magen_tgt', default=None, type=float, help='magen tgt in GeV, if doing an interpolation.')
parser.add_argument('-i', '--img_list', default='img_inputs.txt', type=str, help='List file of imgNtuple inputs.')
parser.add_argument('-g', '--gg_list', default='gg_inputs.txt', type=str, help='List file of ggNtuple inputs.')
parser.add_argument('-m', '--model', default='Models/model_epoch80_mae0.1906.pkl', type=str, help='Regressor model file.')
parser.add_argument('-o', '--outdir', default='MAntuples', type=str, help='Output directory.')
parser.add_argument('-l', '--log_file', default='log.txt', type=str, help='Log file.')
args = parser.parse_args()

sample = args.sample
img_list = args.img_list
gg_list = args.gg_list
model = args.model
outdir = args.outdir
log_file = args.log_file
magen_tgt = args.magen_tgt

magen_instr = sample.split('-')[1].replace('mA','').replace('GeV','')
magen_in = float(magen_instr.replace('p','.'))
magen_tgtstr = None if magen_tgt is None else str(magen_tgt).replace('.','p')

flog = open(log_file, 'w+')
def logger(log_file, log):
    print(log)
    log_file.write('%s\n'%(log))

logger(flog, '>> Sample: %s'%sample)
logger(flog, '>> Model: %s'%model)
logger(flog, '>> Input imgNtuple list: %s'%img_list)
logger(flog, '>> Input ggSkim list: %s'%gg_list)
logger(flog, '>> Output maNtuple dir: %s'%outdir)
logger(flog, '>> Log file: %s'%log_file)
logger(flog, '>> magen,in: %s'%magen_in)
logger(flog, '>> magen,tgt: %s'%magen_tgt)
if magen_tgt is not None:
    sample = sample.replace(magen_instr, magen_tgtstr)
    if magen_tgt > magen_in:
        sample += 'up'
    else:
        sample += 'dn'
    logger(flog, '.. Interpolating mass !!')
    logger(flog, '>> Sample: %s'%sample)

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

# Crop out EB shower from full EB image with padding
def crop_EBshower_padded(imgEB, ieta, iphi, window=32):

    assert len(imgEB.shape) == 3, '!! len(imgEB.shape): %d != 3'%len(imgEB.shape)
    assert ieta[0] < imgEB.shape[1], '!! ieta:%d !< imgEB.shape[1]:%d'%(ieta[0], imgEB.shape[1])
    assert iphi[0] < imgEB.shape[2], '!! iphi:%d !< imgEB.shape[2]:%d'%(iphi[0], imgEB.shape[2])

    # NOTE: image window here should correspond to the one used in RHAnalyzer
    off = window//2
    ieta = int(ieta[0])+1 # seed positioned at [15,15]
    iphi = int(iphi[0])+1 # seed positioned at [15,15]

    # ------------------------------------------------
    # ieta (row) padding
    # ------------------------------------------------
    pad_lo, pad_hi = 0, 0
    # lower padding check
    if ieta >= off:
        ieta_lo = ieta-off
    else:
        pad_lo = abs(ieta-off)
        ieta_lo = 0
    # upper padding check
    if ieta+off <= imgEB.shape[1]:
        ieta_hi = ieta+off
    else:
        pad_hi = abs(ieta+off-imgEB.shape[1])
        ieta_hi = imgEB.shape[1]

    # ------------------------------------------------
    # iphi (col) wrap-around
    # ------------------------------------------------
    # Wrap-around on left side
    if iphi < off:
        diff = off-iphi
        img_crop_ = np.concatenate((imgEB[:, ieta_lo:ieta_hi, -diff:],
                                    imgEB[:, ieta_lo:ieta_hi, :iphi+off]), axis=-1)
    # Wrap-around on right side
    elif 360-iphi < off:
        diff = off - (360-iphi)
        img_crop_ = np.concatenate((imgEB[:, ieta_lo:ieta_hi, iphi-off:],
                                    imgEB[:, ieta_lo:ieta_hi, :diff]), axis=-1)
    # Nominal case
    else:
        img_crop_ = imgEB[:, ieta_lo:ieta_hi, iphi-off:iphi+off]

    # Add ieta padding if needed
    img_crop = np.pad(img_crop_, ((0,0), (pad_lo, pad_hi), (0,0)), 'constant') # pads with 0
    assert img_crop.shape[1] == window, '!! img_crop.shape[1]:%d != window:%d'%(img_crop.shape[1], window)
    assert img_crop.shape[2] == window, '!! img_crop.shape[2]:%d != window:%d'%(img_crop.shape[2], window)

    return img_crop

###########################################################
# Functions for getting seed ieta,iphi given photon eta,phi

# xtal eta edges
xtal_etas = np.linspace(0, 1.479, 85+1)
# stitch [-1.479,...,0],(0,...,1.479] removing repeated `0.`
xtal_etas = np.concatenate([-np.flipud(xtal_etas), xtal_etas[1:]])

# xtal phi edges
xtal_phis = np.linspace(-np.pi, np.pi, 360+1)[:-1] # -pi and pi are same edge
# detector iphi = 0 does not correspond to phi = -pi
# shift `xtal_phis` to align with origin of detector iphis
xtal_phi_origin = 170
xtal_phis = np.concatenate([xtal_phis[xtal_phi_origin:], xtal_phis[:xtal_phi_origin]])
xtal_dphi = 2.*np.pi/360. # phi granularity

# Calculate deltaPhi
def deltaPhi(phi1, phi2):
    # returns the angular displacement from phi1 to phi2 within (0, 2pi)
    # ported from: https://github.com/cms-sw/cmssw/blob/master/DataFormats/Math/interface/deltaPhi.h
    angle = phi1 - phi2
    twoPi = 2. * np.pi
    oneOverTwoPi = 1. / (2. * np.pi)
    epsilon = 1.e-6
    if (abs(angle) <= epsilon) or (abs(twoPi - abs(angle)) <= epsilon):
        return 0.
    if abs(angle) > twoPi:
        nFac = np.trunc(angle * oneOverTwoPi)
        angle -= (nFac * twoPi)
        if abs(angle) <= epsilon:
            return 0.
    if angle < 0.:
        angle += twoPi

    # restrict to magnitude (0, pi)
    # NOTE: gives distance not displacement,
    # so can't be used to get info about "leftmost" edge closest to `phi`
    #if angle > np.pi:
    #    angle = 2.*np.pi - angle

    return angle

def lookup_ieta(eta, etas):
    # get leftmost edge of xtals closest to `eta`
    ieta = np.argwhere(eta > etas)[-1][0]
    return ieta

def lookup_iphi(phi, xtal_phis):
    # get angular displacement in (0, 2pi) between `phi` and all xtal edges `xtal_phis`
    dphis = np.array([deltaPhi(phi, p) for p in xtal_phis])
    # get leftmost edge of xtals closest to `phi`
    iphi = np.argwhere(dphis < xtal_dphi)[0][0]
    return iphi

# Get closest xtal ieta,iphi coords of photon eta, phi
def get_xtal_coords(eta, phi):
    # Get ieta
    ieta = lookup_ieta(eta, xtal_etas)
    #print(ieta, eta)
    # Get iphi
    iphi = lookup_iphi(phi, xtal_phis)
    #print(iphi, phi)
    return ieta, iphi

# Get ieta, iphi coords of xtal energy max ("seed") given photon eta, phi coordinates
def get_seed_ieta_iphi(eta, phi, X_EB, search_window=12):
    assert abs(eta) < 1.479
    # get xtal coords associated with photon `eta`, `phi`
    pho_ieta, pho_iphi = get_xtal_coords(eta, phi)
    # look for energy max ("seed") in `search_window` x `search_window` window around (pho_ieta, pho_iphi)
    X_w = crop_EBshower_padded(X_EB, [pho_ieta], [pho_iphi], window=search_window)
    # get coordinates of seed in search window `X_w`
    seed_wcoords = np.argwhere(X_w == X_w.max())[0]
    # get position of photon in search window `X_w`
    # If `search_window` == 12, will always be at [5, 5]
    # use np.argwhere() anyway in case `search_window` is of different size
    pho_wcoords = np.argwhere(X_w == X_EB[0, pho_ieta, pho_iphi])[0]
    # get offset of seed from pho coords
    seed_off = seed_wcoords - pho_wcoords
    # get global seed coords, i.e. in EB frame
    # shift `pho_ieta` and `pho_iphi` by seed offset `seed_off`
    seed_ieta, seed_iphi = pho_ieta+seed_off[-2], pho_iphi+seed_off[-1]
    # if `iphi` >= 360, wrap-around
    if seed_iphi >= 360:
        seed_iphi -= 360
    return seed_ieta, seed_iphi

# Create an event list containing run:lumi:event:idx IDs for some input `tree`
# Defaults to ggNtuple so events can be skipped if not present here.
# NOTE: event id conventions for the ntuples are as follows:
# IMG -> runId:lumiId:eventId
# GG -> run:lumis:event
def get_evtlist(tree, is_ggntuple=True):
    nEvts = tree.GetEntries()
    idxs = []
    for iEvt in range(nEvts):
        # Initialize event
        tree.GetEntry(iEvt)
        if iEvt%100e3==0: logger(flog, '%d / %d'%(iEvt, nEvts))
        if is_ggntuple:
            eventId = [tree.run, tree.lumis, tree.event, iEvt]
        else:
            eventId = [tree.runId, tree.lumiId, tree.eventId, iEvt]
        idxs.append(eventId)
    # Array index on 1st element should be 0, and nEvts-1 on last element
    idxs = np.array(idxs)
    assert idxs[0,-1] == 0 and idxs[-1,-1] == nEvts-1
    return idxs

# Return the array index in `gg_evtlist` corresponding to event loaded in `img_tree`
# Each event uniquely identified by run, lumi, event no.
# Filter first by run then lumi before looking for event no.
# If evt not found, returns `-1` to trigger TTree event status == bad
def idx_where_run_lumi_evt(img_tree, gg_evtlist):

    # `eventlistf` must have shape (nevts,4) where
    # [:,0]: run
    # [:,1]: lumi
    # [:,2]: event
    # [:,3]: idx
    assert gg_evtlist.shape[-1] == 4

    # This is the target event ID from the main IMG TTree
    evtid = np.array([img_tree.runId, img_tree.lumiId, img_tree.eventId])

    # Find the index in gg_evtlistf corresponding to target img event
    # Filter by run
    iruns = np.argwhere(gg_evtlist[:,0] == evtid[0]).flatten()
    gg_evtlist = gg_evtlist[iruns]
    if len(gg_evtlist) == 0:
        return -1
    # Filter by lumi
    ilumis = np.argwhere(gg_evtlist[:,1] == evtid[1]).flatten()
    gg_evtlist = gg_evtlist[ilumis]
    if len(gg_evtlist) == 0:
        return -1
    # Filter by event
    ievts = np.argwhere(gg_evtlist[:,2] == evtid[2]).flatten()
    gg_evtlist = gg_evtlist[ievts]

    assert len(gg_evtlist) <= 1, '!! More than one evt match found!'

    if len(gg_evtlist) == 0:
        return -1
    else:
        return gg_evtlist.flatten()[-1]

# Load IMG ntuples as main TTree
logger(flog, '>> Setting img inputs as primary tree')
# Read in file list
logger(flog, '   .. opening img input list')
img_inputs = []
with open(img_list, 'r') as img_files:
    for f in img_files:
        img_inputs.append(f.strip('\n'))
logger(flog, '   .. found %d files'%len(img_inputs))
assert len(img_inputs) > 0
logger(flog, '   .. [ 0]: %s'%img_inputs[0])
logger(flog, '   .. [-1]: %s'%img_inputs[-1])
# Load files into tree
img_tree = ROOT.TChain("fevt/RHTree")
for f in img_inputs:
    img_tree.Add(f)
    #break
nEvts = img_tree.GetEntries()
logger(flog, '   .. Nevts: %d'%nEvts)

# Load ggNtuples as secondary tree
logger(flog, '>> Setting gg inputs as secondary tree')
# Read in file list
logger(flog, '   .. opening gg input list')
gg_inputs = []
with open(gg_list, 'r') as gg_files:
    for f in gg_files:
        gg_inputs.append(f.strip('\n'))
logger(flog, '   .. found %d files'%len(gg_inputs))
assert len(gg_inputs) > 0
logger(flog, '   .. [ 0]: %s'%gg_inputs[0])
logger(flog, '   .. [-1]: %s'%gg_inputs[-1])
# Load files into tree
gg_tree = ROOT.TChain('ggNtuplizer/EventTree')
for f in gg_inputs:
    gg_tree.Add(f)
nEvts_gg = gg_tree.GetEntries()
logger(flog, '   .. Nevts: %d'%nEvts_gg)
logger(flog, '   >> Collecting event indices from gg ntuples...')
gg_evtlist = get_evtlist(gg_tree)
logger(flog, '      .. done')

# Initialize output ntuple
# First, clone ggNtuple directory+variables
#if not os.path.isdir(outdir):
#    os.makedirs(outdir)
#file_out = ROOT.TFile("%s/%s_mantuple.root"%(outdir, sample), "RECREATE")
outpath = "%s/%s_mantuple.root"%(outdir, sample)
logger(flog, '>> Initializing output mantuple: %s'%outpath)
file_out = ROOT.TFile.Open(outpath, 'RECREATE')
file_out.mkdir("ggNtuplizer")
file_out.cd("ggNtuplizer")
tree_out = gg_tree.CloneTree(0)
#logger(flog, list(tree_out.GetListOfBranches()))

# Then add branches for regressed m_a
# Initialize branches for the m_as as single floats
ma0 = np.zeros(1, dtype='float32')
ma1 = np.zeros(1, dtype='float32')
tree_out.Branch('ma0', ma0, 'ma0/F')
tree_out.Branch('ma1', ma1, 'ma1/F')
logger(flog, '   .. done.')

# Load mass regressor model
logger(flog, '>> Loading model file...')
import torch_resnet_concat as networks
#epoch = 80
#neg_mass = 300
## AOD
#model_file = glob.glob('../EB_Pi0_massreg_Pt20To100_2017PU_ext3_tzfixed_wrapfix/MODELS/DoublePi0Pt20To100_m0To1600_pythia8_PU2017_genDR10_aodDR16_nPhoN_PhoNeg%dTo0_wgts_EBtzo25_AOD_m0o1.6_ResNet_blocks3_seedPos_FC128x0_MAEloss_lr0.0005_epochs80_n778k_run0/model_epoch%d_*.pkl'%(neg_mass, epoch))
model_file = model #'Models/model_epoch80_mae0.1906.pkl'
resnet = networks.ResNet(2, 3, [16, 32], 128, 0).cuda()
resnet.load_state_dict(torch.load(model_file)['model'])
resnet.eval()
logger(flog, '   .. done.')

eb_scale = 25.
m0_scale = 1.6
def transform_y(y):
    return y/m0_scale
def inv_transform(y):
    return y*m0_scale

h = {}
#c, wd, ht = {}, int(440*1), int(400*1)

k = 'iphi'
h[k] = ROOT.TH1F(k, k, (360//5)+1, -5., 360.)
k = 'ieta'
h[k] = ROOT.TH1F(k, k, (170//5)+1, -5., 170.)

k = 'ma0'
h[k] = ROOT.TH1F(k, k, 56, -0.2, 1.2)
#h[k] = ROOT.TH1F(k, k, 48, 0., 1.2)
k = 'ma1'
h[k] = ROOT.TH1F(k, k, 56, -0.2, 1.2)
#h[k] = ROOT.TH1F(k, k, 48, 0., 1.2)

k = 'ma0vma1'
h[k] = ROOT.TH2F(k, k, 48, 0., 1.2, 48, 0., 1.2)

# Event range to process
iEvtStart = 0
iEvtEnd   = nEvts
#iEvtEnd   = 1000#10
logger(flog, ">> Processing entries: [%d, %d)"%(iEvtStart, iEvtEnd))

def shapeEB(eb):
    return np.array(eb).reshape(1,170,360)

nWrite = 0
nEvts_gg_proc = 0
sw = ROOT.TStopwatch()
sw.Start()
for iEvt in range(iEvtStart,iEvtEnd):

    # Initialize event
    if iEvt%10e3==0: logger(flog, '%d / %d'%(iEvt, iEvtEnd-iEvtStart))
    # Main tree
    evt_status = img_tree.GetEntry(iEvt)
    if evt_status <= 0: continue
    # Secondary tree
    evt_status2 = gg_tree.GetEntry(idx_where_run_lumi_evt(img_tree, gg_evtlist))
    if evt_status2 <= 0: continue
    nEvts_gg_proc += 1

    # Check event ID
    assert((gg_tree.run == img_tree.runId) & (gg_tree.lumis == img_tree.lumiId) & (gg_tree.event == img_tree.eventId))

    # Apply mGG window cut
    #if gg_tree.mgg < 100. or gg_tree.mgg > 180.: continue

    # Check photon indices correspond to same objects
    p4 = {}
    pho_idx = {}
    X_EB = np.array(img_tree.EB_energy).reshape(1,170,360) # Etot, for consistency with seed-finding in SCRegressor
    #X_EB = np.array(img_tree.EB_energyT).reshape(1,170,360) # Et
    seed_ietas, seed_iphis = [], []
    for i in range(len(gg_tree.phoPreselIdxs)):
        pho_idx[i] = gg_tree.phoPreselIdxs[i]
        '''
        # ggntuple photon vector
        p4['gg'] = ROOT.TVector3()
        p4['gg'].SetPtEtaPhi(gg_tree.phoEt[pho_idx[i]], gg_tree.phoEta[pho_idx[i]], gg_tree.phoPhi[pho_idx[i]])
        # img ntuple photon vector
        p4['img'] = ROOT.TVector3()
        p4['img'].SetPtEtaPhi(img_tree.pho_pT[pho_idx[i]], img_tree.pho_eta[pho_idx[i]], img_tree.pho_phi[pho_idx[i]])
        # Ensure photons are alike
        dR = ROOT.Math.VectorUtil.DeltaR(p4['gg'], p4['img'])
        assert dR == 0.
        h['ieta'].Fill(img_tree.SC_ieta[pho_idx[i]])
        h['iphi'].Fill(img_tree.SC_iphi[pho_idx[i]])
        '''
        sieta, siphi = get_seed_ieta_iphi(gg_tree.phoEta[pho_idx[i]], gg_tree.phoPhi[pho_idx[i]], X_EB)
        h['ieta'].Fill(sieta)
        h['iphi'].Fill(siphi)
        seed_ietas.append(sieta)
        seed_iphis.append(siphi)

    # Only keep events with photons within ieta image window
    #npho_roi = sum([0 if (img_tree.SC_ieta[pho_idx[i]] < 15) or (img_tree.SC_ieta[pho_idx[i]]+16 > 169) else 1 for i in range(len(pho_idx))])
    #npho_roi = sum([1 if (img_tree.SC_ieta[pho_idx[i]] >= 0) and (img_tree.SC_ieta[pho_idx[i]] < 170) else 0 for i in range(len(pho_idx))])
    npho_roi = sum([1 if (seed_ietas[i] >= 0) and (seed_ietas[i] < 170) else 0 for i in range(len(pho_idx))])
    if npho_roi != 2:
        #print(img_tree.SC_ieta[pho_idx[0]], img_tree.SC_ieta[pho_idx[1]])
        continue

    # Crop EB windows from full EB frames
    sc_cms = []
    ieta, iphi = [], []
    X_EBt = np.array(img_tree.EB_energyT).reshape(1,170,360) # Et
    X_EBz = np.array(img_tree.EB_energyZ).reshape(1,170,360) # Ez
    X_cms = np.concatenate([X_EBt, X_EBz], axis=0)
    for i in range(npho_roi):
        '''
        ieta.append([img_tree.SC_ieta[pho_idx[i]]])
        iphi.append([img_tree.SC_iphi[pho_idx[i]]])
        '''
        ieta.append([seed_ietas[i]])
        iphi.append([seed_iphis[i]])
        #sc_cms_ = crop_EBshower(X_cms, ieta[-1], iphi[-1])
        sc_cms_ = crop_EBshower_padded(X_cms, ieta[-1], iphi[-1])
        sc_cms.append(sc_cms_)

    # Run inference
    ma = inv_transform(resnet([torch.Tensor(sc_cms).cuda()/eb_scale,\
                               torch.Tensor(iphi).cuda()/360.,\
                               torch.Tensor(ieta).cuda()/170.
                              ])).tolist()

    m0_rescale = 1. if magen_tgt is None else magen_tgt/magen_in
    #print(m0_rescale)
    #break
    # Fill output variables
    #ma0_, ma1_ = ma[0][0], ma[1][0]
    ma0_, ma1_ = ma[0][0]*m0_rescale, ma[1][0]*m0_rescale
    ma0[0] = ma0_
    ma1[0] = ma1_
    tree_out.Fill()
    h['ma0'].Fill(ma0_)
    h['ma1'].Fill(ma1_)
    h['ma0vma1'].Fill(ma0_, ma1_)
    #print(ma0_, ma1_)

    nWrite += 1

file_out.Write()
sw.Stop()
logger(flog, ">> N events written / IMG processed: %d / %d"%(nWrite, iEvtEnd-iEvtStart))
logger(flog, ">> N events written / GG processed: %d / %d"%(nWrite, nEvts_gg_proc))
logger(flog, ">> N events written / GG total: %d / %d"%(nWrite, nEvts_gg))
logger(flog, ">> Real time: %f minutes"%(sw.RealTime()/60.))
logger(flog, ">> CPU time: %f minutes"%(sw.CpuTime() /60.))
flog.close()
