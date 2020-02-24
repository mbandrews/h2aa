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

    '''
    do_pt_reweight = True
    do_ptomGG = False
    #do_ptomGG = True
    # `do_ptomGG` swtich applies to sb only
    run_ptweights(do_ptomGG=do_ptomGG)
    #s = sample.replace('[','').replace(']','')
    #plot_srvsb_pt(s, blind=None, sb='sb')

    #derive_fit = True
    derive_fit = False
    frac = {}
    frac['gg'], frac['sblo2sr'], frac['sbhi2sr'] = run_combined_sbfit(derive_fit=derive_fit, do_pt_reweight=do_pt_reweight, do_ptomGG=do_ptomGG)
    '''

    '''
    norm = {}
    run_bkg = False
    #run_bkg = True
    norm['sblo2sr'] = get_bkg_norm_sb(sb='sblo', do_pt_reweight=do_pt_reweight, do_ptomGG=do_ptomGG, run_bkg=run_bkg)
    norm['sbhi2sr'] = get_bkg_norm_sb(sb='sbhi', do_pt_reweight=do_pt_reweight, do_ptomGG=do_ptomGG, run_bkg=run_bkg)
    print(frac['sblo2sr'], norm['sblo2sr'])
    print(frac['sbhi2sr'], norm['sbhi2sr'])
    '''

    # OLD BKG MODELING
    # Run template fitting
    #run_combined_template(derive_fit=True, do_pt_reweight=True)
    #run_combined_template(derive_fit=False, do_pt_reweight=True, do_ptomGG=False) # `do_ptomGG` swtich applies to sb only

    # Derive normalization
    #norm = get_bkg_norm(blind='sg', sb='sb', do_pt_reweight=True)
    #norm = get_bkg_norm(blind='sg', sb='sbcombo', do_pt_reweight=True, do_ptomGG=False) # `do_ptomGG` swtich applies to sb only
    #norm = get_bkg_norm(blind='sg', sb='sblohi', do_pt_reweight=True, do_ptomGG=False) # `do_ptomGG` swtich applies to sb only
    #'''

    # Rerun data with fixed normalization
    #blind = 'notgjet'
    #blind = 'notgg'
    #blind = 'sg'
    #blind = None
    #blind = 'diag_lo_hi'
    blind = 'offdiag_lo_hi' # for actual limit setting

    '''
    # Run both SB and SR to bkg processes
    ma_inputs = glob.glob('MAntuples/%s_mantuple.root'%sample)
    print('len(ma_inputs):',len(ma_inputs))
    assert len(ma_inputs) > 0
    s = sample.replace('[','').replace(']','')
    #regions = ['sb2sr', 'sr']
    regions = ['sblo2sr', 'sbhi2sr', 'sr']
    #regions = ['sblo2sr', 'sbhi2sr']
    processes = [bkg_process(s, r, blind, ma_inputs, output_dir,\
            #do_combo_template=True if 'sb' in r else False,\
            norm=norm[r]*frac[r] if 'sb' in r else 1.,\
            do_ptomGG=do_ptomGG if 'sb' in r else True,\
            do_pt_reweight=do_pt_reweight if 'sb' in r else False\
            ) for r in regions]

    # Run processes in parallel
    #pool = Pool(processes=len(processes))
    #pool.map(run_process, processes)
    #pool.close()
    #pool.join()
    '''

    s = sample.replace('[','').replace(']','')
    plot_srvsb_sb(s, blind)
    #plot_srvsb(s, blind)
    #plot_srvsb_pt(s, blind)#, sb='sb2sr')
    #'''
