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
#    'B'
#    ,'C'
#    ,'D'
#    ,'E'
    'F'
    ]
samples = ['Run2017%s'%s for s in samples]

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

# Inut IMG directory
#img_campaign = 'Era2017_16Apr2020_IMGv1'
#img_campaign = 'Era2017_11May2020_MINIAOD-IMGv1'
img_campaign = 'Era2017_27May2020_AOD-IMGv1'

def get_img_dir(sample, campaign):
    if '2017' in sample:
        #input_dir = '%s/DoubleEG/%s_%s'%(campaign, sample, campaign)
        input_dir = '%s/DoubleEG'%(campaign)
    elif 'h24gamma_1j_1M' in sample:
        input_dir = '%s/h24gamma_01Nov2019-rhECAL/%s_%s'%(campaign, sample, campaign)
    else:
        input_dir = '%s'%(campaign)
    return input_dir

def run_process(process):
    os.system('python %s'%process)

#output_dir = 'MAntuples'
output_dir = '/uscms/physics_grp/lpcml/nobackup/mandrews/MAntuples_zee'
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)
list_dir = 'Lists'
if not os.path.isdir(list_dir):
    os.makedirs(list_dir)

# NOTE: eosls is an alias variable which isnt visible to subprocess
eosls = 'eos root://cmseos.fnal.gov ls'
#eosfind = 'eos root://cmseos.fnal.gov find /store/user/lpcml/mandrews/2017/Era2017_18Nov2019_IMGv1/DoubleEG/Run2017B_Era2017_18Nov2019_IMGv1_IMG/ | grep root'
eosfind = 'eos root://cmseos.fnal.gov find'
eos_basedir = '/store/user/lpchaa4g/mandrews/2017'
processes = []
for s in samples:

    print('For sample:',s)

    # Get H4G ntuples
    cmd = '%s %s/%s/'%(eosfind, eos_basedir, 'ggSkims_zee') # H4G ntuple same for miniaod or aod IMG ntuple
    print(cmd)
    gg_inputs = subprocess.check_output(cmd, shell=True)
    # subprocess.check_output() returns a byte-string => decode into str then split into files
    gg_inputs = gg_inputs.decode("utf-8").split('\n')
    # eosfind returns directories as well, keep only root files from correct sample and add fnal redir
    gg_inputs = [f for f in gg_inputs if 'ggskim.root' in f]
    gg_inputs = [f for f in gg_inputs if 'ARCHIVE' not in f]
    gg_inputs = [f.replace('/eos/uscms','root://cmseos.fnal.gov/') for f in gg_inputs]
    gg_inputs = [f for f in gg_inputs if s in f]
    # clean up empty elements:
    gg_inputs = list(filter(None, gg_inputs)) # for py2.7: use filter(None, gg_inputs) without list()
    #gg_inputs = ['ggSkims/DoubleEG_2017B_ggskim.root']
    print(gg_inputs[0])
    print('len(gg_inputs):',len(gg_inputs))
    assert len(gg_inputs) > 0
    '''
    gg_inputs = glob.glob('../ggSkims/3pho/%s*ggskim.root'%s)
    print(gg_inputs[0])
    print('len(gg_inputs):',len(gg_inputs))
    assert len(gg_inputs) > 0
    '''

    # Get IMG ntuples
    cmd = '%s %s/%s/'%(eosfind, eos_basedir, get_img_dir(s, img_campaign))
    print(cmd)
    img_inputs = subprocess.check_output(cmd, shell=True)
    # subprocess.check_output() returns a byte-string => decode into str then split into files
    img_inputs = img_inputs.decode("utf-8").split('\n')
    # eosfind returns directories as well, keep only root files and add fnal redir
    img_inputs = [f for f in img_inputs if '.root' in f]
    img_inputs = [f.replace('/eos/uscms','root://cmseos.fnal.gov/') for f in img_inputs]
    img_inputs = [f for f in img_inputs if s in f]
    # clean up empty elements:
    img_inputs = list(filter(None, img_inputs)) # for py2.7: use filter(None, img_inputs) without list()
    #img_inputs = ['output_img.root']
    print(img_inputs[0])
    print('len(img_inputs):',len(img_inputs))
    assert len(img_inputs) > 0

    img_inputs_filestr = '%s/img_inputs_%s.txt'%(list_dir, s)
    with open(img_inputs_filestr, 'w') as f:
        for img_input in img_inputs:
            f.write('%s\n'%img_input)

    njobs = 4# 2 if 'DYToEE' in s else 1
    pyargs = 'mass_ntuplizer.py -s %s -i %s -g %s -o %s'%(s, img_inputs_filestr, ' '.join(gg_inputs), output_dir)
    if njobs > 1:
        for j in range(njobs):
            processes.append('%s -j %d -n %d'%(pyargs, j, njobs))
    else:
        processes.append(pyargs)
    #os.system('python %s'%pyargs)
    #processes.append(pyargs)
    #break

pool = Pool(processes=len(processes))
pool.map(run_process, processes)
pool.close()
pool.join()
