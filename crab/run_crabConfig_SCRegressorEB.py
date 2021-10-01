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
SPLIT = '__SPLIT__'

# If lumimask used on aodskims
aodskim_campaign = 'Era06Sep2020_AODslim-ecal_v1' # Run2018A, Run2016H, 2018*, DY2016
#aodskim_campaign = 'Era28Dec2020_AODslim-ecal_v1' # Run2016H re-AODslim with missing blocks
#aodskim_campaign = 'Era06Sep2020_AODslim-ecal_v2' # DY2017
# If running on whole MINIAOD/AOD dset instead of skim, apply evtlist
#ggskim_campaign = 'ggNtuples-Era24Sep2020v1_ggSkim-v2' # 2018A. data+h4g+hgg, bad h4g,hgg dipho trgs
#ggskim_campaign = 'ggNtuples-Era20May2021v1_ggSkim-v1'  # Add mgg95 trgs for data, h4g, hgg
ggskim_campaign = 'ggNtuples-Era20May2021v1_ggSkim-v2'  # h4g: do NOT apply HLT dipho trg--applied later using trg SFs instead

# run fillEB on AOD only. mgg95 trgs for data, h4g, hgg
#this_campaign = 'Era2016_22Jun2021_AOD-IMGv1'
#this_campaign = 'Era2017_22Jun2021_AOD-IMGv1'
#this_campaign = 'Era2018_22Jun2021_AOD-IMGv1'

# h4g: do NOT apply HLT dipho trg--applied later using trg SFs instead
#this_campaign = 'Era2016_22Jun2021_AOD-IMGv2'
#this_campaign = 'Era2017_22Jun2021_AOD-IMGv2'
this_campaign = 'Era2018_22Jun2021_AOD-IMGv2'

crab_folder = 'crab_%s'%this_campaign
if not os.path.isdir(crab_folder):
    os.makedirs(crab_folder)

samples = {}

# 2016
era_ = 2016
samples_data2016 = [
    'B0', 'B1',
    'C',
    'D',
    'E',
    'F',
    'G0', 'G1',
    'H0', 'H1']
for s in samples_data2016:
    if 'G' in s or 'H' in s:
        samples['data%s-Run2016%s'%(era_, s)] = [
            '/DoubleEG/mandrews-DoubleEG_2016%s_Era2016_06Sep2020_AODslim-ecal_v1-2427c69bd126da1063d393ec79219651/USER'%s[0]
            ]
    else:
        samples['data%s-Run2016%s'%(era_, s)] = [
            '/DoubleEG/mandrews-DoubleEG_2016%s_Era2016_06Sep2020_AODslim-ecal_v1-81ba725143e8ad84d6b47c9ab0eb90c4/USER'%s[0]
            ]

samples_h4g = ['0p1', '0p2', '0p4', '0p6', '0p8', '1p0', '1p2']
for s in samples_h4g:
    samples['h4g%s-mA%sGeV'%(era_, s)] = [
        '/HAHMHToAA_AToGG_MA-%sGeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA%sGeV_Era2016_06Sep2020_AODslim-ecal_v1-f7b11725a86c799f51ca60747917325e/USER'%(s.replace('p0',''), s)
        ]
samples['bg2016-hgg'] = [
            '/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/mandrews-GluGluHToGG_Era2016_06Sep2020_AODslim-ecal_v2-b1a4edca9adfa7a2e4059536bf605cd7/USER'
            ]

# 2017
era_ = 2017
samples_data2017 = [
    'B',
    'C0', 'C1',
    'D',
    'E0', 'E1',
    'F0', 'F1']
for s in samples_data2017:
    if 'F' in s:
        samples['data%s-Run2017%s'%(era_, s)] = [
            '/DoubleEG/mandrews-DoubleEG_2017%s_Era2017_18May2020_AODslim-ecal_v1-964eedbb4080135606054ba835f474dc/USER'%s[0]
            ]
    else:
        samples['data%s-Run2017%s'%(era_, s)] = [
            '/DoubleEG/mandrews-DoubleEG_2017%s_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER'%s[0]
            ]

samples_h4g = ['0p1', '0p2', '0p4', '0p6', '0p8', '1p0', '1p2']
for s in samples_h4g:
    samples['h4g%s-mA%sGeV'%(era_, s)] = [
        '/HAHMHToAA_AToGG_MA-%sGeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA%sGeV_Era2017_06Sep2020_AODslim-ecal_v1-c3d6de13a4792afb4dd0c4ab58e49a3d/USER'%(s.replace('p0',''), s)
        ]
samples['bg2017-hgg'] = [
            '/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/mandrews-GluGluHToGG_Era2017_18May2020_AODslim-ecal_v1-351414bbda2cdc38d49da1680cef2a3f/USER'
            ]

# 2018
samples_data2018 = [
    'A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7',
    'B0', 'B1', 'B2', 'B3', 'B4',
    'C0', 'C1', 'C2', 'C3',
    'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8']
for s in samples_data2018:
    if 'D' in s:
        samples['data2018-Run2018%s'%s] = [
            '/EGamma/mandrews-EGamma_2018%s_Era2018_06Sep2020_AODslim-ecal_v1-306144291bb2d755797972fd22d33d6d/USER'%s[0]
            ]
    else:
        samples['data2018-Run2018%s'%s] = [
            '/EGamma/mandrews-EGamma_2018%s_Era2018_06Sep2020_AODslim-ecal_v1-6e67610c0756643cd1efca7b7fd48fa1/USER'%s[0]
            ]

samples_h4g = ['0p1', '0p2', '0p4', '0p6', '0p8', '1p0', '1p2']
for s in samples_h4g:
    samples['h4g2018-mA%sGeV'%s] = [
        '/HAHMHToAA_AToGG_MA-%sGeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA%sGeV_Era2018_06Sep2020_AODslim-ecal_v1-2fd59cbde119ecab78af65e08efe8aae/USER'%(s.replace('p0',''), s)
        ]
samples['bg2018-hgg'] = [
            '/GluGluHToGG_M125_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-GluGluHToGG_Era2018_06Sep2020_AODslim-ecal_v2-2fd59cbde119ecab78af65e08efe8aae/USER'
            ]

for s,dset in samples.iteritems(): #python3: samples.items()

    #if 'data2017' not in s: continue
    if '2018' not in s: continue
    #if '2017' not in s: continue
    #if '2016' not in s: continue
    #if 'h4g' not in s and 'hgg' not in s: continue
    #if 'h4g' not in s: continue
    if 'hgg' not in s: continue
    #if 'Run2018A' not in s: continue
    #if 'Run2016' not in s: continue
    #if '0p6' not in s: continue
    #if 'Run2018' not in s: continue
    #if 'Run2018A' in s: continue
    #if 'dy' in s: continue

    print('>> For sample:',s)

    if len(dset) != 1:
        print('   !! incomplete sample. Skipping...')
        continue

    assert os.environ['CMSSW_BASE'] != ''
    base_dir = '%s/src'%os.environ['CMSSW_BASE']
    year = re.findall('(201[6-8])', s.split('-')[0])[0]

    #'''
    # Read in crabConfig template
    with open('crabConfig_SCRegressor.py', "r") as template_file:
        file_data = template_file.read()

    # Replace crabConfig template strings with sample-specific values
    file_data = file_data.replace(SAMPLE, s)
    file_data = file_data.replace(DATASET, dset[0])
    #file_data = file_data.replace(DATASET, dset[0])
    #file_data = file_data.replace(SECONDARYDATASET, dset[1])

    # evt and lumi masks
    ggskim_dir = '/eos/uscms/store/user/lpchaa4g/mandrews/%s/%s/ggSkims'%(year, ggskim_campaign)

    # These dsets had partial failures in AOD skim
    #if 'Run2018A' in s:
    if 'Run2018' in s or 'Run2016H' in s:

        # If lumimask needed on AOD skims (due to failed jobs)
        s_aod = re.findall('(.*201[6-8][A-Z])', s)[0]
        lumi_list = '%s/h2aa/aodSkims/%s/%s_lumi_list.json'%(base_dir, aodskim_campaign, s_aod)
        assert os.path.isfile(lumi_list)
        #assert aodskim_campaign.strip('Era') in dset[1]
        file_data = file_data.replace(LUMIMASK, lumi_list)

        '''
        # Include evt list if running on full aod/miniaod dsets
        if 'Run2018A' in s:
            year = re.findall('(201[6-8])', s.split('-')[0])[0]
            ggskim_dir = '/eos/uscms/store/user/lpchaa4g/mandrews/%s/%s/ggSkims'%(year, ggskim_campaign)
            evt_lists = glob.glob('%s/%s*_event_list.txt'%(ggskim_dir, s))
            assert len(evt_lists) == 1
            evt_list = evt_lists[0]
            assert os.path.isfile(evt_list), '%s not found'%evt_list
            file_data = file_data.replace(EVTLIST, evt_list)
        '''
    else:
        # Get lumi list from output of ggSkim
        lumi_lists = glob.glob('%s/%s*_lumi_list.json'%(ggskim_dir, s))
        assert len(lumi_lists) == 1
        lumi_list = lumi_lists[0]
        assert os.path.isfile(lumi_list), '%s not found'%lumi_list
        file_data = file_data.replace(LUMIMASK, lumi_list)

    # Since using AOD skims which have full stats, apply evt list filter
    evt_lists = glob.glob('%s/%s*_event_list.txt'%(ggskim_dir, s))
    assert len(evt_lists) == 1
    evt_list = evt_lists[0]
    assert os.path.isfile(evt_list), '%s not found'%evt_list
    file_data = file_data.replace(EVTLIST, evt_list)

    file_data = file_data.replace(CAMPAIGN, this_campaign)

    job_units = 30 #30,50
    splitting = 'LumiBased'
    if 'data2016' in s:
        job_units = 30
    #if 'Run2018A' in s:
    #    # if running full MINIAOD/AOD to minimize fails -> doesnt seem to help
    #    job_units = 4
    #    splitting = 'FileBased'
    elif 'h4g' in s or 'bg' in s:
        job_units = 50
    #elif 'Run2018' in s:
    #    job_units = 50
    file_data = file_data.replace(UNITSPERJOB, str(job_units))
    file_data = file_data.replace(SPLIT, splitting)

    #break
    # Write out sample-specific crabConfig
    print(crab_folder)
    with open('%s/crabConfig_SCRegressor_%s.py'%(crab_folder, s), "w") as sample_file:
        sample_file.write(file_data)

    #'''
