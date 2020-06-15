from __future__ import print_function
from multiprocessing import Pool
import os, glob
import numpy as np
import subprocess
from data_utils import *

eosls = 'eos root://eoscms.cern.ch ls'
#eosfind = 'eos root://eoscms.cern.ch find'
eosfind = 'eos root://cmseos.fnal.gov find'
#eos_basedir = '/store/group/phys_smp/ggNtuples/13TeV/data/V09_04_13_00'

'''
#2016
eos_basedir = '/store/group/lpcsusystealth/stealth2018Ntuples_with9413'
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

#2017
eos_basedir = '/store/group/lpcsusystealth/stealth2018Ntuples_with9413'
samples = [
    'B'
    ,'C'
    ,'D'
    ,'E'
    ,'F'
    ]
samples = ['Run2017%s'%s for s in samples]
#samples = ['DoubleEG_2017%s'%s for s in samples] v1, deprecated

'''
#2018
eos_basedir = '/store/group/lpcsusystealth/stealth2018Ntuples_with10210'
samples = [
#    'A'
    'B'
    ,'C'
#    ,'D'
    ]
samples = ['Run2018%s'%s for s in samples]

eos_basedir = '/store/user/lpcsusystealth/stealth2018Ntuples_with10210'
samples = [
#    'DiPhotonJets'
#    ,'GJet_Pt20To40'
#    ,'GJet_Pt40ToInf'
#    ,'QCD_Pt30To40'
#    ,'QCD_Pt40ToInf'
    'GluGluHToGG'
    ]
'''

#'''
eos_basedir = '/store/user/lpcml/mandrews/2017/Era2017_16Apr2020_ggntuplev1'
samples = [
    'DYToEE'
    ]
#'''

output_dir = '../ggSkims_zee'
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

processes = []
for s in samples:

    #pyargs = 'skim_ntuple.py -s %s -i %s -o %s'%(s, ' '.join(gg_inputs), output_dir)
    pyargs = 'skim_ntuple_zee.py -s %s -b %s -o %s'%(s, eos_basedir, output_dir)
    #print(pyargs)
    #os.system('python %s'%pyargs)
    processes.append(pyargs)
    #break

print(len(processes))
pool = Pool(processes=len(processes))
pool.map(run_process, processes)
pool.close()
pool.join()
