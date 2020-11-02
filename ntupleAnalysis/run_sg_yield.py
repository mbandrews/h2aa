from __future__ import print_function
from multiprocessing import Pool
import os, glob, shutil
import numpy as np
import subprocess
from data_utils import *
from get_bkg_norm import *
from plot_srvsb import plot_srvsb

samples = [
    #'100MeV',
    #'400MeV',
    '1GeV'
    ]
samples = ['h24gamma_1j_1M_%s'%s for s in samples]
#samples.append('GluGluHToGG')

output_basedir = mkoutdir('Templates')

#campaign = 'prod_fixsb2srnorm/nom-nom'
campaign = 'systTEST'
#regions = ['all']
regions = ['sr']
systPhoIdSFs = ['up', 'dn'] # photon ID SF syst shifts: nom, up, dn
systScales = ['up', 'dn'] # photon ID SF syst shifts: nom, up, dn
systSmears = ['up', 'dn'] # photon ID SF syst shifts: nom, up, dn

processes = []
for s in samples:

    #blind = 'sg'
    #blind = None
    #blind = 'diag_lo_hi'
    blind = 'offdiag_lo_hi' #limit setting

    # Get inputs
    ma_inputs = glob.glob('MAntuples/%s_mantuple.root'%s)
    print('len(ma_inputs):',len(ma_inputs))
    assert len(ma_inputs) > 0
    s = s.replace('[','').replace(']','')

    # Get PU distn
    pyargs = 'get_pu_distn.py -s %s -i %s'%(s, ' '.join(ma_inputs))
    print('Doing: %s'%pyargs)
    os.system('python %s'%pyargs)

    # Run event selection
    for r in regions:
        print('For region:',r)

        # Nominal scenario
        output_dir = mkoutdir('%s/%s/h4g/nom'%(output_basedir, campaign))
        pyargs = 'get_bkg_model.py -s %s -r %s -b %s -i %s -t %s -o %s --do_ptomGG --do_pu_rwgt --systPhoIdSF nom'\
                %(s, r, blind, ' '.join(ma_inputs), get_ma_tree_name(s), output_dir)
        print('Doing: %s'%pyargs)
        processes.append(pyargs)

        # Syst: photon ID SFs
        for systPhoIdSF in systPhoIdSFs:
            print('For systPhoIdSF:',systPhoIdSF)

            output_dir = mkoutdir('%s/%s/h4g/systPhoIdSF_%s'%(output_basedir, campaign, systPhoIdSF))

            pyargs = 'get_bkg_model.py -s %s -r %s -b %s -i %s -t %s -o %s --do_ptomGG --do_pu_rwgt --systPhoIdSF %s'\
                    %(s, r, blind, ' '.join(ma_inputs), get_ma_tree_name(s), output_dir, systPhoIdSF)
            print('Doing: %s'%pyargs)
            processes.append(pyargs)

        # Syst: m_a energy scale
        for systScale in systScales:
            print('For systScale:',systScale)

            output_dir = mkoutdir('%s/%s/h4g/systScale_%s'%(output_basedir, campaign, systScale))

            pyargs = 'get_bkg_model.py -s %s -r %s -b %s -i %s -t %s -o %s --do_ptomGG --do_pu_rwgt --systPhoIdSF nom --systScale %s'\
                    %(s, r, blind, ' '.join(ma_inputs), get_ma_tree_name(s), output_dir, systScale)
            print('Doing: %s'%pyargs)
            processes.append(pyargs)

        # Syst: m_a energy smearing
        for systSmear in systSmears:
            print('For systSmear:',systSmear)

            output_dir = mkoutdir('%s/%s/h4g/systSmear_%s'%(output_basedir, campaign, systSmear))

            pyargs = 'get_bkg_model.py -s %s -r %s -b %s -i %s -t %s -o %s --do_ptomGG --do_pu_rwgt --systPhoIdSF nom --systSmear %s'\
                    %(s, r, blind, ' '.join(ma_inputs), get_ma_tree_name(s), output_dir, systSmear)
            print('Doing: %s'%pyargs)
            processes.append(pyargs)

pool = Pool(processes=len(processes))
pool.map(run_process, processes)
pool.close()
pool.join()
