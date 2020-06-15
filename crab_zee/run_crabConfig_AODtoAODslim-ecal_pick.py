from __future__ import print_function
from multiprocessing import Pool
import os, glob, shutil
import numpy as np
import subprocess

# Strings to replace in crabConfig template
SAMPLE = '__SAMPLE__'
DATASET = '__DATASET__'
CAMPAIGN = '__CAMPAIGN__'
UNITSPERJOB = '__UNITSPERJOB__'
EVTLIST = '__EVTLIST__'
LUMIMASK = '__LUMIMASK__'

#this_campaign = 'Era2016_15Jan2020_AODslim-ext_v1'
#this_campaign = 'Era2016_04May2020_AODslim-ecal_v1'
#this_campaign = 'Era2017_18May2020_AODslim-ecal_pick_v1'
#this_campaign = 'Era2017_18May2020_AODslim-ecal_pick_v2'
this_campaign = 'Era2017_27May2020_AODslim-ecal_pick_v1'

crab_folder = 'crab_%s'%this_campaign
if not os.path.isdir(crab_folder):
    os.makedirs(crab_folder)

#run = 'DoubleEG_2016'
#job_units = 10
#samples = {
#    '%sB'%run: '/DoubleEG/Run2016B-07Aug17_ver2-v2/AOD',
#    '%sC'%run: '/DoubleEG/Run2016C-07Aug17-v1/AOD',
#    '%sD'%run: '/DoubleEG/Run2016D-07Aug17-v1/AOD',
#    '%sE'%run: '/DoubleEG/Run2016E-07Aug17-v1/AOD',
#    '%sF'%run: '/DoubleEG/Run2016F-07Aug17-v1/AOD',
#    '%sG'%run: '/DoubleEG/Run2016G-07Aug17-v1/AOD',
#    '%sH'%run: '/DoubleEG/Run2016H-07Aug17-v1/AOD',
#    }

#job_units = 400 #miniaod
job_units = 50 #aod
samples = {
    'DYToEE': '/DYToEE_M-50_NNPDF31_13TeV-powheg-pythia8/RunIIFall17DRPremix-94X_mc2017_realistic_v10-v1/AODSIM'
    #'DYToEE': '/DYToEE_M-50_NNPDF31_13TeV-powheg-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM'
    }

for s,dset in samples.iteritems(): #python3: samples.items()

    print('For sample:',s)

    assert os.environ['CMSSW_BASE'] != ''
    base_dir = '%s/src'%os.environ['CMSSW_BASE']

    evt_list = '%s/h2aa/evtsToProc_zee/%s_zee_ggskim_event_list.txt'%(base_dir, s.replace('-MINIAOD',''))
    assert os.path.isfile(evt_list), '%s not found'%evt_list

    lumi_list = '%s/h2aa/evtsToProc_zee/%s_zee_ggskim_lumi_list.json'%(base_dir, s.replace('-MINIAOD',''))
    assert os.path.isfile(lumi_list), '%s not found'%lumi_list

    # Read in crabConfig template
    with open('crabConfig_AODtoAODslim-ecal_pick.py', "r") as template_file:
        file_data = template_file.read()

    # Replace crabConfig template strings with sample-specific values
    file_data = file_data.replace(SAMPLE, s)
    file_data = file_data.replace(DATASET, dset)
    file_data = file_data.replace(CAMPAIGN, this_campaign)
    file_data = file_data.replace(UNITSPERJOB, str(job_units))
    file_data = file_data.replace(EVTLIST, evt_list)
    file_data = file_data.replace(LUMIMASK, lumi_list)

    # Write out sample-specific crabConfig
    with open('%s/crabConfig_AODtoAODslim-ecal_pick_%s.py'%(crab_folder, s), "w") as sample_file:
        sample_file.write(file_data)
