from __future__ import print_function
from multiprocessing import Pool
import os, glob
import numpy as np
import subprocess
from get_bkg_norm import *
from plot_srvsb import plot_srvsb
from collections import OrderedDict

samples = [
    '100MeV'
    ,'400MeV'
    ,'1GeV'
    ]
samples = ['h24gamma_1j_1M_%s'%s for s in samples]
#samples = ['Run2017[B-F]']
samples.append('Run2017[B-F]')

output_dir = 'Datacards'
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

hf_in = {}
h_in = {}
h_out = OrderedDict()

def shiftNomUpDn(h_, hname):

    h = h_.Clone()

    print(hname)
    if 'Up' in hname:
        for ib in range(h.GetNbinsX()+2):
            binc = h.GetBinContent(ib)
            h.SetBinContent(ib, binc + np.sqrt(binc))
    elif 'Down' in hname:
        for ib in range(h.GetNbinsX()+2):
            binc = h.GetBinContent(ib)
            h.SetBinContent(ib, binc - np.sqrt(binc))
    #elif 'Nom' in hname:
    else:
        pass
        #binsum = 0
        #for ib in range(h.GetNbinsX()+2):
        #    print(h.GetBinContent(ib))
        #    binsum += h.GetBinContent(ib)
        #print(binsum)
        print(h.GetEntries())
        print(h.Integral())
    #else:
    #    print(hname)
    #    raise Exception('Unknown shift: %s'%hname)

    h.SetName(hname)
    return h

def shiftNomUpDn_2d(h__, hname):

    h_ = h__.Clone()

    #print(h__.GetNbinsX(), h__.GetNbinsY())
    binc_flat = []
    for ix in range(h_.GetNbinsX()+2):
        for iy in range(h_.GetNbinsY()+2):
            if abs(ix - iy) > int(200/25): continue # 200MeV blinding / 25MeV bin widths -> 8 bins
            #if ix != iy: continue
            #print(h_.GetBin(ix, iy))
            binc_flat.append(h_.GetBinContent(ix, iy))

    nbins = len(binc_flat)
    h_flat = ROOT.TH1F(hname+'flat', hname+'flat', nbins+2, 0., nbins+2) # add 2 for under/over flow
    #print('nbins:',nbins)

    print(hname)
    for i in range(len(binc_flat)):
        ib = i + 1
        #print(ib)
        if 'Up' in hname:
            h_flat.SetBinContent(ib, binc_flat[i] + np.sqrt(binc_flat[i]))
        elif 'Down' in hname:
            h_flat.SetBinContent(ib, binc_flat[i] - np.sqrt(binc_flat[i]))
        else:
            h_flat.SetBinContent(ib, binc_flat[i])
        #else:
        #    print(hname)
        #    raise Exception('Unknown shift: %s'%hname)

    #print(h_flat.GetEntries())
    #print(h_flat.Integral())
    h_flat.SetName(hname)
    return h_flat

def get_hname(s, r):

    if 'h24gamma' in s:
        if 'MeV' in s:
            hname = '0p%sGeV'%s.split('_')[-1][0]
        else:
            hname = s.split('_')[-1]
        hname = 'h4g_%s'%hname
    elif 'Run2017' in s:
        if 'sb2sr' in r:
            hname = 'bkg'
        elif 'sr' in r:
            hname = 'data_obs'
        else:
            hname = None
    else:
        hname = None

    return hname

for s in samples:

    #key = 'ma1'
    #key = 'ma0'
    key = 'ma0vma1'
    #key = 'maxy'
    #r = 'sr'
    r = 'sb2sr' if 'Run2017' in s else 'sr'
    #blind = 'sg'
    #blind = None
    blind = 'offdiag_lo_hi'
    s = s.replace('[','').replace(']','')

    hf_in[s] = ROOT.TFile('Templates/%s_%s_blind_%s_templates.root'%(s, r, blind), "READ")
    #hf_in[s] = ROOT.TFile('Templates/no_bdt/%s_%s_blind_%s_templates.root'%(s, r, blind), "READ")
    h_in[s] = hf_in[s].Get(key)

    hname = get_hname(s, r)
    h_out[hname] = h_in[s].Clone()
    h_out[hname].SetName(hname)

    for shift in ['Nom', 'Up', 'Down']:
        hname_shift = '%s_alpha%s'%(hname, shift) if shift != 'Nom' else hname
        #print('shift: %s, hname: %s, hname_shift: %s'%(shift, hname, hname_shift))
        #h_out[hname_shift] = shiftNomUpDn(h_out[hname], hname_shift)
        h_out[hname_shift] = shiftNomUpDn_2d(h_in[s].Clone(), hname_shift) if key == 'ma0vma1' else shiftNomUpDn(h_in[s].Clone(), hname_shift)
        #print('storing in: %s'%hname_shift)

    if 'Run2017' in s:
        h_out['data_obs'] = h_out['bkg'].Clone()
        h_out['data_obs'].SetName('data_obs')

#hf_out = ROOT.TFile('Datacards/%s_hists.root'%hname.split('_')[0], "RECREATE")
hf_out = ROOT.TFile('Datacards/%s_hists.root'%'shape', "RECREATE")
print(h_out.keys())
for hname in h_out.keys():
    #h_out[hname].SetName(hname)
    h_out[hname].Write()
hf_out.Close()

# combine -M AsymptoticLimits realistic-counting-experiment.txt
