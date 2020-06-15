import os
from CRABClient.UserUtilities import config
config = config()
#from Utilities.General.cmssw_das_client import get_data as das_query

SAMPLE = '__SAMPLE__'
DATASET = '__DATASET__'
SECONDARYDATASET = '__SECONDARYDATASET__'
EVTLIST = '__EVTLIST__'
LUMIMASK = '__LUMIMASK__'
CAMPAIGN = '__CAMPAIGN__'
UNITSPERJOB = '__UNITSPERJOB__'
EVTCONT = 'IMG'

#config.General.requestName = '%s_%s_%s'%(SAMPLE,CAMPAIGN,EVTCONT)
config.General.requestName = '%s_%s'%(SAMPLE,CAMPAIGN)
config.General.workArea = 'crab_MC'
config.General.transferOutputs = True
config.General.transferLogs = False

#config.JobType.pluginName = 'PrivateMC'
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = '/uscms/home/mba2012/nobackup/h2aa/CMSSW_10_5_0/src/MLAnalyzer/RecHitAnalyzer/python/SCRegressor_cfg.py'#%os.environ['CMSSW_BASE']
#config.JobType.psetName = '/cvmfs/cms.cern.ch/slc7_amd64_gcc700/cms/cmssw/CMSSW_10_5_0/src/PhysicsTools/Utilities/configuration/copyPickMerge_cfg.py'
config.JobType.maxMemoryMB = 2600
#config.JobType.pyCfgParams = ['eventsToProcess_load=%s'%EVTLIST]
config.JobType.maxJobRuntimeMin = 2750 # mins

config.Data.outputDatasetTag = config.General.requestName
config.Data.splitting = 'LumiBased'
config.Data.unitsPerJob = int(UNITSPERJOB)
if 'json' in LUMIMASK:
    config.Data.lumiMask = LUMIMASK

config.Data.inputDataset = DATASET
#if 'DoubleEG' in SAMPLE or 'h24gamma' in SAMPLE:
#if 'Run201' in SAMPLE or 'h24gamma' in SAMPLE:
if '_AOD' in SECONDARYDATASET or '/AOD' in SECONDARYDATASET:
    config.Data.secondaryInputDataset = SECONDARYDATASET
config.Data.inputDBS = 'phys03' if '/USER' in DATASET or '/USER' in SECONDARYDATASET else 'global'

#config.Data.outLFNDirBase = '/store/group/lpcml/mandrews/2017/%s'%CAMPAIGN
config.Data.outLFNDirBase = '/store/group/lpchaa4g/mandrews/2017/%s'%CAMPAIGN
config.Data.publication = False

#config.Site.storageSite = 'T2_CH_CERN'
config.Site.storageSite = 'T3_US_FNALLPC'
config.Site.ignoreGlobalBlacklist = True if 'GluGluHToGG' in SAMPLE else False
