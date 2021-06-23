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
SPLIT = '__SPLIT__'
EVTCONT = 'IMG'

#config.General.instance = 'preprod'
config.General.requestName = '%s_%s'%(SAMPLE,CAMPAIGN)
config.General.workArea = 'crab_MC'
config.General.transferOutputs = True
config.General.transferLogs = False

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = '/uscms/home/mba2012/nobackup/h2aa/CMSSW_10_5_0/src/MLAnalyzer/RecHitAnalyzer/python/SCRegressor_cfg.py'#%os.environ['CMSSW_BASE']
config.JobType.maxJobRuntimeMin = 2750 # mins
config.JobType.maxMemoryMB = 2600
if 'txt' in EVTLIST:
    config.JobType.pyCfgParams = ['eventsToProcess_load=%s'%EVTLIST]

config.Data.outputDatasetTag = config.General.requestName
#config.Data.splitting = 'LumiBased'
config.Data.splitting = SPLIT
config.Data.unitsPerJob = int(UNITSPERJOB)
if 'json' in LUMIMASK:
    config.Data.lumiMask = LUMIMASK

config.Data.inputDataset = DATASET
if '_AOD' in SECONDARYDATASET or '/AOD' in SECONDARYDATASET:
    config.Data.secondaryInputDataset = SECONDARYDATASET
config.Data.inputDBS = 'phys03' if '/USER' in DATASET or '/USER' in SECONDARYDATASET else 'global'

#config.Data.outLFNDirBase = '/store/group/lpcml/mandrews/2017/%s'%CAMPAIGN
#config.Data.outLFNDirBase = '/store/group/lpchaa4g/mandrews/2017/%s'%CAMPAIGN
config.Data.outLFNDirBase = '/store/user/mandrews/Run%s/%s'%(CAMPAIGN.split('_')[0].replace('Era',''), CAMPAIGN)
config.Data.publication = False
print(config.Data.outLFNDirBase)

#config.Site.storageSite = 'T2_CH_CERN'
#config.Site.storageSite = 'T3_US_FNALLPC'
config.Site.storageSite = 'T3_US_CMU'
#config.Site.ignoreGlobalBlacklist = True if ('GluGluHToGG' in SAMPLE) and ('2017' in SAMPLE) else False
config.Site.whitelist = ['T1_*','T2_*']
#config.Site.whitelist = ['T2_US_Caltech','T2_US_Florida','T2_US_MIT','T2_US_Nebraska','T2_US_Purdue','T2_US_UCSD','T2_US_Vanderbilt'] # T2_US* - T2_US_Wisconsin
#config.Site.whitelist = ['T2_UK*', 'T2_DE*', 'T2_US_Caltech','T2_US_Florida','T2_US_MIT','T2_US_Nebraska','T2_US_Purdue','T2_US_UCSD','T2_US_Vanderbilt'] # T2_US* - T2_US_Wisconsin
#config.Site.blacklist = ['T2_US_Wisconsin', 'T3_US_FNALLPC']
config.Data.ignoreLocality = True
