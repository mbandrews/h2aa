from __future__ import print_function
from Utilities.General.cmssw_das_client import get_data as das_query
from FWCore.PythonUtilities.LumiList import LumiList
import os, re, glob, shutil
import numpy as np
import subprocess

dsets = [
    #'/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext2-v1/MINIAODSIM',
    '/DYToEE_M-50_NNPDF31_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1/MINIAODSIM',
]

#for s,dset in samples.iteritems(): #python3: samples.items()
for dset in dsets: #python3: samples.items()

    print('For dset:',dset)

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
        print('        .. N lumis:', len(lumi))
        lumi_dict[run] = lumi
        break
    assert len(qdata) == len(lumi_dict)

    '''
    # Convert dict to json
    #base_dir = '.'
    lumi_list = '%s/%s_lumi_list.json'%(base_dir, s)
    print('     .. writing to: %s'%lumi_list)
    lumi_json = LumiList(runsAndLumis=lumi_dict)
    lumi_json.writeJSON(lumi_list)
    '''
