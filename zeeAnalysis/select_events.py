from __future__ import print_function
from collections import OrderedDict
import numpy as np
np.random.seed(0)
import os, glob
import time
import argparse
from array import array
from hist_utils import *
from selection_utils import *
from data_utils import *
#from get_bkg_norm import *

import ROOT

# Register command line options
parser = argparse.ArgumentParser(description='Run h24g selection.')
parser.add_argument('-s', '--sample', default='test', type=str, help='Sample name.')
#parser.add_argument('-i', '--inputs', default=None, nargs='+', type=str, help='Input MA ntuple.')
parser.add_argument('--inlist', default=None, type=str, help='Input MA ntuple file list.')
parser.add_argument('-o', '--outdir', default='Templates', type=str, help='Output directory.')
parser.add_argument('-n', '--norm', default=None, type=float, help='SB to SR normalization.')
parser.add_argument('-e', '--events', default=10000, type=int, help='Nevts to process.')
#parser.add_argument('--do_pt_reweight', action='store_true', help='Switch to apply probe pt re-weighting.')
#parser.add_argument('--pu_file', default=None, help='PU reweighting file if to be applied.')
parser.add_argument('--pu_json', default=None, help='PU reweighting file if to be applied. For data only.')
args = parser.parse_args()

sample = args.sample
outdir = args.outdir
#inputs = args.inputs
norm = args.norm
events = args.events

#do_pt_reweight = args.do_pt_reweight if 'Run' not in sample else False
#if do_pt_reweight:
#    print('Using pt weights')
#    #wgt_sample = 'DYToEE2Run2017B-F'
#    wgt_sample = 'DYToEE2Run2017'
#    wgt_file, pt_wgts, pt_edges = {}, {}, {}
#    for k in ['pt1corr', 'elePt1corr']:
#        wgt_file[k] = np.load("Weights/%s_%s_ptwgts.npz"%(wgt_sample, k))
#        pt_wgts[k] = wgt_file[k]['pt_wgts']
#        pt_edges[k] = wgt_file[k]['pt_edges']

#pu_file = args.pu_file
#do_pu_rwgt = False
#if pu_file is not None:
#    if 'data' not in sample:
#        do_pu_rwgt = True
#        print('>> Doing PU re-weighting: %s'%pu_file)
#        fpu = ROOT.TFile.Open(pu_file, "READ")
#        hpu = fpu.Get('pu_ratio')

puRange = None
pu_json = args.pu_json
do_pu_json = False
# for data: if PU json provided
# for MC: PU info taken from ggntuple directly
if pu_json is not None and 'data' in sample:
    do_pu_json = True
    puRange = parseInputFile(pu_json)#inputLumiJSON)

evtlist_f = open("%s/%s_selected_event_list.txt"%(outdir, sample), "w+")
fma = open("%s/%s_ma1.txt"%(outdir, sample), "w+")

# Template histograms
#hists = {}
hists = OrderedDict()
create_hists(hists)

# Cut flow histograms
#cuts = [str(None), 'trg', 'nele']
#cuts = [str(None), 'presel', 'tnp', 'mee']
#cuts = [str(None), 'presel', 'tnp', 'mee', 'ptomee'] # massreg paper
cuts = [str(None), 'presel', 'tnp', 'mee', 'ptomee', 'bdt', 'chgiso'] #h4g selection
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
iEvtEnd   = nEvts
#iEvtEnd   = 100
#iEvtEnd   = events if events < nEvts else nEvts

print(">> Processing entries: [",iEvtStart,"->",iEvtEnd,")")
nWrite = 0
sw = ROOT.TStopwatch()
sw.Start()
for iEvt in range(iEvtStart,iEvtEnd):

    # Initialize event
    if iEvt%100e3==0: print(iEvt,'/',iEvtEnd-iEvtStart)
    evt_statusf = tree.GetEntry(iEvt)
    if evt_statusf <= 0: continue

    # Apply event selection
    outvars = {}
    if not select_event(tree, cuts, cut_hists, counts, outvars): continue

    # Analyze event
    #if not analyze_event(tree, region, blind, do_ptomGG): continue

    # Get event weight
    wgt = 1. if tree.isData else tree.genWeight

    # Fill histograms with appropriate weight
    #if do_pt_reweight:
    #    fill_hists(hists, tree, wgt, outvars, pt_wgts, pt_edges, fma=fma, puRange=puRange)
    #else:
    #    fill_hists(hists, tree, wgt, outvars, fma=fma, puRange=puRange)
    fill_hists(hists, tree, wgt, outvars, fma=fma, puRange=puRange)

    probeIdxs = [str(idx) for idx in outvars['phoProbeIdxs']]
    evtId = '%d:%d:%d:%s'%(tree.run, tree.lumis, tree.event, str(','.join(probeIdxs)))
    evtlist_f.write('%s\n'%evtId)
    nWrite += 1
    #if nWrite > 1:break

sw.Stop()
print(">> N events written: %d / %d"%(nWrite, iEvtEnd-iEvtStart))
print(">> Real time:",sw.RealTime()/60.,"minutes")
print(">> CPU time: ",sw.CpuTime() /60.,"minutes")

if norm is not None:
    print('Renormalizing to:',norm)
    norm_hists(hists, norm)

#print('h[ma0vma1].GetEntries():',hists['ma0vma1'].GetEntries())
#print('h[ma0vma1].Integral():',hists['ma0vma1'].Integral())
#print('h[maxy].GetEntries():',hists['maxy'].GetEntries())
#print('h[maxy].Integral():',hists['maxy'].Integral())

# Write out ntuples
#if do_pt_reweight:
#    write_hists(hists, "%s/%s_rewgt_templates.root"%(outdir, sample))
#else:
#    write_hists(hists, "%s/%s_templates.root"%(outdir, sample))
write_hists(hists, "%s/%s_templates.root"%(outdir, sample))
write_cut_hists(cut_hists, "%s/%s_cut_hists.root"%(outdir, sample))

# Print cut flow summary
print_stats(counts, "%s/%s_cut_stats.txt"%(outdir, sample))

# Close event list file
evtlist_f.close()
fma.close()
