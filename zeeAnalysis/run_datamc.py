from __future__ import print_function
from multiprocessing import Pool
import os, glob, re
import numpy as np
import subprocess
import ROOT
from data_utils import *
from plot_datamc import plot_datamc

eosls = 'eos root://eoscms.cern.ch ls'
#eosfind = 'eos root://eoscms.cern.ch find'
eosfind = 'eos root://cmseos.fnal.gov find'

def get_sg_norm(sample, xsec=50., tgt_lumi=41.9e3): # xsec:pb, tgt_lumi:/pb

    gg_cutflow = glob.glob('../ggSkims_zee/%s_cut_hists.root'%sample)
    assert len(gg_cutflow) == 1

    cut = str(None)
    var = 'npho'
    key = cut+'_'+var
    hf = ROOT.TFile(gg_cutflow[0], "READ")
    h = hf.Get('%s/%s'%(cut, key))

    nevts_gen = h.GetEntries()
    # Sum of wgts
    if sample == 'DiPhotonJets':
        nevts_gen = 1118685275.488525
    elif sample == 'GluGluHToGG':
        nevts_gen = 214099989.445038
    print('xsec',xsec)
    print('nevts_gen',nevts_gen)
    norm = xsec*tgt_lumi/nevts_gen
    #norm = xsec*tgt_lumi
    print('norm',norm)
    return norm

samples = [
    'B'
    ,'C'
    ,'D'
    ,'E'
    ,'F'
    ]
samples = ['Run2017%s'%s for s in samples]
samples.append('DYToEE')

xsec = {
    'DiPhotonJets': 134.3,
    'GJet_Pt20To40': 232.8,#*0.0029,
    'GJet_Pt40ToInf': 872.8,#*0.0558,
    'QCD_Pt30To40': 24750.0,#*0.0004*100.,
    'QCD_Pt40ToInf': 117400.0,#*0.0026*100.,
    'GluGluHToGG': 33.14*2.27e-3,
    'DYToEE': 2137.
}


'''
#2016
samples = [
    'B'
    ,'C'
    ,'D'
    ,'E'
    ,'F'
    ,'G'
    ,'H'
    ]
samples = ['Run2016%s'%s for s in samples]
'''

'''
#2017
eos_basedir = '/store/group/lpchaa4g/mandrews/2017/MAntuples_zee'
samples = [
    'B'
    #,'C'
    #,'D'
    #,'E'
    #,'F'
    ]
samples = ['Run2017%s'%s for s in samples]
#samples = ['Run2017[C-F]']
'''

'''
#2018
samples = [
#    'A'
    'B'
    ,'C'
#    ,'D'
    ]
samples = ['Run2018%s'%s for s in samples]

samples = [
#    'DiPhotonJets'
#    ,'GJet_Pt20To40'
#    ,'GJet_Pt40ToInf'
#    ,'QCD_Pt30To40'
#    ,'QCD_Pt40ToInf'
    'GluGluHToGG'
    ]
'''

'''
eos_basedir = '/store/group/lpchaa4g/mandrews/2017/MAntuples_zee'
samples = [
    'DYToEE'
    ]
'''

output_dir = 'Templates_datamc'
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

processes = []
norm = {}
for s in samples:

    print(s)

    '''
    cmd = '%s %s/'%(eosfind, eos_basedir) # H4G ntuple same for miniaod or aod IMG ntuple
    print(cmd)
    ma_inputs = subprocess.check_output(cmd, shell=True)
    # subprocess.check_output() returns a byte-string => decode into str then split into files
    ma_inputs = ma_inputs.decode("utf-8").split('\n')
    # eosfind returns directories as well, keep only root files from correct sample and add fnal redir
    ma_inputs = [f for f in ma_inputs if 'mantuple.root' in f]
    ma_inputs = [f.replace('/eos/uscms','root://cmseos.fnal.gov/') for f in ma_inputs]
    #ma_inputs = [f for f in ma_inputs if s in f]
    ma_inputs = [f for f in ma_inputs if re.search(s, f) is not None]
    # clean up empty elements:
    ma_inputs = list(filter(None, ma_inputs)) # for py2.7: use filter(None, ma_inputs) without list()
    print(ma_inputs[0])
    print('len(ma_inputs):',len(ma_inputs))
    assert len(ma_inputs) > 0

    s = s.replace('[','').replace(']','')
    pyargs = 'evt_selector.py -s %s -i %s -o %s'%(s, ' '.join(ma_inputs), output_dir)
    #os.system('python %s'%pyargs)
    processes.append(pyargs)
    #break
    '''
    sample = s.replace('[','').replace(']','')

    # Sample norm
    norm[sample] = get_sg_norm(sample, xsec=xsec[sample]) if 'Run' not in sample else 1.
    print(sample, norm[sample])

#print(len(processes))
#pool = Pool(processes=len(processes))
#pool.map(run_process, processes)
#pool.close()
#pool.join()

plot_datamc(samples, blind=None, norm=norm, regions=['all'])
