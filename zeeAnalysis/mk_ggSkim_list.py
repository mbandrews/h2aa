from __future__ import print_function
import os, glob, re
from data_utils import *

#campaign = 'ggNtuples-Era24Sep2020v1_ggSkimZee-v2' # data zee skim(nele)
#campaign = 'ggNtuples-Era24Sep2020v1_ggSkimZee-v3' # data zee skim(nele+presel). dy(DYToLL) no good
campaign = 'ggNtuples-Era09Mar2021v1_ggSkimZee-v1' # dy only:DYToEE zee skim(nele+presel)

eos_redir, eos_basedir, samples = {}, {}, {}

output_dir = '../ggSkims/%s'%campaign
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

# Data
eos_redir['2016'] = 'root://cmseos.fnal.gov'
eos_redir['2017'] = 'root://cmseos.fnal.gov'
eos_redir['2018'] = 'root://cmseos.fnal.gov'

eos_basedir['2016'] = '/store/user/lpchaa4g/mandrews/2016/%s/ggSkims'%campaign
eos_basedir['2017'] = '/store/user/lpchaa4g/mandrews/2017/%s/ggSkims'%campaign
eos_basedir['2018'] = '/store/user/lpchaa4g/mandrews/2018/%s/ggSkims'%campaign

samples['data2016'] = [
    'B'
    ,'C'
    ,'D'
    ,'E'
    ,'F'
    ,'G'
    ,'H'
    ]

samples['data2017'] = [
    'B'
    ,'C'
    ,'D'
    ,'E'
    ,'F'
    ]

samples['data2018'] = [
    'A'
    ,'B'
    ,'C'
    #,'D'
    ,'D0'
    ,'D1'
    ,'D2'
    ,'D3'
    ]

samples['bg2016'] = [
    'dy0',
    'dy1',
    'dy2',
    'dy3'
    ]
samples['bg2017'] = [
    'dy0',
    ]
samples['bg2018'] = [
    'dy0',
    ]

for r in ['2016', '2017', '2018']:

    #if r != '2016': continue

    print('Run:',r)

    for d in ['data', 'bg']:

        #if d != 'data': continue
        if d != 'bg': continue

        print('Data:',d)

        for s in samples[d+r]:

            #if s != 'hgg': continue
            #if s == 'dy': continue

            print('Sample:',s)

            # Define output list string name
            if d == 'data':
                s_list = 'Run'+r+s
            else:
                s_list = s

            # Define EOS search string
            s_search = '%s%s-%s'%(d, r, s_list)

            # Get list of files
            fs = run_eosfind(eos_basedir[r], s_search, eos_redir[r])
            fs = [f for f in fs if 'ggskim' in f]
            print('>> sample:',s_search, len(fs))
            if len(fs) == 0:
                print('>> EMPTY SAMPLE!!')
                continue
            print(fs[0])
            print(fs[-1])

            # All others
            fname = '%s/%s%s-%s_file_list.txt'%(output_dir, d, r, s_list)
            print('Writing to %s'%fname)
            with open(fname, 'w') as file_list:
                for f in fs:
                    file_list.write('%s\n'%f)
