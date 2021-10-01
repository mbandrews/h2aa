from __future__ import print_function
from multiprocessing import Pool
import os, re, glob, shutil
import numpy as np
import subprocess

# Strings to replace in crabConfig template
SAMPLE = '__SAMPLE__'
DATASET = '__DATASET__'
EVTLIST = '__EVTLIST__'
LUMIMASK = '__LUMIMASK__'
CAMPAIGN = '__CAMPAIGN__'
UNITSPERJOB = '__UNITSPERJOB__'
SPLIT = '__SPLIT__'

#input_campaign = 'ggNtuples-Era24Sep2020v1_ggSkim-v2' # data+h4g+hgg, bad h4g,hgg dipho trgs
#input_campaign = 'ggNtuples-Era24Sep2020v1_ggSkimZee-v1' # zee
#input_campaign = 'ggNtuples-Era04Dec2020v1_ggSkim-v1' # h4g+hgg, fixed dipho trgs
#input_campaign = 'ggNtuples-Era24Sep2020v1_ggSkim-v4' # data only pi0 skim: trg-npho-presel(hgg hoe)
#input_campaign = 'ggNtuples-Era20May2021v1_ggSkim-v1' # Add mgg95 trgs for data, h4g, hgg
input_campaign = 'ggNtuples-Era20May2021v1_ggSkim-v2' # h4g, hgg: do NOT apply HLT dipho trg--applied later using trg SFs instead

#this_campaign = 'Era2017_17Dec2019_MINIAOD-skimv1'
#this_campaign = 'Era2017_29Jan2020_MINIAOD-skimv1'
#this_campaign = 'Era2017_20Feb2020_MINIAOD-skimv1'
#this_campaign = 'Era2017_23Feb2020_MINIAOD-skimv1'
#this_campaign = 'Era2017_23Feb2020_MINIAOD-skimv2'
#this_campaign = 'Era2017_23Feb2020_MINIAOD-skimv3'

# fixed total Nevts, mgg100-180
#this_campaign = 'Era2016_06Sep2020_MINIAOD-skimv2'
#this_campaign = 'Era2017_06Sep2020_MINIAOD-skimv2'
#this_campaign = 'Era2018_06Sep2020_MINIAOD-skimv2'

# fixed h4g,hgg dipho trgs
#this_campaign = 'Era2016_04Dec2020_MINIAOD-skimv1'
#this_campaign = 'Era2017_04Dec2020_MINIAOD-skimv1'
#this_campaign = 'Era2018_04Dec2020_MINIAOD-skimv1'

# redo 06Sep2020_MINIAOD-skimv2 DY only with more memory: v2 had excessive mem
#this_campaign = 'Era2016_06Sep2020_MINIAOD-skimv3'
#this_campaign = 'Era2017_06Sep2020_MINIAOD-skimv3'
#this_campaign = 'Era2018_06Sep2020_MINIAOD-skimv3'

# with evt picks+lumimask: ggNtuples-Era24Sep2020v1_ggSkim-v2
# redo 06Sep2020_MINIAOD-skimv2 2018A
#this_campaign = 'Era2016_06Sep2020_MINIAOD-skimv7'
#this_campaign = 'Era2017_06Sep2020_MINIAOD-skimv7'
#this_campaign = 'Era2018_06Sep2020_MINIAOD-skimv7'

# for data pi0 skim only
#this_campaign = 'Era2017_15Mar2021_MINIAOD-skimv1' # too much mem usage
#this_campaign = 'Era2016_15Mar2021_MINIAOD-skimv2' # lower jobUnits
#this_campaign = 'Era2017_15Mar2021_MINIAOD-skimv2' # lower jobUnits
#this_campaign = 'Era2018_15Mar2021_MINIAOD-skimv2' # lower jobUnits

# Add mgg95 trgs for data, h4g, hgg
#this_campaign = 'Era2016_20May2021_MINIAOD-skimv1'
#this_campaign = 'Era2017_20May2021_MINIAOD-skimv1'
#this_campaign = 'Era2018_20May2021_MINIAOD-skimv1'

# h4g: do NOT apply HLT dipho trg--applied later using trg SFs instead
this_campaign = 'Era2016_20May2021_MINIAOD-skimv2'
#this_campaign = 'Era2017_20May2021_MINIAOD-skimv2'
#this_campaign = 'Era2018_20May2021_MINIAOD-skimv2'

crab_folder = 'crab_%s'%this_campaign
if not os.path.isdir(crab_folder):
    os.makedirs(crab_folder)

#'''
samples = {
    #2016
    'data2016-Run2016B': "/DoubleEG/Run2016B-17Jul2018_ver2-v1/MINIAOD",
    'data2016-Run2016C': "/DoubleEG/Run2016C-17Jul2018-v1/MINIAOD",
    'data2016-Run2016D': "/DoubleEG/Run2016D-17Jul2018-v1/MINIAOD",
    'data2016-Run2016E': "/DoubleEG/Run2016E-17Jul2018-v1/MINIAOD",
    'data2016-Run2016F': "/DoubleEG/Run2016F-17Jul2018-v1/MINIAOD",
    'data2016-Run2016G': "/DoubleEG/Run2016G-17Jul2018-v1/MINIAOD",
    'data2016-Run2016H': "/DoubleEG/Run2016H-17Jul2018-v1/MINIAOD",
    'h4g2016-mA0p1GeV': '/HAHMHToAA_AToGG_MA-0p1GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1/MINIAODSIM',
    'h4g2016-mA0p2GeV': '/HAHMHToAA_AToGG_MA-0p2GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1/MINIAODSIM',
    'h4g2016-mA0p4GeV': '/HAHMHToAA_AToGG_MA-0p4GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1/MINIAODSIM',
    'h4g2016-mA0p6GeV': '/HAHMHToAA_AToGG_MA-0p6GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1/MINIAODSIM',
    'h4g2016-mA0p8GeV': '/HAHMHToAA_AToGG_MA-0p8GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1/MINIAODSIM',
    'h4g2016-mA1p0GeV': '/HAHMHToAA_AToGG_MA-1GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1/MINIAODSIM',
    'h4g2016-mA1p2GeV': '/HAHMHToAA_AToGG_MA-1p2GeV_TuneCUETP8M1_PSweights_13TeV-madgraph_pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1/MINIAODSIM',
    'bg2016-hgg': '/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext2-v2/MINIAODSIM',
    'bg2016-dy':  '/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext2-v1/MINIAODSIM',

    #2017
    'data2017-Run2017B': '/DoubleEG/Run2017B-31Mar2018-v1/MINIAOD',
    'data2017-Run2017C': '/DoubleEG/Run2017C-31Mar2018-v1/MINIAOD',
    'data2017-Run2017D': '/DoubleEG/Run2017D-31Mar2018-v1/MINIAOD',
    'data2017-Run2017E': '/DoubleEG/Run2017E-31Mar2018-v1/MINIAOD',
    'data2017-Run2017F': '/DoubleEG/Run2017F-31Mar2018-v1/MINIAOD',
    'h4g2017-mA0p1GeV': '/HAHMHToAA_AToGG_MA-0p1GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM',
    'h4g2017-mA0p2GeV': '/HAHMHToAA_AToGG_MA-0p2GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM',
    'h4g2017-mA0p4GeV': '/HAHMHToAA_AToGG_MA-0p4GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM',
    'h4g2017-mA0p6GeV': '/HAHMHToAA_AToGG_MA-0p6GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM',
    'h4g2017-mA0p8GeV': '/HAHMHToAA_AToGG_MA-0p8GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM',
    'h4g2017-mA1p0GeV': '/HAHMHToAA_AToGG_MA-1GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM',
    'h4g2017-mA1p2GeV': '/HAHMHToAA_AToGG_MA-1p2GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM',
    'bg2017-hgg': '/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM',
    'bg2017-dy':  '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/MINIAODSIM',

    #2018
    'data2018-Run2018A': "/EGamma/Run2018A-17Sep2018-v2/MINIAOD",
    'data2018-Run2018B': "/EGamma/Run2018B-17Sep2018-v1/MINIAOD",
    'data2018-Run2018C': "/EGamma/Run2018C-17Sep2018-v1/MINIAOD",
    'data2018-Run2018D': "/EGamma/Run2018D-22Jan2019-v2/MINIAOD",
    'h4g2018-mA0p1GeV': '/HAHMHToAA_AToGG_MA-0p1GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/MINIAODSIM',
    'h4g2018-mA0p2GeV': '/HAHMHToAA_AToGG_MA-0p2GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/MINIAODSIM',
    'h4g2018-mA0p4GeV': '/HAHMHToAA_AToGG_MA-0p4GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/MINIAODSIM',
    'h4g2018-mA0p6GeV': '/HAHMHToAA_AToGG_MA-0p6GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/MINIAODSIM',
    'h4g2018-mA0p8GeV': '/HAHMHToAA_AToGG_MA-0p8GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/MINIAODSIM',
    'h4g2018-mA1p0GeV': '/HAHMHToAA_AToGG_MA-1GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/MINIAODSIM',
    'h4g2018-mA1p2GeV': '/HAHMHToAA_AToGG_MA-1p2GeV_TuneCP5_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/MINIAODSIM',
    'bg2018-hgg': '/GluGluHToGG_M125_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1/MINIAODSIM',
    #'bg2018-dy':  '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext2-v1/MINIAODSIM'
    }
#'''

'''
#job_units = 100
job_units = 1000
samples = {
#    'DiPhotonJets':
#        '/DiPhotonJets_MGG-80toInf_13TeV_amcatnloFXFX_pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM',
#    'GJet_Pt20To40':
#        '/GJet_Pt-20to40_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM',
#    'GJet_Pt40ToInf':
#        '/GJet_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/MINIAODSIM',
#    'QCD_Pt30To40':
#        '/QCD_Pt-30to40_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM',
#    'QCD_Pt40ToInf':
#        '/QCD_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM',
    'GluGluHToGG':
        '/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM'
    }
'''

for s,dset in samples.iteritems(): #python3: samples.items()

    #if 'data2018-Run2018A' not in s: continue

    #if 'data2018' not in s: continue
    #if 'data2017' not in s: continue
    #if 'data2016' not in s: continue

    #if 'h4g2016' not in s: continue
    #if 'h4g2017' not in s: continue
    #if 'h4g2018' not in s: continue

    #if '2016-dy' not in s: continue
    #if '2017-dy' not in s: continue
    #if '2018-dy' not in s: continue

    if '2016' not in s: continue
    #if '2017' not in s: continue
    #if '2018' not in s: continue

    if 'hgg' not in s: continue
    #if 'h4g' not in s and 'hgg' not in s: continue

    print('For sample:',s)

    #assert os.environ['CMSSW_BASE'] != ''
    #base_dir = '%s/src'%os.environ['CMSSW_BASE']

    year = re.findall('(201[6-8])', s.split('-')[0])[0]
    base_dir = '/eos/uscms/store/user/lpchaa4g/mandrews/%s/%s/ggSkims'%(year, input_campaign)

    #evt_list = '%s/%s_event_list.txt'%(base_dir, s)
    evt_lists = glob.glob('%s/%s*_event_list.txt'%(base_dir, s))
    for evt_list in evt_lists:

        assert os.path.isfile(evt_list), '%s not found'%evt_list
        s = evt_list.split('/')[-1].split('_')[0]

        print('  >> Doing:',s)

        # Run edmPickEvents on filtered event list for this sample
        # Itemized by runId:lumiId:eventId
        cmd = 'edmPickEvents.py "%s" %s --crab'%(dset[0], evt_list)
        returncode = subprocess.call(cmd.split(' '))
        if returncode != 0:
            raise Exception('edmPickEvents failed')

        # Copy generated lumi mask
        lumi_list = '%s/%s_lumi_list.json'%(base_dir, s)
        shutil.move('%s/pickevents.json'%os.getcwd(), '%s'%(lumi_list)) # shutil.move(src, dest)
        # Work-around since data ggNtuples were not ntuplized with rereco lumi-mask
        # Use rereco lumimask instead
        if 'data2016' in s:
            #lumi_list = 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt'
            lumi_list = 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt'
        elif 'data2017' in s:
            #lumi_list = 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions17/13TeV/ReReco/Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt'
            lumi_list = 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions17/13TeV/ReReco/Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt'
        elif 'data2018' in s:
            #lumi_list = 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions18/13TeV/ReReco/Cert_314472-325175_13TeV_17SeptEarlyReReco2018ABC_PromptEraD_Collisions18_JSON.txt'
            lumi_list = 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions18/13TeV/ReReco/Cert_314472-325175_13TeV_17SeptEarlyReReco2018ABC_PromptEraD_Collisions18_JSON.txt'

        # Read in crabConfig template
        with open('crabConfig_pickEvents.py', "r") as template_file:
            file_data = template_file.read()

        # Replace crabConfig template strings with sample-specific values
        # NOTE: event list generated by edmPickEvents (pickevents_runEvents.txt) does not include LS numbers!!
        # This gives non-unique eventIds and so MUST be replaced with the original input `evt_list` above!
        file_data = file_data.replace(SAMPLE, s)
        file_data = file_data.replace(DATASET, dset)
        file_data = file_data.replace(EVTLIST, evt_list)
        file_data = file_data.replace(CAMPAIGN, this_campaign)

        splitting = 'LumiBased'
        if 'data2016' in s:
            job_units = 500 #800
            if '15Mar2021' in this_campaign:
                job_units = 300 # pi0 skim

        elif 'data2017' in s:
            job_units = 300 #500
            # didnt need:
            #if '15Mar2021' in this_campaign:
            #    job_units = 200 # pi0 skim

        elif 'data2018' in s:
            job_units = 40 #50
            if '15Mar2021' in this_campaign:
                job_units = 30 # pi0 skim

        elif 'h4g' in s:
            job_units = 1000

        elif 'dy' in s:
            # DY samples too large to query lumi-based info
            lumi_list = 'None'
            splitting = 'FileBased'
            job_units = 1

        else:
            job_units = 1000 # hgg

        file_data = file_data.replace(SPLIT, splitting)
        file_data = file_data.replace(UNITSPERJOB, str(job_units))
        file_data = file_data.replace(LUMIMASK, lumi_list)

        # Write out sample-specific crabConfig
        with open('%s/crabConfig_pickEvents_%s.py'%(crab_folder, s), "w") as sample_file:
            sample_file.write(file_data)
