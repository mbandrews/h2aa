import os
from CRABClient.UserUtilities import config
config = config()
#from Utilities.General.cmssw_das_client import get_data as das_query

SAMPLE = '__SAMPLE__'
DATASET = '__DATASET__'
CAMPAIGN = '__CAMPAIGN__'
UNITSPERJOB = '__UNITSPERJOB__'
LUMIMASK = '__LUMIMASK__'

config.General.requestName = '%s_%s'%(SAMPLE,CAMPAIGN)
config.General.workArea = 'crab_MC'
config.General.transferOutputs = True
config.General.transferLogs = False

#config.JobType.pluginName = 'PrivateMC'
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = '/uscms/home/mba2012/nobackup/h2aa/CMSSW_10_5_0/src/h2aa/crab/HIG-RunIIFall17DRPremix_cfg_slim-ecal.py'
config.JobType.maxMemoryMB = 2600
config.JobType.maxJobRuntimeMin = 2750 # mins

config.Data.outputDatasetTag = config.General.requestName
config.Data.splitting = 'LumiBased'
config.Data.unitsPerJob = int(UNITSPERJOB)
if LUMIMASK != 'None':
    config.Data.lumiMask = LUMIMASK

config.Data.inputDataset = DATASET

#config.Data.outLFNDirBase = '/store/group/lpchaa4g/mandrews/2017/%s'%CAMPAIGN
#config.Data.outLFNDirBase = '/store/user/mandrews/2016/%s'%CAMPAIGN
#config.Data.outLFNDirBase = '/store/user/mandrews/Run%s/%s'%(SAMPLE.split('_')[-1][:-1], CAMPAIGN)
config.Data.outLFNDirBase = '/store/user/mandrews/Run%s/%s'%(CAMPAIGN.split('_')[0].replace('Era',''), CAMPAIGN)
#config.Data.publication = False
config.Data.publication = True
print(config.Data.outLFNDirBase)

#config.Site.storageSite = 'T2_CH_CERN'
#config.Site.storageSite = 'T3_US_FNALLPC'
config.Site.storageSite = 'T3_US_CMU'
#config.Site.ignoreGlobalBlacklist = True if 'BAD_ERA' in SAMPLE else False
