from __future__ import print_function
from multiprocessing import Pool
import os, glob
import numpy as np
from data_utils import *
from Utilities.General.cmssw_das_client import get_data as das_query
from FWCore.PythonUtilities.LumiList import LumiList

run = 'Run2017'
samples = {
    '%sB'%run: '/DoubleEG/mandrews-Run2017B_17Nov2017-v1_AOD_slim-ext_v2-3bfee02a0afb4bfd03fd5261a90623cd/USER',
    '%sC'%run: '/DoubleEG/mandrews-Run2017C_17Nov2017-v1_AOD_slim-ext_v2-3bfee02a0afb4bfd03fd5261a90623cd/USER',
    '%sD'%run: '/DoubleEG/mandrews-Run2017D_17Nov2017-v1_AOD_slim-ext-3bfee02a0afb4bfd03fd5261a90623cd/USER',
    '%sE'%run: '/DoubleEG/mandrews-Run2017E_17Nov2017-v1_AOD_slim-ext_v2-3bfee02a0afb4bfd03fd5261a90623cd/USER',
    '%sF'%run: '/DoubleEG/mandrews-Run2017F_17Nov2017-v1_AOD_slim-ext_v2-964eedbb4080135606054ba835f474dc/USER'
    }

output_dir = '../evtsToProc/'
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

def mk_secondary_lumimask(dset):

    dq = das_query("file dataset=%s instance=prod/phys03"%dset, cmd='dasgoclient --dasmaps=./')
    assert 'data' in dq.keys()
    fs = [str(f['file'][0]['name']) for f in dq['data']]
    #fs = fs[:2]
    print('N files:',len(fs))

    lumis = []
    dqs = [das_query("lumi file=%s instance=prod/phys03"%f, cmd='dasgoclient --dasmaps=./') for f in fs]
    for dq in dqs:
        for data in dq['data']:
            for lumi in data['lumi'][0]['lumi_section_num']:
                lumis.append([data['lumi'][0]['run_number'], lumi])

    jsonList = LumiList(lumis=lumis)
    #print(jsonList)
    output_file = dset.split('/')[2].split('-')[1].split('_')[0]
    #print(output_file)
    jsonList.writeJSON(output_dir+output_file+'_3photons_imgskim_lumi_list.json')

dsets = []
for s,dset in samples.iteritems():

    print('For sample:',s)

    #input_files = glob.glob('../ggSkims/%s_ggskim.root'%s)
    #input_files = glob.glob('../ggSkims/3pho/%s_*ggskim.root'%s)
    #print('len(input_files):',len(input_files))
    #assert len(input_files) == 1

    print(dset)
    dsets.append(dset)
    #dsets.append('getEventsToProc.py -i %s -s %s -o %s'%(' '.join(input_files), s, output_dir))
    #print(cmd)
    #os.system(cmd)
    #break

print('N procs:',len(dsets))
#mk_secondary_lumimask(dsets[0])
pool = Pool(processes=len(dsets))
#pool.map(run_process, dsets)
pool.map(mk_secondary_lumimask, dsets)
pool.close()
pool.join()
