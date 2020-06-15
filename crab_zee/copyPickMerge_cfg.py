import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing ('analysis')

# add a list of strings for events to process
options.register ('eventsToProcess',
				  '',
				  VarParsing.multiplicity.list,
				  VarParsing.varType.string,
				  "Events to process")
options.register ('maxSize',
				  0,
				  VarParsing.multiplicity.singleton,
				  VarParsing.varType.int,
				  "Maximum (suggested) file size (in Kb)")
options.parseArguments()

process = cms.Process("PickEvent")
process.source = cms.Source ("PoolSource",
	  fileNames = cms.untracked.vstring (options.inputFiles),
)

if options.eventsToProcess:
    process.source.eventsToProcess = \
           cms.untracked.VEventRange (options.eventsToProcess)


process.maxEvents = cms.untracked.PSet(
	    input = cms.untracked.int32 (options.maxEvents)
)


process.Out = cms.OutputModule("PoolOutputModule",
        fileName = cms.untracked.string (options.outputFile)
)

if options.maxSize:
    process.Out.maxSize = cms.untracked.int32 (options.maxSize)

#process.HLTLabel = cms.EDFilter("PATTriggerObjectStandAloneSelector",
#                                          src = cms.InputTag("slimmedPatTrigger"),
#                                          cut = cms.string('coll("hltEGL1SingleEGOrFilter")')
#)

process.HLTFilter = cms.EDFilter("HLTHighLevel",
                                          eventSetupPathsKey = cms.string(''),
                                          TriggerResultsTag = cms.InputTag("TriggerResults","","HLT"),
                                          HLTPaths = cms.vstring('HLT_Ele32_WPTight_Gsf_L1DoubleEG_v*'),
                                          andOr = cms.bool(True), # True = OR, False = AND
                                          throw = cms.bool(True) # Tolerate if triggers not available
                                          )

#process.end = cms.EndPath(process.HLTLabel*process.HLTFilter*process.Out)
process.end = cms.EndPath(process.HLTFilter*process.Out)
#process.end = cms.EndPath(process.Out)
