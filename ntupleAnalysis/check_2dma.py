from __future__ import print_function
import numpy as np
import ROOT
import os, glob
from get_bkg_norm import load_hists

def floor_hist(h):
    for ix in range(0,h.GetNbinsX()+1):
        for iy in range(0,h.GetNbinsY()+1):
            if h.GetBinContent(ix, iy) < 0.:
                h.SetBinContent(ix, iy, 0.)
    return h

h, hf = {}, {}

#samples = ['Run2017B-F', 'GluGluHToGG']
samples = ['GluGluHToGG']
#regions = ['sb', 'sr']
#regions = ['sblo', 'sbhi', 'sr']
regions = ['sr']
keys = ['ma0vma1']
load_hists(h, hf, samples, regions, keys, 'sg', 'Templates')

scale_num = 1.e3
h['gg'] = h['GluGluHToGG_sr_ma0vma1'].Clone()
#h['gg'].Scale(scale_num/h['gg'].Integral())
h['gg'] = floor_hist(h['gg'])

for ix in range(0,h['gg'].GetNbinsX()+1):
    for iy in range(0,h['gg'].GetNbinsY()+1):
        print(h['gg'].GetBinContent(ix, iy))
