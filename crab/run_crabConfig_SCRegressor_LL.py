from __future__ import print_function
from multiprocessing import Pool
import os, glob, shutil, re
import numpy as np
import subprocess
from Utilities.General.cmssw_das_client import get_data as das_query
from FWCore.PythonUtilities.LumiList import LumiList

# Strings to replace in crabConfig template
SAMPLE = '__SAMPLE__'
DATASET = '__DATASET__'
SECONDARYDATASET = '__SECONDARYDATASET__'
EVTLIST = '__EVTLIST__'
LUMIMASK = '__LUMIMASK__'
CAMPAIGN = '__CAMPAIGN__'
UNITSPERJOB = '__UNITSPERJOB__'
SPLIT = '__SPLIT__'

# If lumimask used on aodskims
aodskim_campaign = 'Era06Sep2020_AODslim-ecal_v1' # Run2018A, Run2016H, 2018*, DY2016
# If running on whole MINIAOD/AOD dset instead of skim, apply evtlist
#ggskim_campaign = 'ggNtuples-Era24Sep2020v1_ggSkim-v2' # 2018A. data+h4g+hgg, bad h4g,hgg dipho trgs
#ggskim_campaign = 'ggNtuples-Era20May2021v1_ggSkim-v1'  # Add mgg95 trgs for data, h4g, hgg
#ggskim_campaign = 'ggNtuples-Era18Nov2021v1_ggSkim-v1'  # h4g LL, bad tau units
ggskim_campaign = 'ggNtuples-Era18Nov2021v2_ggSkim-v1'  # h4g LL, fixed tau units

# Add mgg95 trgs for data, h4g, hgg
#this_campaign = 'Era2017_18Nov2021_AOD-IMGv1'
#this_campaign = 'Era2017_18Nov2021_AOD-IMGv2' # add decay vertex pos. NOTE: some samples renamed by hand from _tau0 to -tau0
this_campaign = 'Era2017_18Nov2021_AOD-IMGv3' # fixed tau units

crab_folder = 'crab_%s'%this_campaign
if not os.path.isdir(crab_folder):
    os.makedirs(crab_folder)

#'''
splitting = 'LumiBased'
job_units = 50
# 2017
era_ = 2017
#samples_h4g = ['0p1', '0p2', '0p4', '0p6', '0p8', '1p0', '1p2']
samples_h4g = [
    '0p1GeV-ctau0-0ep00mm',
    '0p1GeV-ctau0-1ep00mm',
    '0p1GeV-ctau0-1ep01mm',
    '0p2GeV-ctau0-0ep00mm',
    '0p2GeV-ctau0-1ep00mm',
    '0p2GeV-ctau0-1ep01mm',
    '0p4GeV-ctau0-0ep00mm',
    '0p4GeV-ctau0-1ep00mm',
    '0p4GeV-ctau0-1ep01mm'
    #'0p1GeV-tau0-0ep00',
    #'0p1GeV-tau0-3em09',
    #'0p1GeV-tau0-3em11',
    #'0p2GeV-tau0-0ep00',
    #'0p2GeV-tau0-3em09',
    #'0p2GeV-tau0-3em11',
    #'0p4GeV-tau0-0ep00',
    #'0p4GeV-tau0-3em09',
    #'0p4GeV-tau0-3em11',
    #'0p1GeV-tau0-3em03',
    #'0p1GeV-tau0-3em05',
    #'0p1GeV-tau0-3em07',
    #'0p2GeV-tau0-3em03',
    #'0p2GeV-tau0-3em05',
    #'0p2GeV-tau0-3em07',
    #'0p4GeV-tau0-3em03',
    #'0p4GeV-tau0-3em05',
    #'0p4GeV-tau0-3em07'
    ]
samples = {}
for s in samples_h4g:
    samples['h4g%s-mA%s'%(era_, s)] = [
        '/hToaaTo4gammaLL/mandrews-hToaaTo4gammaLL_ma%s_RunIIFall17_RunIIFall17_MINIAODSIM-442a7f6ea2510b243c486adb7160c528/USER'%s,
        '/hToaaTo4gammaLL/mandrews-hToaaTo4gammaLL_ma%s_RunIIFall17_RunIIFall17_AODSIM-fcfc615a65be9fb627e3afc83a7469ff/USER'%s
        #'/hToaaTo4gammaLL/mandrews-hToaaTo4gammaLL_ma%s_RunIIFall17_MINIAODSIM-442a7f6ea2510b243c486adb7160c528/USER'%s.replace('-tau','_tau'),
        #'/hToaaTo4gammaLL/mandrews-hToaaTo4gammaLL_ma%s_RunIIFall17_AODSIM-fcfc615a65be9fb627e3afc83a7469ff/USER'%s.replace('-tau','_tau')
        ]

for s,dset in samples.iteritems(): #python3: samples.items()

    if 'h4g2017' not in s: continue

    print('>> For sample:',s)

    if len(dset) != 2:
        print('   !! incomplete sample. Skipping...')
        continue

    assert os.environ['CMSSW_BASE'] != ''
    base_dir = '%s/src'%os.environ['CMSSW_BASE']

    #'''
    # Read in crabConfig template
    with open('crabConfig_SCRegressor.py', "r") as template_file:
        file_data = template_file.read()

    # Replace crabConfig template strings with sample-specific values
    file_data = file_data.replace(SAMPLE, s)
    file_data = file_data.replace(DATASET, dset[0])
    file_data = file_data.replace(SECONDARYDATASET, dset[1])

    #if 'Run2018' in s or 'Run2016H' in s:

    #    # If lumimask needed on AODs
    #    s_aod = re.findall('(.*201[6-8][A-Z])', s)[0]
    #    lumi_list = '%s/h2aa/aodSkims/%s/%s_lumi_list.json'%(base_dir, aodskim_campaign, s_aod)
    #    assert os.path.isfile(lumi_list)
    #    #assert aodskim_campaign.strip('Era') in dset[1]
    #    file_data = file_data.replace(LUMIMASK, lumi_list)

    #    # Include evt list if running on full aod/miniaod dsets
    #    if 'Run2018A' in s:
    #        year = re.findall('(201[6-8])', s.split('-')[0])[0]
    #        ggskim_dir = '/eos/uscms/store/user/lpchaa4g/mandrews/%s/%s/ggSkims'%(year, ggskim_campaign)
    #        evt_lists = glob.glob('%s/%s*_event_list.txt'%(ggskim_dir, s))
    #        assert len(evt_lists) == 1
    #        evt_list = evt_lists[0]
    #        assert os.path.isfile(evt_list), '%s not found'%evt_list
    #        file_data = file_data.replace(EVTLIST, evt_list)

    file_data = file_data.replace(CAMPAIGN, this_campaign)
    file_data = file_data.replace(UNITSPERJOB, str(job_units))
    file_data = file_data.replace(SPLIT, splitting)

    #break
    # Write out sample-specific crabConfig
    with open('%s/crabConfig_SCRegressor_%s.py'%(crab_folder, s), "w") as sample_file:
        sample_file.write(file_data)

    #'''
