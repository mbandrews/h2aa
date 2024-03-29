from __future__ import print_function
from multiprocessing import Pool
import os, glob, shutil
import numpy as np
import subprocess

# Strings to replace in crabConfig template
SAMPLE = '__SAMPLE__'
DATASET = '__DATASET__'
EVTLIST = '__EVTLIST__'
LUMIMASK = '__LUMIMASK__'
CAMPAIGN = '__CAMPAIGN__'
UNITSPERJOB = '__UNITSPERJOB__'

#this_campaign = 'Era2017_16Apr2020_MINIAOD-skimzeev1'
#this_campaign = 'Era2017_16Apr2020_MINIAOD-skimzeev2'
#this_campaign = 'Era2017_16Apr2020_MINIAOD-skimzeev3'
#this_campaign = 'Era2017_16Apr2020_MINIAOD-skimzeev4'
this_campaign = 'Era2017_27May2020_MINIAOD-skimzeev1'

crab_folder = 'crab_%s'%this_campaign
if not os.path.isdir(crab_folder):
    os.makedirs(crab_folder)

'''
run = 'Run2016'
job_units = 800
samples = {
    '%sB'%run: "/DoubleEG/Run2016B-17Jul2018_ver2-v1/MINIAOD",
    '%sC'%run: "/DoubleEG/Run2016C-17Jul2018-v1/MINIAOD",
    '%sD'%run: "/DoubleEG/Run2016D-17Jul2018-v1/MINIAOD",
    '%sE'%run: "/DoubleEG/Run2016E-17Jul2018-v1/MINIAOD",
    '%sF'%run: "/DoubleEG/Run2016F-17Jul2018-v1/MINIAOD",
    '%sG'%run: "/DoubleEG/Run2016G-17Jul2018-v1/MINIAOD",
    '%sH'%run: "/DoubleEG/Run2016H-17Jul2018-v1/MINIAOD"
    }
'''

'''
#run = 'DoubleEG_2017'
run = 'Run2017'
#job_units = 500
#job_units = 300
job_units = 200
samples = {
    #'%sB'%run: '/DoubleEG/Run2017B-31Mar2018-v1/MINIAOD',
    '%sB0'%run: '/DoubleEG/Run2017B-31Mar2018-v1/MINIAOD',
    '%sB1'%run: '/DoubleEG/Run2017B-31Mar2018-v1/MINIAOD',
    '%sB2'%run: '/DoubleEG/Run2017B-31Mar2018-v1/MINIAOD',
    #'%sC'%run: '/DoubleEG/Run2017C-31Mar2018-v1/MINIAOD',
    '%sC0'%run: '/DoubleEG/Run2017C-31Mar2018-v1/MINIAOD',
    '%sC1'%run: '/DoubleEG/Run2017C-31Mar2018-v1/MINIAOD',
    '%sC2'%run: '/DoubleEG/Run2017C-31Mar2018-v1/MINIAOD',
    '%sC3'%run: '/DoubleEG/Run2017C-31Mar2018-v1/MINIAOD',
    #'%sD'%run: '/DoubleEG/Run2017D-31Mar2018-v1/MINIAOD',
    '%sD0'%run: '/DoubleEG/Run2017D-31Mar2018-v1/MINIAOD',
    '%sD1'%run: '/DoubleEG/Run2017D-31Mar2018-v1/MINIAOD',
    #'%sE'%run: '/DoubleEG/Run2017E-31Mar2018-v1/MINIAOD',
    '%sE0'%run: '/DoubleEG/Run2017E-31Mar2018-v1/MINIAOD',
    '%sE1'%run: '/DoubleEG/Run2017E-31Mar2018-v1/MINIAOD',
    '%sE2'%run: '/DoubleEG/Run2017E-31Mar2018-v1/MINIAOD',
    '%sE3'%run: '/DoubleEG/Run2017E-31Mar2018-v1/MINIAOD',
    #'%sF'%run: '/DoubleEG/Run2017F-31Mar2018-v1/MINIAOD'
    '%sF0'%run: '/DoubleEG/Run2017F-31Mar2018-v1/MINIAOD',
    '%sF1'%run: '/DoubleEG/Run2017F-31Mar2018-v1/MINIAOD',
    '%sF2'%run: '/DoubleEG/Run2017F-31Mar2018-v1/MINIAOD',
    '%sF3'%run: '/DoubleEG/Run2017F-31Mar2018-v1/MINIAOD'
    }
'''

'''
run = 'Run2018'
#job_units = 100
job_units = 50 #D
samples = {
    #'%sA'%run: "/EGamma/Run2018A-17Sep2018-v2/MINIAOD",
    #'%sB'%run: "/EGamma/Run2018B-17Sep2018-v1/MINIAOD",
    #'%sC'%run: "/EGamma/Run2018C-17Sep2018-v1/MINIAOD",
    '%sD'%run: "/EGamma/Run2018D-22Jan2019-v2/MINIAOD"
    }
'''

'''
job_units = 500
run = 'h24gamma_1j_1M'
samples = {
    '%s_100MeV'%run: '/h24gamma_01Nov2019-rhECAL/mandrews-h24gamma_1j_1M_100MeV_PU2017_MINIAODSIM_v2-919c80a76a70185609d372d13ecbc645/USER',
    '%s_400MeV'%run: '/h24gamma_01Nov2019-rhECAL/mandrews-h24gamma_1j_1M_400MeV_PU2017_MINIAODSIM_v2-919c80a76a70185609d372d13ecbc645/USER',
    '%s_1GeV'%run:   '/h24gamma_01Nov2019-rhECAL/mandrews-h24gamma_1j_1M_1GeV_PU2017_MINIAODSIM_v2-919c80a76a70185609d372d13ecbc645/USER',
    }
'''
#'''
#job_units = 500
#job_units = 300
job_units = 200
samples = {
#    'DiPhotonJets':
#        '/DiPhotonJets_MGG-80toInf_13TeV_amcatnloFXFX_pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM',
#    'GJet_Pt20To40':
#        '/GJet_Pt-20to40_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM',
#    'GJet_Pt40ToInf':
#        '/GJet_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/MINIAODSIM',
#    'QCD_Pt30To40':
#        '/QCD_Pt-30to40_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM',
#    'QCD_Pt40ToInf':
#        '/QCD_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM',
#    'GluGluHToGG':
#        '/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM'
    'DYToEE':
        '/DYToEE_M-50_NNPDF31_13TeV-powheg-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM'
    }
#'''

for s,dset in samples.iteritems(): #python3: samples.items()

    print('For sample:',s)

    assert os.environ['CMSSW_BASE'] != ''
    base_dir = '%s/src'%os.environ['CMSSW_BASE']

    evt_list = '%s/h2aa/evtsToProc_zee/%s_zee_ggskim_event_list.txt'%(base_dir, s.replace('-MINIAOD',''))
    assert os.path.isfile(evt_list), '%s not found'%evt_list

    # Run edmPickEvents on filtered event list for this sample
    # Itemized by runId:lumiId:eventId
    cmd = 'edmPickEvents.py "%s" %s --crab'%(dset[0], evt_list)
    returncode = subprocess.call(cmd.split(' '))
    if returncode != 0:
        raise Exception('edmPickEvents failed')

    # Copy generated lumi mask
    lumi_list = '%s/h2aa/evtsToProc_zee/%s_zee_ggskim_lumi_list.json'%(base_dir, s.replace('-MINIAOD',''))
    shutil.move('%s/pickevents.json'%os.getcwd(), '%s'%(lumi_list)) # shutil.move(src, dest)

    # Read in crabConfig template
    with open('crabConfig_pickEvents.py', "r") as template_file:
        file_data = template_file.read()

    # Replace crabConfig template strings with sample-specific values
    # NOTE: event list generated by edmPickEvents (pickevents_runEvents.txt) does not include LS numbers!!
    # This gives non-unique eventIds and so MUST be replaced with the original input `evt_list` above!
    file_data = file_data.replace(SAMPLE, s)
    file_data = file_data.replace(DATASET, dset)
    file_data = file_data.replace(EVTLIST, evt_list)
    file_data = file_data.replace(LUMIMASK, lumi_list)
    file_data = file_data.replace(CAMPAIGN, this_campaign)
    file_data = file_data.replace(UNITSPERJOB, str(job_units))

    # Write out sample-specific crabConfig
    with open('%s/crabConfig_pickEvents_%s_zee.py'%(crab_folder, s), "w") as sample_file:
        sample_file.write(file_data)
