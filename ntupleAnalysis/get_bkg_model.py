from __future__ import print_function
from collections import OrderedDict
import numpy as np
np.random.seed(0)
import os, glob
import time
import argparse
from array import array
from hist_utils import *
from evt_analyzers import *
from get_bkg_norm import *

import ROOT

# Register command line options
parser = argparse.ArgumentParser(description='Run h2aa bkg model.')
parser.add_argument('-s', '--sample', default='test', type=str, help='Sample name.')
parser.add_argument('-r', '--region', default='sb', type=str, help='Region: `sb` or `sr`.')
parser.add_argument('-i', '--inputs', default=['MAntuples/Run2017F_mantuple.root'], nargs='+', type=str, help='Input MA ntuple.')
parser.add_argument('-t', '--treename', default='Data', type=str, help='MA TTree name prefix.')
parser.add_argument('-o', '--outdir', default='Templates', type=str, help='Output directory.')
parser.add_argument('-b', '--blind', default=None, type=str, help='Regions to blind.')
parser.add_argument('--do_ptomGG', action='store_true', help='Switch to apply pt/mGG cuts.')
parser.add_argument('--do_pt_reweight', action='store_true', help='Switch to apply 2d pt re-weighting.')
parser.add_argument('--do_combined_template', action='store_true', help='Switch to apply 2d ma re-weighting corresponding to combined hgg SR + data SB template.')
parser.add_argument('--do_mini2aod', action='store_true', help='Switch to apply mini2oad wgts.')
parser.add_argument('--write_pts', action='store_true', help='Write out photon pts.')
parser.add_argument('-n', '--norm', default=None, type=float, help='SB to SR normalization.')
parser.add_argument('-e', '--events', default=-1, type=int, help='Number of evts to process.')
parser.add_argument('--systPhoIdSF', default=None, type=str, help='Syst, photon ID SF: None, nom, up, dn.')
parser.add_argument('--systScale', default=None, type=str, help='Syst, m_a energy scale: None, up, dn.')
parser.add_argument('--systSmear', default=None, type=str, help='Syst, m_a energy smear: None, up, dn.')
parser.add_argument('--do_pu_rwgt', action='store_true', help='Apply PU reweighting')
args = parser.parse_args()

ma_binw = 25. # MeV
diag_w = 200. # MeV
blind = args.blind
sample = args.sample
region = args.region
norm = args.norm
outdir = args.outdir
#if sample == 'sb2sr':
#    norm = 0.8526129175228655
do_combined_template = args.do_combined_template
if args.do_combined_template and 'Run2017' in sample and region == 'sr':
    print('WARNING: will not use combined template for SR data!')
    do_combined_template = False

#do_combined_template = args.do_combined_template and (region != 'sr' or 'Run2017' not in sample)
if do_combined_template:
    print('Using combined template')
    s = 'Run2017B-F+GluGluHToGG'
    r = 'sb2sr'
    nfma = np.load("Weights/%s_%s_blind_%s_wgts.npz"%(s, r, None))

do_pt_reweight = args.do_pt_reweight
if do_pt_reweight:
    assert region != 'sr'
    print('Using pt weights')
    s = 'Run2017B-F'
    r = 'sb2sr'
    #r = 'sb2srsblo0p20'
    #r = 'sb2srsbhi0p20'
    #r = 'sb2srsblo'
    #r = 'sb2srsbhi'
    #r = 'sb2sblo'
    #r = 'sb2sbhi'
    nfpt = np.load("Weights/%s_%s_blind_%s_ptwgts.npz"%(s, r, None))
    #nfpt = np.load("Weights/%s_%s_resample_blind_%s_ptwgts.npz"%(s, r, None))

do_ptomGG = args.do_ptomGG
#do_ptomGG = args.do_ptomGG if 'sb' not in region else False
if do_ptomGG:
    print('Using pt/mGG cuts')
else:
    assert region != 'sr'
    #assert do_pt_reweight

do_mini2aod = args.do_mini2aod
if do_mini2aod:
    assert 'GluGluHToGG' in sample
    print('Using mini2oad wgts')
    nfmini2aod = np.load("Weights/Photon_Pt25To100_mAn0p4To1p6_mini2aod_ptmawgts.npz")

write_pts = args.write_pts
if write_pts:
    evtlist_f = open("Weights/%s_region_%s_blind_%s_selected_phoEt_list.txt"%(sample, region, blind), "w+")

do_pu_rwgt = args.do_pu_rwgt
if 'data' in sample: assert do_pu_rwgt is False
if do_pu_rwgt:
    print('Doing PU re-weighting')
    year = str(2017)
    fpu = ROOT.TFile('PU/puwgts_Run%so%s.root'%(year, sample), "READ")
    hpu = fpu.Get('pu_ratio')

systPhoIdSF = args.systPhoIdSF
if 'data' in sample: assert systPhoIdSF is None
if systPhoIdSF is not None:
    print('Doing syst: photon ID SF shift:',systPhoIdSF)
    year = str(2017)
    fsf = ROOT.TFile("SF/SF%s_egammaEffi.txt_EGM2D.root"%(year), "READ")
    hsf = fsf.Get('EGamma_SF2D')

systScale = args.systScale
if 'data' in sample: assert systScale is None
print('Doing syst: energy scale shift:',systScale)

systSmear = args.systSmear
if 'data' in sample: assert systSmear is None
print('Doing syst: energy smear shift:',systSmear)

hists = {}
create_hists(hists)

#cuts = [str(None), 'npho', 'dR', 'ptomGG', 'bdt'] if do_ptomGG else [str(None), 'npho', 'dR', 'bdt']
#cuts = [str(None), 'npho', 'ptomGG'] if do_ptomGG else [str(None), 'npho']
#cuts = [str(None), 'npho', 'ptomGG', 'bdt'] if do_ptomGG else [str(None), 'npho', 'bdt']
#cuts = [str(None), 'npho', 'ptomGG'] if do_ptomGG else [str(None), 'npho']
#cuts = [str(None), 'ptomGG', 'bdt'] if do_ptomGG else [str(None), 'bdt']
#cuts = [str(None), 'ptomGG', 'chgiso'] if do_ptomGG else [str(None), 'chgiso']
#cuts = [str(None), 'ptomGG'] if do_ptomGG else [str(None)]
#cuts = [str(None), 'ptomGG', 'chgiso', 'bdt'] if do_ptomGG else [str(None), 'chgiso', 'bdt']
cuts = [str(None), 'ptomGG', 'bdt', 'chgiso'] if do_ptomGG else [str(None), 'bdt', 'chgiso']
cut_hists = OrderedDict()
create_cut_hists(cut_hists, cuts)
counts = OrderedDict([(cut, 0) for cut in cuts])

print('Setting MA as TTree')
print('N MA files:',len(args.inputs))
print('MA file[0]:',args.inputs[0])
#tree = ROOT.TChain("h4gCandidateDumper/trees/%s_13TeV_2photons"%args.treename)
tree = ROOT.TChain('ggNtuplizer/EventTree')
#for fh in args.inputs:
for i,fh in enumerate(args.inputs):
    tree.Add(fh)
    #if i > 10: break
nEvts = tree.GetEntries()
print('N evts in MA ntuple:',nEvts)
# Event range to process
iEvtStart = 0
iEvtEnd   = nEvts if args.events == -1 else args.events
#iEvtEnd   = 100000

'''
# Inject sg
#sgbr = 1.e-1 # *xsec(h)
#sgbr = 0. # *xsec(h)
#sgbr = 0.0047 # *xsec(h)
#sgbr = 0.0079 # *xsec(h)
#ma = '100MeV'
##sgbr = 0.0014 # *xsec(h)
#sgbr = 0.0024 # *xsec(h)
#ma = '400MeV'
#sgbr = 0.0026 # *xsec(h)
#sgbr = 0.0046 # *xsec(h)
#ma = '1GeV'
h24g_sample = 'h24gamma_1j_1M_%s'%ma
sginj_wgt = sgbr*get_sg_norm(h24g_sample)
#sginj_wgt = 1. # no sg scaling
print('sginj_wgt:',sginj_wgt)
'''
sginj_wgt = 0. # no sg injection

print(">> Processing entries: [",iEvtStart,"->",iEvtEnd,")")
nWrite = 0
sw = ROOT.TStopwatch()
sw.Start()
for iEvt in range(iEvtStart,iEvtEnd):

    # Initialize event
    #if iEvt%10e3==0: print(iEvt,'/',iEvtEnd-iEvtStart)
    if iEvt%1e5==0: print(iEvt,'/',iEvtEnd-iEvtStart)
    evt_statusf = tree.GetEntry(iEvt)
    if evt_statusf <= 0: continue

    # Apply event selection
    outvars = {}
    if not select_event(tree, cuts, cut_hists, counts, outvars): continue

    # Analyze event
    if not analyze_event(tree, region, blind, do_ptomGG): continue

    # Get event weight
    #wgt = 1. if 'Data' in args.treename else tree.weight
    wgt = 1. if tree.isData else tree.genWeight
    #wgt = 1.
    #if region != 'sr' and do_pt_reweight:
    #if 'sb' in region and do_pt_reweight:
    if do_pt_reweight:
        wgt = wgt*get_pt_wgt(tree, nfpt['pt_edges_lead'], nfpt['pt_edges_sublead'], nfpt['pt_wgts'])
    if do_combined_template:
        wgt = wgt*get_combined_template_wgt(tree, nfma['ma_edges'], nfma['wgts'])
        #print(wgt)
    if do_mini2aod:
        wgt = wgt*get_mini2aod_wgt(tree, nfmini2aod['ma_edges'], nfmini2aod['pt_edges'], nfmini2aod['wgts'])
    if 'Run20' in sample and not tree.isData:
        wgt = wgt*sginj_wgt
    if systPhoIdSF is not None and not tree.isData:
        wgtSF = get_sftot(tree, hsf, systPhoIdSF)
        wgt = wgt*wgtSF
    if do_pu_rwgt and not tree.isData:
        wgtPU = get_puwgt(tree, hpu)
        wgt = wgt*wgtPU

    #if nWrite > 10:break
    # Fill histograms with appropriate weight
    #fill_hists(hists, tree, wgt)
    fill_hists(hists, tree, wgt, wgtPU, wgtSF, systScale, systSmear)

    if write_pts:
        #evtId = '%f:%f'%(tree.phoEt[0], tree.phoEt[1])
        evtId = '%f:%f:%f:%f:%f'%(tree.phoEt[0], tree.phoEt[1], tree.phoIDMVA[0], tree.phoIDMVA[1], tree.mgg)
        evtlist_f.write('%s\n'%evtId)

    nWrite += 1

sw.Stop()
print(">> N events written: %d / %d"%(nWrite, iEvtEnd-iEvtStart))
print(">> Real time:",sw.RealTime()/60.,"minutes")
print(">> CPU time: ",sw.CpuTime() /60.,"minutes")

if norm is not None:
    print('Renormalizing to:',norm)
    norm_hists(hists, norm)

print('h[ma0vma1].GetEntries():',hists['ma0vma1'].GetEntries())
print('h[ma0vma1].Integral():',hists['ma0vma1'].Integral())
#print('h[maxy].GetEntries():',hists['maxy'].GetEntries())
#print('h[maxy].Integral():',hists['maxy'].Integral())

# Initialize output ntuple
write_hists(hists, "%s/%s_%s_blind_%s_templates.root"%(outdir, sample, region, blind))
write_cut_hists(cut_hists, "%s/%s_%s_cut_hists.root"%(outdir, sample, region))

# Print cut flow summary
print_stats(counts, "%s/%s_%s_cut_stats.txt"%(outdir, sample, region))

if write_pts:
    evtlist_f.close()
