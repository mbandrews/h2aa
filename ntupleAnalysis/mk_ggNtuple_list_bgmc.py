from __future__ import print_function
import os, glob, re
from data_utils import *

#campaign = 'Era24Sep2020_v1'
#campaign = 'Era04Dec2020_v1' # Fixed mc diphoton trg
#campaign = 'Era06Sep2020_v1' # 2017 bkg mc only
campaign = 'Era20May2021_v2' # 2017 bkg mc only. Include mass95 trg. 20May2021_ggntuplev2

eos_redir, eos_basedir, samples = {}, {}, {}

output_dir = '../ggNtuples/%s'%campaign
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

#mc_campaign = '06Sep2020_ggntuplev1' # h4g,hgg: wrong diphoton trg, DY: ok
#mc_campaign = '04Dec2020_ggntuplev1' # h4g,hgg: fixed diphoton trg
#mc_campaign = '06Sep2020_ggntuplev1' # h4g,hgg: fixed diphoton trg
mc_campaign = '20May2021_ggntuplev2' # Include mass95 trg

sample_maps = {
    'diphotonjets': 'DiPhotonJets',
    'gjetPt20to40': 'GJet_Pt-20to40',
    'gjetPt40toInf': 'GJet_Pt-40toInf',
    'qcdPt30to40': 'QCD_Pt-30to40',
    'qcdPt40toInf': 'QCD_Pt-40toInf'
    }

eos_redir['bg2016'] = 'root://cmsdata.phys.cmu.edu'
eos_redir['bg2017'] = 'root://cmsdata.phys.cmu.edu'
eos_redir['bg2018'] = 'root://cmsdata.phys.cmu.edu'
eos_basedir['bg2016'] = '/store/user/mandrews/Run2016/Era2016_%s'%mc_campaign
eos_basedir['bg2017'] = '/store/user/mandrews/Run2017/Era2017_%s'%mc_campaign
eos_basedir['bg2018'] = '/store/user/mandrews/Run2018/Era2018_%s'%mc_campaign
samples['bg2016'] = [
    ]
samples['bg2017'] = [s for s in sample_maps.keys()]
samples['bg2018'] = [
    ]

for d in ['bg']:

    print('Category:',d)

    for r in ['2016', '2017', '2018']:

        if r != '2017': continue

        print('Run:',r)

        for s in samples[d+r]:

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
                #s_search = s_list
                s_search = sample_maps[s]

            # Get list of files
            fs = run_eosfind(eos_basedir[d+r], s_search, eos_redir[d+r])
            fs = [f for f in fs if 'ggtree' in f]
            print('>> sample:',s_search, len(fs))
            print(fs[0])
            print(fs[-1])

            # Write list to file

            batch_size = 160
            if len(fs) > batch_size:
                for i,b in enumerate(range(0, len(fs), batch_size)):
                    start = b
                    end = b+batch_size
                    fs_batch = fs[start:end]
                    print(i, start, end, len(fs_batch))
                    print(fs_batch[0])
                    print(fs_batch[-1])
                    fname = '%s/%s%s-%s_file_list.txt'%(output_dir, d, r, s_list+'-%d'%i)
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
                        pass
                        file_list.write('%s\n'%f)
