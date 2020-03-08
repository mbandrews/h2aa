from __future__ import print_function
from multiprocessing import Pool
import os, glob, shutil
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

#this_campaign = 'Era2017_17Dec2019_IMGv1'
#this_campaign = 'Era2017_23Feb2020_IMGv1'
#this_campaign = 'Era2017_23Feb2020_IMGv2'
this_campaign = 'Era2017_23Feb2020_IMGv3'

crab_folder = 'crab_%s'%this_campaign
if not os.path.isdir(crab_folder):
    os.makedirs(crab_folder)

'''
#run = 'DoubleEG_2017'
run = 'Run2017'
job_units = 50
#samples = {
#    '%sB'%run: '/DoubleEG/mandrews-Run2017B_17Nov2017-v1_AOD_slim-ext_v2-3bfee02a0afb4bfd03fd5261a90623cd/USER',
#    '%sC'%run: '/DoubleEG/mandrews-Run2017C_17Nov2017-v1_AOD_slim-ext_v2-3bfee02a0afb4bfd03fd5261a90623cd/USER',
#    '%sD'%run: '/DoubleEG/mandrews-Run2017D_17Nov2017-v1_AOD_slim-ext-3bfee02a0afb4bfd03fd5261a90623cd/USER',
#    '%sE'%run: '/DoubleEG/mandrews-Run2017E_17Nov2017-v1_AOD_slim-ext_v2-3bfee02a0afb4bfd03fd5261a90623cd/USER',
#    '%sF'%run: '/DoubleEG/mandrews-Run2017F_17Nov2017-v1_AOD_slim-ext_v2-964eedbb4080135606054ba835f474dc/USER',
#    }
# key: [<primary dset>, <secondary dset>]
samples = {
    '%sB'%run: [
                #'/DoubleEG/mandrews-DoubleEG_2017B_Era2017_17Dec2019_MINIAOD-skimv1_MINIAOD-skim-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-Run2017B_Era2017_23Feb2020_MINIAOD-skimv1-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-Run2017B_17Nov2017-v1_AOD_slim-ext_v2-3bfee02a0afb4bfd03fd5261a90623cd/USER'],
    '%sC'%run: [
                #'/DoubleEG/mandrews-DoubleEG_2017C_Era2017_17Dec2019_MINIAOD-skimv1_MINIAOD-skim-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-Run2017C_Era2017_23Feb2020_MINIAOD-skimv1-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-Run2017C_17Nov2017-v1_AOD_slim-ext_v2-3bfee02a0afb4bfd03fd5261a90623cd/USER'],
    '%sD'%run: [
                #'/DoubleEG/mandrews-DoubleEG_2017D_Era2017_17Dec2019_MINIAOD-skimv1_MINIAOD-skim-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-Run2017D_Era2017_23Feb2020_MINIAOD-skimv1-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-Run2017D_17Nov2017-v1_AOD_slim-ext-3bfee02a0afb4bfd03fd5261a90623cd/USER'],
    '%sE'%run: [
                #'/DoubleEG/mandrews-DoubleEG_2017E_Era2017_17Dec2019_MINIAOD-skimv1_MINIAOD-skim-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-Run2017E_Era2017_23Feb2020_MINIAOD-skimv1-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-Run2017E_17Nov2017-v1_AOD_slim-ext_v2-3bfee02a0afb4bfd03fd5261a90623cd/USER'],
    '%sF'%run: [
                #'/DoubleEG/mandrews-DoubleEG_2017F_Era2017_17Dec2019_MINIAOD-skimv1_MINIAOD-skim-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-Run2017F_Era2017_23Feb2020_MINIAOD-skimv1-84d4062339350c0b82cf1392552beb97/USER',
                '/DoubleEG/mandrews-Run2017F_17Nov2017-v1_AOD_slim-ext_v2-964eedbb4080135606054ba835f474dc/USER']
    }
'''
'''
run = 'Run2017'
job_units = 1000
samples = {
    '%sB-MINIAOD'%run: '/DoubleEG/Run2017B-31Mar2018-v1/MINIAOD',
    '%sC-MINIAOD'%run: '/DoubleEG/Run2017C-31Mar2018-v1/MINIAOD',
    '%sD-MINIAOD'%run: '/DoubleEG/Run2017D-31Mar2018-v1/MINIAOD',
    '%sE-MINIAOD'%run: '/DoubleEG/Run2017E-31Mar2018-v1/MINIAOD',
    '%sF-MINIAOD'%run: '/DoubleEG/Run2017F-31Mar2018-v1/MINIAOD'
    }
'''
#'''
#job_units = 50
job_units = 100
run = 'h24gamma_1j_1M'
samples = {
    '%s_100MeV'%run: [
            #'/h24gamma_01Nov2019-rhECAL/mandrews-h24gamma_1j_1M_100MeV_Era2017_17Dec2019_MINIAOD-skimv1-919c80a76a70185609d372d13ecbc645/USER',
            '/h24gamma_01Nov2019-rhECAL/mandrews-h24gamma_1j_1M_100MeV_Era2017_23Feb2020_MINIAOD-skimv1-919c80a76a70185609d372d13ecbc645/USER',
            '/h24gamma_01Nov2019-rhECAL/mandrews-h24gamma_1j_1M_100MeV_PU2017_MINIAODSIM_v2-919c80a76a70185609d372d13ecbc645/USER'],
    '%s_400MeV'%run: [
            #'/h24gamma_01Nov2019-rhECAL/mandrews-h24gamma_1j_1M_400MeV_Era2017_17Dec2019_MINIAOD-skimv1-919c80a76a70185609d372d13ecbc645/USER',
            '/h24gamma_01Nov2019-rhECAL/mandrews-h24gamma_1j_1M_400MeV_Era2017_23Feb2020_MINIAOD-skimv1-919c80a76a70185609d372d13ecbc645/USER',
            '/h24gamma_01Nov2019-rhECAL/mandrews-h24gamma_1j_1M_400MeV_PU2017_MINIAODSIM_v2-919c80a76a70185609d372d13ecbc645/USER'],
    '%s_1GeV'%run:   [
            #'/h24gamma_01Nov2019-rhECAL/mandrews-h24gamma_1j_1M_1GeV_Era2017_17Dec2019_MINIAOD-skimv1-919c80a76a70185609d372d13ecbc645/USER',
            '/h24gamma_01Nov2019-rhECAL/mandrews-h24gamma_1j_1M_1GeV_Era2017_23Feb2020_MINIAOD-skimv1-919c80a76a70185609d372d13ecbc645/USER',
            '/h24gamma_01Nov2019-rhECAL/mandrews-h24gamma_1j_1M_1GeV_PU2017_MINIAODSIM_v2-919c80a76a70185609d372d13ecbc645/USER'],
    }
#'''
'''
job_units = 500
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
    'GluGluHToGG':    [
        #'/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/mandrews-GluGluHToGG_Era2017_17Dec2019_MINIAOD-skimv1-18783c0a07109245951450a1a4f55409/USER',
        '/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/mandrews-GluGluHToGG_Era2017_23Feb2020_MINIAOD-skimv1-18783c0a07109245951450a1a4f55409/USER',
        '/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM'],
    }
'''

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
    if 'Run2017' in s:
        lumi_list = '%s/h2aa/evtsToProc/%s_3photons_imgskim_lumi_list.json'%(base_dir, s.replace('-MINIAOD',''))
        assert os.path.isfile(lumi_list)
        file_data = file_data.replace(LUMIMASK, lumi_list)
    file_data = file_data.replace(CAMPAIGN, this_campaign)
    file_data = file_data.replace(UNITSPERJOB, str(job_units))

    #break
    # Write out sample-specific crabConfig
    with open('%s/crabConfig_SCRegressor_%s.py'%(crab_folder, s), "w") as sample_file:
        sample_file.write(file_data)

