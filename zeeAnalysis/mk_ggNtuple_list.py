from __future__ import print_function
import os, glob, re
from data_utils import *

#campaign = 'Era24Sep2020_v1'
#campaign = 'Era04Dec2020_v1' # Fixed mc diphoton trg
campaign = 'Era09Mar2021_v1' # DYToEE

eos_redir, eos_basedir, samples = {}, {}, {}

output_dir = '../ggNtuples/%s'%campaign
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

# Data
eos_redir['data2016'] = 'root://cmseos.fnal.gov'
eos_redir['data2017'] = 'root://cmseos.fnal.gov'
eos_redir['data2018'] = 'root://cmseos.fnal.gov'

eos_basedir['data2016'] = '/store/group/lpcsusystealth/stealth2018Ntuples_with9413'
eos_basedir['data2017'] = '/store/group/lpcsusystealth/stealth2018Ntuples_with9413'
eos_basedir['data2018'] = '/store/group/lpcsusystealth/stealth2018Ntuples_with10210'

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
    ,'D'
    ]

#mc_campaign = '06Sep2020_ggntuplev1' # h4g,hgg: wrong diphoton trg, DY: ok
#mc_campaign = '04Dec2020_ggntuplev1' # h4g,hgg: fixed diphoton trg
mc_campaign = '09Mar2020_ggntuplev1' # DYToEE

eos_redir['bg2016'] = 'root://cmsdata.phys.cmu.edu'
eos_redir['bg2017'] = 'root://cmsdata.phys.cmu.edu'
eos_redir['bg2018'] = 'root://cmsdata.phys.cmu.edu'
eos_basedir['bg2016'] = '/store/user/mandrews/Run2016/Era2016_%s'%mc_campaign
eos_basedir['bg2017'] = '/store/user/mandrews/Run2017/Era2017_%s'%mc_campaign
eos_basedir['bg2018'] = '/store/user/mandrews/Run2018/Era2018_%s'%mc_campaign
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

    if d != 'bg': continue
    #if d == 'data': continue
    #if d != 'data': continue

    print('Data:',d)

    for r in ['2016', '2017', '2018']:

        #if r == '2016': continue
        #if r != '2016': continue

        print('Run:',r)

        for s in samples[d+r]:

            if s != 'dy': continue

            print('Sample:',s)

            # Define output list string name
            if d == 'data':
                s_list = 'Run'+r+s
            else:
                s_list = s

            # Define EOS search string
            if 'dy' in s:
                #s_search = 'DYJetsToEE'
                s_search = 'DYToEE'
            else:
                s_search = s_list

            # Get list of files
            fs = run_eosfind(eos_basedir[d+r], s_search, eos_redir[d+r])
            fs = [f for f in fs if 'ggtree' in f]
            print('>> sample:',s_search, len(fs))
            print(fs[0])
            print(fs[-1])

            # Write list to file

            if 'DY' in s_search:
                # DY only
                batch_size = 155
                #batch_size = 350 if r == '2016' else 500
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

            else:
                # All others
                fname = '%s/%s%s-%s_file_list.txt'%(output_dir, d, r, s_list)
                print('Writing to %s'%fname)
                with open(fname, 'w') as file_list:
                    for f in fs:
                        file_list.write('%s\n'%f)
            '''
            if s_search == 'Run2018D':
                # Run2018D only
                batch_size = 2100
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

            elif 'DY' in s_search:
                # DY only
                #batch_size = 500
                batch_size = 300 if r == '2016' else 500
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
            else:
                # All others
                fname = '%s/%s%s-%s_file_list.txt'%(output_dir, d, r, s_list)
                print('Writing to %s'%fname)
                with open(fname, 'w') as file_list:
                    for f in fs:
                        file_list.write('%s\n'%f)
            '''
