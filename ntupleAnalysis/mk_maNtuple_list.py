from __future__ import print_function
import os, glob, re
from data_utils import *

#campaign = 'Era04Dec2020v1' # h4g,hgg dipho trgs fixed. 2018A added later, 2018+2016H failed lumis
#campaign = 'Era22Jun2021v1' # data, h4g, hgg. mgg95 trgs. gg:ggNtuples-Era20May2021v1_ggSkim-v1 + img:Era22Jun2021_AOD-IMGv1
#campaign = 'Era22Jun2021v2' # h4g, hgg w/o HLT. gg:ggNtuples-Era20May2021v1_ggSkim-v2 + img:Era22Jun2021_AOD-IMGv2
campaign = 'Era22Jun2021v3' # Era22Jun2021v2 + interpolated mass samples

# /store/group/lpchaa4g/mandrews/2017/maNtuples-Era04Dec2020v1/h4g2017-mA1p2GeV_mantuple.root
# To make full year: cat data2017-Run2017*_file_list.txt > data2017_file_list.txt
# To make full Run2: cat data*-Run*_file_list.txt > data_file_list.txt

eos_redir, eos_basedir, samples = {}, {}, {}

output_dir = '../maNtuples/%s'%campaign
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

# Data
eos_redir['2016'] = 'root://cmseos.fnal.gov'
eos_redir['2017'] = 'root://cmseos.fnal.gov'
eos_redir['2018'] = 'root://cmseos.fnal.gov'

eos_basedir['2016'] = '/store/user/lpchaa4g/mandrews/2016/maNtuples-%s'%campaign
eos_basedir['2017'] = '/store/user/lpchaa4g/mandrews/2017/maNtuples-%s'%campaign
eos_basedir['2018'] = '/store/user/lpchaa4g/mandrews/2018/maNtuples-%s'%campaign

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
mass_pts = [
    '0p1',
    '0p2',
    '0p3',
    '0p4',
    '0p5',
    '0p6',
    '0p7',
    '0p8',
    '0p9',
    '1p0',
    '1p1',
    '1p2'
    ]
#    '0p1',
#    '0p2',
#    '0p4',
#    '0p6',
#    '0p8',
#    '1p0',
#    '1p2'
#    ]
samples['h4g2016'] = mass_pts
samples['h4g2017'] = mass_pts
samples['h4g2018'] = mass_pts

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

for r in ['2016', '2017', '2018']:

    #if r != '2018': continue
    #if r != '2016': continue
    #if r != '2017': continue

    print('Run:',r)

    for d in ['data', 'h4g', 'bg']:

        #if d != 'data': continue
        #if d == 'data': continue
        if d != 'h4g': continue

        print('Data:',d)

        for s in samples[d+r]:

            #if s != 'hgg': continue
            #if s == 'dy': continue

            print('Sample:',s)

            # Define output list string name
            if d == 'data':
                s_list = 'Run'+r+s
            elif d == 'h4g':
                s_list = 'mA'+s+'GeV'
            else:
                s_list = s

            # Define EOS search string
            s_search = '%s%s-%s'%(d, r, s_list)

            # Get list of files
            fs = run_eosfind(eos_basedir[r], s_search, eos_redir[r])
            fs = [f for f in fs if 'mantuple' in f]
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
