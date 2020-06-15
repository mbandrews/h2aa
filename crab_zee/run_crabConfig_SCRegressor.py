from __future__ import print_function
from multiprocessing import Pool
import os, glob, shutil, re
import numpy as np
import subprocess
from Utilities.General.cmssw_das_client import get_data as das_query
from FWCore.PythonUtilities.LumiList import LumiList

# Strings to replace in crabConfig template
SAMPLE = '__SAMPLE__'
DATASET = '__DATASET__'
SECONDARYDATASET = '__SECONDARYDATASET__'
EVTLIST = '__EVTLIST__'
LUMIMASK = '__LUMIMASK__'
CAMPAIGN = '__CAMPAIGN__'
UNITSPERJOB = '__UNITSPERJOB__'

#this_campaign = 'Era2017_16Apr2020_IMGv1'
#this_campaign = 'Era2017_11May2020_MINIAOD-IMGv1'
#this_campaign = 'Era2017_11May2020_AOD-IMGv1'
this_campaign = 'Era2017_27May2020_AOD-IMGv2'

crab_folder = 'crab_%s'%this_campaign
if not os.path.isdir(crab_folder):
    os.makedirs(crab_folder)

'''
run = 'Run2017'
#job_units = 400 #miniaod
job_units = 50 #aod
# key: [<primary dset>, <secondary dset>]
samples = {
#    '%sB0'%run: [
#                '/DoubleEG/mandrews-Run2017B0_Era2017_27May2020_MINIAOD-skimzeev1-84d4062339350c0b82cf1392552beb97/USER',
#                '/DoubleEG/mandrews-DoubleEG_2017B_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER',
#                ],
    '%sB1'%run: [
                '/DoubleEG/mandrews-Run2017B1_Era2017_27May2020_MINIAOD-skimzeev1-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-DoubleEG_2017B_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER',
                ],
    '%sB2'%run: [
                '/DoubleEG/mandrews-Run2017B2_Era2017_27May2020_MINIAOD-skimzeev1-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-DoubleEG_2017B_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER',
                ],

    '%sC0'%run: [
                '/DoubleEG/mandrews-Run2017C0_Era2017_27May2020_MINIAOD-skimzeev1-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-DoubleEG_2017C_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER',
                ],
    '%sC1'%run: [
                '/DoubleEG/mandrews-Run2017C1_Era2017_27May2020_MINIAOD-skimzeev1-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-DoubleEG_2017C_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER',
                ],
    '%sC2'%run: [
                '/DoubleEG/mandrews-Run2017C2_Era2017_27May2020_MINIAOD-skimzeev1-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-DoubleEG_2017C_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER',
                ],
    '%sC3'%run: [
                '/DoubleEG/mandrews-Run2017C3_Era2017_27May2020_MINIAOD-skimzeev1-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-DoubleEG_2017C_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER',
                ],

    '%sD0'%run: [
                '/DoubleEG/mandrews-Run2017D0_Era2017_27May2020_MINIAOD-skimzeev1-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-DoubleEG_2017D_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER',
                ],
    '%sD1'%run: [
                '/DoubleEG/mandrews-Run2017D1_Era2017_27May2020_MINIAOD-skimzeev1-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-DoubleEG_2017D_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER',
                ],

    '%sE0'%run: [
                '/DoubleEG/mandrews-Run2017E0_Era2017_27May2020_MINIAOD-skimzeev1-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-DoubleEG_2017E_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER',
                ],
    '%sE1'%run: [
                '/DoubleEG/mandrews-Run2017E1_Era2017_27May2020_MINIAOD-skimzeev1-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-DoubleEG_2017E_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER',
                ],
    '%sE2'%run: [
                '/DoubleEG/mandrews-Run2017E2_Era2017_27May2020_MINIAOD-skimzeev1-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-DoubleEG_2017E_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER',
                ],
    '%sE3'%run: [
                '/DoubleEG/mandrews-Run2017E3_Era2017_27May2020_MINIAOD-skimzeev1-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-DoubleEG_2017E_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER',
                ],

    '%sF0'%run: [
                '/DoubleEG/mandrews-Run2017F0_Era2017_27May2020_MINIAOD-skimzeev1-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-DoubleEG_2017F_Era2017_18May2020_AODslim-ecal_v1-964eedbb4080135606054ba835f474dc/USER',
                ],
    '%sF1'%run: [
                '/DoubleEG/mandrews-Run2017F1_Era2017_27May2020_MINIAOD-skimzeev1-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-DoubleEG_2017F_Era2017_18May2020_AODslim-ecal_v1-964eedbb4080135606054ba835f474dc/USER',
                ],
    '%sF2'%run: [
                '/DoubleEG/mandrews-Run2017F2_Era2017_27May2020_MINIAOD-skimzeev1-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-DoubleEG_2017F_Era2017_18May2020_AODslim-ecal_v1-964eedbb4080135606054ba835f474dc/USER',
                ],
    '%sF3'%run: [
                '/DoubleEG/mandrews-Run2017F3_Era2017_27May2020_MINIAOD-skimzeev1-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-DoubleEG_2017F_Era2017_18May2020_AODslim-ecal_v1-964eedbb4080135606054ba835f474dc/USER',
                ]
    }
'''
#'''
#job_units = 400 #miniaod
job_units = 50 #aod
samples = {
    #'DiPhotonJets':   [
    #    '/DiPhotonJets_MGG-80toInf_13TeV_amcatnloFXFX_pythia8/mandrews-DiPhotonJets_Era2017_17Dec2019_MINIAOD-skimv1-18783c0a07109245951450a1a4f55409/USER',
    #    '/DiPhotonJets_MGG-80toInf_13TeV_amcatnloFXFX_pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM'],
    #'GJet_Pt20To40':  [
    #    '/GJet_Pt-20to40_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8/mandrews-GJet_Pt20To40_Era2017_17Dec2019_MINIAOD-skimv1-18783c0a07109245951450a1a4f55409/USER',
    #    '/GJet_Pt-20to40_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM'],
    #'GJet_Pt40ToInf': [
    #    '/GJet_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8/mandrews-GJet_Pt40ToInf_Era2017_17Dec2019_MINIAOD-skimv1-5f646ecd4e1c7a39ab0ed099ff55ceb9/USER',
    #    '/GJet_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/MINIAODSIM'],
    #'QCD_Pt30To40':   [
    #    '/QCD_Pt-30to40_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8/mandrews-QCD_Pt30To40_Era2017_17Dec2019_MINIAOD-skimv1-18783c0a07109245951450a1a4f55409/USER',
    #    '/QCD_Pt-30to40_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM'],
    #'QCD_Pt40ToInf':  [
    #    '/QCD_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8/mandrews-QCD_Pt40ToInf_Era2017_17Dec2019_MINIAOD-skimv1-18783c0a07109245951450a1a4f55409/USER',
    #    '/QCD_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM'],
    #'GluGluHToGG':    [
    #    '/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/mandrews-GluGluHToGG_Era2017_23Feb2020_MINIAOD-skimv1-18783c0a07109245951450a1a4f55409/USER',
    #    '/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM'],
    'DYtoEE': [
        '/DYToEE_M-50_NNPDF31_13TeV-powheg-pythia8/mandrews-DYToEE_Era2017_27May2020_MINIAOD-skimzeev1-18783c0a07109245951450a1a4f55409/USER',
        '/DYToEE_M-50_NNPDF31_13TeV-powheg-pythia8/mandrews-DYToEE_Era2017_27May2020_AODslim-ecal_v1-3e98cc8e83f1853b5c5f781f2307a57e/USER'
        #'/DYToEE_M-50_NNPDF31_13TeV-powheg-pythia8/mandrews-DYToEE_Era2017_27May2020_AODslim-ecal_pick_v1-443f35f23358d50dd133f8dcb9fe30d9/USER'
        ]
    }
#'''

for s,dset in samples.iteritems(): #python3: samples.items()

    print('For sample:',s)

    assert os.environ['CMSSW_BASE'] != ''
    base_dir = '%s/src'%os.environ['CMSSW_BASE']

    '''
    #evt_list = '%s/flashgg/evtsToProc/%s_2photons_EBonly_event_list.txt'%(base_dir, s)
    evt_list = '%s/h2aa/evtsToProc/%s_2photons_ggskim_event_list.txt'%(base_dir, s.replace('-MINIAOD',''))
    assert os.path.isfile(evt_list), '%s not found'%evt_list

    # Run edmPickEvents on filtered event list for this sample
    # Itemized by runId:lumiId:eventId
    cmd = 'edmPickEvents.py "%s" %s --crab'%(dset[0], evt_list)
    returncode = subprocess.call(cmd.split(' '))
    if returncode != 0:
        raise Exception('edmPickEvents failed')

    # Copy generated lumi mask
    #lumi_list = '%s/flashgg/evtsToProc/%s_2photons_EBonly_lumi_list.json'%(base_dir, s)
    lumi_list = '%s/h2aa/evtsToProc/%s_2photons_ggskim_lumi_list.json'%(base_dir, s.replace('-MINIAOD',''))
    shutil.move('%s/pickevents.json'%os.getcwd(), '%s'%(lumi_list)) # shutil.move(src, dest)
    '''

    # Read in crabConfig template
    #with open('crabConfig_SCRegressor_pickEvts.py', "r") as template_file:
    with open('crabConfig_SCRegressor.py', "r") as template_file:
        file_data = template_file.read()

    # Replace crabConfig template strings with sample-specific values
    # NOTE: event list generated by edmPickEvents (pickevents_runEvents.txt) does not include LS numbers!!
    # This gives non-unique eventIds and so MUST be replaced with the original input `evt_list` above!
    file_data = file_data.replace(SAMPLE, s)
    # dset workaround: AOD-slim goes to primary inputDataset and MINIAOD goes to secondaryInputDataset so that
    # inputDBS can point to phys03 where AOD-slims are located
    file_data = file_data.replace(DATASET, dset[0])
    file_data = file_data.replace(SECONDARYDATASET, dset[1])
    #file_data = file_data.replace(EVTLIST, evt_list)
    '''
    if 'Run2017' in s:
        #lumi_list = '%s/h2aa/evtsToProc/%s_3photons_imgskim_lumi_list.json'%(base_dir, s.replace('-MINIAOD',''))
        lumi_list = '%s/h2aa/evtsToProc/%s_3photons_imgskim_lumi_list.json'%(base_dir, re.sub('(201[6-8][A-Z])[0-9]','\\1',s.replace('-MINIAOD','')))
        assert os.path.isfile(lumi_list)
        file_data = file_data.replace(LUMIMASK, lumi_list)
    '''
    file_data = file_data.replace(CAMPAIGN, this_campaign)
    file_data = file_data.replace(UNITSPERJOB, str(job_units))

    #break
    # Write out sample-specific crabConfig
    with open('%s/crabConfig_SCRegressor_%s.py'%(crab_folder, s), "w") as sample_file:
        sample_file.write(file_data)

