import os
from CRABClient.UserUtilities import config, getUsernameFromSiteDB
config = config()
#from Utilities.General.cmssw_das_client import get_data as das_query

SAMPLE = '__SAMPLE__'
DATASET = '__DATASET__'
#SECONDARYDATASET = '__SECONDARYDATASET__'
#EVTLIST = '__EVTLIST__'
#LUMIMASK = '__LUMIMASK__'
CAMPAIGN = '__CAMPAIGN__'
UNITSPERJOB = '__UNITSPERJOB__'
#EVTCONT = 'IMG'
EVTCONT = 'ggntuple'

#config.General.requestName = '%s_%s_%s'%(SAMPLE,CAMPAIGN,EVTCONT)
config.General.requestName = '%s_%s'%(SAMPLE,CAMPAIGN)
config.General.workArea = 'crab_MC'
config.General.transferOutputs = True
config.General.transferLogs = False

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = '/uscms/home/mba2012/nobackup/h2aa/CMSSW_9_4_13/src/ggAnalysis/ggNtuplizer/test/run_mc2017_94X.py'
#config.JobType.maxMemoryMB = 2800
#config.JobType.pyCfgParams = ['eventsToProcess_load=%s'%EVTLIST]

config.Data.outputDatasetTag = config.General.requestName
config.Data.splitting = 'LumiBased'
config.Data.unitsPerJob = int(UNITSPERJOB)
#config.Data.lumiMask = LUMIMASK

config.Data.inputDataset = DATASET
#config.Data.secondaryInputDataset = SECONDARYDATASET
config.Data.inputDBS = 'phys03' if '/USER' in DATASET else 'global'

config.Data.outLFNDirBase = '/store/group/lpcml/mandrews/2017/%s'%CAMPAIGN
#config.Data.publication = False # Only edm output files are publishable

#config.Site.storageSite = 'T2_CH_CERN'
config.Site.storageSite = 'T3_US_FNALLPC'
