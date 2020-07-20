from __future__ import print_function
from multiprocessing import Pool
import os, glob, shutil
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

#flo_ = 0.90
#flo_ = 0.790
#flo_ = 0.756 #qcd nom
#flo_ = 0.722
#flo_ = 0.618
#flo_ = 0.10
#flo_ = 1.
#flo_ = 0.758
#flo_ = 0.405796915293

#flo_ = None # by evt-wgtd average: flo_=0.687
#flo_ = 9.32459e-01 # by unrewgt ma temp frac
#flo_ = 3.62495e-01 # by 2d pt temp frac

#for flo_ in [0.504404008389, 0.791357934475]:
for flo_ in [None]:

    expmt_dir = '%s/scan_ptrwgt/flo_%s'%(output_dir, str('%.3f'%flo_).replace('.','p') if flo_ is not None else None)
    #expmt_dir = '%s/scan_ptrwgt/nom-nom/flo_%s'%(output_dir, str('%.3f'%flo_).replace('.','p') if flo_ is not None else None)
    #expmt_dir = '%s/scan_ptrwgt/nom-nom/flo_%s_noptcap'%(output_dir, str('%.3f'%flo_).replace('.','p') if flo_ is not None else None)
    #expmt_dir = '%s_hgg_dn'%expmt_dir
    if not os.path.isdir(expmt_dir):
        os.makedirs(expmt_dir)

    for sample in samples:

        do_pt_reweight = True
        #do_pt_reweight = False
        #do_ptomGG = False
        do_ptomGG = True
        # `do_ptomGG` swtich applies to sb only
        flo_ = run_ptweights(do_ptomGG=do_ptomGG, flo_=flo_)

        for b in ['diag_lo_hi', 'offdiag_lo_hi']:
        #for b in ['diag_lo_hi']:

            #norm_blind = 'sg'
            #norm_blind = 'diag_lo_hi'
            norm_blind = None
            derive_fit = True
            #derive_fit = False
            frac = {}
            frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = run_combined_sbfit(derive_fit=derive_fit, do_pt_reweight=do_pt_reweight, do_ptomGG=do_ptomGG, blind=norm_blind, flo_=flo_)
            if not derive_fit:
                pass
                #----
                #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 5.42048e-02, 5.46852e-01, 3.98950e-01 # nom, bdt>-0.98, relchgiso < 0.05
                #frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = 7.17730e-02, 6.12411e-01, 3.15820e-01 # diaglohi nom, bdt>-0.98, relchgiso < 0.05

            frac = normalize_fracs(frac)
            #frac = normalize_fracs_byhgg(frac)
            print(frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'])

            #'''
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
            #blind = 'sg'
            #blind = None
            #blind = 'diag_lo_hi'
            #blind = 'offdiag_lo_hi' # for actual limit setting
            blind = b

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
            #apply_blinding = False
            apply_blinding = True if blind == 'offdiag_lo_hi' else False
            plot_srvsb_sb(s, blind, apply_blinding=apply_blinding)
            #plot_srvsb(s, blind)
            #plot_srvsb_pt(s, blind)#, sb='sb2sr')
            #'''

        # Move output
        rootfiles = glob.glob('%s/*root'%output_dir)
        txtfiles = glob.glob('%s/*txt'%output_dir)
        outfiles = rootfiles+txtfiles
        for outf in outfiles:
            outf = outf.split('/')[-1]
            shutil.move('%s/%s'%(output_dir, outf), '%s/%s'%(expmt_dir, outf))
