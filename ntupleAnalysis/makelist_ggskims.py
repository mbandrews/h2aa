import os, glob, re
from data_utils import *

campaign = 'Era24Sep2020_v1'

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

# Signal MC
eos_redir['h4g2016'] = 'root://cmsdata.phys.cmu.edu'
eos_redir['h4g2017'] = 'root://cmsdata.phys.cmu.edu'
eos_redir['h4g2018'] = 'root://cmsdata.phys.cmu.edu'

eos_basedir['h4g2016'] = '/store/user/mandrews/Run2016/Era2017_06Sep2020_ggntuplev1'
eos_basedir['h4g2017'] = '/store/user/mandrews/Run2017/Era2017_06Sep2020_ggntuplev1'
eos_basedir['h4g2018'] = '/store/user/mandrews/Run2018/Era2017_06Sep2020_ggntuplev1'

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

eos_basedir['bg2016'] = '/store/user/mandrews/Run2016/Era2017_06Sep2020_ggntuplev1'
eos_basedir['bg2017'] = '/store/user/mandrews/Run2017/Era2017_06Sep2020_ggntuplev1'
eos_basedir['bg2018'] = '/store/user/mandrews/Run2018/Era2017_06Sep2020_ggntuplev1'
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

for d in ['data', 'h4g']:
    if d != 'h4g': continue
    for r in ['2016', '2017', '2018']:
        if r != '2017': continue
        for s in samples[d+r]:

            #if s != '1p0': continue

            if d == 'data':
                s_cleaned = 'Run'+r+s
            elif d == 'h4g':
                s_cleaned = 'mA'+s+'GeV'
            else:
                s_cleaned = s

            # String cleaning
            if d == 'h4g' and '1p0' in s_cleaned:
                #s_fixed = s_cleaned.replace('p0', '')
                s_fixed = s_cleaned
            else:
                s_fixed = s_cleaned

            # Get list of files
            fs = run_eosfind(eos_basedir[d+r], s_fixed, eos_redir[d+r])
            fs = [f for f in fs if 'ggtree' in f]
            print('>> sample:',s_fixed, len(fs))
            print(fs[0])
            print(fs[-1])

            # Write list to file
            fname = '%s/%s%s-%s_file_list.txt'%(output_dir, d, r, s_cleaned)
            print('Writing to %s'%fname)
            with open(fname, 'w') as file_list:
                for f in fs:
                    file_list.write('%s\n'%f)
