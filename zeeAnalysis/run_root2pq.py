from __future__ import print_function
from multiprocessing import Pool
import os, glob
import numpy as np
import subprocess

##2016
#samples = [
#    'B'
#    ,'C'
#    ,'D'
#    ,'E'
#    ,'F'
#    ,'G'
#    ,'H'
#    ]
#samples = ['Run2016%s'%s for s in samples]

#2017
samples = [
    'B'
    ,'C'
    ,'D'
    ,'E'
    ,'F'
    ]
samples = ['Run2017%s'%s for s in samples]
#samples = ['Run2017B-F']
#samples = []

##2018
#samples = [
##    'A'
#    'B'
#    ,'C'
##    ,'D'
#    ]
#samples = ['Run2018%s'%s for s in samples]

#samples = [
#    '100MeV'
#    ,'400MeV'
#    ,'1GeV'
#    ]
#samples = ['h24gamma_1j_1M_%s'%s for s in samples]
#samples.append('Run2017B')

#samples = [
#    'DiPhotonJets'
#    ,'GJet_Pt20To40'
#    ,'GJet_Pt40ToInf'
#    ,'QCD_Pt30To40'
#    ,'QCD_Pt40ToInf'
#    'GluGluHToGG'
#    'DYToEE'
#    ]

#samples.append('DYToEE')
samples_mc = glob.glob('Templates/DYToEE?_selected_event_list.txt')
samples_mc = [s.split('/')[-1].split('_')[0] for s in samples_mc]
for s in samples_mc:
    samples.append(s)

nEvtsData = 38400
#nEvtsData = 200
nEvtsMC = 38400*5

def run_process(process):
    os.system('python %s'%process)

output_dir = '/uscms/physics_grp/lpcml/nobackup/mandrews/PQntuples_zee'
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)
list_dir = 'Lists'

# NOTE: eosls is an alias variable which isnt visible to subprocess
eosls = 'eos root://cmseos.fnal.gov ls'
eosfind = 'eos root://cmseos.fnal.gov find'
eos_basedir = '/store/user/lpchaa4g/mandrews/2017'

processes = []
for s in samples:

    print('For sample:',s)

    img_inputs_filestr = '%s/img_inputs_%s.txt'%(list_dir, s if 'Run' in s else s[:-1])
    assert os.path.isfile(img_inputs_filestr), '%s not found'%img_inputs_filestr

    sel_evtlist_fname = 'Templates/%s_selected_event_list.txt'%s
    assert os.path.isfile(sel_evtlist_fname)

    img_evtlist_fname = 'Lists/img_event_list_%s.npz'%s
    #assert os.path.isfile(img_evtlist_fname)

    s = s.replace('[','').replace(']','')
    #pyargs = 'convert_root2pq.py -s %s -i %s -o %s -e %d'%(s, img_inputs_filestr, output_dir, nEvtsData if 'Run' in s else nEvtsMC)
    pyargs = 'convert_root2pq.py -s %s -i %s -o %s -e %d -l %s -m %s'\
            %(s, img_inputs_filestr, output_dir, nEvtsData, sel_evtlist_fname, img_evtlist_fname)
    processes.append(pyargs)
    print(pyargs)

pool = Pool(processes=len(processes))
pool.map(run_process, processes)
pool.close()
pool.join()
