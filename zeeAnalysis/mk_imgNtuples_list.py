from __future__ import print_function
import os, glob, re
from data_utils import *

#campaign = '06Sep2020_AOD-IMGZeev3' # lumi-based unitsPerJob = 6
#campaign = '06Sep2020_AOD-IMGZeev4' # 2017, whole MINIAOD+AOD processing. lumi-based unitsPerJob = 6, dy+data zee skim(nele+presel)
#campaign = '06Sep2020_AOD-IMGZeev5' # 2016, skim-based processin. dy+data zee skim(nele+presel) -> wrong miniaodskim input
#campaign = '16Feb2021_AOD-IMGZeev1' # data, fixed: use zee miniaod skim input. [data zee skim(nele+presel), dy no good]
campaign = '09Mar2021_AOD-IMGZeev1' # dy[DYToEE] using full miniaod/aod + evt list. [zee skim(nele+presel)]

eos_redir, eos_basedir, samples = {}, {}, {}

output_dir = '../imgNtuples/Era%s'%campaign
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

# Data
eos_redir['data2016'] = 'root://cmsdata.phys.cmu.edu'
eos_redir['data2017'] = 'root://cmsdata.phys.cmu.edu'
eos_redir['data2018'] = 'root://cmsdata.phys.cmu.edu'
eos_basedir['data2016'] = '/store/user/mandrews/Run2016/Era2016_%s/DoubleEG'%campaign
eos_basedir['data2017'] = '/store/user/mandrews/Run2017/Era2017_%s/DoubleEG'%campaign
eos_basedir['data2018'] = '/store/user/mandrews/Run2018/Era2018_%s/EGamma'%campaign

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
    #,'D0'
    #,'D1'
    #,'D2'
    #,'D3'
    ]

eos_redir['bg2016'] = 'root://cmsdata.phys.cmu.edu'
eos_redir['bg2017'] = 'root://cmsdata.phys.cmu.edu'
eos_redir['bg2018'] = 'root://cmsdata.phys.cmu.edu'
eos_basedir['bg2016'] = '/store/user/mandrews/Run2016/Era2016_%s'%campaign
eos_basedir['bg2017'] = '/store/user/mandrews/Run2017/Era2017_%s'%campaign
eos_basedir['bg2018'] = '/store/user/mandrews/Run2018/Era2018_%s'%campaign
samples['bg2016'] = [
    'dy0',
    'dy1',
    'dy2',
    'dy3',
    ]
samples['bg2017'] = [
    'dy0',
    ]
samples['bg2018'] = [
    'dy0',
    ]

for d in ['data', 'bg']:

    #if d != 'h4g' and d != 'bg': continue
    #if d != 'h4g': continue
    if d != 'bg': continue
    #if d == 'data': continue
    #if d != 'data': continue

    print('Data:',d)

    for r in ['2016', '2017', '2018']:

        #if r != '2018': continue
        #if r != '2017': continue
        if r != '2016': continue
        #if r == '2016': continue

        print('Run:',r)

        for s in samples[d+r]:

            if 'dy' not in s: continue
            #if 'dy' in s: continue

            print('Sample:',s)

            # Define output list string name
            if d == 'data':
                s_list = 'Run'+r+s
            else:
                s_list = s

            # Define EOS search string
            s_search = s_list

            # Get list of files
            fs = run_eosfind(eos_basedir[d+r], s_search, eos_redir[d+r])
            print('>> sample:',s_search, len(fs))
            if len(fs) == 0:
                print('>> EMPTY SAMPLE!!')
                continue
            print(fs[0])
            print(fs[-1])

            # Write list to file

            #batch_size = 27 if ('dy' in s_search and r == '2017') else 25
            batch_size = 25 if ('dy' in s_search and r == '2018') else 27
            for i,b in enumerate(range(0, len(fs), batch_size)):
                start = b
                end = b+batch_size
                fs_batch = fs[start:end]
                print(i, start, end, len(fs_batch))
                print(fs_batch[0])
                print(fs_batch[-1])
                fname = '%s/%s%s-%s_file_list.txt'%(output_dir, d, r, s_list+str(i))
                print('Writing to %s'%fname)
                with open(fname, 'w') as file_list:
                    for f in fs_batch:
                        file_list.write('%s\n'%f)
            #else:
            ## All others
            #fname = '%s/%s%s-%s_file_list.txt'%(output_dir, d, r, s_list)
            #print('Writing to %s'%fname)
            #with open(fname, 'w') as file_list:
            #    for f in fs:
            #        file_list.write('%s\n'%f)
