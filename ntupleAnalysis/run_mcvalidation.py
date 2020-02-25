from __future__ import print_function
from multiprocessing import Pool
import os, glob
import numpy as np
import subprocess
from data_utils import *
from get_bkg_norm import *
from plot_srvsb import plot_srvsb
from plot_srvsb_pt import plot_srvsb_pt
from plot_srvsb_sb import plot_srvsb_sb
from plot_1dma import plot_1dma

#samples = [
#    'B'
#    ,'C'
#    ,'D'
#    ,'E'
#    ,'F'
#    ]
#samples = ['Run2017%s'%s for s in samples]
#samples = ['Run2017%s-MINIAOD'%s for s in samples]
samples = ['Run2017[B-F]']

#samples = [
#    '100MeV'
#    ,'400MeV'
#    ,'1GeV'
#    ]
#samples = ['h24gamma_1j_1M_%s'%s for s in samples]

#samples = [
#    'DiPhotonJets'
#    ,'GJet_Pt-20to40'
#    ,'GJet_Pt-40toInf'
#    ,'QCD_Pt-30to40'
#    ,'QCD_Pt-40toInf'
#    ,'GluGluHToGG'
#    ]

output_dir = 'Templates'
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

for sample in samples:

    do_pt_reweight = False
    do_ptomGG = False

    # Rerun data with fixed normalization
    blind = 'notgjet'
    #blind = 'notgg'
    #blind = 'sg'
    #blind = None
    #blind = 'diag_lo_hi'
    #blind = 'offdiag_lo_hi' # for actual limit setting

    #'''
    # Run both SB and SR to bkg processes
    ma_inputs = glob.glob('MAntuples/%s_mantuple.root'%sample)
    print('len(ma_inputs):',len(ma_inputs))
    assert len(ma_inputs) > 0
    s = sample.replace('[','').replace(']','')
    regions = ['sblo']
    #regions = ['all']
    processes = [bkg_process(s, r, blind, ma_inputs, output_dir,\
            #do_combo_template=True if 'sb' in r else False,\
            #norm=norm[r]*frac[r] if 'sb' in r else 1.,\
            do_ptomGG=do_ptomGG,\
            do_pt_reweight=False,\
            #nevts=100000\
            nevts=-1\
            ) for r in regions]

    # Run processes in parallel
    pool = Pool(processes=len(processes))
    pool.map(run_process, processes)
    pool.close()
    pool.join()
    #'''

    s = sample.replace('[','').replace(']','')
    plot_1dma(s, blind, regions)
    #plot_srvsb_sb(s, blind)
    #plot_srvsb(s, blind)
    #plot_srvsb_pt(s, blind)#, sb='sb2sr')
    #'''
