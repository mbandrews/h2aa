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

#this_campaign = 'Era2017_17Dec2019_IMGv1'
#this_campaign = 'Era2017_23Feb2020_IMGv1'
#this_campaign = 'Era2017_23Feb2020_IMGv2'
#this_campaign = 'Era2017_23Feb2020_IMGv3'
#this_campaign = 'Era2017_07Apr2020_IMGv1'
#this_campaign = 'Era2017_11May2020_AOD-IMGv1'
#this_campaign = 'Era2017_11May2020_AOD-IMGv2'

# If lumimask used on aodskims
aodskim_campaign = 'Era06Sep2020_AODslim-ecal_v1' # Run2018A, Run2016H, 2018*, DY2016
#aodskim_campaign = 'Era28Dec2020_AODslim-ecal_v1' # Run2016H re-AODslim with missing blocks
#aodskim_campaign = 'Era06Sep2020_AODslim-ecal_v2' # DY2017
# If running on whole MINIAOD/AOD dset instead of skim, apply evtlist
#ggskim_campaign = 'ggNtuples-Era24Sep2020v1_ggSkim-v2' # 2018A. data+h4g+hgg, bad h4g,hgg dipho trgs
ggskim_campaign = 'ggNtuples-Era20May2021v1_ggSkim-v1'  # Add mgg95 trgs for data, h4g, hgg

# Era2016_06Sep2020_MINIAOD-skimv2+Era2016_06Sep2020_AODslim-ecal_v1
# h4g, hgg have bad dipho trgs. data, dy ok
#this_campaign = 'Era2016_06Sep2020_AOD-IMGv1'
#this_campaign = 'Era2017_06Sep2020_AOD-IMGv1'
#this_campaign = 'Era2018_06Sep2020_AOD-IMGv1'

# Era2016_04Dec2020_MINIAOD-skimv1+Era2016_06Sep2020_AODslim-ecal_v1
# h4g, hgg only, fixed dipho trg
# 2016H, 2018 missing aod lumis
#this_campaign = 'Era2016_04Dec2020_AOD-IMGv1'
#this_campaign = 'Era2017_04Dec2020_AOD-IMGv1'
#this_campaign = 'Era2018_04Dec2020_AOD-IMGv1'

# Era2016_06Sep2020_MINIAOD-skimv1+Era2016_06Sep2020_AODslim-ecal_v3
# 2016H+2018 data only
# fixed missing lumis: aods skimmed w/o lumimask
#this_campaign = 'Era2018_06Sep2020_AOD-IMGv2'

# v3: with lumimask due to missing lumis in aod
# FAIL: no parents [BAD-NoSite] -> problem with CMU T3 -> must include whiteList+ignoreLocality -> redo
#this_campaign = 'Era2016_06Sep2020_AOD-IMGv3' # Era2016_06Sep2020_MINIAOD-skimv2+Era2016_06Sep2020_AODslim-ecal_v1
#this_campaign = 'Era2018_06Sep2020_AOD-IMGv3' # 2018A:Era2018_06Sep2020_MINIAOD-skimv7+Era2018_06Sep2020_AODslim-ecal_v1 [BAD-NoParents], others: Era2018_06Sep2020_MINIAOD-skimv2+Era2018_06Sep2020_AODslim-ecal_v1
# v3: 2018 except A: redo v2 since even with no lumimask on AODslim-ecal_v3, few jobs still fail. See TEST_crabConfig_cmut3/.

# v4: 2018A using full MINIAOD+AOD and ggSkim evtlist+lumimask otherwise like v3: v3 gave submitfailed due to no parents
# v4: 2018 except A: redo v3 with less unitsPerJob since some jobs still failed due to code 134 and wall clock limit
#this_campaign = 'Era2018_06Sep2020_AOD-IMGv4'

# v5: 2018A: MINIAOD+AOD, like v4 data-only but with ggSkim evtlist+lumimask. v5, outcome: had missing crab whitelist
# v5: 2018 except A: redo v4 with even less unitsPerJob since takes too long
#this_campaign = 'Era2018_06Sep2020_AOD-IMGv5'

# MINIAOD+AOD
# 2018A data only with ggSkim evtlist+lumimask
# remove whitelist
# v5 had missing evtlist
#this_campaign = 'Era2018_06Sep2020_AOD-IMGv6' # some lumis still fail

# MINIAOD+AOD
# 2018A data only with ggSkim evtlist+lumimask
# minimize unitsPerJob, FileBased splitting
#this_campaign = 'Era2018_06Sep2020_AOD-IMGv7' # some lumis still fail
#this_campaign = 'Era2018_06Sep2020_AOD-IMGv8' # retry v7 since some failed. v8: mass failure--include T1 in whitelist
#this_campaign = 'Era2018_06Sep2020_AOD-IMGv9' # retry v8 and include T1*, T2* in whitelist

# 2016H: re-AODslim but with missing blocks
#this_campaign = 'Era2016_28Dec2020_AOD-IMGv1' # Era2016_06Sep2020_MINIAOD-skimv2+Era2016_28Dec2020_AODslim-ecal_v1

# Add mgg95 trgs for data, h4g, hgg
#this_campaign = 'Era2017_20May2021_AOD-IMGv1'
#this_campaign = 'Era2018_20May2021_AOD-IMGv1'

# run fillEB on AOD only
this_campaign = 'Era2018_22Jun2021_AOD-IMGv1'

crab_folder = 'crab_%s'%this_campaign
if not os.path.isdir(crab_folder):
    os.makedirs(crab_folder)

#'''
#job_units_ = 50
job_units_ = 30
# key: [<primary dset>, <secondary dset>]
samples = {
    # 2016
    'data2016-Run2016B': [
            '/DoubleEG/mandrews-data2016-Run2016B_Era2016_06Sep2020_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
            '/DoubleEG/mandrews-DoubleEG_2016B_Era2016_06Sep2020_AODslim-ecal_v1-81ba725143e8ad84d6b47c9ab0eb90c4/USER'
            ],
    'data2016-Run2016C': [
            '/DoubleEG/mandrews-data2016-Run2016C_Era2016_06Sep2020_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
            '/DoubleEG/mandrews-DoubleEG_2016C_Era2016_06Sep2020_AODslim-ecal_v1-81ba725143e8ad84d6b47c9ab0eb90c4/USER'
            ],
    'data2016-Run2016D': [
            '/DoubleEG/mandrews-data2016-Run2016D_Era2016_06Sep2020_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
            '/DoubleEG/mandrews-DoubleEG_2016D_Era2016_06Sep2020_AODslim-ecal_v1-81ba725143e8ad84d6b47c9ab0eb90c4/USER'
            ],
    'data2016-Run2016E': [
            '/DoubleEG/mandrews-data2016-Run2016E_Era2016_06Sep2020_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
            '/DoubleEG/mandrews-DoubleEG_2016E_Era2016_06Sep2020_AODslim-ecal_v1-81ba725143e8ad84d6b47c9ab0eb90c4/USER'
            ],
    'data2016-Run2016F': [
            '/DoubleEG/mandrews-data2016-Run2016F_Era2016_06Sep2020_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
            '/DoubleEG/mandrews-DoubleEG_2016F_Era2016_06Sep2020_AODslim-ecal_v1-81ba725143e8ad84d6b47c9ab0eb90c4/USER'
            ],
    'data2016-Run2016G': [
            '/DoubleEG/mandrews-data2016-Run2016G_Era2016_06Sep2020_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
            '/DoubleEG/mandrews-DoubleEG_2016G_Era2016_06Sep2020_AODslim-ecal_v1-2427c69bd126da1063d393ec79219651/USER'
            ],
    'data2016-Run2016H': [
            '/DoubleEG/mandrews-data2016-Run2016H_Era2016_06Sep2020_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
            #'/DoubleEG/mandrews-DoubleEG_2016H_Era2016_06Sep2020_AODslim-ecal_v1-2427c69bd126da1063d393ec79219651/USER'
            '/DoubleEG/mandrews-DoubleEG_2016H_Era2016_28Dec2020_AODslim-ecal_v1-2427c69bd126da1063d393ec79219651/USER'
            ],
    'h4g2016-mA0p1GeV': [
            #'/HAHMHToAA_AToGG_MA-0p1GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2016-mA0p1GeV_Era2016_06Sep2020_MINIAOD-skimv2-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
            '/HAHMHToAA_AToGG_MA-0p1GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2016-mA0p1GeV_Era2016_04Dec2020_MINIAOD-skimv1-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
            '/HAHMHToAA_AToGG_MA-0p1GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA0p1GeV_Era2016_06Sep2020_AODslim-ecal_v1-f7b11725a86c799f51ca60747917325e/USER'
            ],
    'h4g2016-mA0p2GeV': [
            #'/HAHMHToAA_AToGG_MA-0p2GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2016-mA0p2GeV_Era2016_06Sep2020_MINIAOD-skimv2-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
            '/HAHMHToAA_AToGG_MA-0p2GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2016-mA0p2GeV_Era2016_04Dec2020_MINIAOD-skimv1-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
            '/HAHMHToAA_AToGG_MA-0p2GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA0p2GeV_Era2016_06Sep2020_AODslim-ecal_v1-f7b11725a86c799f51ca60747917325e/USER'
            ],
    'h4g2016-mA0p4GeV': [
            #'/HAHMHToAA_AToGG_MA-0p4GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2016-mA0p4GeV_Era2016_06Sep2020_MINIAOD-skimv2-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
            '/HAHMHToAA_AToGG_MA-0p4GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2016-mA0p4GeV_Era2016_04Dec2020_MINIAOD-skimv1-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
            '/HAHMHToAA_AToGG_MA-0p4GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA0p4GeV_Era2016_06Sep2020_AODslim-ecal_v1-f7b11725a86c799f51ca60747917325e/USER'
            ],
    'h4g2016-mA0p6GeV': [
            #'/HAHMHToAA_AToGG_MA-0p6GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2016-mA0p6GeV_Era2016_06Sep2020_MINIAOD-skimv2-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
            '/HAHMHToAA_AToGG_MA-0p6GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2016-mA0p6GeV_Era2016_04Dec2020_MINIAOD-skimv1-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
            '/HAHMHToAA_AToGG_MA-0p6GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA0p6GeV_Era2016_06Sep2020_AODslim-ecal_v1-f7b11725a86c799f51ca60747917325e/USER'
            ],
    'h4g2016-mA0p8GeV': [
            #'/HAHMHToAA_AToGG_MA-0p8GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2016-mA0p8GeV_Era2016_06Sep2020_MINIAOD-skimv2-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
            '/HAHMHToAA_AToGG_MA-0p8GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2016-mA0p8GeV_Era2016_04Dec2020_MINIAOD-skimv1-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
            '/HAHMHToAA_AToGG_MA-0p8GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA0p8GeV_Era2016_06Sep2020_AODslim-ecal_v1-f7b11725a86c799f51ca60747917325e/USER'
            ],
    'h4g2016-mA1p0GeV': [
            #'/HAHMHToAA_AToGG_MA-1GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2016-mA1p0GeV_Era2016_06Sep2020_MINIAOD-skimv2-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
            '/HAHMHToAA_AToGG_MA-1GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2016-mA1p0GeV_Era2016_04Dec2020_MINIAOD-skimv1-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
            '/HAHMHToAA_AToGG_MA-1GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA1p0GeV_Era2016_06Sep2020_AODslim-ecal_v1-f7b11725a86c799f51ca60747917325e/USER'
            ],
    'h4g2016-mA1p2GeV': [
            #'/HAHMHToAA_AToGG_MA-1p2GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2016-mA1p2GeV_Era2016_06Sep2020_MINIAOD-skimv2-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
            '/HAHMHToAA_AToGG_MA-1p2GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2016-mA1p2GeV_Era2016_04Dec2020_MINIAOD-skimv1-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
            '/HAHMHToAA_AToGG_MA-1p2GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA1p2GeV_Era2016_06Sep2020_AODslim-ecal_v1-f7b11725a86c799f51ca60747917325e/USER'
            ],
    'bg2016-hgg': [
            #'/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/mandrews-bg2016-hgg_Era2016_06Sep2020_MINIAOD-skimv2-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
            '/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/mandrews-bg2016-hgg_Era2016_04Dec2020_MINIAOD-skimv1-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
            '/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/mandrews-GluGluHToGG_Era2016_06Sep2020_AODslim-ecal_v2-b1a4edca9adfa7a2e4059536bf605cd7/USER'
            ],
    'bg2016-dy0':  [
            '/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/mandrews-bg2016-dy0_Era2016_06Sep2020_MINIAOD-skimv3-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
            '/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/mandrews-DYToLL_Era2016_06Sep2020_AODslim-ecal_v1-b1a4edca9adfa7a2e4059536bf605cd7/USER'
            ],
    'bg2016-dy1':  [
            '/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/mandrews-bg2016-dy1_Era2016_06Sep2020_MINIAOD-skimv3-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
            '/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/mandrews-DYToLL_Era2016_06Sep2020_AODslim-ecal_v1-b1a4edca9adfa7a2e4059536bf605cd7/USER'
            ],
    'bg2016-dy2':  [
            '/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/mandrews-bg2016-dy2_Era2016_06Sep2020_MINIAOD-skimv3-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
            '/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/mandrews-DYToLL_Era2016_06Sep2020_AODslim-ecal_v1-b1a4edca9adfa7a2e4059536bf605cd7/USER'
            ],


    # 2017
    #'data2017-Run2017B': [
    #        '/DoubleEG/mandrews-data2017-Run2017B_Era2017_06Sep2020_MINIAOD-skimv2-84d4062339350c0b82cf1392552beb97/USER',
    #        '/DoubleEG/mandrews-DoubleEG_2017B_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER'
    #        ],
    #'data2017-Run2017C': [
    #        '/DoubleEG/mandrews-data2017-Run2017C_Era2017_06Sep2020_MINIAOD-skimv2-84d4062339350c0b82cf1392552beb97/USER',
    #        '/DoubleEG/mandrews-DoubleEG_2017C_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER'
    #        ],
    #'data2017-Run2017D': [
    #        '/DoubleEG/mandrews-data2017-Run2017D_Era2017_06Sep2020_MINIAOD-skimv2-84d4062339350c0b82cf1392552beb97/USER',
    #        '/DoubleEG/mandrews-DoubleEG_2017D_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER'
    #        ],
    #'data2017-Run2017E': [
    #        '/DoubleEG/mandrews-data2017-Run2017E_Era2017_06Sep2020_MINIAOD-skimv2-84d4062339350c0b82cf1392552beb97/USER',
    #        '/DoubleEG/mandrews-DoubleEG_2017E_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER'
    #        ],
    #'data2017-Run2017F': [
    #        '/DoubleEG/mandrews-data2017-Run2017F_Era2017_06Sep2020_MINIAOD-skimv2-84d4062339350c0b82cf1392552beb97/USER',
    #        '/DoubleEG/mandrews-DoubleEG_2017F_Era2017_18May2020_AODslim-ecal_v1-964eedbb4080135606054ba835f474dc/USER'
    #        ],
    #'h4g2017-mA0p1GeV': [
    #        #'/HAHMHToAA_AToGG_MA-0p1GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2017-mA0p1GeV_Era2017_06Sep2020_MINIAOD-skimv2-5f646ecd4e1c7a39ab0ed099ff55ceb9/USER',
    #        '/HAHMHToAA_AToGG_MA-0p1GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2017-mA0p1GeV_Era2017_04Dec2020_MINIAOD-skimv1-5f646ecd4e1c7a39ab0ed099ff55ceb9/USER',
    #        '/HAHMHToAA_AToGG_MA-0p1GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA0p1GeV_Era2017_06Sep2020_AODslim-ecal_v1-c3d6de13a4792afb4dd0c4ab58e49a3d/USER'
    #        ],
    #'h4g2017-mA0p2GeV': [
    #        #'/HAHMHToAA_AToGG_MA-0p2GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2017-mA0p2GeV_Era2017_06Sep2020_MINIAOD-skimv2-5f646ecd4e1c7a39ab0ed099ff55ceb9/USER',
    #        '/HAHMHToAA_AToGG_MA-0p2GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2017-mA0p2GeV_Era2017_04Dec2020_MINIAOD-skimv1-5f646ecd4e1c7a39ab0ed099ff55ceb9/USER',
    #        '/HAHMHToAA_AToGG_MA-0p2GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA0p2GeV_Era2017_06Sep2020_AODslim-ecal_v1-c3d6de13a4792afb4dd0c4ab58e49a3d/USER'
    #        ],
    #'h4g2017-mA0p4GeV': [
    #        #'/HAHMHToAA_AToGG_MA-0p4GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2017-mA0p4GeV_Era2017_06Sep2020_MINIAOD-skimv2-5f646ecd4e1c7a39ab0ed099ff55ceb9/USER',
    #        '/HAHMHToAA_AToGG_MA-0p4GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2017-mA0p4GeV_Era2017_04Dec2020_MINIAOD-skimv1-5f646ecd4e1c7a39ab0ed099ff55ceb9/USER',
    #        '/HAHMHToAA_AToGG_MA-0p4GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA0p4GeV_Era2017_06Sep2020_AODslim-ecal_v1-c3d6de13a4792afb4dd0c4ab58e49a3d/USER'
    #        ],
    #'h4g2017-mA0p6GeV': [
    #        #'/HAHMHToAA_AToGG_MA-0p6GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2017-mA0p6GeV_Era2017_06Sep2020_MINIAOD-skimv2-5f646ecd4e1c7a39ab0ed099ff55ceb9/USER',
    #        '/HAHMHToAA_AToGG_MA-0p6GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2017-mA0p6GeV_Era2017_04Dec2020_MINIAOD-skimv1-5f646ecd4e1c7a39ab0ed099ff55ceb9/USER',
    #        '/HAHMHToAA_AToGG_MA-0p6GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA0p6GeV_Era2017_06Sep2020_AODslim-ecal_v1-c3d6de13a4792afb4dd0c4ab58e49a3d/USER'
    #        ],
    #'h4g2017-mA0p8GeV': [
    #        #'/HAHMHToAA_AToGG_MA-0p8GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2017-mA0p8GeV_Era2017_06Sep2020_MINIAOD-skimv2-5f646ecd4e1c7a39ab0ed099ff55ceb9/USER',
    #        '/HAHMHToAA_AToGG_MA-0p8GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2017-mA0p8GeV_Era2017_04Dec2020_MINIAOD-skimv1-5f646ecd4e1c7a39ab0ed099ff55ceb9/USER',
    #        '/HAHMHToAA_AToGG_MA-0p8GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA0p8GeV_Era2017_06Sep2020_AODslim-ecal_v1-c3d6de13a4792afb4dd0c4ab58e49a3d/USER'
    #        ],
    #'h4g2017-mA1p0GeV': [
    #        #'/HAHMHToAA_AToGG_MA-1GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2017-mA1p0GeV_Era2017_06Sep2020_MINIAOD-skimv2-5f646ecd4e1c7a39ab0ed099ff55ceb9/USER',
    #        '/HAHMHToAA_AToGG_MA-1GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2017-mA1p0GeV_Era2017_04Dec2020_MINIAOD-skimv1-5f646ecd4e1c7a39ab0ed099ff55ceb9/USER',
    #        '/HAHMHToAA_AToGG_MA-1GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA1p0GeV_Era2017_06Sep2020_AODslim-ecal_v1-c3d6de13a4792afb4dd0c4ab58e49a3d/USER'
    #        ],
    #'h4g2017-mA1p2GeV': [
    #        #'/HAHMHToAA_AToGG_MA-1p2GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2017-mA1p2GeV_Era2017_06Sep2020_MINIAOD-skimv2-5f646ecd4e1c7a39ab0ed099ff55ceb9/USER',
    #        '/HAHMHToAA_AToGG_MA-1p2GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2017-mA1p2GeV_Era2017_04Dec2020_MINIAOD-skimv1-5f646ecd4e1c7a39ab0ed099ff55ceb9/USER',
    #        '/HAHMHToAA_AToGG_MA-1p2GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA1p2GeV_Era2017_06Sep2020_AODslim-ecal_v1-c3d6de13a4792afb4dd0c4ab58e49a3d/USER'
    #        ],
    'bg2017-hgg': [
            #'/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/mandrews-bg2017-hgg_Era2017_06Sep2020_MINIAOD-skimv2-18783c0a07109245951450a1a4f55409/USER',
            #'/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/mandrews-bg2017-hgg_Era2017_04Dec2020_MINIAOD-skimv1-18783c0a07109245951450a1a4f55409/USER',
            '/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/mandrews-bg2017-hgg_Era2017_20May2021_MINIAOD-skimv1-18783c0a07109245951450a1a4f55409/USER',
            '/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/mandrews-GluGluHToGG_Era2017_18May2020_AODslim-ecal_v1-351414bbda2cdc38d49da1680cef2a3f/USER'
            ],
    'bg2017-dy0':  [
            '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2017-dy0_Era2017_06Sep2020_MINIAOD-skimv3-18783c0a07109245951450a1a4f55409/USER',
            '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-DYToLL_Era2017_06Sep2020_AODslim-ecal_v2-351414bbda2cdc38d49da1680cef2a3f/USER'
            ],
    'bg2017-dy1':  [
            '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2017-dy1_Era2017_06Sep2020_MINIAOD-skimv3-18783c0a07109245951450a1a4f55409/USER',
            '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-DYToLL_Era2017_06Sep2020_AODslim-ecal_v2-351414bbda2cdc38d49da1680cef2a3f/USER'
            ],
    'bg2017-dy2':  [
            '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2017-dy2_Era2017_06Sep2020_MINIAOD-skimv3-18783c0a07109245951450a1a4f55409/USER',
            '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-DYToLL_Era2017_06Sep2020_AODslim-ecal_v2-351414bbda2cdc38d49da1680cef2a3f/USER'
            ],
    'bg2017-dy3':  [
            '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2017-dy3_Era2017_06Sep2020_MINIAOD-skimv3-18783c0a07109245951450a1a4f55409/USER',
            '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-DYToLL_Era2017_06Sep2020_AODslim-ecal_v2-351414bbda2cdc38d49da1680cef2a3f/USER'
            ],
    'bg2017-dy4':  [
            '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2017-dy4_Era2017_06Sep2020_MINIAOD-skimv3-18783c0a07109245951450a1a4f55409/USER',
            '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-DYToLL_Era2017_06Sep2020_AODslim-ecal_v2-351414bbda2cdc38d49da1680cef2a3f/USER'
            ],

    # 2018
    #'data2018-Run2018A': [
    #        '/EGamma/Run2018A-17Sep2018-v2/MINIAOD',
    #        '/EGamma/Run2018A-17Sep2018-v2/AOD'
    #        #'/EGamma/mandrews-data2018-Run2018A_Era2018_06Sep2020_MINIAOD-skimv7-6e67610c0756643cd1efca7b7fd48fa1/USER',
    #        #'/EGamma/mandrews-data2018-Run2018A_Era2018_06Sep2020_MINIAOD-skimv2-6e67610c0756643cd1efca7b7fd48fa1/USER',
    #        #'/EGamma/mandrews-EGamma_2018A_Era2018_06Sep2020_AODslim-ecal_v1-6e67610c0756643cd1efca7b7fd48fa1/USER'
    #        ],
    #'data2018-Run2018B': [
    #        '/EGamma/mandrews-data2018-Run2018B_Era2018_06Sep2020_MINIAOD-skimv2-6e67610c0756643cd1efca7b7fd48fa1/USER',
    #        '/EGamma/mandrews-EGamma_2018B_Era2018_06Sep2020_AODslim-ecal_v1-6e67610c0756643cd1efca7b7fd48fa1/USER'
    #        ],
    #'data2018-Run2018C': [
    #        '/EGamma/mandrews-data2018-Run2018C_Era2018_06Sep2020_MINIAOD-skimv2-6e67610c0756643cd1efca7b7fd48fa1/USER',
    #        #'/EGamma/mandrews-EGamma_2018C_Era2018_06Sep2020_AODslim-ecal_v3-6e67610c0756643cd1efca7b7fd48fa1/USER' #redo but without json lumimask
    #        '/EGamma/mandrews-EGamma_2018C_Era2018_06Sep2020_AODslim-ecal_v1-6e67610c0756643cd1efca7b7fd48fa1/USER'
    #        ],
    #'data2018-Run2018D0': [
    #        '/EGamma/mandrews-data2018-Run2018D0_Era2018_06Sep2020_MINIAOD-skimv2-306144291bb2d755797972fd22d33d6d/USER',
    #        '/EGamma/mandrews-EGamma_2018D_Era2018_06Sep2020_AODslim-ecal_v1-306144291bb2d755797972fd22d33d6d/USER'
    #        ],
    #'data2018-Run2018D1': [
    #        '/EGamma/mandrews-data2018-Run2018D1_Era2018_06Sep2020_MINIAOD-skimv2-306144291bb2d755797972fd22d33d6d/USER',
    #        '/EGamma/mandrews-EGamma_2018D_Era2018_06Sep2020_AODslim-ecal_v1-306144291bb2d755797972fd22d33d6d/USER'
    #        ],
    #'data2018-Run2018D2': [
    #        '/EGamma/mandrews-data2018-Run2018D2_Era2018_06Sep2020_MINIAOD-skimv2-306144291bb2d755797972fd22d33d6d/USER',
    #        '/EGamma/mandrews-EGamma_2018D_Era2018_06Sep2020_AODslim-ecal_v1-306144291bb2d755797972fd22d33d6d/USER'
    #        ],
    #'data2018-Run2018D3': [
    #        '/EGamma/mandrews-data2018-Run2018D3_Era2018_06Sep2020_MINIAOD-skimv2-306144291bb2d755797972fd22d33d6d/USER',
    #        '/EGamma/mandrews-EGamma_2018D_Era2018_06Sep2020_AODslim-ecal_v1-306144291bb2d755797972fd22d33d6d/USER'
    #        ],
    #'h4g2018-mA0p1GeV': [
    #        #'/HAHMHToAA_AToGG_MA-0p1GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2018-mA0p1GeV_Era2018_06Sep2020_MINIAOD-skimv2-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        #'/HAHMHToAA_AToGG_MA-0p1GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2018-mA0p1GeV_Era2018_04Dec2020_MINIAOD-skimv1-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        '/HAHMHToAA_AToGG_MA-0p8GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2018-mA0p1GeV_Era2018_20May2021_MINIAOD-skimv1-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        '/HAHMHToAA_AToGG_MA-0p1GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA0p1GeV_Era2018_06Sep2020_AODslim-ecal_v1-2fd59cbde119ecab78af65e08efe8aae/USER'
    #        ],
    #'h4g2018-mA0p2GeV': [
    #        #'/HAHMHToAA_AToGG_MA-0p2GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2018-mA0p2GeV_Era2018_06Sep2020_MINIAOD-skimv2-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        #'/HAHMHToAA_AToGG_MA-0p2GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2018-mA0p2GeV_Era2018_04Dec2020_MINIAOD-skimv1-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        '/HAHMHToAA_AToGG_MA-0p8GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2018-mA0p2GeV_Era2018_20May2021_MINIAOD-skimv1-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        '/HAHMHToAA_AToGG_MA-0p2GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA0p2GeV_Era2018_06Sep2020_AODslim-ecal_v1-2fd59cbde119ecab78af65e08efe8aae/USER'
    #        ],
    #'h4g2018-mA0p4GeV': [
    #        #'/HAHMHToAA_AToGG_MA-0p4GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2018-mA0p4GeV_Era2018_06Sep2020_MINIAOD-skimv2-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        #'/HAHMHToAA_AToGG_MA-0p4GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2018-mA0p4GeV_Era2018_04Dec2020_MINIAOD-skimv1-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        '/HAHMHToAA_AToGG_MA-0p8GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2018-mA0p4GeV_Era2018_20May2021_MINIAOD-skimv1-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        '/HAHMHToAA_AToGG_MA-0p4GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA0p4GeV_Era2018_06Sep2020_AODslim-ecal_v1-2fd59cbde119ecab78af65e08efe8aae/USER'
    #        ],
    #'h4g2018-mA0p6GeV': [
    #        #'/HAHMHToAA_AToGG_MA-0p6GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2018-mA0p6GeV_Era2018_06Sep2020_MINIAOD-skimv2-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        #'/HAHMHToAA_AToGG_MA-0p6GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2018-mA0p6GeV_Era2018_04Dec2020_MINIAOD-skimv1-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        '/HAHMHToAA_AToGG_MA-0p8GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2018-mA0p6GeV_Era2018_20May2021_MINIAOD-skimv1-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        '/HAHMHToAA_AToGG_MA-0p6GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA0p6GeV_Era2018_06Sep2020_AODslim-ecal_v1-2fd59cbde119ecab78af65e08efe8aae/USER'
    #        ],
    #'h4g2018-mA0p8GeV': [
    #        #'/HAHMHToAA_AToGG_MA-0p8GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2018-mA0p8GeV_Era2018_06Sep2020_MINIAOD-skimv2-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        #'/HAHMHToAA_AToGG_MA-0p8GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2018-mA0p8GeV_Era2018_04Dec2020_MINIAOD-skimv1-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        '/HAHMHToAA_AToGG_MA-0p8GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2018-mA0p8GeV_Era2018_20May2021_MINIAOD-skimv1-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        '/HAHMHToAA_AToGG_MA-0p8GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA0p8GeV_Era2018_06Sep2020_AODslim-ecal_v1-2fd59cbde119ecab78af65e08efe8aae/USER'
    #        ],
    #'h4g2018-mA1p0GeV': [
    #        #'/HAHMHToAA_AToGG_MA-1GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2018-mA1p0GeV_Era2018_06Sep2020_MINIAOD-skimv2-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        #'/HAHMHToAA_AToGG_MA-1GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2018-mA1p0GeV_Era2018_04Dec2020_MINIAOD-skimv1-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        '/HAHMHToAA_AToGG_MA-1GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2018-mA1p0GeV_Era2018_20May2021_MINIAOD-skimv1-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        '/HAHMHToAA_AToGG_MA-1GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA1p0GeV_Era2018_06Sep2020_AODslim-ecal_v1-2fd59cbde119ecab78af65e08efe8aae/USER'
    #        ],
    #'h4g2018-mA1p2GeV': [
    #        #'/HAHMHToAA_AToGG_MA-1p2GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2018-mA1p2GeV_Era2018_06Sep2020_MINIAOD-skimv2-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        #'/HAHMHToAA_AToGG_MA-1p2GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2018-mA1p2GeV_Era2018_04Dec2020_MINIAOD-skimv1-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        '/HAHMHToAA_AToGG_MA-1p2GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2018-mA1p2GeV_Era2018_20May2021_MINIAOD-skimv1-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        '/HAHMHToAA_AToGG_MA-1p2GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA1p2GeV_Era2018_06Sep2020_AODslim-ecal_v1-2fd59cbde119ecab78af65e08efe8aae/USER'
    #        ],
    'bg2018-hgg': [
            #'/GluGluHToGG_M125_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2018-hgg_Era2018_06Sep2020_MINIAOD-skimv2-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
            #'/GluGluHToGG_M125_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2018-hgg_Era2018_04Dec2020_MINIAOD-skimv1-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
            '/GluGluHToGG_M125_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2018-hgg_Era2018_20May2021_MINIAOD-skimv1-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
            '/GluGluHToGG_M125_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-GluGluHToGG_Era2018_06Sep2020_AODslim-ecal_v2-2fd59cbde119ecab78af65e08efe8aae/USER'
            ],
    #'bg2018-dy0':  [
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2018-dy0_Era2018_06Sep2020_MINIAOD-skimv3-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        ''
    #        ],
    #'bg2018-dy1':  [
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2018-dy1_Era2018_06Sep2020_MINIAOD-skimv3-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        ''
    #        ],
    #'bg2018-dy2':  [
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2018-dy2_Era2018_06Sep2020_MINIAOD-skimv3-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        ''
    #        ],
    #'bg2018-dy3':  [
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2018-dy3_Era2018_06Sep2020_MINIAOD-skimv3-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        ''
    #        ],
    #'bg2018-dy4':  [
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2018-dy4_Era2018_06Sep2020_MINIAOD-skimv3-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        ''
    #        ],
    #'bg2018-dy5':  [
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2018-dy5_Era2018_06Sep2020_MINIAOD-skimv3-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        ''
    #        ]

}
#'''
'''
#job_units = 500
job_units = 50
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
        '/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/mandrews-GluGluHToGG_Era2017_18May2020_AODslim-ecal_v1-351414bbda2cdc38d49da1680cef2a3f/USER'],
        #'/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/RunIIFall17DRPremix-94X_mc2017_realistic_v10-v1/AODSIM'],
        #'/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM'],
    }
'''
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
            '/DoubleEG/mandrews-data2017-Run2017%s_Era2017_20May2021_MINIAOD-skimv1-84d4062339350c0b82cf1392552beb97/USER'%s,
            '/DoubleEG/mandrews-DoubleEG_2017%s_Era2017_18May2020_AODslim-ecal_v1-964eedbb4080135606054ba835f474dc/USER'%s[0]
            ]
    else:
        samples['data%s-Run2017%s'%(era_, s)] = [
            '/DoubleEG/mandrews-data2017-Run2017%s_Era2017_20May2021_MINIAOD-skimv1-84d4062339350c0b82cf1392552beb97/USER'%s,
            '/DoubleEG/mandrews-DoubleEG_2017%s_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER'%s[0]
            ]

samples_h4g = ['0p1', '0p2', '0p4', '0p6', '0p8', '1p0', '1p2']
for s in samples_h4g:
    samples['h4g%s-mA%sGeV'%(era_, s)] = [
        '/HAHMHToAA_AToGG_MA-%sGeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2017-mA%sGeV_Era2017_20May2021_MINIAOD-skimv1-5f646ecd4e1c7a39ab0ed099ff55ceb9/USER'%(s.replace('p0',''), s),
        '/HAHMHToAA_AToGG_MA-%sGeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA%sGeV_Era2017_06Sep2020_AODslim-ecal_v1-c3d6de13a4792afb4dd0c4ab58e49'%(s.replace('p0',''), s)
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
            '/EGamma/mandrews-data2018-Run2018%s_Era2018_20May2021_MINIAOD-skimv1-306144291bb2d755797972fd22d33d6d/USER'%s,
            '/EGamma/mandrews-EGamma_2018%s_Era2018_06Sep2020_AODslim-ecal_v1-306144291bb2d755797972fd22d33d6d/USER'%s[0]
            ]
    else:
        samples['data2018-Run2018%s'%s] = [
            '/EGamma/mandrews-data2018-Run2018%s_Era2018_20May2021_MINIAOD-skimv1-6e67610c0756643cd1efca7b7fd48fa1/USER'%s,
            '/EGamma/mandrews-EGamma_2018%s_Era2018_06Sep2020_AODslim-ecal_v1-6e67610c0756643cd1efca7b7fd48fa1/USER'%s[0]
            ]

samples_h4g = ['0p1', '0p2', '0p4', '0p6', '0p8', '1p0', '1p2']
for s in samples_h4g:
    samples['h4g2018-mA%sGeV'%s] = [
        '/HAHMHToAA_AToGG_MA-%sGeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-h4g2018-mA%sGeV_Era2018_20May2021_MINIAOD-skimv1-3ee3afd6b5a1410aea6d0b4d52723d06/USER'%(s.replace('p0',''), s),
        '/HAHMHToAA_AToGG_MA-%sGeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/mandrews-H4G_mA%sGeV_Era2018_06Sep2020_AODslim-ecal_v1-2fd59cbde119ecab78af65e08efe8aae/USER'%(s.replace('p0',''), s)
        ]
#'data2018-Run2018A': [
#        '/EGamma/Run2018A-17Sep2018-v2/MINIAOD',
#        '/EGamma/Run2018A-17Sep2018-v2/AOD'
#        #'/EGamma/mandrews-data2018-Run2018A_Era2018_06Sep2020_MINIAOD-skimv7-6e67610c0756643cd1efca7b7fd48fa1/USER',
#        #'/EGamma/mandrews-data2018-Run2018A_Era2018_06Sep2020_MINIAOD-skimv2-6e67610c0756643cd1efca7b7fd48fa1/USER',
#        #'/EGamma/mandrews-EGamma_2018A_Era2018_06Sep2020_AODslim-ecal_v1-6e67610c0756643cd1efca7b7fd48fa1/USER'
#        ],
#'data2018-Run2018B': [
#        '/EGamma/mandrews-data2018-Run2018B_Era2018_06Sep2020_MINIAOD-skimv2-6e67610c0756643cd1efca7b7fd48fa1/USER',
#        '/EGamma/mandrews-EGamma_2018B_Era2018_06Sep2020_AODslim-ecal_v1-6e67610c0756643cd1efca7b7fd48fa1/USER'
#        ],
#'data2018-Run2018C': [
#        '/EGamma/mandrews-data2018-Run2018C_Era2018_06Sep2020_MINIAOD-skimv2-6e67610c0756643cd1efca7b7fd48fa1/USER',
#        '/EGamma/mandrews-EGamma_2018C_Era2018_06Sep2020_AODslim-ecal_v1-6e67610c0756643cd1efca7b7fd48fa1/USER'
#        ],
#'data2018-Run2018D0': [
#        '/EGamma/mandrews-data2018-Run2018D0_Era2018_06Sep2020_MINIAOD-skimv2-306144291bb2d755797972fd22d33d6d/USER',
#        '/EGamma/mandrews-EGamma_2018D_Era2018_06Sep2020_AODslim-ecal_v1-306144291bb2d755797972fd22d33d6d/USER'
#        ],

for s,dset in samples.iteritems(): #python3: samples.items()

    #if 'data2017' not in s: continue
    if '2018' not in s: continue
    #if '2017' not in s: continue
    #if '2016' not in s: continue
    #if 'h4g' not in s and 'hgg' not in s: continue
    #if 'Run2018A' not in s: continue
    #if 'Run2016H' not in s: continue
    #if '0p6' not in s: continue
    #if 'Run2018' not in s: continue
    #if 'Run2018A' in s: continue
    #if 'dy' in s: continue

    print('>> For sample:',s)

    if len(dset) != 2:
        print('   !! incomplete sample. Skipping...')
        continue

    assert os.environ['CMSSW_BASE'] != ''
    base_dir = '%s/src'%os.environ['CMSSW_BASE']

    #'''
    # Read in crabConfig template
    with open('crabConfig_SCRegressor.py', "r") as template_file:
        file_data = template_file.read()

    # Replace crabConfig template strings with sample-specific values
    file_data = file_data.replace(SAMPLE, s)
    file_data = file_data.replace(DATASET, dset[1])
    #file_data = file_data.replace(DATASET, dset[0])
    #file_data = file_data.replace(SECONDARYDATASET, dset[1])
    #if 'Run2018A' in s:
    if 'Run2018' in s or 'Run2016H' in s:

        # If lumimask needed on AODs
        s_aod = re.findall('(.*201[6-8][A-Z])', s)[0]
        lumi_list = '%s/h2aa/aodSkims/%s/%s_lumi_list.json'%(base_dir, aodskim_campaign, s_aod)
        assert os.path.isfile(lumi_list)
        #assert aodskim_campaign.strip('Era') in dset[1]
        file_data = file_data.replace(LUMIMASK, lumi_list)

        # Include evt list if running on full aod/miniaod dsets
        if 'Run2018A' in s:
            year = re.findall('(201[6-8])', s.split('-')[0])[0]
            ggskim_dir = '/eos/uscms/store/user/lpchaa4g/mandrews/%s/%s/ggSkims'%(year, ggskim_campaign)
            evt_lists = glob.glob('%s/%s*_event_list.txt'%(ggskim_dir, s))
            assert len(evt_lists) == 1
            evt_list = evt_lists[0]
            assert os.path.isfile(evt_list), '%s not found'%evt_list
            file_data = file_data.replace(EVTLIST, evt_list)

    file_data = file_data.replace(CAMPAIGN, this_campaign)

    job_units = job_units_ #30,50
    splitting = 'LumiBased'
    if 'data2016' in s:
        job_units = 30
    #if 'Run2018A' in s:
    #    # if running full MINIAOD/AOD to minimize fails -> doesnt seem to help
    #    job_units = 4
    #    splitting = 'FileBased'
    elif 'h4g' in s or 'bg' in s:
        job_units = 50
    elif 'Run2018' in s:
        job_units = 50
    file_data = file_data.replace(UNITSPERJOB, str(job_units))
    file_data = file_data.replace(SPLIT, splitting)

    #break
    # Write out sample-specific crabConfig
    with open('%s/crabConfig_SCRegressor_%s.py'%(crab_folder, s), "w") as sample_file:
        sample_file.write(file_data)

    #'''
