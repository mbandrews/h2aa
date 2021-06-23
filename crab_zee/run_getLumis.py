from __future__ import print_function
from Utilities.General.cmssw_das_client import get_data as das_query
from FWCore.PythonUtilities.LumiList import LumiList
import os, re, glob, shutil
import numpy as np
import subprocess

samples = {
    'bg2016-dy': '/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/mandrews-DYToLL_Era2016_06Sep2020_AODslim-ecal_v1-b1a4edca9adfa7a2e4059536bf605cd7/USER',
    'bg2017-dy': '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/mandrews-DYToLL_Era2017_06Sep2020_AODslim-ecal_v2-351414bbda2cdc38d49da1680cef2a3f/USER'
}

for s,dset in samples.iteritems(): #python3: samples.items()

    print('For sample:',s)

    if 'bg2017-dy' in s:
        input_campaign = '06Sep2020_AODslim-ecal_v2' # DY2017
    else:
        input_campaign = '06Sep2020_AODslim-ecal_v1' # data,h4g,hgg, DY2016
        #input_campaign = '28Dec2020_AODslim-ecal_v1' # data-2016H

    assert os.environ['CMSSW_BASE'] != ''
    assert os.environ['CMSSW_BASE'] in os.getcwd()
    #assert input_campaign in dset, 'Input campaign does not match sample dset: %s vs %s'%(input_campaign, dset.split('/')[1])

    year = re.findall('(201[6-8])', s.split('-')[0])[0]
    base_dir = '%s/src/h2aa/aodSkims/Era%s'%(os.environ['CMSSW_BASE'], input_campaign)
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
