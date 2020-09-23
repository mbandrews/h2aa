from __future__ import print_function
from multiprocessing import Pool
import os, glob, shutil
import numpy as np
import subprocess
from data_utils import *
from get_bkg_norm import *
from plot_srvsb_sb import plot_srvsb_sb

#samples = ['Run2017[B-F]']
eras = ['Run2017']

do_pt_reweight = True
#do_pt_reweight = False
do_ptomGG = True # `do_ptomGG` swtich applies to SB only, SR always has this True

#for flo_ in [None, 0.504, 0.791]:
#for flo_ in [0.791]:
for flo_ in [None]:

    #expmt_dir = '%s/scan_ptrwgt/flo_%s'%(output_dir, str('%.3f'%flo_).replace('.','p') if flo_ is not None else None)
    #expmt_dir = 'Templates/prod_normblind_diaglohi/nom-nom/flo_%s'%(str('%.3f'%flo_).replace('.','p') if flo_ is not None else None)
    expmt_dir = 'Templates/prod_fixsb2srnorm/nom-nom/flo_%s'%(str('%.3f'%flo_).replace('.','p') if flo_ is not None else None)
    #expmt_dir += '_hgg_dn'

    if not os.path.isdir(expmt_dir):
        os.makedirs(expmt_dir)

    for era in eras:

        #'''
        # Derive SB -> SR pt weights
        print('>> Getting pt weights <<<<<<<<<<')
        samples = ['Run2017[B-F]']
        regions = {'Run2017[B-F]': ['sblo', 'sbhi', 'sr']}
        blind = None
        workdir = 'Templates_tmp'
        distn = 'pt0vpt1'
        if flo_ is None:
            flo_nom = run_ptweights(samples, regions, blind, workdir=workdir, do_ptomGG=do_ptomGG, flo_=flo_, distn=distn)
            flo_syst = flo_nom
        else:
            flo_nom = 0.640902 #nom-nom
            flo_syst = run_ptweights(samples, regions, blind, workdir=workdir, do_ptomGG=do_ptomGG, flo_=flo_, distn=distn)

        samples = ['Run2017[B-F]', 'GluGluHToGG']
        regions = {'Run2017[B-F]': ['sblo', 'sbhi', 'sr'],
                   'GluGluHToGG': ['sr']}

        # Derive SB lo vs hi frac
        frac = {}
        print('>> Getting SB fracs <<<<<<<<<<')
        blind = None
        output_dir = 'Templates_tmp'
        distn = 'pt0vpt1'
        frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = run_combined_sbfit(samples, regions, blind=blind, output_dir=output_dir, do_pt_reweight=do_pt_reweight, do_ptomGG=do_ptomGG, flo_=flo_syst, distn=distn, flo_nom=flo_nom)
        print("frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr'] = %f, %f, %f"%(frac['hgg2sr'], frac['sblo2sr'], frac['sbhi2sr']))

        #'''
        # Derive SB -> SR normalization
        norm = {}
        print('>> Getting normalizations <<<<<<<<<<')
        blind = 'diag_lo_hi'
        workdir = 'Templates_tmp'
        distn = 'ma0vma1'
        norm['sblo2sr'], norm['sbhi2sr'], norm['hgg2sr'] = get_bkg_norm_sb(samples, regions, blind=blind, workdir=workdir, do_pt_reweight=do_pt_reweight, do_ptomGG=do_ptomGG, distn=distn)
        print(frac['sblo2sr'], norm['sblo2sr'])
        print(frac['sbhi2sr'], norm['sbhi2sr'])
        print(frac['hgg2sr'], norm['hgg2sr'])
        print("norm['sblo2sr'], norm['sbhi2sr'], norm['hgg2sr'] = %f, %f, %f"%(norm['sblo2sr'], norm['sbhi2sr'], norm['hgg2sr']))

        # Rerun bkg model with derived fracs and norms
        print('>> Running bkg model w fracs and norms <<<<<<<<<<')

        samples = ['Run2017[B-F]', 'GluGluHToGG']
        regions = {'Run2017[B-F]': ['sblo2sr', 'sbhi2sr', 'sr'],
                   'GluGluHToGG': ['hgg2sr']}

        #for blind in [None]:
        for blind in ['diag_lo_hi', 'offdiag_lo_hi']:

            output_dir = 'Templates'
            if not os.path.isdir(output_dir):
                os.makedirs(output_dir)

            print('>> Running blind: %s <<<<<<<<<<'%blind)
            processes = []
            for sample in samples:
                ma_inputs = get_mantuples(sample)
                s = sample.replace('[','').replace(']','')
                for r in regions[sample]:
                    processes.append(bkg_process(s, r, blind, ma_inputs, output_dir,\
                                                norm=norm[r]*frac[r] if 'sb' in r or 'GluGluH' in s else 1.,\
                                                do_ptomGG=do_ptomGG if 'sb' in r else True,\
                                                do_pt_reweight=do_pt_reweight if 'sb' in r else False))

            # Run processes in parallel
            pool = Pool(processes=len(processes))
            pool.map(run_process, processes)
            pool.close()
            pool.join()

            #s = samples[0].replace('[','').replace(']','')
            workdir = 'Templates'
            output_dir = 'Plots'
            #apply_blinding = False
            #apply_blinding = True if blind == 'offdiag_lo_hi' else False
            apply_blinding = True
            plot_srvsb_sb(samples, regions, blind, apply_blinding=apply_blinding, workdir=workdir, output_dir=output_dir)

        # Move output
        workdir = 'Templates'
        rootfiles = glob.glob('%s/*root'%workdir)
        txtfiles = glob.glob('%s/*txt'%workdir)
        outfiles = rootfiles+txtfiles
        for outf in outfiles:
            outf = outf.split('/')[-1]
            shutil.move('%s/%s'%(workdir, outf), '%s/%s'%(expmt_dir, outf))
        #'''
