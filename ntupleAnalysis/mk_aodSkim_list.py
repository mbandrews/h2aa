from __future__ import print_function
import os, glob, re
from data_utils import *

campaign = '06Sep2020_AODslim-ecal_v1' # data,h4g,hgg
#campaign = '06Sep2020_AODslim-ecal_v2' # DY

eos_redir, eos_basedir, samples = {}, {}, {}

output_dir = '../aodSkims/Era%s'%campaign
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

# Data
eos_redir['data2018'] = 'root://cmsdata.phys.cmu.edu'
eos_basedir['data2018'] = '/store/user/mandrews/Run2018/Era2018_%s'%campaign
samples['data2018'] = [
    'A'
    ]

# Bkg MC
eos_redir['bg2016'] = 'root://cmsdata.phys.cmu.edu'
eos_redir['bg2017'] = 'root://cmsdata.phys.cmu.edu'
eos_redir['bg2018'] = 'root://cmsdata.phys.cmu.edu'
eos_basedir['bg2016'] = '/store/user/mandrews/Run2016/Era2016_%s'%campaign
eos_basedir['bg2017'] = '/store/user/mandrews/Run2017/Era2017_%s'%campaign
eos_basedir['bg2018'] = '/store/user/mandrews/Run2018/Era2018_%s'%campaign
samples['bg2016'] = [
    'dy'
    ]
samples['bg2017'] = [
    'dy'
    ]
samples['bg2018'] = [
    'dy'
    ]

for d in ['data', 'bg']:

    if d != 'data': continue

    print('Data:',d)

    for r in ['2016', '2017', '2018']:

        if r != '2018': continue

        print('Run:',r)

        for s in samples[d+r]:

            #if s != 'dy': continue

            print('Sample:',s)

            # Define output list string name
            if d == 'data':
                s_list = 'Run'+r+s
            elif d == 'h4g':
                s_list = 'mA'+s+'GeV'
            else:
                s_list = s

            # Define EOS search string
            if 'hgg' in s:
                s_search = 'GluGluHToGG'
            elif 'dy' in s:
                s_search = 'DYJetsToLL'
            elif d == 'data':
                # AOD skim dset names do not have 'Run' in folder names
                # so need to add 'EGamma' or 'DoubleEG' to ensure MC dsets not picked up
                trgset = 'EGamma' if r == '2018' else 'DoubleEG'
                s_search = '%s_%s'%(trgset, r+s)
            else:
                s_search = s_list

            # Get list of files
            fs = run_eosfind(eos_basedir[d+r], s_search, eos_redir[d+r])
            print('>> sample:',s_search, len(fs))
            print(fs[0])
            print(fs[-1])

            # Write list to file

            fname = '%s/%s%s-%s_file_list.txt'%(output_dir, d, r, s_list)
            print('Writing to %s'%fname)
            with open(fname, 'w') as file_list:
                for f in fs:
                    file_list.write('%s\n'%f)
