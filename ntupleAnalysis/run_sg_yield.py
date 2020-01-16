from __future__ import print_function
from multiprocessing import Pool
import os, glob
import numpy as np
import subprocess
from data_utils import *
from get_bkg_norm import *
from plot_srvsb import plot_srvsb

samples = [
    '100MeV'
    ,'400MeV'
    ,'1GeV'
    ]
samples = ['h24gamma_1j_1M_%s'%s for s in samples]

output_dir = 'Templates'
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

def get_sg_norm(sample, xsec=50., tgt_lumi=41.e3): # xsec:pb, tgt_lumi:/pb

    gg_cutflow = glob.glob('../ggSkims/%s_cut_hists.root'%sample)
    assert len(gg_cutflow) == 1

    cut = str(None)
    var = 'npho'
    key = cut+'_'+var
    hf = ROOT.TFile(gg_cutflow[0], "READ")
    h = hf.Get('%s/%s'%(cut, key))

    nevts_gen = h.GetEntries()
    #print(nevts_gen)
    norm = xsec*tgt_lumi/nevts_gen
    #print(norm)
    return norm

regions = ['sr']

for s in samples:

    #blind = 'sg'
    #blind = None
    blind = 'offdiag_lo_hi'

    # Do data
    ma_inputs = glob.glob('MAntuples/%s_mantuple.root'%s)
    print('len(ma_inputs):',len(ma_inputs))
    assert len(ma_inputs) > 0
    processes = []
    s = s.replace('[','').replace(']','')
    regions = ['sr']
    for r in regions:
        print('For region:',r)
        # Regress 2d ma off-diagonals in signal region (SR) and sideband (SB)
        pyargs = 'get_bkg_model.py -s %s -r %s -b %s -i %s -t %s -o %s --do_ptomGG'\
                %(s, r, blind, ' '.join(ma_inputs), get_ma_tree_name(s), output_dir)
        print('Doing: %s'%pyargs)
        processes.append(pyargs)
        #break
    pool = Pool(processes=len(processes))
    pool.map(run_process, processes)
    pool.close()
    pool.join()

    #norm = 41.e3 # /pb 2017 int lumi
    #norm = 41. # /fb 2017 int lumi
    #norm = norm
    # NOTE: `scale` here is needed to improve limit setting fits and needs to be undone when making plots!
    scale = 1.e-3
    norm = get_sg_norm(s)*scale

    # Rerun data with fixed normalization
    r = 'sr'
    pyargs = 'get_bkg_model.py -s %s -r %s -b %s -i %s -t %s -o %s -n %f --do_ptomGG'\
            %(s, r, blind, ' '.join(ma_inputs), get_ma_tree_name(s), output_dir, norm)
    print('Doing: %s'%pyargs)
    os.system('python %s'%pyargs)

    #plot_srvsb(s, blind)

