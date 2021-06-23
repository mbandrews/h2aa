from __future__ import print_function
import numpy as np
np.random.seed(0)
import os, glob
import time
import argparse
from data_utils import *

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
parser.add_argument('-i', '--img_inputs', default='img_inputs.txt', type=str, help='List file of img inputs.')
parser.add_argument('-o', '--outdir', default='Guntuples', type=str, help='Output directory.')
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

def get_weight_2d(m0, pt, m0_edges, pt_edges, wgts):
    idx_m0 = np.argmax(m0 <= m0_edges)-1
    idx_pt = np.argmax(pt <= pt_edges)-1
    #print(idx_m0, idx_pt)
    return wgts[idx_m0, idx_pt]

hmvpts, m_edgess, pt_edgess = {}, {}, {}
if args.wgt_files is not None:
    nPasses = len(args.wgt_files)
    for p,wgt_file in enumerate(args.wgt_files):
        w = np.load(wgt_file)
        hmvpts[p], m_edgess[p], pt_edgess[p] = w['mvpt'], w['m_edges'], w['pt_edges']

sample = args.sample
sample = 'DoublePi0Pt10To100_m0To1600_pythia8_ReAOD_PU2017_MINIAODSIM_pu'

# Load IMG ntuples as main TTree
eos_basedir = '/store/user/lpcml/mandrews/IMG'
#img_inputs = []
img_inputs = run_eosfind(eos_basedir, sample)
#print('Opening img input list:',args.img_inputs)
#with open(args.img_inputs, 'r') as img_file:
#    for img_input in img_file:
#        img_inputs.append(img_input[:-1])
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

# Initialize output ntuple
if not os.path.isdir(args.outdir):
    os.makedirs(args.outdir)
file_out = ROOT.TFile("%s/%s_guntuple.root"%(args.outdir, sample), "RECREATE")
tree_out = tree.CloneTree(0)
#print(list(tree_out.GetListOfBranches()))

# Initialize branches for the m_as as single floats
# [PyROOT boilerplate for single float branches]
ma0 = np.zeros(1, dtype='float32')
ma1 = np.zeros(1, dtype='float32')
tree_out.Branch('ma0', ma0, 'ma0/F')
tree_out.Branch('ma1', ma1, 'ma1/F')
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

# Event range to process
iEvtStart = 0
iEvtEnd   = nEvts
iEvtEnd   = 10#50000#10
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

    nPhoEvt = len(rhTree.SC_mass)

    npho_roi = 0
    # Only keep events with photons within ieta image window
    for i in range(nPhoEvt):
        if (tree.SC_ieta[i] < 15) or (tree.SC_ieta[i]+16 > 169): continue
        if rhTree.pho_pT[i] > 100.: continue
        npho_roi += 1

    if npho_roi < 1: continue

    if args.wgt_files is not None:
        rands = np.random.random((npho_roi, nPasses))

    for i in range(npho_roi):
        h['ieta'].Fill(tree.SC_ieta[i])
        h['iphi'].Fill(tree.SC_iphi[i])

    # Only keep events with barrel photons
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
        ieta.append([tree.SC_ieta[pho_idx[i]]])
        iphi.append([tree.SC_iphi[pho_idx[i]]])
        #print(tree.SC_ieta[pho_idx[i]], ieta[-1])
        #print(tree.SC_iphi[pho_idx[i]], iphi[-1])
        sc_cms_ = crop_EBshower(X_cms, ieta[-1], iphi[-1])
        sc_cms.append(sc_cms_)
        #print(sc_cms_.shape)
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

    #break
    nWrite += 1

sw.Stop()
print(">> N events written: %d / %d"%(nWrite, iEvtEnd-iEvtStart))
print(">> Real time:",sw.RealTime()/60.,"minutes")
print(">> CPU time: ",sw.CpuTime() /60.,"minutes")


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

#blue: leading
#red: sub-leading
'''
file_out.Write()
file_out.Close()

