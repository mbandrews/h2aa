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
from data_utils import *
#from get_bkg_norm import *

import ROOT

# Register command line options
parser = argparse.ArgumentParser(description='Run h24g selection.')
parser.add_argument('-s', '--sample', default='test', type=str, help='Sample name.')
parser.add_argument('-i', '--inputs', default=None, nargs='+', type=str, help='Input MA ntuple.')
parser.add_argument('-b', '--eos_basedir', default='/store/group/lpcsusystealth/stealth2018Ntuples_with9413', type=str, help='Input EOS basedir.')
parser.add_argument('-t', '--treename', default='Data', type=str, help='MA TTree name prefix.')
parser.add_argument('-o', '--outdir', default='.', type=str, help='Output directory.')
args = parser.parse_args()

sample = args.sample
outdir = args.outdir
#inputs = args.inputs
eos_basedir = args.eos_basedir

cuts = [str(None), 'trg', 'npho', 'presel', 'mgg']
#cuts = [str(None), 'npho', 'presel', 'mgg']
hists = OrderedDict()
create_cut_hists(hists, cuts)
counts = OrderedDict([(cut, 0) for cut in cuts])

inputs = run_eosfind(eos_basedir, sample) if args.inputs is None else args.inputs
if 'lpcsusystealth' in sample:
    inputs = [f for f in inputs if ('ntuplizedOct2019' in f) and ('failed' not in f)]
print('N ggntuple input files:',len(inputs))
print('ggntuple file[0]:',inputs[0])
print('ggntuple file[-1]:',inputs[-1])
tree = ROOT.TChain('ggNtuplizer/EventTree')
for i,fh in enumerate(inputs):
    tree.Add(fh)
    #break
tree.SetBranchStatus('pfMET*', 0)
tree.SetBranchStatus('ele*', 0)
tree.SetBranchStatus('mu*', 0)
tree.SetBranchStatus('jet*', 0)
nEvts = tree.GetEntries()
print('N evts in ggntuples:',nEvts)
# Event range to process
iEvtStart = 0
iEvtEnd   = nEvts
#iEvtEnd   = 10000

file_out = ROOT.TFile("%s/%s_ggskim.root"%(outdir, sample), "RECREATE")
file_out.mkdir('ggNtuplizer')
file_out.cd('ggNtuplizer')
# Clone TTree structure of ggntuple
tree_out = tree.CloneTree(0)
#print(list(tree_out.GetListOfBranches()))

# Initialize branches for the m_as as single floats
# [PyROOT boilerplate for single float branches]
mgg = np.zeros(1, dtype='float32')
#phoPreselIdxs = np.zeros(2, dtype='float32')
phoPreselIdxs = np.zeros(2, dtype='int32')
tree_out.Branch('mgg', mgg, 'mgg/F')
#tree_out.Branch('phoPreselIdxs', phoPreselIdxs, 'phoPreselIdxs[2]/F')
tree_out.Branch('phoPreselIdxs', phoPreselIdxs, 'phoPreselIdxs[2]/I')

print(">> Processing entries: [",iEvtStart,"->",iEvtEnd,")")
nWrite = 0
sw = ROOT.TStopwatch()
sw.Start()
for iEvt in range(iEvtStart,iEvtEnd):

    # Initialize event
    if iEvt%100e3==0: print(iEvt,'/',iEvtEnd-iEvtStart)
    evt_statusf = tree.GetEntry(iEvt)
    if evt_statusf <= 0: continue

    #if tree.run != 297114: continue
    #if tree.lumis != 14: continue
    # Analyze event
    outvars = {}
    if not select_event(tree, cuts, hists, counts, outvars): continue

    mgg[0] = outvars['mgg']
    phoPreselIdxs[0] = outvars['phoPreselIdxs'][0]
    phoPreselIdxs[1] = outvars['phoPreselIdxs'][1]
    #leadIdx = outvars['phoPreselIdxs'][0]
    #subLeadIdx = outvars['phoPreselIdxs'][1]
    #print(tree.run, tree.lumis, tree.event)
    #print(leadIdx, subLeadIdx)
    #print(leadIdx, tree.phoEt[leadIdx], tree.phoEta[leadIdx], tree.phoPhi[leadIdx])
    #print(subLeadIdx, tree.phoEt[subLeadIdx], tree.phoEta[subLeadIdx], tree.phoPhi[subLeadIdx])
    tree_out.Fill()

    #if nWrite > 10:break
    nWrite += 1

sw.Stop()
print(">> N events written: %d / %d"%(nWrite, nEvts))
print(">> Real time:",sw.RealTime()/60.,"minutes")
print(">> CPU time: ",sw.CpuTime() /60.,"minutes")

# Write out ntuples
file_out.Write()
file_out.Close()
write_cut_hists(hists, "%s/%s_cut_hists.root"%(outdir, sample))

# Print cut flow summary
print_stats(counts, "%s/%s_cut_stats.txt"%(outdir, sample))
