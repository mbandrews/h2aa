from __future__ import print_function
from collections import OrderedDict
import os
import sys
import numpy as np
import argparse
import ROOT
from hist_utils import *
from evt_analyzers import *
#from get_bkg_norm import *

# Register command line options
parser = argparse.ArgumentParser(description='Run STEALTH selection.')
parser.add_argument('-i', '--infiles', default=['test.root'], nargs='+', type=str, help='Input root files.')
parser.add_argument('-o', '--outdir', default='PU', type=str, help='Output directory.')
parser.add_argument('-s', '--sample', default='test', type=str, help='Sample name.')
args = parser.parse_args()

# Load input TTrees into TChain
tree = ROOT.TChain('ggNtuplizer/EventTree')
print('N input files:',len(args.infiles))
print('Input file[0]:',args.infiles[0])
for f_in in args.infiles:
    tree.Add(f_in)
nEvts = tree.GetEntries()

# Event range to process
iEvtStart = 0
iEvtEnd   = nEvts
#iEvtEnd   = 10000
print(">> Processing entries: [",iEvtStart,"->",iEvtEnd,")")

#cuts = [str(None), 'ptomGG', 'chgiso', 'bdt']
cuts = [str(None), 'ptomGG', 'bdt', 'chgiso']
cut_hists = OrderedDict()
create_cut_hists(cut_hists, cuts)
counts = OrderedDict([(cut, 0) for cut in cuts])

hpu = {}
year = str(2017)
sample = args.sample

fpuin = ROOT.TFile("PU/dataPU_%s.root"%(year), "READ")
hpu['data'] = fpuin.Get('pileup')
hpu['data'].SetName('pu_data')
#print(hpu['data'].GetEntries())

hpu['mc'] = hpu['data'].Clone()
hpu['mc'].SetName('pu_mc')
hpu['mc'].Reset()

#already set for input hist
#for k in hpu:
#    hpu[k].Sumw2()


'''
hpu['mcrwgt'] = hpu['data'].Clone()
hpu['mcrwgt'].SetName('pu_mcrwgt')
hpu['mcrwgt'].Reset()

fpuwgts = ROOT.TFile('PU/puwgts_run%so%s_.root'%(year, sample), "READ")
hpu['wgts'] = fpuwgts.Get('pu_ratio')
hpu['wgts'].SetName('pu_wgts')

fsfin = ROOT.TFile("SF/SF%s_egammaEffi.txt_EGM2D.root"%(year), "READ")
hsf = fsfin.Get('EGamma_SF2D')
def get_sf(tree, preselIdx, h, shift='nom'):

    pt = tree.phoEt[preselIdx]
    sceta = tree.phoSCEta[preselIdx]

    ieta = h.GetXaxis().FindBin(sceta)
    ipt = h.GetYaxis().FindBin(pt)
    sf = h.GetBinContent(ieta, ipt)
    sf = sf if sf > 0. else 1.

    if shift == 'nom':
        sf = sf
    elif shift == 'up':
       sf += h.GetBinError(ieta, ipt)
    elif shift == 'dn':
       sf -= h.GetBinError(ieta, ipt)
    else:
       raise Exception('unknown syst shift: %s'%shift)

    #print(preselIdx, pt, sceta, sf)
    return sf

def get_sftot(tree, h, shift='nom'):
    sftot = 1.
    for idx in tree.phoPreselIdxs:
        sftot *= get_sf(tree, idx, hsf, shift)
    return sftot

def get_puwgt(tree, h):

    bx = np.array(tree.puBX)
    pu = np.array(tree.puTrue)
    ibx0 = np.argwhere(bx == 0)

    ib = h.GetXaxis().FindBin(pu[ibx0])
    wgt = h.GetBinContent(ib)
    return wgt
'''

nWrite = 0
sw = ROOT.TStopwatch()
sw.Start()
for iEvt in range(iEvtStart,iEvtEnd):

    # Initialize event
    tree.GetEntry(iEvt)

    if iEvt%100e3 == 0: print(iEvt,'/',(iEvtEnd-iEvtStart))

    if not select_event(tree, cuts, cut_hists, counts, outvars={}): continue

    bx = np.array(tree.puBX)
    pu = np.array(tree.puTrue)
    ibx0 = np.argwhere(bx == 0)

    # Filter mGG
    #if tree.mGG < 100. or tree.mGG > 180.: continue
    hpu['mc'].Fill(pu[ibx0])

    '''
    hpu['mcrwgt'].Fill(pu[ibx0], get_puwgt(tree, hpu['wgts']))

    sftot = get_sftot(tree, hsf)
    print(sftot)
    for idx in tree.phoPreselIdxs:
        sf = get_sf(tree, idx, hsf)
        #sf = get_sf(tree, idx, hsf, 'dn')
        #sf = get_sf(tree, idx, hsf, 'up')
    '''

    nWrite += 1

sw.Stop()
print(">> N events written: %d / %d"%(nWrite, nEvts))
print(">> Real time:",sw.RealTime()/60.,"minutes")
print(">> CPU time: ",sw.CpuTime() /60.,"minutes")
print_stats(counts)

#for k in ['data', 'mc', 'mcrwgt']:
for k in hpu:
    hpu[k].Scale(1./hpu[k].Integral())

hpu['ratio'] = hpu['data'].Clone()
hpu['ratio'].SetName('pu_ratio')
hpu['ratio'].Divide(hpu['mc'])

fpuout = ROOT.TFile('%s/puwgts_Run%so%s.root'%(args.outdir, year, sample), "RECREATE")
for k in hpu:
    hpu[k].Write()
fpuout.Close()
