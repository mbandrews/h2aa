from __future__ import print_function
from collections import OrderedDict
import numpy as np
np.random.seed(0)
import os, re, glob
import time
import argparse
from hist_utils import *
from selection_utils import *
#from get_bkg_norm import *

import ROOT

# Register command line options
parser = argparse.ArgumentParser(description='Run h2aa bkg model.')
parser.add_argument('-s', '--sample', default='test', type=str, help='Sample name.')
parser.add_argument('-r', '--region', default='sb', type=str, help='mH-region: sr, sb, sblo, sbhi, all.')
parser.add_argument('-i', '--inputs', default=['MAntuples/Run2017F_mantuple.root'], nargs='+', type=str, help='Input MA ntuple.')
parser.add_argument('--inlist', default=None, type=str, help='Input MA ntuple file list.')
parser.add_argument('-o', '--outdir', default='Templates', type=str, help='Output directory.')
parser.add_argument('-w', '--wgtsdir', default='Weights', type=str, help='Weights output directory.')
parser.add_argument('-b', '--blind', default=None, type=str, help='Regions to blind.')
parser.add_argument('-n', '--norm', default=None, type=float, help='SB to SR normalization.')
parser.add_argument('-e', '--events', default=-1, type=int, help='Number of evts to process.')
parser.add_argument('--pt_rwgt', default=None, type=str, help='pt re-weighting file.')
parser.add_argument('--do_ptomGG', action='store_true', help='Switch to apply pt/mGG cuts.')
parser.add_argument('--write_pts', action='store_true', help='Write out photon pts.')
parser.add_argument('--systTrgSF', default=None, type=str, help='Syst, trigger SF: None, nom, up, dn.')
parser.add_argument('--systPhoIdSF', default=None, type=str, help='Syst, photon ID SF: None, nom, up, dn.')
parser.add_argument('--systPhoIdFile', default=None, type=str, help='Syst, photon ID input file.')
#parser.add_argument('--systScale', default=None, type=str, help='Syst, m_a energy scale: None, up, dn.')
#parser.add_argument('--systSmear', default=None, type=str, help='Syst, m_a energy smear: None, up, dn.')
parser.add_argument('--systScale', default=None, type=float, nargs=3, help='Syst, m_a energy scale: eta(cntr) eta(mid) eta(fwd)')
parser.add_argument('--systSmear', default=None, type=float, nargs=3, help='Syst, m_a energy smear: eta(cntr) eta(mid) eta(fwd)')
#parser.add_argument('--do_pu_rwgt', action='store_true', help='Apply PU reweighting')
parser.add_argument('--pu_file', default=None, help='PU reweighting file if to be applied.')
args = parser.parse_args()

ma_binw = 25. # MeV
diag_w = 200. # MeV
sample = args.sample
print('>> Doing sample:',sample)
year = re.findall('(201[6-8])', sample.split('-')[0])
year = year[0] if len(year) != 0 else None
print('>> Doing year:',year)
region = args.region
print('>> Doing mH-region:',region)
blind = args.blind
print('>> Blinding mA:',blind)
norm = args.norm
outdir = args.outdir
print('>> Will output templates to:',outdir)
#wgtsdir = args.wgtsdir
if 'h4g' in sample:
    # h4g2017-mA1p0GeV
    magen = float(sample.split('-')[-1].replace('GeV','').replace('mA','').replace('p','.'))
else:
    magen = None
print('>> mA,gen [GeV]:',str(magen))

do_ptomGG = args.do_ptomGG
#do_ptomGG = args.do_ptomGG if 'sb' not in region else False
if do_ptomGG:
    print('>> Using pt/mGG cuts')
else:
    assert region != 'sr'
    #assert do_pt_rwgt

write_pts = args.write_pts
if write_pts:
    #evtlist_f = open("Weights/%s_region_%s_blind_%s_selected_phoEt_list.txt"%(sample, region, blind), "w+")
    evtlist_f = open("%s/%s_region_%s_blind_%s_selected_phoEt_list.txt"%(outdir, sample, region, blind), "w+")

do_pt_rwgt = True if args.pt_rwgt is not None else False
if do_pt_rwgt:
    assert region != 'sr'
    print('>> Applying pt re-weighting:', args.pt_rwgt)
    fpt = ROOT.TFile.Open(args.pt_rwgt, "READ")
    hpt = fpt.Get('pt0vpt1_ratio')
    #nfpt = np.load("Weights/%s_%s_blind_%s_ptwgts.npz"%(s, r, None))
    #nfpt = np.load("%s/%s_%s_blind_%s_ptwgts.npz"%(wgtsdir, s, r, None))

pu_file = args.pu_file
do_pu_rwgt = False
if pu_file is not None:
    if 'data' not in sample:
        do_pu_rwgt = True
        print('>> Doing PU re-weighting: %s'%pu_file)
        fpu = ROOT.TFile.Open(pu_file, "READ")
        hpu = fpu.Get('pu_ratio')

#do_pu_rwgt = args.do_pu_rwgt
#if 'data' in sample: assert do_pu_rwgt is False
#if do_pu_rwgt:
#    print('Doing PU re-weighting')
#    year = str(2017)
#    fpu = ROOT.TFile('PU/puwgts_Run%so%s.root'%(year, sample), "READ")
#    hpu = fpu.Get('pu_ratio')

systPhoIdSF = args.systPhoIdSF
systPhoIdFile = args.systPhoIdFile
if 'data' in sample: assert systPhoIdSF is None
if systPhoIdSF is not None:
    assert systPhoIdFile is not None, '!! Pho ID syst is %s but no syst file found!'%systPhoIdSF
    print('>> Doing syst: photon ID SF shift:',systPhoIdSF)
    print('   .. syst input file: %s'%systPhoIdFile)
    fsf = ROOT.TFile(systPhoIdFile, "READ")
    hsf = fsf.Get('EGamma_SF2D')

systTrgSF = args.systTrgSF
if 'data' in sample: assert systTrgSF is None
print('>> Doing syst: trg SF shift:',systTrgSF)

systScale = args.systScale
if 'data' in sample: assert systScale is None
print('>> Doing syst: energy scale shift:',systScale)

systSmear = args.systSmear
if 'data' in sample: assert systSmear is None
print('>> Doing syst: energy smear shift:',systSmear)

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
#cuts = [str(None), 'ptomGG', 'bdt', 'chgiso'] if do_ptomGG else [str(None), 'bdt', 'chgiso']
#cuts = [str(None), 'bdt', 'chgiso']
cuts = [str(None), 'bdt', 'chgiso', 'phoEta']
cut_hists = OrderedDict()
create_cut_hists(cut_hists, cuts)
counts = OrderedDict([(cut, 0) for cut in cuts])

print('>> Reading input maNtuples...')
if args.inlist is not None:
    inlist = args.inlist
    print('   .. input list file provided: %s'%inlist)
    assert os.path.isfile(inlist), '   !! input maNtuple list not found!'
    inputs = open(inlist).readlines()
    inputs = [f.strip('\n') for f in inputs]
else:
    inputs = args.inputs
print('   .. Nfiles:',len(inputs))
#print('   .. [ 0]:',inputs[0])
#print('   .. [-1]:',inputs[-1])
tree = ROOT.TChain('ggNtuplizer/EventTree')
for i,fh in enumerate(inputs):
    tree.Add(fh)
    print('   .. adding file: %s'%fh)
    #if i > 10: break
nEvts = tree.GetEntries()
print('   .. Nevts: %d'%nEvts)
# Event range to process
iEvtStart = 0
iEvtEnd   = nEvts if args.events == -1 else args.events
#iEvtEnd   = 100

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
    if not select_event(tree, cuts, cut_hists, counts, outvars, year): continue

    # Analyze event
    if not analyze_event(tree, region, blind, do_ptomGG): continue

    # Get event weight
    #wgt = 1. if 'Data' in args.treename else tree.weight
    wgt = 1. if tree.isData else tree.genWeight
    #wgtPt, wgtSF, wgtPU = 1., 1., 1.
    wgtPt, wgtTrgSF, wgtSF, wgtPU = 1., 1., 1., 1.
    if do_pt_rwgt:
        wgtPt = get_ptwgt(tree, hpt)
        wgt = wgt*wgtPt
    #if 'Run20' in sample and not tree.isData:
    if 'data' in sample and not tree.isData:
        wgt = wgt*sginj_wgt
    if systTrgSF is not None and not tree.isData:
        wgtTrgSF = get_trgSFtot(tree, year, systTrgSF)
        wgt = wgt*wgtTrgSF
    if systPhoIdSF is not None and not tree.isData:
        wgtSF = get_sftot(tree, hsf, systPhoIdSF)
        wgt = wgt*wgtSF
    if do_pu_rwgt and not tree.isData:
        wgtPU = get_puwgt(tree, hpu)
        wgt = wgt*wgtPU

    # Fill histograms with appropriate weight
    #fill_hists(hists, tree, wgt, wgtPt, wgtPU, wgtSF, systScale, systSmear, magen)
    fill_hists(hists, tree, wgt, wgtPt, wgtPU, wgtSF, wgtTrgSF, systScale, systSmear, magen)

    if write_pts:
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

# Initialize output ntuple
write_hists(hists, "%s/%s_%s_blind_%s_templates.root"%(outdir, sample, region, blind))
write_cut_hists(cut_hists, "%s/%s_%s_cut_hists.root"%(outdir, sample, region))

# Print cut flow summary
print_stats(counts, "%s/%s_%s_cut_stats.txt"%(outdir, sample, region))

if write_pts:
    evtlist_f.close()

if counts['None'] != (iEvtEnd-iEvtStart):
        print('!!! WARNING !!! Evt count mismatch !!! processed:%d vs. total:%d'%(counts['None'], (iEvtEnd-iEvtStart)))
