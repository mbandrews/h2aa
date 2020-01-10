from __future__ import print_function
from multiprocessing import Pool
import os, glob
import numpy as np
import subprocess
from data_utils import *
from get_bkg_norm import *
from plot_srvsb import plot_srvsb
from plot_srvsb_pt import plot_srvsb_pt

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

regions = ['sr', 'sb']

for sample in samples:

    # Rerun data with fixed normalization
    #blind = 'sg'
    #blind = None

    run_ptweights()
    #s = sample.replace('[','').replace(']','')
    #plot_srvsb_pt(s, blind=None, sb='sb')

    # Run template fitting
    #run_combined_template(derive_fit=True)
    #run_combined_template(derive_fit=False)
    #run_combined_template(derive_fit=True, do_pt_reweight=True)
    #run_combined_template(derive_fit=False, do_pt_reweight=True)

    '''
    # Derive normalization
    #norm = get_bkg_norm(blind='sg', sb='sbcombo')
    #norm = get_bkg_norm(blind='sg', sb='sb')
    #norm = 0.870115
    #norm = 0.888882
    #norm = get_bkg_norm(blind='sg', sb='sb', do_pt_reweight=True)
    norm = get_bkg_norm(blind='sg', sb='sbcombo', do_pt_reweight=True)

    # Rerun data with fixed normalization
    #blind = 'notgjet'
    #blind = 'notgg'
    #blind = 'sg'
    #blind = None
    #blind = 'diag_lo_hi'
    blind = 'offdiag_lo_hi' # for actual limit setting

    # Run both SB and SR to bkg processes
    ma_inputs = glob.glob('MAntuples/%s_mantuple.root'%sample)
    print('len(ma_inputs):',len(ma_inputs))
    assert len(ma_inputs) > 0
    s = sample.replace('[','').replace(']','')
    do_combo_template = True
    #do_combo_template = False
    do_ptomGG = True
    do_pt_reweight = True
    #r = 'sb2sr'
    regions = ['sb2sr', 'sr']
    #regions = ['sb2sr']
    #processes = [bkg_process(s, r, blind, ma_inputs, output_dir, do_combo_template, norm) for r in regions]
    processes = [bkg_process(s, r, blind, ma_inputs, output_dir,\
            do_combo_template if 'sb' in r else False,\
            1. if r == 'sr' else norm,\
            do_ptomGG=do_ptomGG,\
            do_pt_reweight=do_pt_reweight) for r in regions]

    # Run processes in parallel
    pool = Pool(processes=len(processes))
    pool.map(run_process, processes)
    pool.close()
    pool.join()

    plot_srvsb(s, blind)
    #plot_srvsb_pt(s, blind, sb='sb2sr')
    '''

    '''
    # Run bkg model in SR
    blind = 'offdiag_lo_hi'

    ma_inputs = glob.glob('MAntuples/%s_mantuple.root'%sample)
    print('len(ma_inputs):',len(ma_inputs))
    assert len(ma_inputs) > 0
    s = sample.replace('[','').replace(']','')
    do_combo_template = True
    #do_combo_template = False
    regions = ['sb2sr']
    processes = [bkg_process(s, r, blind, ma_inputs, output_dir, do_combo_template, norm) for r in regions]

    # Run processes in parallel
    pool = Pool(processes=len(processes))
    pool.map(run_process, processes)
    pool.close()
    pool.join()
    '''
