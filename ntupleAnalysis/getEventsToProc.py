from __future__ import print_function
import os
import sys
import numpy as np
import argparse
import ROOT

# Register command line options
parser = argparse.ArgumentParser(description='Run STEALTH selection.')
parser.add_argument('-i', '--infiles', default=['test.root'], nargs='+', type=str, help='Input root files.')
parser.add_argument('-o', '--outdir', default='evtsToProc', type=str, help='Output directory.')
parser.add_argument('-s', '--sample', default='test', type=str, help='Sample name.')
parser.add_argument('-t', '--treename', default='', type=str, help='TTree name prefix.')
args = parser.parse_args()

# Load input TTrees into TChain
tree = ROOT.TChain('ggNtuplizer/EventTree')
print('N input files:',len(args.infiles))
print('Input file[0]:',args.infiles[0])
for f_in in args.infiles:
    tree.Add(f_in)
nEvts = tree.GetEntries()

#f = open("%s/%s_2photons_ggskim_event_list.txt"%(args.outdir, args.sample),"w+")
f = open("%s/%s_3photons_ggskim_event_list.txt"%(args.outdir, args.sample),"w+")

# Event range to process
iEvtStart = 0
iEvtEnd   = nEvts
#iEvtEnd   = 10000
print(">> Processing entries: [",iEvtStart,"->",iEvtEnd,")")

nWrite = 0
sw = ROOT.TStopwatch()
sw.Start()
for iEvt in range(iEvtStart,iEvtEnd):

    # Initialize event
    tree.GetEntry(iEvt)

    if iEvt%100e3 == 0: print(iEvt,'/',(iEvtEnd-iEvtStart))

    # Event ID
    eventId = '%d:%d:%d'%(tree.run, tree.lumis, tree.event)
    #print(eventId)

    # Filter mGG
    #if tree.mGG < 100. or tree.mGG > 180.: continue

    #print(tree.phoSeedPos1_z, tree.phoSeedPos1_row, tree.phoSeedPos1_col) # z,ieta,iphi
    #print(tree.phoSeedPos2_z, tree.phoSeedPos2_row, tree.phoSeedPos2_col) # z,ieta,iphi

    # Only keep events with barrel photons
    #if tree.phoSeedPos1_z != 0. or tree.phoSeedPos2_z != 0.: continue

    # Only keep events with photons within ieta image window
    #if tree.phoSeedPos1_row < 15 or tree.phoSeedPos1_row+16 > 169: continue
    #if tree.phoSeedPos2_row < 15 or tree.phoSeedPos2_row+16 > 169: continue

    f.write('%s\n'%eventId)
    nWrite += 1

sw.Stop()
print(">> N events written: %d / %d"%(nWrite, nEvts))
print(">> Real time:",sw.RealTime()/60.,"minutes")
print(">> CPU time: ",sw.CpuTime() /60.,"minutes")
f.close()
