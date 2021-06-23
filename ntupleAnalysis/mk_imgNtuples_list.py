from __future__ import print_function
import os, glob, re
from data_utils import *

#campaign = '06Sep2020_AOD-IMGv1' # data, dy: ok, h4g, hgg: bad dipho trgs, data: missing lumis in 2016H, 2018. 2018A missing.
campaign = '06Sep2020_AOD-IMGv6' # 2018A
#campaign = '04Dec2020_AOD-IMGv1' # h4g, hgg only: fixed dipho trgs

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
    ,'D0'
    ,'D1'
    ,'D2'
    ,'D3'
    ]

# Signal MC
eos_redir['h4g2016'] = 'root://cmsdata.phys.cmu.edu'
eos_redir['h4g2017'] = 'root://cmsdata.phys.cmu.edu'
eos_redir['h4g2018'] = 'root://cmsdata.phys.cmu.edu'
eos_basedir['h4g2016'] = '/store/user/mandrews/Run2016/Era2016_%s'%campaign
eos_basedir['h4g2017'] = '/store/user/mandrews/Run2017/Era2017_%s'%campaign
eos_basedir['h4g2018'] = '/store/user/mandrews/Run2018/Era2018_%s'%campaign

samples['h4g2016'] = [
    '0p1',
    '0p2',
    '0p4',
    '0p6',
    '0p8',
    '1p0',
    '1p2'
    ]
samples['h4g2017'] = [
    '0p1',
    '0p2',
    '0p4',
    '0p6',
    '0p8',
    '1p0',
    '1p2'
    ]
samples['h4g2018'] = [
    '0p1',
    '0p2',
    '0p4',
    '0p6',
    '0p8',
    '1p0',
    '1p2'
    ]

eos_redir['bg2016'] = 'root://cmsdata.phys.cmu.edu'
eos_redir['bg2017'] = 'root://cmsdata.phys.cmu.edu'
eos_redir['bg2018'] = 'root://cmsdata.phys.cmu.edu'
eos_basedir['bg2016'] = '/store/user/mandrews/Run2016/Era2016_%s'%campaign
eos_basedir['bg2017'] = '/store/user/mandrews/Run2017/Era2017_%s'%campaign
eos_basedir['bg2018'] = '/store/user/mandrews/Run2018/Era2018_%s'%campaign
samples['bg2016'] = [
    'hgg',
    'dy'
    ]
samples['bg2017'] = [
    'hgg',
    'dy'
    ]
samples['bg2018'] = [
    'hgg',
    'dy'
    ]

for d in ['data', 'h4g', 'bg']:

    #if d != 'h4g' and d != 'bg': continue
    #if d != 'h4g': continue
    #if d != 'bg': continue
    #if d == 'data': continue
    if d != 'data': continue

    print('Data:',d)

    for r in ['2016', '2017', '2018']:

        if r != '2018': continue
        #if r != '2017': continue
        #if r != '2016': continue

        print('Run:',r)

        for s in samples[d+r]:

            if s == 'dy': continue
            #if s != 'hgg': continue
            #if s != 'D': continue
            #if s == 'H': continue
            #if s != '1p0': continue
            if s != 'A': continue

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
            else:
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

            #batch_size = 2100
            #if s_search == 'Run2018D':
            #    # Run2018D only
            #    for i,b in enumerate(range(0, len(fs), batch_size)):
            #        start = b
            #        end = b+batch_size
            #        fs_batch = fs[start:end]
            #        print(i, start, end, len(fs_batch))
            #        print(fs_batch[0])
            #        print(fs_batch[-1])
            #        fname = '%s/%s%s-%s_file_list.txt'%(output_dir, d, r, s_list+str(i))
            #        print('Writing to %s'%fname)
            #        #with open(fname, 'w') as file_list:
            #        #    for f in fs_batch:
            #        #        file_list.write('%s\n'%f)
            #else:
            # All others
            fname = '%s/%s%s-%s_file_list.txt'%(output_dir, d, r, s_list)
            print('Writing to %s'%fname)
            with open(fname, 'w') as file_list:
                for f in fs:
                    file_list.write('%s\n'%f)
