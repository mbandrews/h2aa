from __future__ import print_function
import ROOT
from data_utils import *

eos_basedir = '/store/user/lpcsusystealth/stealth2018Ntuples_with10210'
samples = [
#    'DiPhotonJets'
    #'GJet_Pt20To40'
    #,'GJet_Pt40ToInf'
    #'QCD_Pt30To40'
    'QCD_Pt40ToInf',
    'GluGluHToGG'
    ]

for sample in samples:

    inputs = run_eosfind(eos_basedir, sample)
    if 'lpcsusystealth' in sample:
        inputs = [f for f in inputs if ('ntuplizedOct2019' in f) and ('failed' not in f)]
    print('N ggntuple input files:',len(inputs))
    print('ggntuple file[0]:',inputs[0])
    print('ggntuple file[-1]:',inputs[-1])
    tree = ROOT.TChain('ggNtuplizer/EventTree')
    for i,fh in enumerate(inputs):
        tree.Add(fh)
        #break
    nEvts = tree.GetEntries()
    print('N evts in tree:', nEvts)
    iEvtStart = 0
    iEvtEnd = nEvts
    #iEvtEnd = 10000

    print(">> Processing entries: [",iEvtStart,"->",iEvtEnd,")")
    nWrite = 0
    sumWeights = 0.
    sw = ROOT.TStopwatch()
    sw.Start()
    for iEvt in range(iEvtStart,iEvtEnd):

        # Initialize event
        if iEvt%100e3==0: print(iEvt,'/',iEvtEnd-iEvtStart)
        evt_statusf = tree.GetEntry(iEvt)
        if evt_statusf <= 0: continue

        sumWeights += tree.genWeight
        nWrite += 1

    sw.Stop()
    print(">> N events: %d / Sum weights: %f"%(nWrite, sumWeights))
    print(">> Real time:",sw.RealTime()/60.,"minutes")
    print(">> CPU time: ",sw.CpuTime() /60.,"minutes")
