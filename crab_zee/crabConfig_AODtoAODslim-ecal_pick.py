import os
from CRABClient.UserUtilities import config
config = config()
#from Utilities.General.cmssw_das_client import get_data as das_query

SAMPLE = '__SAMPLE__'
DATASET = '__DATASET__'
CAMPAIGN = '__CAMPAIGN__'
UNITSPERJOB = '__UNITSPERJOB__'
EVTLIST = '__EVTLIST__'
LUMIMASK = '__LUMIMASK__'

config.General.requestName = '%s_%s'%(SAMPLE,CAMPAIGN)
config.General.workArea = 'crab_MC'
config.General.transferOutputs = True
config.General.transferLogs = False

#config.JobType.pluginName = 'PrivateMC'
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = '/uscms/home/mba2012/nobackup/h2aa/CMSSW_10_5_0/src/h2aa/crab_zee/HIG-RunIIFall17DRPremix_cfg_slim-ecal_pick.py'
#config.JobType.maxMemoryMB = 2800
config.JobType.maxJobRuntimeMin = 2750 # mins
config.JobType.pyCfgParams = ['eventsToProcess_load=%s'%EVTLIST]

config.Data.outputDatasetTag = config.General.requestName
config.Data.splitting = 'LumiBased'
config.Data.unitsPerJob = int(UNITSPERJOB)
config.Data.lumiMask = LUMIMASK

config.Data.inputDataset = DATASET

config.Data.outLFNDirBase = '/store/group/lpchaa4g/mandrews/2017/%s'%CAMPAIGN
#config.Data.publication = False
config.Data.publication = True

#config.Site.storageSite = 'T2_CH_CERN'
config.Site.storageSite = 'T3_US_FNALLPC'
#config.Site.ignoreGlobalBlacklist = True if 'BAD_ERA' in SAMPLE else False
