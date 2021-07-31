from __future__ import print_function
from multiprocessing import Pool
import os, re, glob, shutil
import numpy as np
import subprocess

# Strings to replace in crabConfig template
SAMPLE = '__SAMPLE__'
DATASET = '__DATASET__'
EVTLIST = '__EVTLIST__'
LUMIMASK = '__LUMIMASK__'
CAMPAIGN = '__CAMPAIGN__'
UNITSPERJOB = '__UNITSPERJOB__'
SPLIT = '__SPLIT__'

input_campaign = 'ggNtuples-Era24Sep2020v1_ggSkimZee-v3' # data+dy zee skim(nele+presel)

# do dy+data miniaod skims with zee event skim
#this_campaign = 'Era2017_16Feb2021_MINIAOD-skimv1' # excessive mem -> reduce data to 20 job units, inc max mem

#this_campaign = 'Era2017_16Feb2021_MINIAOD-skimv2' # 20 job units, inc max mem
#this_campaign = 'Era2016_16Feb2021_MINIAOD-skimv2' # 20 job units, inc max mem
this_campaign = 'Era2018_16Feb2021_MINIAOD-skimv2' # 20 job units, inc max mem

crab_folder = 'crab_%s'%this_campaign
if not os.path.isdir(crab_folder):
    os.makedirs(crab_folder)

#'''
samples = {
    #2016
    'data2016-Run2016B': "/DoubleEG/Run2016B-17Jul2018_ver2-v1/MINIAOD",
    'data2016-Run2016C': "/DoubleEG/Run2016C-17Jul2018-v1/MINIAOD",
    'data2016-Run2016D': "/DoubleEG/Run2016D-17Jul2018-v1/MINIAOD",
    'data2016-Run2016E': "/DoubleEG/Run2016E-17Jul2018-v1/MINIAOD",
    'data2016-Run2016F': "/DoubleEG/Run2016F-17Jul2018-v1/MINIAOD",
    'data2016-Run2016G': "/DoubleEG/Run2016G-17Jul2018-v1/MINIAOD",
    'data2016-Run2016H': "/DoubleEG/Run2016H-17Jul2018-v1/MINIAOD",
    'bg2016-dy':  '/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext2-v1/MINIAODSIM',

    #2017
    'data2017-Run2017B': '/DoubleEG/Run2017B-31Mar2018-v1/MINIAOD',
    'data2017-Run2017C': '/DoubleEG/Run2017C-31Mar2018-v1/MINIAOD',
    'data2017-Run2017D': '/DoubleEG/Run2017D-31Mar2018-v1/MINIAOD',
    'data2017-Run2017E': '/DoubleEG/Run2017E-31Mar2018-v1/MINIAOD',
    'data2017-Run2017F': '/DoubleEG/Run2017F-31Mar2018-v1/MINIAOD',
    'bg2017-dy':  '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/MINIAODSIM',

    #2018
    'data2018-Run2018A': "/EGamma/Run2018A-17Sep2018-v2/MINIAOD",
    'data2018-Run2018B': "/EGamma/Run2018B-17Sep2018-v1/MINIAOD",
    'data2018-Run2018C': "/EGamma/Run2018C-17Sep2018-v1/MINIAOD",
    'data2018-Run2018D': "/EGamma/Run2018D-22Jan2019-v2/MINIAOD",
    'bg2018-dy':  '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext2-v1/MINIAODSIM'
    }
#'''

'''
#job_units = 100
job_units = 1000
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
    'GluGluHToGG':
        '/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM'
    }
'''

for s,dset in samples.iteritems(): #python3: samples.items()

    #if 'data2018-Run2018A' not in s: continue

    #if 'data2018' not in s: continue
    #if 'data2017' not in s: continue
    #if 'data2016' not in s: continue

    #if 'h4g2016' not in s: continue
    #if 'h4g2017' not in s: continue
    #if 'h4g2018' not in s: continue

    #if '2016-dy' not in s: continue
    #if '2017-dy' not in s: continue
    #if '2018-dy' not in s: continue

    #if '2016' not in s: continue
    #if '2017' not in s: continue
    if '2018' not in s: continue

    #if 'h4g' not in s and 'hgg' not in s: continue

    print('For sample:',s)

    #assert os.environ['CMSSW_BASE'] != ''
    #base_dir = '%s/src'%os.environ['CMSSW_BASE']

    year = re.findall('(201[6-8])', s.split('-')[0])[0]
    base_dir = '/eos/uscms/store/user/lpchaa4g/mandrews/%s/%s/ggSkims'%(year, input_campaign)

    #evt_list = '%s/%s_event_list.txt'%(base_dir, s)
    evt_lists = glob.glob('%s/%s*_event_list.txt'%(base_dir, s))
    for evt_list in evt_lists:

        assert os.path.isfile(evt_list), '%s not found'%evt_list
        s = evt_list.split('/')[-1].split('_')[0]

        print('  >> Doing:',s)

        # Run edmPickEvents on filtered event list for this sample
        # Itemized by runId:lumiId:eventId
        cmd = 'edmPickEvents.py "%s" %s --crab'%(dset[0], evt_list)
        returncode = subprocess.call(cmd.split(' '))
        if returncode != 0:
            raise Exception('edmPickEvents failed')

        # Copy generated lumi mask
        lumi_list = '%s/%s_lumi_list.json'%(base_dir, s)
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
        file_data = file_data.replace(CAMPAIGN, this_campaign)

        splitting = 'LumiBased'
        job_units = 20
        if 'dy' in s:
            # DY samples too large to query lumi-based info
            lumi_list = 'None'
            splitting = 'FileBased'
            job_units = 1

        file_data = file_data.replace(SPLIT, splitting)
        file_data = file_data.replace(UNITSPERJOB, str(job_units))
        file_data = file_data.replace(LUMIMASK, lumi_list)

        # Write out sample-specific crabConfig
        with open('%s/crabConfig_pickEvents_%s.py'%(crab_folder, s), "w") as sample_file:
            sample_file.write(file_data)