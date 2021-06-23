from __future__ import print_function
from Utilities.General.cmssw_das_client import get_data as das_query
from FWCore.PythonUtilities.LumiList import LumiList
import os, re, glob, shutil
import numpy as np
import subprocess

input_campaign = '06Sep2020_AODslim-ecal_v1' # data,h4g,hgg, DY2016
#input_campaign = '28Dec2020_AODslim-ecal_v1' # data-2016H
#input_campaign = '06Sep2020_AODslim-ecal_v2' # DY2017

samples = {
    #'data2018-Run2018Cminiaod': '/EGamma/mandrews-data2018-Run2018C_Era2018_06Sep2020_MINIAOD-skimv2-6e67610c0756643cd1efca7b7fd48fa1/USER',
    #'data2018-Run2018A': '/EGamma/mandrews-EGamma_2018A_Era2018_06Sep2020_AODslim-ecal_v1-6e67610c0756643cd1efca7b7fd48fa1/USER',
    #'data2018-Run2018B': '/EGamma/mandrews-EGamma_2018B_Era2018_06Sep2020_AODslim-ecal_v1-6e67610c0756643cd1efca7b7fd48fa1/USER',
    #'data2018-Run2018C': '/EGamma/mandrews-EGamma_2018C_Era2018_06Sep2020_AODslim-ecal_v1-6e67610c0756643cd1efca7b7fd48fa1/USER',
    #'data2018-Run2018D': '/EGamma/mandrews-EGamma_2018D_Era2018_06Sep2020_AODslim-ecal_v1-306144291bb2d755797972fd22d33d6d/USER'
    #'data2018-Run2018C': '/EGamma/mandrews-EGamma_2018C_AODslim-ecal_TESTv2-6e67610c0756643cd1efca7b7fd48fa1/USER'
    #'data2018-Run2018C': '/EGamma/mandrews-data2018-Run2018C_Era2018_06Sep2020_MINIAOD-skimv2-6e67610c0756643cd1efca7b7fd48fa1/USER'
    #'data2018-Run2018C': '/EGamma/mandrews-EGamma_2018C_Era2018_06Sep2020_AODslim-ecal_v2-6e67610c0756643cd1efca7b7fd48fa1/USER'
    #'data2018-Run2018C': '/EGamma/mandrews-EGamma_2018C_AODslim-ecal_TESTv4-6e67610c0756643cd1efca7b7fd48fa1/USER'
    #'data2018-Run2018C': '/EGamma/mandrews-EGamma_2018C_Era2018_06Sep2020_AODslim-ecal_v3-6e67610c0756643cd1efca7b7fd48fa1/USER'
    #'data2018-Run2018C': '/EGamma/Run2018C-17Sep2018-v1/AOD'
    #'data2016-Run2016H': '/DoubleEG/mandrews-DoubleEG_2016H_Era2016_28Dec2020_AODslim-ecal_v1-2427c69bd126da1063d393ec79219651/USER'
    #'data2016-Run2016H': '/DoubleEG/mandrews-DoubleEG_2016H_Era2016_06Sep2020_AODslim-ecal_v1-2427c69bd126da1063d393ec79219651/USER'
    # AOD-slims:
    'data2016-Run2016B': '/DoubleEG/mandrews-DoubleEG_2016B_Era2016_06Sep2020_AODslim-ecal_v1-81ba725143e8ad84d6b47c9ab0eb90c4/USER',
    'data2016-Run2016C': '/DoubleEG/mandrews-DoubleEG_2016C_Era2016_06Sep2020_AODslim-ecal_v1-81ba725143e8ad84d6b47c9ab0eb90c4/USER',
    'data2016-Run2016D': '/DoubleEG/mandrews-DoubleEG_2016D_Era2016_06Sep2020_AODslim-ecal_v1-81ba725143e8ad84d6b47c9ab0eb90c4/USER',
    'data2016-Run2016E': '/DoubleEG/mandrews-DoubleEG_2016E_Era2016_06Sep2020_AODslim-ecal_v1-81ba725143e8ad84d6b47c9ab0eb90c4/USER',
    'data2016-Run2016F': '/DoubleEG/mandrews-DoubleEG_2016F_Era2016_06Sep2020_AODslim-ecal_v1-81ba725143e8ad84d6b47c9ab0eb90c4/USER',
    'data2016-Run2016G': '/DoubleEG/mandrews-DoubleEG_2016G_Era2016_06Sep2020_AODslim-ecal_v1-2427c69bd126da1063d393ec79219651/USER',
    'data2016-Run2016H': '/DoubleEG/mandrews-DoubleEG_2016H_Era2016_06Sep2020_AODslim-ecal_v1-2427c69bd126da1063d393ec79219651/USER',

    'data2017-Run2017B': '/DoubleEG/mandrews-DoubleEG_2017B_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER',
    'data2017-Run2017C': '/DoubleEG/mandrews-DoubleEG_2017C_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER',
    'data2017-Run2017D': '/DoubleEG/mandrews-DoubleEG_2017D_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER',
    'data2017-Run2017E': '/DoubleEG/mandrews-DoubleEG_2017E_Era2017_18May2020_AODslim-ecal_v1-3bfee02a0afb4bfd03fd5261a90623cd/USER',
    'data2017-Run2017F': '/DoubleEG/mandrews-DoubleEG_2017F_Era2017_18May2020_AODslim-ecal_v1-964eedbb4080135606054ba835f474dc/USER',

    'data2018-Run2018A': '/EGamma/mandrews-EGamma_2018A_Era2018_06Sep2020_AODslim-ecal_v1-6e67610c0756643cd1efca7b7fd48fa1/USER',
    'data2018-Run2018B': '/EGamma/mandrews-EGamma_2018B_Era2018_06Sep2020_AODslim-ecal_v1-6e67610c0756643cd1efca7b7fd48fa1/USER',
    'data2018-Run2018C': '/EGamma/mandrews-EGamma_2018C_Era2018_06Sep2020_AODslim-ecal_v1-6e67610c0756643cd1efca7b7fd48fa1/USER',
    'data2018-Run2018D': '/EGamma/mandrews-EGamma_2018D_Era2018_06Sep2020_AODslim-ecal_v1-306144291bb2d755797972fd22d33d6d/USER'

    # MINIAOD-skims:
    #'data2016-Run2016B': '/DoubleEG/mandrews-data2016-Run2016B_Era2016_06Sep2020_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
    #'data2016-Run2016C': '/DoubleEG/mandrews-data2016-Run2016C_Era2016_06Sep2020_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
    #'data2016-Run2016D': '/DoubleEG/mandrews-data2016-Run2016D_Era2016_06Sep2020_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
    #'data2016-Run2016E': '/DoubleEG/mandrews-data2016-Run2016E_Era2016_06Sep2020_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
    #'data2016-Run2016F': '/DoubleEG/mandrews-data2016-Run2016F_Era2016_06Sep2020_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
    #'data2016-Run2016G': '/DoubleEG/mandrews-data2016-Run2016G_Era2016_06Sep2020_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
    #'data2016-Run2016H': '/DoubleEG/mandrews-data2016-Run2016H_Era2016_06Sep2020_MINIAOD-skimv2-da20b4dc2a59d4df854398f842269346/USER',
}

for s,dset in samples.iteritems(): #python3: samples.items()

    print('For sample:',s)

    assert os.environ['CMSSW_BASE'] != ''
    assert os.environ['CMSSW_BASE'] in os.getcwd()
    #assert input_campaign in dset, 'Input campaign does not match sample dset: %s vs %s'%(input_campaign, dset.split('/')[1])

    year = re.findall('(201[6-8])', s.split('-')[0])[0]
    #base_dir = '%s/src/h2aa/aodSkims/Era%s'%(os.environ['CMSSW_BASE'], input_campaign)
    base_dir = '%s/src/h2aa/json/Era%s'%(os.environ['CMSSW_BASE'], input_campaign)
    if not os.path.isdir(base_dir):
        os.makedirs(base_dir)

    print('  >> Doing:',s)

    # Query DAS for run,lumi list
    # das query dict if successful: [u'status', u'mongo_query', u'ctime', u'nresults', u'timestamp', u'ecode', u'data']
    print('     .. querying: %s'%dset)
    #q = das_query('run,lumi dataset=%s instance=prod/phys03'%dset)
    q = das_query('run,lumi dataset=%s %s'%(dset, 'instance=prod/phys03' if 'USER' in dset else ''))
    print('     .. status: %s'%q['status'])
    if q['status'] != 'ok':
        print('     !! Query failed, skipping...')
        continue

    # Get run,lumi data
    lumi_dict = {}
    qdata = q['data'] # len(qdata) == N runs
    print('     .. N runs: %d'%len(qdata))
    for d in qdata:
        # d is a dict with keys: [u'run', u'lumi', u'qhash', u'das']
        run = d['run'][0]['run_number'] # gets actual run number as int
        lumi = d['lumi'][0]['number'] # gets actual lumis as list
        #print(run, lumi)
        lumi_dict[run] = lumi
        #break
    assert len(qdata) == len(lumi_dict)

    # Convert dict to json
    #base_dir = '.'
    lumi_list = '%s/%s_lumi_list.json'%(base_dir, s)
    print('     .. writing to: %s'%lumi_list)
    lumi_json = LumiList(runsAndLumis=lumi_dict)
    lumi_json.writeJSON(lumi_list)
    #'''
