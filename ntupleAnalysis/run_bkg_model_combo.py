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

def normalize_fracs(frac):

    frac_tot = sum(frac[k] for k in frac.keys())
    for k in frac.keys():
        frac[k] = frac[k]/frac_tot

    return frac

def normalize_fracs_byhgg(frac):

    frac_tot = sum(frac[k] for k in frac.keys())
    frac_diff = 1. - frac_tot

    fsblo_sb = frac['sblo2sr']/(frac['sblo2sr']+frac['sbhi2sr'])
    fsbhi_sb = frac['sbhi2sr']/(frac['sblo2sr']+frac['sbhi2sr'])

    frac['sblo2sr'] = frac['sblo2sr'] + fsblo_sb*frac_diff
    frac['sbhi2sr'] = frac['sbhi2sr'] + fsbhi_sb*frac_diff

    return frac

for sample in samples:

    do_pt_reweight = True
    #do_pt_reweight = False
    do_ptomGG = False
    #do_ptomGG = True
    # `do_ptomGG` swtich applies to sb only
    run_ptweights(do_ptomGG=do_ptomGG)
    #s = sample.replace('[','').replace(']','')
    #plot_srvsb_pt(s, blind=None, sb='sb')

    #'''
    norm_blind = 'sg'
    #norm_blind = 'diag_lo_hi'
    derive_fit = True
    #derive_fit = False
    frac = {}
    frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = run_combined_sbfit(derive_fit=derive_fit, do_pt_reweight=do_pt_reweight, do_ptomGG=do_ptomGG, blind=norm_blind)
    if not derive_fit:
        pass
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 0.0304458196811, 0.491386002466, 0.47816547587 # 2pho, nobdt
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 3.60406e-02, 4.97720e-01, 4.66204e-01 # 2pho, bdt>-0.98
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 3.51963e-02, 4.95205e-01, 4.69576e-01 # 3pho, bdt>-0.98
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 3.10294e-02, 4.90150e-01, 4.78847e-01 # 3pho, nobdt
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 1.e-02, 4.90150e-01, 4.78847e-01 # TEST, 3pho, nobdt
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 6.07102e-03, 5.08034e-01, 4.85880e-01 # scale_num=1.e3, 3pho, nobdt
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 6.06678e-03, 5.08018e-01, 4.85915e-01 # scale_num=1.e3, 3pho, nobdt, run2
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 7.74656e-03, 5.08153e-01, 4.84109e-01 # scale_num=1.e3, 3pho, nobdt, 400MeV@BRx1.e-2
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 7.74743e-03, 5.08152e-01, 4.84110e-01 # scale_num=1.e3, 3pho, nobdt, 400MeV@BRx0.
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 5.80278e-03, 5.47802e-01, 4.46405e-01 # scale_num=1.e3, 3pho, nobdt, chgiso<3
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 5.47038e-03, 5.60021e-01, 4.34507e-01 # scale_num=1.e3, 3pho, nobdt, chgiso<2
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 7.95171e-03, 5.38586e-01, 4.53448e-01 # scale_num=1.e3, 3pho, nobdt, chgiso<4
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 8.27412e-03, 5.45171e-01, 4.46564e-01 # scale_num=1.e3, 3pho, nobdt, relchgiso<0.05
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 9.43533e-03, 5.51212e-01, 4.39349e-01 # scale_num=1.e3, 3pho, nobdt, relchgiso<0.04
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 9.28751e-03, 5.46645e-01, 4.44074e-01 # scale_num=1.e3, 3pho, nobdt, relchgiso<0.045
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 1.05010e-02, 5.59225e-01, 4.30274e-01 # scale_num=1.e3, 3pho, bdt>-0.99, relchgiso<0.05
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 8.45170e-03, 5.45209e-01, 4.46332e-01 # scale_num=1.e3, 3pho, bdt>-0.999, relchgiso<0.05
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 1.28215e-02, 5.69404e-01, 4.17747e-01 # scale_num=1.e3, 3pho, bdt>-0.98, relchgiso<0.05
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 2.49387e-02, 6.42636e-01, 3.32428e-01 # scale_num=1.e3, 3pho, bdt>-0.98, relchgiso<0.05, norm_blind = diag_lo_hi
        #----AOD
        frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 3.68826e-03, 7.43592e-01, 2.52719e-01 # scale_num=5.e3, 3pho, bdt>-0.98, relchgiso<0.05
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 6.06340e-02, 5.43426e-01, 3.95941e-01 # scale_num=1.e3, 3pho, bdt>-0.98, relchgiso<0.05
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 2.09568e-02, 8.74201e-01, 1.04860e-01 # scale_num=5.e3, 3pho, bdt>-0.98, relchgiso<0.05, norm_blind = diag_lo_hi
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 1.09738e-01, 5.86114e-01, 3.04182e-01 # scale_num=1.e3, 3pho, bdt>-0.98, relchgiso<0.05, norm_blind = diag_lo_hi
        #----
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 1.62840e-02, 5.66072e-01, 4.17630e-01 # scale_num=1.e3, 3pho, bdt>-0.98, relchgiso<0.05, mA100MeV@BRx1.e-2
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 6.27249e-03, 5.71591e-01, 4.22125e-01 # scale_num=1.e3, 3pho, bdt>-0.98, relchgiso<0.05, mA400MeV@BRx1.e-2
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 1.06912e-02, 5.69350e-01, 4.19974e-01 # scale_num=1.e3, 3pho, bdt>-0.98, relchgiso<0.05, mA1GeV@BRx1.e-2
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 1.50632e-10, 5.72059e-01, 4.27947e-01 # scale_num=1.e3, 3pho, bdt>-0.98, relchgiso<0.05, mA1GeV@BRx1.e-1
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 6.95173e-11, 5.72757e-01, 4.27246e-01 # scale_num=1.e3, 3pho, bdt>-0.98, relchgiso<0.05, mA400MeV@BRx1.e-1
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 4.06724e-02, 5.49263e-01, 4.10066e-01 # scale_num=1.e3, 3pho, bdt>-0.98, relchgiso<0.05, mA100MeV@BRx1.e-1
        #----
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 1.47295e-02, 5.67245e-01, 4.18008e-01 # scale_num=1.e3, 3pho, bdt>-0.98, relchgiso<0.05, mA100MeV@BRx3sg
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 1.57052e-02, 5.66435e-01, 4.17846e-01 # scale_num=1.e3, 3pho, bdt>-0.98, relchgiso<0.05, mA100MeV@BRx5sg
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 1.20432e-02, 5.69286e-01, 4.18660e-01 # scale_num=1.e3, 3pho, bdt>-0.98, relchgiso<0.05, mA400MeV@BRx3sg
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 1.13491e-02, 5.69590e-01, 4.19074e-01 # scale_num=1.e3, 3pho, bdt>-0.98, relchgiso<0.05, mA400MeV@BRx5sg
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 1.23998e-02, 5.68782e-01, 4.18801e-01 # scale_num=1.e3, 3pho, bdt>-0.98, relchgiso<0.05, mA1GeV@BRx3sg
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 1.18823e-02, 5.68999e-01, 4.19118e-01 # scale_num=1.e3, 3pho, bdt>-0.98, relchgiso<0.05, mA1GeV@BRx5sg
        #----
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 1.56347e-03, 1.56347e-03, 3.35616e-01 # a0: inv, a1: inv
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 8.36973e-03, 6.58834e-01, 3.32224e-01 # a0: inv, a1: nom
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 1.11395e-02, 5.58782e-01, 4.30080e-01 # a0: nom, a1: inv
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 8.91068e-03, 5.42051e-01, 4.49043e-01 # 1xinv
        #--fixed norm
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 1.11395e-02, 5.58782e-01, 4.30080e-01 # a0: nom, a1: inv
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 1.56347e-03, 6.62815e-01, 3.35616e-01 # a0: inv, a1: inv
        #--aod scale_num=5.e3
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 1.52607e-03, 7.45480e-01, 2.52995e-01 # a0: nom, a1: inv, with pt/mGG
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 7.47749e-03, 7.24466e-01, 2.68056e-01 # a0: nom, a1: inv
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] =  # a0: inv, a1: inv
        #----
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 5.42048e-02, 5.46852e-01, 3.98950e-01 # nom, bdt>-0.98, relchgiso < 0.05
        #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 7.17730e-02, 6.12411e-01, 3.15820e-01 # diaglohi nom, bdt>-0.98, relchgiso < 0.05

    frac = normalize_fracs(frac)
    #frac = normalize_fracs_byhgg(frac)
    print(frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'])

    norm = {}
    run_bkg = False
    #run_bkg = True
    norm['sblo2sr'] = get_bkg_norm_sb(blind=norm_blind, sb='sblo', do_pt_reweight=do_pt_reweight, do_ptomGG=do_ptomGG, run_bkg=run_bkg)
    norm['sbhi2sr'] = get_bkg_norm_sb(blind=norm_blind, sb='sbhi', do_pt_reweight=do_pt_reweight, do_ptomGG=do_ptomGG, run_bkg=run_bkg)
    norm['hgg2sr'] = get_bkg_norm_sb(blind=norm_blind, sb='sr', sample='GluGluHToGG', do_pt_reweight=False, do_ptomGG=True, run_bkg=run_bkg)
    print(frac['sblo2sr'], norm['sblo2sr'])
    print(frac['sbhi2sr'], norm['sbhi2sr'])
    print(frac['hgg2sr'], norm['hgg2sr'])

    # Rerun data with fixed normalization
    #blind = 'notgjet'
    #blind = 'notgg'
    blind = 'sg'
    #blind = None
    #blind = 'diag_lo_hi'
    #blind = 'offdiag_lo_hi' # for actual limit setting

    # Run both SB and SR to bkg processes
    ma_inputs = glob.glob('MAntuples/%s_mantuple.root'%sample)
    print('len(ma_inputs):',len(ma_inputs))
    assert len(ma_inputs) > 0

    ## Run sg injection
    #ma = '1GeV'
    #h24g_sample = 'h24gamma_1j_1M_%s'%ma
    #h24g_inputs = glob.glob('MAntuples/%s_mantuple.root'%h24g_sample)
    #print('len(h24g_inputs):',len(h24g_inputs))
    #assert len(h24g_inputs) > 0
    #ma_inputs = ma_inputs + h24g_inputs
    #print('len(ma_inputs):',len(ma_inputs))

    s = sample.replace('[','').replace(']','')
    #regions = ['sb2sr', 'sr']
    #regions = ['sblo2sr', 'sbhi2sr']
    regions = ['sblo2sr', 'sbhi2sr', 'sr']
    processes = [bkg_process(s, r, blind, ma_inputs, output_dir,\
            #do_combo_template=True if 'sb' in r else False,\
            norm=norm[r]*frac[r] if 'sb' in r else 1.,\
            do_ptomGG=do_ptomGG if 'sb' in r else True,\
            do_pt_reweight=do_pt_reweight if 'sb' in r else False\
            ) for r in regions]

    r_hgg = 'hgg2sr'
    s_hgg = 'GluGluHToGG'
    ma_inputs = glob.glob('MAntuples/%s_mantuple.root'%s_hgg)
    processes.append(bkg_process(s_hgg, 'sr', blind, ma_inputs, output_dir,\
            norm=norm[r_hgg]*frac[r_hgg]\
            #norm=norm[r_hgg]*frac[r_hgg],\
            #do_mini2aod=True\
            ))

    # Run processes in parallel
    pool = Pool(processes=len(processes))
    pool.map(run_process, processes)
    pool.close()
    pool.join()
    #'''

    #'''
    #blind = 'offdiag_lo_hi' # for actual limit setting
    #blind = 'sg'
    s = sample.replace('[','').replace(']','')
    plot_srvsb_sb(s, blind, apply_blinding=False)
    #plot_srvsb_sb(s, blind, apply_blinding=True)
    #plot_srvsb(s, blind)
    #plot_srvsb_pt(s, blind)#, sb='sb2sr')
    #'''
