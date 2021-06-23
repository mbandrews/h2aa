from __future__ import print_function
import numpy as np
np.random.seed(0)
import os, glob
import time
import argparse

import ROOT
from array import array


# Register command line options
parser = argparse.ArgumentParser(description='Run rechit analysis.')
parser.add_argument('-s', '--sample', default='test', type=str, help='Sample name.')
parser.add_argument('-i', '--img_inputs', default='img_inputs_Run2017B.txt', type=str, help='List file of img inputs.')
parser.add_argument('-g', '--gg_inputs', default=['../ggSkims/3pho/Run2017B_ggskim.root'], nargs='+', type=str, help='Input GG files.')
parser.add_argument('-o', '--outdir', default='errvE', type=str, help='Output directory.')
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

# Load GG ntuples as TTree friend
print('Setting GG as TTree friend')
print('N GG files:',len(args.gg_inputs))
print('GG file[0]:',args.gg_inputs[0])
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

file_out = ROOT.TFile("%s/%s_rechit_hists.root"%(args.outdir, args.sample), "RECREATE")

#'''
c, h = {}, {}
wd, ht = int(440*1), int(400*1)

k = 'iphi'
#c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
h[k] = ROOT.TH1F(k, k, 360//5, 0., 360)
k = 'ieta'
#c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
h[k] = ROOT.TH1F(k, k, 170//5, 0., 170)

#nbins_rh, maxE_rh = 20, 10.
#nbins_rh, maxE_rh = 50, 25.
#nbins_rh, maxE_rh = 100, 50.
nbins_rh, maxE_rh = 200, 100.

k = 'rechitE'
c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
h[k] = ROOT.TH1F(k, k, nbins_rh, 0., maxE_rh)

k = 'rechitErrvE1d'
c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
h[k] = ROOT.TProfile(k, k, nbins_rh, 0., maxE_rh)

k = 'rechitErrvE2d'
c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
#h[k] = ROOT.TH2F(k, k, nbins_rh, 0., maxE_rh, 10, 0.05, 0.15)
#h[k] = ROOT.TH2F(k, k, nbins_rh, 0., maxE_rh, 10, 0., 0.15)
h[k] = ROOT.TH2F(k, k, nbins_rh, 0., maxE_rh, 50, 0., 0.5)

# Event range to process
iEvtStart = 0
iEvtEnd   = nEvts
#iEvtEnd   = 100000
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
    evt_statusf = treef.GetEntry(idxf_where_run_lumi_evt(tree, evtlistf))
    if evt_statusf <= 0: continue

    # Event ID
    assert((treef.run == tree.runId) & (treef.lumis == tree.lumiId) & (treef.event == tree.eventId))

    if treef.mgg < 100. or treef.mgg > 180.: continue

    p4 = {}
    pho_idx = {}
    for i in range(len(treef.phoPreselIdxs)):
        pho_idx[i] = treef.phoPreselIdxs[i]
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
    ieta, iphi = [], []
    eb_energyT = np.array(tree.EB_energyT).reshape(1,170,360)
    eb_energyZ = np.array(tree.EB_energyZ).reshape(1,170,360)
    eb_energyErr = np.array(tree.EB_energyErr).reshape(1,170,360)
    eb_all = np.concatenate([eb_energyT, eb_energyZ, eb_energyErr], axis=0)
    for i in range(npho_roi):
        ieta.append([tree.SC_ieta[pho_idx[i]]])
        iphi.append([tree.SC_iphi[pho_idx[i]]])
        sc_all = crop_EBshower(eb_all, ieta[-1], iphi[-1])
        sc_energy = np.sqrt(sc_all[0]*sc_all[0] + sc_all[1]*sc_all[1]).flatten() # E = sqrt( Et^2 + Ez^2 )
        sc_energyErr = sc_all[2].flatten()
        assert len(sc_energy) == len(sc_energyErr)
        for en, err in zip(sc_energy, sc_energyErr):
            if not (en > 0.): continue
            h['rechitE'].Fill(en)
            h['rechitErrvE1d'].Fill(en, err)
            h['rechitErrvE2d'].Fill(en, err)

    nWrite += 1

sw.Stop()
print(">> N events written: %d / %d"%(nWrite, iEvtEnd-iEvtStart))
print(">> Real time:",sw.RealTime()/60.,"minutes")
print(">> CPU time: ",sw.CpuTime() /60.,"minutes")

def set_hist(h, c, xtitle, ytitle, htitle=''):
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
k = 'rechitE'
c[k].cd()
c[k].SetLogy()
h[k], c[k] = set_hist(h[k], c[k], "Energy [GeV]", "N_{rechit}")
h[k].SetLineColor(9)
h[k].Draw("hist")
c[k].Draw()
c[k].Print('Plots/%s_%s.eps'%(args.sample, k))
#______________________________________________________
k = 'rechitErrvE1d'
c[k].cd()
h[k], c[k] = set_hist(h[k], c[k], "Energy [GeV]", "Err [GeV]")
h[k].SetLineColor(9)
h[k].Draw()
c[k].Draw()
c[k].Print('Plots/%s_%s.eps'%(args.sample, k))
#______________________________________________________
k = 'rechitErrvE2d'
c[k].cd()
c[k].SetLogz()
h[k], c[k] = set_hist(h[k], c[k], "Energy [GeV]", "Err [GeV]")
#ROOT.gPad.SetRightMargin(0.17)
#ROOT.gStyle.SetPalette(55)#53
h[k].GetYaxis().SetTitleOffset(1.1)
#h[k].GetZaxis().SetTitle("Events")
#h[k].GetZaxis().SetTitleOffset(1.1)
#h[k].GetZaxis().SetTitleSize(0.05)
#h[k].GetZaxis().SetTitleFont(62)
#h[k].GetZaxis().SetLabelSize(0.04)
#h[k].GetZaxis().SetLabelFont(62)
h[k].Draw("COL Z")
#h[k].Draw()
#h[k].SetMaximum(150.) #2: 150, 3: 220
c[k].Draw()
c[k].Print('Plots/%s_%s.eps'%(args.sample, k))
#palette = h[k].GetListOfFunctions().FindObject("palette")
#palette.SetX1NDC(0.84)
#palette.SetX2NDC(0.89)
#palette.SetY1NDC(0.13)
#______________________________________________________
h[k].FitSlicesY()
for i in range(3):
    ki = '%s_%d'%(k, i)
    c[ki] = ROOT.TCanvas("c%s"%ki, "c%s"%ki, wd, ht)
    h[ki] = ROOT.gDirectory.Get(ki)
    for ib in range(h[ki].GetNbinsX()+2):
        pass
        #print(ib,  h[ki].GetBinContent(ib))
    h[ki].Draw()
    c[ki].Draw()
    c[ki].Print('Plots/%s_%s.eps'%(args.sample, ki))
#######################################################
'''
k = 'ma0'
c[k].cd()
h[k], c[k] = set_hist(h[k], c[k], "m_{a,pred} [GeV]", "N_{a}", "m_{a,pred}")
h[k].SetLineColor(9)
h[k].Draw("hist")
k = 'ma1'
h[k].SetLineColor(2)
h[k].Draw("hist SAME")

ymax = 1.2*max(h['ma0'].GetMaximum(), h['ma1'].GetMaximum())
h['ma0'].GetYaxis().SetRangeUser(0., ymax)

l = ROOT.TLine(mass_line, 0., mass_line, ymax) # x0,y0, x1,y1
l.SetLineColor(14)
l.SetLineStyle(7)
l.Draw("same")
hatch = ROOT.TGraph(2, array('d',[0.,0.]), array('d',[0.,ymax]));
hatch.SetLineColor(14)
hatch.SetLineWidth(2001)
hatch.SetFillStyle(3004)
hatch.SetFillColor(14)
hatch.Draw("same")

#c[k].SetGrid()
c['ma0'].Draw()
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
