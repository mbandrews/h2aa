import os
from CRABClient.UserUtilities import config#, getUsernameFromSiteDB
config = config()
#from Utilities.General.cmssw_das_client import get_data as das_query

SAMPLE = '__SAMPLE__'
DATASET = '__DATASET__'
SECONDARYDATASET = '__SECONDARYDATASET__'
EVTLIST = '__EVTLIST__'
LUMIMASK = '__LUMIMASK__'
CAMPAIGN = '__CAMPAIGN__'
UNITSPERJOB = '__UNITSPERJOB__'
SPLIT = '__SPLIT__'
EVTCONT = 'MINIAOD-skim'

#config.General.instance = 'preprod'
#config.General.requestName = '%s_%s_%s'%(SAMPLE,CAMPAIGN,EVTCONT)
config.General.requestName = '%s_%s'%(SAMPLE,CAMPAIGN)
config.General.workArea = 'crab_MC'
config.General.transferOutputs = True
config.General.transferLogs = False

#config.JobType.pluginName = 'PrivateMC'
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = '/cvmfs/cms.cern.ch/slc7_amd64_gcc700/cms/cmssw/CMSSW_10_5_0/src/PhysicsTools/Utilities/configuration/copyPickMerge_cfg.py'
#if SAMPLE == 'Run2018D':
#if 'dy' in SAMPLE:
config.JobType.maxMemoryMB = 2800
config.JobType.pyCfgParams = ['eventsToProcess_load=%s'%EVTLIST]
config.JobType.maxJobRuntimeMin = 2750 # mins

config.Data.outputDatasetTag = config.General.requestName
#config.Data.splitting = 'LumiBased'
config.Data.splitting = SPLIT
config.Data.unitsPerJob = int(UNITSPERJOB)
if LUMIMASK != 'None':
    config.Data.lumiMask = LUMIMASK

config.Data.inputDataset = DATASET
config.Data.inputDBS = 'phys03' if '/USER' in DATASET or '/USER' in SECONDARYDATASET else 'global'

#config.Data.outLFNDirBase = '/store/group/lpcml/mandrews/2017/%s'%CAMPAIGN
config.Data.outLFNDirBase = '/store/user/mandrews/Run%s/%s'%(CAMPAIGN.split('_')[0].replace('Era',''), CAMPAIGN)
config.Data.publication = True
#config.Data.publication = False
print(config.Data.outLFNDirBase)

#config.Site.storageSite = 'T2_CH_CERN'
#config.Site.storageSite = 'T3_US_FNALLPC'
config.Site.storageSite = 'T3_US_CMU'

config.Site.ignoreGlobalBlacklist = True if 'GluGluHToGG' in SAMPLE else False
#config.Site.whitelist = ['T2_US*']
#config.Site.whitelist = ['T2_US_Caltech','T2_US_Florida','T2_US_MIT','T2_US_Nebraska','T2_US_Purdue','T2_US_UCSD','T2_US_Vanderbilt'] # T2_US* - T2_US_Wisconsin
config.Site.blacklist = ['T2_US_Wisconsin']
#config.Data.ignoreLocality = True
