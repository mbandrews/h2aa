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
LUMIMASK = '__LUMIMASK__'

#this_campaign = 'Era2016_15Jan2020_AODslim-ext_v1'
#this_campaign = 'Era2016_04May2020_AODslim-ecal_v1'
#this_campaign = 'Era2017_18May2020_AODslim-ecal_v1'
#this_campaign = 'Era2016_03Sep2020_AODslim-ecal_v1'
this_campaign = 'Era2016_06Sep2020_AODslim-ecal_v2'
#this_campaign = 'Era2018_06Sep2020_AODslim-ecal_v2'

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
#lumi_mask = 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt'

#run = 'DoubleEG_2017'
#job_units = 10
#samples = {
#    '%sB'%run: '/DoubleEG/Run2017B-17Nov2017-v1/AOD',
#    '%sC'%run: '/DoubleEG/Run2017C-17Nov2017-v1/AOD',
#    '%sD'%run: '/DoubleEG/Run2017D-17Nov2017-v1/AOD',
#    '%sE'%run: '/DoubleEG/Run2017E-17Nov2017-v1/AOD',
#    '%sF'%run: '/DoubleEG/Run2017F-17Nov2017-v1/AOD',
#    }
#lumi_mask = 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions17/13TeV/ReReco/Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt'

#run = 'EGamma_2018'
#job_units = 10
#samples = {
#    '%sA'%run: '/EGamma/Run2018A-17Sep2018-v2/AOD',
#    '%sB'%run: '/EGamma/Run2018B-17Sep2018-v1/AOD',
#    '%sC'%run: '/EGamma/Run2018C-17Sep2018-v1/AOD',
#    '%sD'%run: '/EGamma/Run2018D-22Jan2019-v2/AOD',
#    }
#lumi_mask = 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions18/13TeV/ReReco/Cert_314472-325175_13TeV_17SeptEarlyReReco2018ABC_PromptEraD_Collisions18_JSON.txt'

#job_units = 100
job_units = 50
samples = {
    'GluGluHToGG': '/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1/AODSIM'
    #'GluGluHToGG': '/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/RunIIFall17DRPremix-94X_mc2017_realistic_v10-v1/AODSIM'
    #'GluGluHToGG': '/GluGluHToGG_M125_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIAutumn18DRPremix-102X_upgrade2018_realistic_v15-v1/AODSIM'
    }

for s,dset in samples.iteritems(): #python3: samples.items()

    print('For sample:',s)

    assert os.environ['CMSSW_BASE'] != ''
    base_dir = '%s/src'%os.environ['CMSSW_BASE']

    # Read in crabConfig template
    with open('crabConfig_AODtoAODslim-ecal.py', "r") as template_file:
        file_data = template_file.read()


    # Replace crabConfig template strings with sample-specific values
    file_data = file_data.replace(SAMPLE, s)
    file_data = file_data.replace(DATASET, dset)
    file_data = file_data.replace(CAMPAIGN, this_campaign)
    file_data = file_data.replace(UNITSPERJOB, str(job_units))
    #file_data = file_data.replace(LUMIMASK, lumi_mask if 'DoubleEG' in s else None)
    if 'Run201' in dset:
        file_data = file_data.replace(LUMIMASK, lumi_mask)
    else:
        file_data = file_data.replace(LUMIMASK, str(None))

    # Write out sample-specific crabConfig
    with open('%s/crabConfig_AODtoAODslim-ecal_%s.py'%(crab_folder, s), "w") as sample_file:
        sample_file.write(file_data)
