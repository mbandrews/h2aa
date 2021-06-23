from __future__ import print_function
from collections import OrderedDict
import numpy as np
np.random.seed(0)
import os, glob
import time
import argparse
from array import array
from hist_utils import *
from data_utils import *
from selection_utils import *

import ROOT

# Register command line options
parser = argparse.ArgumentParser(description='Skim ggntuples.')
parser.add_argument('-i', '--inlist', default='../ggNtuples/Era24Sep2020_v1/bg2017-dy_file_list.txt', type=str, help='Input list of ggntuples.')
parser.add_argument('-o', '--outdir', default='ggSkims', type=str, help='Output directory.')
args = parser.parse_args()

inlist = args.inlist
assert os.path.isfile(inlist)
print('Input list:',inlist)

outdir = args.outdir
if not os.path.isdir(outdir):
    os.makedirs(outdir)
print('Output dir:',outdir)

sample = inlist.split('/')[-1].split('_')[0]
print('Sample name:',sample)

#cuts = [str(None), 'trg', 'nele']
#cuts = [str(None), 'nele']
cuts = [str(None), 'nele', 'presel']
hists = OrderedDict()
create_cut_hists(hists, cuts)
counts = OrderedDict([(cut, 0) for cut in cuts])

inputs = open(args.inlist).readlines()
inputs = [f.strip('\n') for f in inputs]
print('N ggntuple input files:',len(inputs))
print('ggntuple file[0]:',inputs[0])
print('ggntuple file[-1]:',inputs[-1])
tree = ROOT.TChain('ggNtuplizer/EventTree')
for i,fh in enumerate(inputs):
    tree.Add(fh)
    #break
tree.SetBranchStatus('pfMET*', 0)
#tree.SetBranchStatus('ele*', 0)
tree.SetBranchStatus('mu*', 0)
tree.SetBranchStatus('jet*', 0)
nEvts = tree.GetEntries()
print('N evts in ggntuples:',nEvts)
# Event range to process
nEvts_ceil = 150000000
iEvtStart = 0
#iEvtEnd   = nEvts
iEvtEnd   = nEvts if nEvts < nEvts_ceil else nEvts_ceil
#iEvtEnd   = 1000

file_out = ROOT.TFile("%s/%s_ggskim.root"%(outdir, sample), "RECREATE")
file_out.mkdir('ggNtuplizer')
file_out.cd('ggNtuplizer')
# Clone TTree structure of ggntuple
tree_out = tree.CloneTree(0)
#print(list(tree_out.GetListOfBranches()))

# Evt list
evt_list = open("%s/%s_event_list.txt"%(outdir, sample),"w+")

print(">> Processing entries: [",iEvtStart,"->",iEvtEnd,")")
nWrite = 0
sw = ROOT.TStopwatch()
sw.Start()
for iEvt in range(iEvtStart,iEvtEnd):

    # Initialize event
    if iEvt%100e3==0: print(iEvt,'/',iEvtEnd-iEvtStart)
    evt_statusf = tree.GetEntry(iEvt)
    if evt_statusf <= 0: continue

    # Analyze event
    if not select_event(tree, cuts, hists, counts): continue

    tree_out.Fill()

    eventId = '%d:%d:%d'%(tree.run, tree.lumis, tree.event)
    evt_list.write('%s\n'%eventId)
    nWrite += 1

sw.Stop()
print(">> N events written: %d / %d"%(nWrite, iEvtEnd-iEvtStart))
print(">> Real time:",sw.RealTime()/60.,"minutes")
print(">> CPU time: ",sw.CpuTime() /60.,"minutes")

# Write out ntuples
file_out.Write()
file_out.Close()
write_cut_hists(hists, "%s/%s_cut_hists.root"%(outdir, sample))
evt_list.close()

# Print cut flow summary
print_stats(counts, "%s/%s_cut_stats.txt"%(outdir, sample))

if counts['None'] != (iEvtEnd-iEvtStart):
    print('!!! WARNING !!! Evt count mismatch !!! processed:%d vs. total:%d'%(counts['None'], (iEvtEnd-iEvtStart)))
