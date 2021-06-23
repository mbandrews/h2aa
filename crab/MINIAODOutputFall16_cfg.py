# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: step2 --filein step_LHEGSR.root --fileout file:step_aodsim.root --mc --eventcontent MINIAOD runUnscheduled --datatier MINIAOD --conditions 94X_mc2017_realistic_v10 --step RAW2DIGI,RECO,RECOSIM,EI --nThreads 8 --era Run2_2017 --python_filename HIG-RunIIFall17DRPremix-00086_2_cfg.py --no_exec
import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Eras import eras

process = cms.Process('MINIAODskim',eras.Run2_2016)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
#process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
#process.load('SimGeneral.MixingModule.mixNoPU_cfi')
#process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
#process.load('Configuration.StandardSequences.MagneticField_cff')
#process.load('Configuration.StandardSequences.RawToDigi_cff')
#process.load('Configuration.StandardSequences.Reconstruction_cff')
#process.load('Configuration.StandardSequences.RecoSim_cff')
#process.load('CommonTools.ParticleFlow.EITopPAG_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(50)
)

# Input source
process.source = cms.Source("PoolSource",
    #fileNames = cms.untracked.vstring('file:step_aodsim.root'),
    #fileNames = cms.untracked.vstring('file:step_LHEGSR.root'),
    fileNames = cms.untracked.vstring('root://cmsdata.phys.cmu.edu//store/user/mandrews/Run2018/Era2018_06Sep2020_MINIAOD-skimv2/EGamma/data2018-Run2018C_Era2018_06Sep2020_MINIAOD-skimv2/201127_175240/0000/output_1.root'),
    secondaryFileNames = cms.untracked.vstring()
)

process.options = cms.untracked.PSet(

)

# Production Info
#process.configurationMetadata = cms.untracked.PSet(
#    annotation = cms.untracked.string('step2 nevts:1'),
#    name = cms.untracked.string('Applications'),
#    version = cms.untracked.string('$Revision: 1.19 $')
#)

# Output definition
#process.MINIAODEventContent.outputCommands.extend([
#  'drop *_*_*_*'
#  #,'keep recoGenParticles_genParticles_*_*'
#  #,'keep EcalRecHits*_reducedEcalRecHits*_*_*'
#  ,'keep EcalRecHits*_*_*_*'
#  #,'keep HBHERecHits*_reduced*_*_*'
#  #,'keep recoTracks*_generalTracks_*_*'
#  #,'keep recoPhoton*_gedPhoton*_*_*'
#  ])
process.MINIAODoutput = cms.OutputModule("PoolOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(4),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('MINIAOD'),
        filterName = cms.untracked.string('')
    ),
    eventAutoFlushCompressedSize = cms.untracked.int32(31457280),
    fileName = cms.untracked.string('file:step_miniaod.root'),
    outputCommands = process.MINIAODEventContent.outputCommands
)

# Additional output definition

# Other statements
#from Configuration.AlCa.GlobalTag import GlobalTag
#process.GlobalTag = GlobalTag(process.GlobalTag, '94X_mc2017_realistic_v10', '')
#process.DiPhotonFilter = cms.EDFilter("HLTHighLevel",
#                                          eventSetupPathsKey = cms.string(''),
#                                          TriggerResultsTag = cms.InputTag("TriggerResults","","HLT"),
#                                          HLTPaths = cms.vstring('HLT_DiPhoton*'),
#                                          andOr = cms.bool(True),
#                                          throw = cms.bool(False)
#                                          )
#process.hltfilter_step = cms.Path(process.DiPhotonFilter)

# Path and EndPath definitions
#process.raw2digi_step = cms.Path(process.RawToDigi)
#process.reconstruction_step = cms.Path(process.reconstruction)
#process.recosim_step = cms.Path(process.recosim)
#process.eventinterpretaion_step = cms.Path(process.EIsequence)
#process.endjob_step = cms.EndPath(process.endOfProcess)
process.MINIAODoutput_step = cms.EndPath(process.MINIAODoutput)

# Schedule definition
#process.schedule = cms.Schedule(process.raw2digi_step,process.reconstruction_step,process.recosim_step,process.eventinterpretaion_step,process.endjob_step,process.MINIAODoutput_step)
process.schedule = cms.Schedule(process.MINIAODoutput_step)
#process.schedule = cms.Schedule(process.hltfilter_step,process.MINIAODoutput_step)
#from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
#associatePatAlgosToolsTask(process)

#Setup FWK for multithreaded
#process.options.numberOfThreads=cms.untracked.uint32(8)
#process.options.numberOfStreams=cms.untracked.uint32(0)


# Customisation from command line

#Have logErrorHarvester wait for the same EDProducers to finish as those providing data for the OutputModule
#from FWCore.Modules.logErrorHarvester_cff import customiseLogErrorHarvesterUsingOutputCommands
#process = customiseLogErrorHarvesterUsingOutputCommands(process)

# Add early deletion of temporary data products to reduce peak memory need
#from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
#process = customiseEarlyDelete(process)
# End adding early deletion
