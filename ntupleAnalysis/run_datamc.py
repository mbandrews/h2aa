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
from plot_datamc import plot_datamc

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

#samples = [
#    'B'
#    ,'C'
#    ,'D'
#    ,'E'
#    ,'F'
#    ]
#samples = ['Run2017%s'%s for s in samples]
#samples = ['Run2017%s-MINIAOD'%s for s in samples]
#samples = ['Run2017[B-F]']

#samples = [
#    '100MeV'
#    ,'400MeV'
#    ,'1GeV'
#    ]
#samples = ['h24gamma_1j_1M_%s'%s for s in samples]

samples = [
    'DiPhotonJets',
    'GJet_Pt20To40',
    'GJet_Pt40ToInf',
    'QCD_Pt30To40',
    'QCD_Pt40ToInf',
    'GluGluHToGG'
    ]
samples.append('Run2017[B-F]')

xsec = {
    'DiPhotonJets': 135.1,
    'GJet_Pt20To40': 220.0,
    'GJet_Pt40ToInf': 850.8,
    'QCD_Pt30To40': 24810.0,
    'QCD_Pt40ToInf': 118100.0,
    'GluGluHToGG': 44.14*2.27e-3,
#    'Run2017B-F': 1.
}

output_dir = 'Templates'
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

regions = ['sr', 'sb']

processes = []
norm = {}
for sample in samples:

    print(sample)
    #run_ptweights()
    #plot_srvsb_pt(s, blind=None, sb='sb')
    #do_pt_reweight = True
    #do_ptomGG = False
    do_pt_reweight = False
    do_ptomGG = True
    # `do_ptomGG` swtich applies to sb only

    '''
    #derive_fit = True
    derive_fit = False
    frac = {}
    frac['gg'], frac['sblo2sr'], frac['sbhi2sr'] = run_combined_sbfit(derive_fit=derive_fit, do_pt_reweight=do_pt_reweight, do_ptomGG=do_ptomGG)

    norm = {}
    run_bkg = False
    #run_bkg = True
    norm['sblo2sr'] = get_bkg_norm_sb(sb='sblo', do_pt_reweight=do_pt_reweight, do_ptomGG=do_ptomGG, run_bkg=run_bkg)
    norm['sbhi2sr'] = get_bkg_norm_sb(sb='sbhi', do_pt_reweight=do_pt_reweight, do_ptomGG=do_ptomGG, run_bkg=run_bkg)
    print(frac['sblo2sr'], norm['sblo2sr'])
    print(frac['sbhi2sr'], norm['sbhi2sr'])
    '''

    # Rerun data with fixed normalization
    #blind = 'notgjet'
    #blind = 'notgg'
    #blind = 'sg'
    blind = None
    #blind = 'diag_lo_hi'
    #blind = 'offdiag_lo_hi' # for actual limit setting

    # Run both SB and SR to bkg processes
    ma_inputs = glob.glob('MAntuples/%s_mantuple.root'%sample)
    print('len(ma_inputs):',len(ma_inputs))
    assert len(ma_inputs) > 0
    sample = sample.replace('[','').replace(']','')
    #norm[s] = get_bkg_norm_sb(sb='sblo', do_pt_reweight=do_pt_reweight, do_ptomGG=do_ptomGG, run_bkg=run_bkg)
    norm[sample] = get_sg_norm(sample, xsec=xsec[sample], tgt_lumi=41.e3) if 'Run' not in sample else 1.
    print(sample, norm[sample])
    #regions = ['sb2sr', 'sr']
    #regions = ['sblo2sr', 'sbhi2sr', 'sr']
    regions = ['sblo2sr']
    for r in regions:
        processes.append(bkg_process(sample, r, blind, ma_inputs, output_dir,\
                #do_combo_template=True if 'sb' in r else False,\
                #norm=norm[r]*frac[r] if 'sb' in r else 1.,\
                norm=norm[sample],\
                #do_ptomGG=False if 'sb' in r else True,\
                #do_pt_reweight=True if 'sb' in r else False)\
                nevts=10000
                ))

# Run processes in parallel
pool = Pool(processes=len(processes))
pool.map(run_process, processes)
pool.close()
pool.join()

plot_datamc(samples, blind, norm)
