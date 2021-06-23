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

# Era2016_06Sep2020_MINIAOD-skimv2+Era2016_06Sep2020_AODslim-ecal_v2
#this_campaign = 'Era2017_06Sep2020_AOD-IMGZeev1' # SUBMITFAILED: no parent error

# Use whole MINIAOD/AOD dsets instead but split by skim
#this_campaign = 'Era2017_06Sep2020_AOD-IMGZeev2' # AOD at 62% in DAS, lumi-based unitsPerJob = 10 => too much mem
#this_campaign = 'Era2017_06Sep2020_AOD-IMGZeev3' # lumi-based unitsPerJob = 6

#this_campaign = 'Era2016_06Sep2020_AOD-IMGZeev4' # lumi-based unitsPerJob = 6, dy+data zee skim(nele+presel)
#this_campaign = 'Era2017_06Sep2020_AOD-IMGZeev4' # lumi-based unitsPerJob = 6, dy+data zee skim(nele+presel)

#this_campaign = 'Era2016_06Sep2020_AOD-IMGZeev5' # dy2016: use skims otherwise SUBMITFAILED due to too many lumis--using FileBased+no lumimask doesnt help
#this_campaign = 'Era2018_06Sep2020_AOD-IMGZeev5' # use skims
# PROBLEM: ^ skims are from sg selection -> can lead to low zee efficiency

#this_campaign = 'Era2017_16Feb2021_AOD-IMGZeev1' # data: use zee miniod skims, dy: no parent complain if running directly on skims->use whole aod+miniod then filter with zee skims
#this_campaign = 'Era2016_16Feb2021_AOD-IMGZeev1' # data: use zee miniod skims, dy: no parent
#this_campaign = 'Era2018_16Feb2021_AOD-IMGZeev1' # data: use zee miniod skims, 2018A:usee full miniaod/aod(incomplete), dy: no parent

#this_campaign = 'Era2017_16Feb2021_AOD-IMGZeev2' # dy only: use miniaod clone input + evt/lumi mask -> SUBMITFAILED: no parent still...

#this_campaign = 'Era2018_16Feb2021_AOD-IMGZeev3' # dy only: use full miniaod/aod + evt mask only -> SUBMITFAILED: too many lumis

this_campaign = 'Era2016_09Mar2021_AOD-IMGZeev1' # DYToEE using full miniaod/aod (tape recall by crab_Era2016_23Mar2021_AODslim-ecal_v1)
#this_campaign = 'Era2017_09Mar2021_AOD-IMGZeev1' # DYToEE using full miniaod/aod (transferred to cmu)
#this_campaign = 'Era2018_09Mar2021_AOD-IMGZeev1' # DYToEE using full miniaod/aod (tape recall by crab_Era2018_23Mar2021_AODslim-ecal_v1)

crab_folder = 'crab_%s'%this_campaign
if not os.path.isdir(crab_folder):
    os.makedirs(crab_folder)

#'''
# key: [<primary dset>, <secondary dset>]
samples = {


    # 2016
    'data2016-Run2016B': [
            #"/DoubleEG/Run2016B-17Jul2018_ver2-v1/MINIAOD",
            #'/DoubleEG/Run2016B-07Aug17_ver2-v2/AOD'
            #'/DoubleEG/mandrews-data2016-Run2016B_Era2016_06Sep2020_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
            '/DoubleEG/mandrews-data2016-Run2016B_Era2016_16Feb2021_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
            '/DoubleEG/mandrews-DoubleEG_2016B_Era2016_06Sep2020_AODslim-ecal_v1-81ba725143e8ad84d6b47c9ab0eb90c4/USER'
            ],
    'data2016-Run2016C': [
            #"/DoubleEG/Run2016C-17Jul2018-v1/MINIAOD",
            #'/DoubleEG/Run2016C-07Aug17-v1/AOD'
            #'/DoubleEG/mandrews-data2016-Run2016C_Era2016_06Sep2020_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
            '/DoubleEG/mandrews-data2016-Run2016C_Era2016_16Feb2021_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
            '/DoubleEG/mandrews-DoubleEG_2016C_Era2016_06Sep2020_AODslim-ecal_v1-81ba725143e8ad84d6b47c9ab0eb90c4/USER'
            ],
    'data2016-Run2016D': [
            #"/DoubleEG/Run2016D-17Jul2018-v1/MINIAOD",
            #'/DoubleEG/Run2016D-07Aug17-v1/AOD'
            #'/DoubleEG/mandrews-data2016-Run2016D_Era2016_06Sep2020_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
            '/DoubleEG/mandrews-data2016-Run2016D_Era2016_16Feb2021_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
            '/DoubleEG/mandrews-DoubleEG_2016D_Era2016_06Sep2020_AODslim-ecal_v1-81ba725143e8ad84d6b47c9ab0eb90c4/USER'
            ],
    'data2016-Run2016E': [
            #"/DoubleEG/Run2016E-17Jul2018-v1/MINIAOD",
            #'/DoubleEG/Run2016E-07Aug17-v1/AOD'
            #'/DoubleEG/mandrews-data2016-Run2016E_Era2016_06Sep2020_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
            '/DoubleEG/mandrews-data2016-Run2016E_Era2016_16Feb2021_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
            '/DoubleEG/mandrews-DoubleEG_2016E_Era2016_06Sep2020_AODslim-ecal_v1-81ba725143e8ad84d6b47c9ab0eb90c4/USER'
            ],
    'data2016-Run2016F': [
            #"/DoubleEG/Run2016F-17Jul2018-v1/MINIAOD",
            #'/DoubleEG/Run2016F-07Aug17-v1/AOD'
            #'/DoubleEG/mandrews-data2016-Run2016F_Era2016_06Sep2020_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
            '/DoubleEG/mandrews-data2016-Run2016F_Era2016_16Feb2021_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
            '/DoubleEG/mandrews-DoubleEG_2016F_Era2016_06Sep2020_AODslim-ecal_v1-81ba725143e8ad84d6b47c9ab0eb90c4/USER'
            ],
    'data2016-Run2016G': [
            #"/DoubleEG/Run2016G-17Jul2018-v1/MINIAOD",
            #'/DoubleEG/Run2016G-07Aug17-v1/AOD'
            #'/DoubleEG/mandrews-data2016-Run2016G_Era2016_06Sep2020_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
            '/DoubleEG/mandrews-data2016-Run2016G_Era2016_16Feb2021_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
            '/DoubleEG/mandrews-DoubleEG_2016G_Era2016_06Sep2020_AODslim-ecal_v1-2427c69bd126da1063d393ec79219651/USER'
            ],
    'data2016-Run2016H': [
            #"/DoubleEG/Run2016H-17Jul2018-v1/MINIAOD",
            #'/DoubleEG/Run2016H-07Aug17-v1/AOD'
            #'/DoubleEG/mandrews-data2016-Run2016H_Era2016_06Sep2020_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
            '/DoubleEG/mandrews-data2016-Run2016H_Era2016_16Feb2021_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
            '/DoubleEG/mandrews-DoubleEG_2016H_Era2016_06Sep2020_AODslim-ecal_v1-2427c69bd126da1063d393ec79219651/USER'
            #'/DoubleEG/mandrews-DoubleEG_2016H_Era2016_28Dec2020_AODslim-ecal_v1-2427c69bd126da1063d393ec79219651/USER'
            ],
    'bg2016-dy0':  [
            '/DYToEE_NNPDF30_13TeV-powheg-pythia8/RunIISummer16MiniAODv2-EGM0_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM',
            '/DYToEE_NNPDF30_13TeV-powheg-pythia8/RunIISummer16DR80Premix-EGM0_80X_mcRun2_asymptotic_end2016_forEGM_v0-v1/AODSIM'
            ],
    'bg2016-dy1':  [
            '/DYToEE_NNPDF30_13TeV-powheg-pythia8/RunIISummer16MiniAODv2-EGM0_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM',
            '/DYToEE_NNPDF30_13TeV-powheg-pythia8/RunIISummer16DR80Premix-EGM0_80X_mcRun2_asymptotic_end2016_forEGM_v0-v1/AODSIM'
            ],
    'bg2016-dy2':  [
            '/DYToEE_NNPDF30_13TeV-powheg-pythia8/RunIISummer16MiniAODv2-EGM0_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM',
            '/DYToEE_NNPDF30_13TeV-powheg-pythia8/RunIISummer16DR80Premix-EGM0_80X_mcRun2_asymptotic_end2016_forEGM_v0-v1/AODSIM'
            ],
    'bg2016-dy3':  [
            '/DYToEE_NNPDF30_13TeV-powheg-pythia8/RunIISummer16MiniAODv2-EGM0_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM',
            '/DYToEE_NNPDF30_13TeV-powheg-pythia8/RunIISummer16DR80Premix-EGM0_80X_mcRun2_asymptotic_end2016_forEGM_v0-v1/AODSIM'
            ],
    #'bg2016-dy0':  [
    #        #'/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext2-v1/MINIAODSIM',
    #        #'/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1/AODSIM'
    #        #'/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/mandrews-bg2016-dy0_Era2016_06Sep2020_MINIAOD-skimv3-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
    #        '/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/mandrews-bg2016-dy0_Era2016_16Feb2021_MINIAOD-skimv2-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
    #        '/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/mandrews-DYToLL_Era2016_06Sep2020_AODslim-ecal_v1-b1a4edca9adfa7a2e4059536bf605cd7/USER'
    #        ],
    #'bg2016-dy1':  [
    #        #'/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext2-v1/MINIAODSIM',
    #        #'/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1/AODSIM'
    #        #'/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/mandrews-bg2016-dy1_Era2016_06Sep2020_MINIAOD-skimv3-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
    #        '/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/mandrews-bg2016-dy1_Era2016_16Feb2021_MINIAOD-skimv2-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
    #        '/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/mandrews-DYToLL_Era2016_06Sep2020_AODslim-ecal_v1-b1a4edca9adfa7a2e4059536bf605cd7/USER'
    #        ],
    #'bg2016-dy2':  [
    #        #'/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext2-v1/MINIAODSIM',
    #        #'/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1/AODSIM'
    #        #'/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/mandrews-bg2016-dy2_Era2016_06Sep2020_MINIAOD-skimv3-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
    #        '/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/mandrews-bg2016-dy2_Era2016_16Feb2021_MINIAOD-skimv2-bd3e7bcff6c9bcad356ea4ed7e4f08b4/USER',
    #        '/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/mandrews-DYToLL_Era2016_06Sep2020_AODslim-ecal_v1-b1a4edca9adfa7a2e4059536bf605cd7/USER'
    #        ],


    # 2017
    'data2017-Run2017B': [
            '/DoubleEG/mandrews-data2017-Run2017B_Era2017_16Feb2021_MINIAOD-skimv2-84d4062339350c0b82cf1392552beb97/USER',
            '/DoubleEG/mandrews-DoubleEG_2017B_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER'
            #'/DoubleEG/Run2017B-31Mar2018-v1/MINIAOD',
            #'/DoubleEG/Run2017B-17Nov2017-v1/AOD'
            ],
    'data2017-Run2017C': [
            '/DoubleEG/mandrews-data2017-Run2017C_Era2017_16Feb2021_MINIAOD-skimv2-84d4062339350c0b82cf1392552beb97/USER',
            '/DoubleEG/mandrews-DoubleEG_2017C_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER'
            #'/DoubleEG/Run2017C-31Mar2018-v1/MINIAOD',
            #'/DoubleEG/Run2017C-17Nov2017-v1/AOD'
            ],
    'data2017-Run2017D': [
            '/DoubleEG/mandrews-data2017-Run2017D_Era2017_16Feb2021_MINIAOD-skimv2-84d4062339350c0b82cf1392552beb97/USER',
            '/DoubleEG/mandrews-DoubleEG_2017D_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER'
            #'/DoubleEG/Run2017D-31Mar2018-v1/MINIAOD',
            #'/DoubleEG/Run2017D-17Nov2017-v1/AOD'
            ],
    'data2017-Run2017E': [
            '/DoubleEG/mandrews-data2017-Run2017E_Era2017_16Feb2021_MINIAOD-skimv2-84d4062339350c0b82cf1392552beb97/USER',
            '/DoubleEG/mandrews-DoubleEG_2017E_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER'
            #'/DoubleEG/Run2017E-31Mar2018-v1/MINIAOD',
            #'/DoubleEG/Run2017E-17Nov2017-v1/AOD'
            ],
    'data2017-Run2017F': [
            '/DoubleEG/mandrews-data2017-Run2017F_Era2017_16Feb2021_MINIAOD-skimv2-84d4062339350c0b82cf1392552beb97/USER',
            '/DoubleEG/mandrews-DoubleEG_2017F_Era2017_18May2020_AODslim-ecal_v1-964eedbb4080135606054ba835f474dc/USER'
            #'/DoubleEG/Run2017F-31Mar2018-v1/MINIAOD',
            #'/DoubleEG/Run2017F-17Nov2017-v1/AOD'
            ],
    'bg2017-dy0':  [
            '/DYToEE_M-50_NNPDF31_13TeV-powheg-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM',
            '/DYToEE_M-50_NNPDF31_13TeV-powheg-pythia8/RunIIFall17DRPremix-94X_mc2017_realistic_v10-v1/AODSIM'
            ],
    #'bg2017-dy':  [
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/MINIAODSIM',
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17DRPremix-94X_mc2017_realistic_v10_ext1-v1/AODSIM'
    #        ],
    #'bg2017-dy0':  [
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2017-dy0_Era2017_16Feb2021_MINIAOD-skimv2-18783c0a07109245951450a1a4f55409/USER',
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/MINIAODSIM',
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2017-dy_Era2017_16Feb2021_MINIAOD-clonev1-18783c0a07109245951450a1a4f55409/USER',
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17DRPremix-94X_mc2017_realistic_v10_ext1-v1/AODSIM'
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2017-dy0_Era2017_06Sep2020_MINIAOD-skimv3-18783c0a07109245951450a1a4f55409/USER',
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-DYToLL_Era2017_06Sep2020_AODslim-ecal_v2-351414bbda2cdc38d49da1680cef2a3f/USER'
    #        ],
    #'bg2017-dy1':  [
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2017-dy1_Era2017_16Feb2021_MINIAOD-skimv2-18783c0a07109245951450a1a4f55409/USER',
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/MINIAODSIM',
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2017-dy_Era2017_16Feb2021_MINIAOD-clonev1-18783c0a07109245951450a1a4f55409/USER',
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17DRPremix-94X_mc2017_realistic_v10_ext1-v1/AODSIM'
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2017-dy1_Era2017_06Sep2020_MINIAOD-skimv3-18783c0a07109245951450a1a4f55409/USER',
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-DYToLL_Era2017_06Sep2020_AODslim-ecal_v2-351414bbda2cdc38d49da1680cef2a3f/USER'
    #        ],
    #'bg2017-dy2':  [
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2017-dy2_Era2017_16Feb2021_MINIAOD-skimv2-18783c0a07109245951450a1a4f55409/USER',
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/MINIAODSIM',
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2017-dy_Era2017_16Feb2021_MINIAOD-clonev1-18783c0a07109245951450a1a4f55409/USER',
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17DRPremix-94X_mc2017_realistic_v10_ext1-v1/AODSIM'
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2017-dy2_Era2017_06Sep2020_MINIAOD-skimv3-18783c0a07109245951450a1a4f55409/USER',
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-DYToLL_Era2017_06Sep2020_AODslim-ecal_v2-351414bbda2cdc38d49da1680cef2a3f/USER'
    #        ],
    #'bg2017-dy3':  [
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2017-dy3_Era2017_16Feb2021_MINIAOD-skimv2-18783c0a07109245951450a1a4f55409/USER',
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/MINIAODSIM',
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2017-dy_Era2017_16Feb2021_MINIAOD-clonev1-18783c0a07109245951450a1a4f55409/USER',
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17DRPremix-94X_mc2017_realistic_v10_ext1-v1/AODSIM'
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2017-dy3_Era2017_06Sep2020_MINIAOD-skimv3-18783c0a07109245951450a1a4f55409/USER',
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-DYToLL_Era2017_06Sep2020_AODslim-ecal_v2-351414bbda2cdc38d49da1680cef2a3f/USER'
    #        ],
    #'bg2017-dy4':  [
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2017-dy4_Era2017_16Feb2021_MINIAOD-skimv2-18783c0a07109245951450a1a4f55409/USER',
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/MINIAODSIM',
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2017-dy_Era2017_16Feb2021_MINIAOD-clonev1-18783c0a07109245951450a1a4f55409/USER',
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17DRPremix-94X_mc2017_realistic_v10_ext1-v1/AODSIM'
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2017-dy4_Era2017_06Sep2020_MINIAOD-skimv3-18783c0a07109245951450a1a4f55409/USER',
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-DYToLL_Era2017_06Sep2020_AODslim-ecal_v2-351414bbda2cdc38d49da1680cef2a3f/USER'
    #        ],

    # 2018
    'data2018-Run2018A': [
            '/EGamma/Run2018A-17Sep2018-v2/MINIAOD',
            '/EGamma/Run2018A-17Sep2018-v2/AOD'
            #'/EGamma/mandrews-data2018-Run2018A_Era2018_06Sep2020_MINIAOD-skimv7-6e67610c0756643cd1efca7b7fd48fa1/USER',
            #'/EGamma/mandrews-data2018-Run2018A_Era2018_06Sep2020_MINIAOD-skimv2-6e67610c0756643cd1efca7b7fd48fa1/USER',
            #'/EGamma/mandrews-EGamma_2018A_Era2018_06Sep2020_AODslim-ecal_v1-6e67610c0756643cd1efca7b7fd48fa1/USER'
            ],
    'data2018-Run2018B': [
            #"/EGamma/Run2018B-17Sep2018-v1/MINIAOD",
            #'/EGamma/Run2018B-17Sep2018-v1/AOD'
            #'/EGamma/mandrews-data2018-Run2018B_Era2018_06Sep2020_MINIAOD-skimv2-6e67610c0756643cd1efca7b7fd48fa1/USER',
            '/EGamma/mandrews-data2018-Run2018B_Era2018_16Feb2021_MINIAOD-skimv2-6e67610c0756643cd1efca7b7fd48fa1/USER',
            '/EGamma/mandrews-EGamma_2018B_Era2018_06Sep2020_AODslim-ecal_v1-6e67610c0756643cd1efca7b7fd48fa1/USER'
            ],
    'data2018-Run2018C': [
            #'/EGamma/Run2018C-17Sep2018-v1/AOD'
            #"/EGamma/Run2018C-17Sep2018-v1/MINIAOD",
            #'/EGamma/mandrews-data2018-Run2018C_Era2018_06Sep2020_MINIAOD-skimv2-6e67610c0756643cd1efca7b7fd48fa1/USER',
            #'/EGamma/mandrews-EGamma_2018C_Era2018_06Sep2020_AODslim-ecal_v3-6e67610c0756643cd1efca7b7fd48fa1/USER' #redo but without json lumimask
            '/EGamma/mandrews-data2018-Run2018C_Era2018_16Feb2021_MINIAOD-skimv2-6e67610c0756643cd1efca7b7fd48fa1/USER',
            '/EGamma/mandrews-EGamma_2018C_Era2018_06Sep2020_AODslim-ecal_v1-6e67610c0756643cd1efca7b7fd48fa1/USER'
            ],
    'data2018-Run2018D0': [
            #"/EGamma/Run2018D-22Jan2019-v2/MINIAOD",
            #'/EGamma/Run2018D-22Jan2019-v2/AOD'
            #'/EGamma/mandrews-data2018-Run2018D0_Era2018_06Sep2020_MINIAOD-skimv2-306144291bb2d755797972fd22d33d6d/USER',
            '/EGamma/mandrews-data2018-Run2018D0_Era2018_16Feb2021_MINIAOD-skimv2-306144291bb2d755797972fd22d33d6d/USER',
            '/EGamma/mandrews-EGamma_2018D_Era2018_06Sep2020_AODslim-ecal_v1-306144291bb2d755797972fd22d33d6d/USER'
            ],
    'data2018-Run2018D1': [
            #"/EGamma/Run2018D-22Jan2019-v2/MINIAOD",
            #'/EGamma/Run2018D-22Jan2019-v2/AOD'
            #'/EGamma/mandrews-data2018-Run2018D1_Era2018_06Sep2020_MINIAOD-skimv2-306144291bb2d755797972fd22d33d6d/USER',
            '/EGamma/mandrews-data2018-Run2018D1_Era2018_16Feb2021_MINIAOD-skimv2-306144291bb2d755797972fd22d33d6d/USER',
            '/EGamma/mandrews-EGamma_2018D_Era2018_06Sep2020_AODslim-ecal_v1-306144291bb2d755797972fd22d33d6d/USER'
            ],
    'data2018-Run2018D2': [
            #"/EGamma/Run2018D-22Jan2019-v2/MINIAOD",
            #'/EGamma/Run2018D-22Jan2019-v2/AOD'
            #'/EGamma/mandrews-data2018-Run2018D2_Era2018_06Sep2020_MINIAOD-skimv2-306144291bb2d755797972fd22d33d6d/USER',
            '/EGamma/mandrews-data2018-Run2018D2_Era2018_16Feb2021_MINIAOD-skimv2-306144291bb2d755797972fd22d33d6d/USER',
            '/EGamma/mandrews-EGamma_2018D_Era2018_06Sep2020_AODslim-ecal_v1-306144291bb2d755797972fd22d33d6d/USER'
            ],
    'data2018-Run2018D3': [
            #"/EGamma/Run2018D-22Jan2019-v2/MINIAOD",
            #'/EGamma/Run2018D-22Jan2019-v2/AOD'
            #'/EGamma/mandrews-data2018-Run2018D3_Era2018_06Sep2020_MINIAOD-skimv2-306144291bb2d755797972fd22d33d6d/USER',
            '/EGamma/mandrews-data2018-Run2018D3_Era2018_16Feb2021_MINIAOD-skimv2-306144291bb2d755797972fd22d33d6d/USER',
            '/EGamma/mandrews-EGamma_2018D_Era2018_06Sep2020_AODslim-ecal_v1-306144291bb2d755797972fd22d33d6d/USER'
            ],
    'bg2018-dy0':  [
            '/DYToEE_M-50_NNPDF31_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1/MINIAODSIM',
            '/DYToEE_M-50_NNPDF31_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18DRPremix-102X_upgrade2018_realistic_v15-v1/AODSIM'
            ]
    #'bg2018-dy0':  [
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext2-v1/MINIAODSIM',
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIAutumn18DRPremix-102X_upgrade2018_realistic_v15_ext2-v1/AODSIM'
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2018-dy0_Era2018_06Sep2020_MINIAOD-skimv3-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        #''
    #        ],
    #'bg2018-dy1':  [
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext2-v1/MINIAODSIM',
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIAutumn18DRPremix-102X_upgrade2018_realistic_v15_ext2-v1/AODSIM'
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2018-dy1_Era2018_06Sep2020_MINIAOD-skimv3-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2018-dy1_Era2018_16Feb2021_MINIAOD-skimv2-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        #''
    #        ],
    #'bg2018-dy2':  [
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext2-v1/MINIAODSIM',
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIAutumn18DRPremix-102X_upgrade2018_realistic_v15_ext2-v1/AODSIM'
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2018-dy2_Era2018_06Sep2020_MINIAOD-skimv3-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2018-dy2_Era2018_16Feb2021_MINIAOD-skimv2-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        #''
    #        ],
    #'bg2018-dy3':  [
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext2-v1/MINIAODSIM',
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIAutumn18DRPremix-102X_upgrade2018_realistic_v15_ext2-v1/AODSIM'
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2018-dy3_Era2018_06Sep2020_MINIAOD-skimv3-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2018-dy3_Era2018_16Feb2021_MINIAOD-skimv2-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        #''
    #        ],
    #'bg2018-dy4':  [
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext2-v1/MINIAODSIM',
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIAutumn18DRPremix-102X_upgrade2018_realistic_v15_ext2-v1/AODSIM'
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2018-dy4_Era2018_06Sep2020_MINIAOD-skimv3-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2018-dy4_Era2018_16Feb2021_MINIAOD-skimv2-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        #''
    #        ],
    #'bg2018-dy5':  [
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext2-v1/MINIAODSIM',
    #        '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIAutumn18DRPremix-102X_upgrade2018_realistic_v15_ext2-v1/AODSIM'
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2018-dy5_Era2018_06Sep2020_MINIAOD-skimv3-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-bg2018-dy5_Era2018_16Feb2021_MINIAOD-skimv2-3ee3afd6b5a1410aea6d0b4d52723d06/USER',
    #        #''
    #        ]

}
#'''

for s,dset in samples.iteritems(): #python3: samples.items()

    #if 'Run2016' not in s: continue
    #if 'Run2018' not in s: continue
    #if 'Run2018A' not in s: continue
    #if 'Run2018A' in s: continue
    if 'bg2016-dy' not in s: continue
    #if 'bg2017-dy' not in s: continue
    #if 'bg2018-dy' not in s: continue
    #if 'dy1' in s or 'dy3' in s: continue
    #if 'dy1' not in s and 'dy3' not in s: continue
    #if 'Run2017' not in s: continue
    #if '2017' not in s: continue
    #if '2016' not in s: continue
    #if 'bg2016' not in s: continue

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
    file_data = file_data.replace(DATASET, dset[0])
    file_data = file_data.replace(SECONDARYDATASET, dset[1])
    #if 'Run2018A' in s:
    #if 'Run2018' in s or 'Run2016H' in s or 'dy' in s:
    #if 'Run2018' in s or 'Run2016H' in s:
    #if 'Run2018' in s:

    #    # If lumimask needed on skimmed AODs
    #    #if 'bg2017-dy' in s:
    #    #    # only if using aod skim with missing lumis, otherwise use evt skim lumimask
    #    #    aodskim_campaign = 'Era06Sep2020_AODslim-ecal_v2' # DY2017
    #    #    s_aod = re.findall('(.*dy)[0-9]', s)[0]
    #    ##elif 'Run2016H' in s:
    #    ##    aodskim_campaign = 'Era28Dec2020_AODslim-ecal_v1' # Run2016H re-AODslim with missing blocks
    #    #else:
    #    aodskim_campaign = 'Era06Sep2020_AODslim-ecal_v1' # Run2018A, Run2016H, 2018*, DY2016
    #    s_aod = re.findall('(.*201[6-8][A-Z])', s)[0]
    #    lumi_list = '%s/h2aa/aodSkims/%s/%s_lumi_list.json'%(base_dir, aodskim_campaign, s_aod)
    #    assert os.path.isfile(lumi_list)
    #    assert aodskim_campaign.strip('Era') in dset[1]
    #    file_data = file_data.replace(LUMIMASK, lumi_list)

    #    # Include evt list if running on full aod/miniaod dsets
    #    if 'Run2018A' in s:
    #        #ggskim_campaign = 'ggNtuples-Era24Sep2020v1_ggSkim-v2' # 2018A. data+h4g+hgg, bad h4g,hgg dipho trgs
    #        ggskim_campaign = 'ggNtuples-Era24Sep2020v1_ggSkimZee-v3' # dy+data zee skim(nele+presel)
    #        year = re.findall('(201[6-8])', s.split('-')[0])[0]
    #        ggskim_dir = '/eos/uscms/store/user/lpchaa4g/mandrews/%s/%s/ggSkims'%(year, ggskim_campaign)
    #        evt_lists = glob.glob('%s/%s*_event_list.txt'%(ggskim_dir, s))
    #        assert len(evt_lists) == 1
    #        evt_list = evt_lists[0]
    #        assert os.path.isfile(evt_list), '%s not found'%evt_list
    #        file_data = file_data.replace(EVTLIST, evt_list)

    #if '2017' in s or '2016' in s:
    #if '2018' in s or '2017' in s or '2016' in s:
    #if 'bg2017-dy' in s:
    #if 'dy' in s:
    if 'Run2018A' in s or 'dy' in s:

        # Use full miniaod+aod inputs so need to include skimmed evt+lumi list as job mask
        # for others, input miniaod already skimmed so no need to include mask again

        #ggskim_campaign = 'ggNtuples-Era24Sep2020v1_ggSkimZee-v1' # dy
        if 'Run' in s:
            ggskim_campaign = 'ggNtuples-Era24Sep2020v1_ggSkimZee-v3' # dy(DYToLL)+data zee skim(nele+presel). dy here not used anymore.
        else:
            ggskim_campaign = 'ggNtuples-Era09Mar2021v1_ggSkimZee-v1' # dy(DYToEE) zee skim(nele+presel)
        year = re.findall('(201[6-8])', s.split('-')[0])[0]
        ggskim_dir = '/eos/uscms/store/user/lpchaa4g/mandrews/%s/%s/ggSkims'%(year, ggskim_campaign)
        # evt list
        evt_lists = glob.glob('%s/%s*_event_list.txt'%(ggskim_dir, s))
        assert len(evt_lists) == 1
        evt_list = evt_lists[0]
        assert os.path.isfile(evt_list), '%s not found'%evt_list
        file_data = file_data.replace(EVTLIST, evt_list)

        # lumi list
        ## bg2016-dy has more than 10k lumis so do not use lumimask or will trigger SUBMITFAILED
        ##if 'bg2016-dy' not in s:

        # Run edmPickEvents on filtered event list for this sample
        # Itemized by runId:lumiId:eventId
        cmd = 'edmPickEvents.py "%s" %s --crab'%(dset[0], evt_list)
        returncode = subprocess.call(cmd.split(' '))
        if returncode != 0:
            raise Exception('edmPickEvents failed')

        # Copy generated lumi mask
        lumi_list = '%s/%s_lumi_list.json'%(ggskim_dir, s)
        shutil.move('%s/pickevents.json'%os.getcwd(), '%s'%(lumi_list)) # shutil.move(src, dest)

        #lumi_lists = glob.glob('%s/%s*_lumi_list.json'%(ggskim_dir, s))
        #assert len(lumi_lists) == 1
        #lumi_list = lumi_lists[0]
        #assert os.path.isfile(lumi_list), '%s not found'%lumi_list
        file_data = file_data.replace(LUMIMASK, lumi_list)

    # if using miniaod skims, no need to use evt,lumi filters
    file_data = file_data.replace(CAMPAIGN, this_campaign)

    job_units = 30 #30,50
    splitting = 'LumiBased'
    #if 'data2016' in s:
    #    job_units = 30
    if 'Run2018A' in s:
        # if running full MINIAOD/AOD to minimize fails -> doesnt seem to help
        job_units = 4
        splitting = 'FileBased'
    #elif 'Run2018' in s:
    #    job_units = 10
    elif 'data' in s: #2017,2016,2018 except 2018A
        job_units = 25
    #if 'bg2016-dy' in s:
    #    # if using skim inputs
    #    job_units = 25 # if using skims
    #    # if using whole miniaod/aod
    #    # bg2016-dy has more than 100k lumis so use FileBased or will trigger SUBMITFAILED
    #    #splitting = 'FileBased'
    #    job_units = 25 # if using whole miniaod
    #elif 'dy' in s: # if using skims
    #    job_units = 6 #10
    elif 'dy' in s: # if using whole miniaod+aod since nlumis can be >100k
        splitting = 'FileBased'
        job_units = 1
    file_data = file_data.replace(UNITSPERJOB, str(job_units))
    file_data = file_data.replace(SPLIT, splitting)

    #break
    # Write out sample-specific crabConfig
    with open('%s/crabConfig_SCRegressor_%s.py'%(crab_folder, s), "w") as sample_file:
        sample_file.write(file_data)

    #'''
