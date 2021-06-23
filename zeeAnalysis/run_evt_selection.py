from __future__ import print_function
from multiprocessing import Pool
import os, glob, re
import numpy as np
import subprocess
import shutil
from data_utils import *
from selection_utils import *

eosls = 'eos root://eoscms.cern.ch ls'
#eosfind = 'eos root://eoscms.cern.ch find'
eosfind = 'eos root://cmseos.fnal.gov find'

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

#'''
#2017
eos_basedir = '/store/group/lpchaa4g/mandrews/2017/MAntuples_zee'
#samples = [
#    'B'
#    #,'C'
#    #,'D'
#    #,'E'
#    #,'F'
#    ]
#samples = ['Run2017%s'%s for s in samples]
samples = ['Run2017[B-F]']
#'''

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
#eos_basedir = '/store/group/lpchaa4g/mandrews/2017/MAntuples_zee'
samples = [
    'DYToEE'
    ]
'''
samples.append('DYToEE')

output_dir = 'Templates'
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

procs = []
procs_rewgt = []

for s in samples:

    print(s)

    #'''
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
    '''
    ma_inputs = glob.glob('MAntuples/%s_mantuple.root'%s)
    #ma_inputs = glob.glob('MAntuples/%s_mantuple_200k.root'%s)
    print('len(ma_inputs):',len(ma_inputs))
    assert len(ma_inputs) > 0
    '''

    s = s.replace('[','').replace(']','')
    pyargs = 'evt_selector.py -s %s -i %s -o %s'%(s, ' '.join(ma_inputs), output_dir)
    procs.append(pyargs)
    #break
    if 'Run' in s: continue
    pyargs = 'evt_selector.py -s %s -i %s -o %s --do_pt_reweight'%(s, ' '.join(ma_inputs), output_dir)
    procs_rewgt.append(pyargs)

print(len(procs))
pool = Pool(processes=len(procs))
pool.map(run_process, procs)
pool.close()
pool.join()

#'''
get_ptweights()

print(len(procs_rewgt))
pool = Pool(processes=len(procs_rewgt))
pool.map(run_process, procs_rewgt)
pool.close()
pool.join()

assert 'Run' in samples[0]
s = samples[0].replace('[','').replace(']','')
shutil.copyfile('Templates/%s_templates.root'%s, 'Templates/%s_rewgt_templates.root'%s)
#'''
