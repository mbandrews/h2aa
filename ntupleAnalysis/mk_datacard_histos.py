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
    elif 'Nom':
        pass
    else:
        raise Exception('Unknown shift: %s'%hname)

    h.SetName(hname)
    return h

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

    #r = 'sr'
    r = 'sb2sr' if 'Run2017' in s else 'sr'
    #blind = 'sg'
    #blind = None
    blind = 'offdiag_lo_hi'
    s = s.replace('[','').replace(']','')

    hf_in[s] = ROOT.TFile('Templates/%s_%s_blind_%s_templates.root'%(s, r, blind), "READ")
    h_in[s] = hf_in[s].Get('maxy')

    hname = get_hname(s, r)
    h_out[hname] = h_in[s].Clone()
    h_out[hname].SetName(hname)

    for shift in ['Nom', 'Up', 'Down']:
        hname_shift = '%s_alpha%s'%(hname, shift) if shift != 'Nom' else hname
        h_out[hname_shift] = shiftNomUpDn(h_out[hname], hname_shift)

    if 'Run2017' in s:
        h_out['data_obs'] = h_out['bkg'].Clone()
        h_out['data_obs'].SetName('data_obs')

hf_out = ROOT.TFile('Datacards/%s_hists.root'%hname.split('_')[0], "RECREATE")
print(h_out.keys())
for hname in h_out.keys():
    #h_out[hname].SetName(hname)
    h_out[hname].Write()
hf_out.Close()

# combine -M AsymptoticLimits realistic-counting-experiment.txt
