from __future__ import print_function
import os, glob, re
from data_utils import *

#campaign = 'ggNtuples-Era24Sep2020v1_ggSkim-v2' # h4g,hgg bad dipho trgs, data,dy: ok
#campaign = 'ggNtuples-Era04Dec2020v1_ggSkim-v1' # h4g,hgg dipho trgs fixed
#campaign = 'ggNtuples-Era24Sep2020v1_ggSkim-v4' # data only pi0 skim: trg-npho-presel(hgg hoe)
#campaign = 'ggNtuples-Era20May2021v1_ggSkim-v1' # data, h4g, hgg. mgg95 trgs
#campaign = 'ggNtuples-Era20May2021v1_ggSkim-v2' # h4g, hgg mgg95 trgs, no HLT req: do NOT apply HLT dipho trg--applied later using trg SFs instead
#campaign = 'ggNtuples-Era18Nov2021v1_ggSkim-v1' # h4g 2017, LL no HLT req: do NOT apply HLT dipho trg--applied later using trg SFs instead
campaign = 'ggNtuples-Era18Nov2021v2_ggSkim-v1' # h4g 2017, LL fixed tau units

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
    'B0', 'B1',
    'C',
    'D',
    'E',
    'F',
    'G0', 'G1',
    'H0', 'H1'
    ]

samples['data2017'] = [
    'B',
    'C0', 'C1',
    'D',
    'E0', 'E1',
    'F0', 'F1'
    ]

samples['data2018'] = [
    'A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7',
    'B0', 'B1', 'B2', 'B3', 'B4',
    'C0', 'C1', 'C2', 'C3',
    'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8'
    ]

# Signal MC
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
    '0p1GeV-ctau0-0ep00mm',
    '0p1GeV-ctau0-1ep00mm',
    '0p1GeV-ctau0-1ep01mm',
    '0p2GeV-ctau0-0ep00mm',
    '0p2GeV-ctau0-1ep00mm',
    '0p2GeV-ctau0-1ep01mm',
    '0p4GeV-ctau0-0ep00mm',
    '0p4GeV-ctau0-1ep00mm',
    '0p4GeV-ctau0-1ep01mm'

    #'0p1GeV-tau0-0ep00',
    #'0p1GeV-tau0-3em09',
    #'0p1GeV-tau0-3em11',
    #'0p2GeV-tau0-0ep00',
    #'0p2GeV-tau0-3em09',
    #'0p2GeV-tau0-3em11',
    #'0p4GeV-tau0-0ep00',
    #'0p4GeV-tau0-3em09',
    #'0p4GeV-tau0-3em11'
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
    if r != '2017': continue

    print('Run:',r)

    for d in ['data', 'h4g', 'bg']:

        #if d != 'data': continue
        if d != 'h4g': continue
        #if d == 'data': continue

        print('Data:',d)

        for s in samples[d+r]:

            #if s != 'hgg': continue
            #if s == 'dy': continue

            print('Sample:',s)

            # Define output list string name
            if d == 'data':
                s_list = 'Run'+r+s
            elif d == 'h4g':
                s_list = 'mA'+s#+'GeV'
            else:
                s_list = s

            # Define EOS search string
            s_search = '%s%s-%s'%(d, r, s_list)
            s_search = s_search.strip('mm').replace('ctau0', 'tau0') # forgot to add ctau and mm units naming convention in input ggntuple jobs and skims

            # Get list of files
            print(s_search)
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
            #break
