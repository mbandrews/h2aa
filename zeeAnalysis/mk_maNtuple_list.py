from __future__ import print_function
import os, glob, re
from data_utils import *

#campaign = 'Era04Dec2020v1' # h4g,hgg dipho trgs fixed. 2018A added later, 2018+2016H failed lumis
#campaign = 'Era09Feb2021-Zeev1' # dy+data zee skim(nele+presel), # gg:ggNtuples-Era24Sep2020v1_ggSkimZee-v3 + img:Era06Sep2020_AOD-IMGZeev4, model:Models/resnet/precise300/model_epoch90_val_mae0.1889.json
#campaign = 'Era16Feb2021-Zeev1' # dy+data zee skim(nele+presel), # gg:ggNtuples-Era24Sep2020v1_ggSkimZee-v3 + img:Era16Feb2021_AOD-IMGZeev1, model:Models/resnet/precise300/model_epoch90_val_mae0.1889.json
#campaign = 'Era16Feb2021-Zeev2' # dy+data zee skim(nele+presel), # gg:ggNtuples-Era24Sep2020v1_ggSkimZee-v3 + img:Era16Feb2021_AOD-IMGZeev1, model:Models/model_epoch80_mae0.1906.pkl
campaign = 'Era16Feb2021-Zeev3' # same as Era16Feb2021-Zeev2 but rotate 90deg CW: gg[data]:ggNtuples-Era24Sep2020v1_ggSkimZee-v3/gg[dy]:ggNtuples-Era09Mar20    21v    1_ggSkimZee-v1 + img[data]:Era16Feb2021_AOD-IMGZeev1/img[dy]:Era09Mar2021_AOD-IMGZeev1, model:Models/model_epoch80_mae0.1906.pkl

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

samples['bg2016'] = [
    'dy00',
    'dy01',
    'dy02',
    'dy03',
    'dy10',
    'dy11',
    'dy12',
    'dy13',
    'dy20',
    'dy21',
    'dy22',
    'dy23',
    'dy30',
    'dy31',
    'dy32',
    'dy33',
    ]
samples['bg2017'] = [
    'dy00',
    'dy01',
    'dy02',
    'dy03',
    ]
samples['bg2018'] = [
    'dy00',
    'dy01',
    'dy02',
    'dy03',
    'dy04'
    ]

for r in ['2016', '2017', '2018']:

    if r != '2018': continue
    #if r != '2017': continue
    #if r != '2016': continue
    #if r == '2017': continue
    #if r == '2016': continue

    print('Run:',r)

    for d in ['data', 'bg']:

        #if d != 'data': continue
        #if d == 'data': continue

        print('Data:',d)

        for s in samples[d+r]:

            #if s != 'hgg': continue
            #if 'dy' not in s: continue
            #if 'dy' in s: continue

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
