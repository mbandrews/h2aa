
## Edited By Raman Khurana
##
## CRAB documentation : https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideCrab
##
## CRAB 3 parameters : https://twiki.cern.ch/twiki/bin/view/CMSPublic/CRAB3ConfigurationFile#CRAB_configuration_parameters
##
## Once you are happy with this file, please run
## crab submit

## In CRAB3 the configuration file is in Python language. It consists of creating a Configuration object imported from the WMCore library: 

from WMCore.Configuration import Configuration
config = Configuration()

##  Once the Configuration object is created, it is possible to add new sections into it with corresponding parameters
config.section_("General")
config.General.requestName = 'pickEvents'
config.General.workArea = 'crab_pickevents_20210610_213739'


config.section_("JobType")
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = '/cvmfs/cms.cern.ch/slc7_amd64_gcc700/cms/cmssw/CMSSW_10_5_0/src/PhysicsTools/Utilities/configuration/copyPickMerge_cfg.py'
config.JobType.pyCfgParams = ['eventsToProcess_load=pickevents_runEvents.txt', 'outputFile=pickevents.root']

config.section_("Data")
config.Data.inputDataset = '"/"'

config.Data.inputDBS = 'global'
config.Data.splitting = 'LumiBased'
config.Data.unitsPerJob = 5
config.Data.lumiMask = 'pickevents.json'
#config.Data.publication = True
#config.Data.publishDbsUrl = 'phys03'
#config.Data.publishDataName = 'CRAB3_CSA_DYJets'
#config.JobType.allowNonProductionCMSSW=True

config.section_("Site")
## Change site name accordingly
config.Site.storageSite = "T2_US_Wisconsin"

