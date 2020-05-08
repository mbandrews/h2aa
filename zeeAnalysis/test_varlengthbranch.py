from __future__ import print_function
from collections import OrderedDict
import numpy as np
np.random.seed(0)
import os, glob
import time
import argparse
from array import array
#from get_bkg_norm import *

import ROOT

# Register command line options
parser = argparse.ArgumentParser(description='Run h24g selection.')
parser.add_argument('-s', '--sample', default='test', type=str, help='Sample name.')
parser.add_argument('-o', '--outdir', default='.', type=str, help='Output directory.')
args = parser.parse_args()

sample = args.sample
outdir = args.outdir

file_out = ROOT.TFile("%s/%s_varlength.root"%(outdir, sample), "RECREATE")
tree_out = ROOT.TTree("test", "test")

Nmax = 10
nParticles = array( 'i', [ 0 ] )
pt = array( 'd', Nmax*[ 0. ] )
tree_out.Branch( 'nParticles', nParticles, 'nParticles/I' )
tree_out.Branch( 'pt', pt, 'pt[nParticles]/D' )

for i in range(10): # loop over events
    nParticles[0] = i+1
    for j in range(nParticles[0]): # loop over particles in this event
       pt[j] = j
    tree_out.Fill()

file_out.Write()
file_out.Close()

tree_in = ROOT.TChain('test')
tree_in.Add('test_varlength.root')
nEvts = tree_in.GetEntries()

for i in range(nEvts):
   tree_in.GetEntry(i)
   print(i, len(tree_in.pt))
