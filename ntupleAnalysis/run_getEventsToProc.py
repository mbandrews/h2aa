from __future__ import print_function
from multiprocessing import Pool
import os, glob
import numpy as np
from data_utils import *

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

#2017
samples = [
    'B'
    ,'C'
    ,'D'
    ,'E'
    ,'F'
    ]
samples = ['Run2017%s'%s for s in samples]
#samples = ['DoubleEG_2017%s'%s for s in samples] v1, deprecated

#2018
eos_basedir = '/store/group/lpcsusystealth/stealth2018Ntuples_with10210'
samples = [
    'A'
    ,'B'
    ,'C'
    ,'D'
    ]
samples = ['Run2018%s'%s for s in samples]

#samples = [
#    '100MeV'
#    ,'400MeV'
#    ,'1GeV'
#    ]
#samples = ['h24gamma_1j_1M_%s'%s for s in samples]
#
#samples = [
#    'DiPhotonJets'
#    ,'GJet_Pt20To40'
#    ,'GJet_Pt40ToInf'
#    ,'QCD_Pt30To40'
#    ,'QCD_Pt40ToInf'
#    ,'GluGluHToGG'
#    ]

output_dir = '../evtsToProc'
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

processes = []
for s in samples:

    print('For sample:',s)

    #input_files = glob.glob('../ggSkims/%s_ggskim.root'%s)
    input_files = glob.glob('../ggSkims/3pho/%s_*ggskim.root'%s)
    print('len(input_files):',len(input_files))
    #assert len(input_files) == 1

    processes.append('getEventsToProc.py -i %s -s %s -o %s'%(' '.join(input_files), s, output_dir))
    #print(cmd)
    #os.system(cmd)
    #break

pool = Pool(processes=len(processes))
pool.map(run_process, processes)
pool.close()
pool.join()
