from __future__ import print_function
from collections import OrderedDict
import os, re
import sys
import numpy as np
import argparse
import ROOT
from hist_utils import *
from selection_utils import *

# Register command line options
parser = argparse.ArgumentParser(description='Run STEALTH selection.')
parser.add_argument('-i', '--infiles', default=['test.root'], nargs='+', type=str, help='Input root files.')
parser.add_argument('--inlist', default=None, type=str, help='Input MA ntuple file list.')
parser.add_argument('-p', '--pu_data', default='PU/dataPU_2017.root', type=str, help='Input PU ref file.')
parser.add_argument('-o', '--outfile', default='PU/puwgts_dataomc.root', type=str, help='Output PU file.')
parser.add_argument('-s', '--sample', default='test', type=str, help='Sample name.')
args = parser.parse_args()

sample = args.sample
print('>> Doing sample:',sample)
year = re.findall('(201[6-8])', sample.split('-')[0])[0]
pu_data = args.pu_data
print('>> Input PU reference:',pu_data)
outfile = args.outfile
print('>> Output PU wgts file:',outfile)

# NOTE: the `cuts` list here *must* match the list in select_events.py when run by run_sg_selection.py
#cuts = [str(None), 'ptomGG', 'chgiso', 'bdt']
#cuts = [str(None), 'ptomGG', 'bdt', 'chgiso']
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

# Data pu created using pileupCalc: https://twiki.cern.ch/twiki/bin/viewauth/CMS/PileupJSONFileforData
# See e.g. https://github.com/tanmaymudholkar/STEALTH/blob/tanmay-devel/miscUtils/PUReweighting/makeDataPUDistributions.sh
# Output from Tanmay: https://github.com/tanmaymudholkar/STEALTH/tree/tanmay-devel/getMCSystematics/data
hpu = {}
fpuin = ROOT.TFile.Open(pu_data, "READ")
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

print(">> Processing entries: [",iEvtStart,"->",iEvtEnd,")")
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

#fpuout = ROOT.TFile('%s/puwgts_Run%so%s.root'%(args.outdir, year, sample), "RECREATE")
fpuout = ROOT.TFile.Open(outfile, "RECREATE")
for k in hpu:
    hpu[k].Write()
fpuout.Close()
