from __future__ import print_function
import os, glob, re
from data_utils import *
#import numpy as np

# sample names
#bg2016-hgg_file_list.txt
#bg2017-hgg_file_list.txt
#bg2018-hgg_file_list.txt
#h4g2016-mA0p1GeV_file_list.txt
#h4g2016-mA0p2GeV_file_list.txt
#h4g2016-mA0p4GeV_file_list.txt
#h4g2016-mA0p6GeV_file_list.txt
#h4g2016-mA0p8GeV_file_list.txt
#h4g2016-mA1p0GeV_file_list.txt
#h4g2016-mA1p2GeV_file_list.txt
#h4g2017-mA0p1GeV_file_list.txt
#h4g2017-mA0p2GeV_file_list.txt
#h4g2017-mA0p4GeV_file_list.txt
#h4g2017-mA0p6GeV_file_list.txt
#h4g2017-mA0p8GeV_file_list.txt
#h4g2017-mA1p0GeV_file_list.txt
#h4g2017-mA1p2GeV_file_list.txt
#h4g2018-mA0p1GeV_file_list.txt
#h4g2018-mA0p2GeV_file_list.txt
#h4g2018-mA0p4GeV_file_list.txt
#h4g2018-mA0p6GeV_file_list.txt
#h4g2018-mA0p8GeV_file_list.txt
#h4g2018-mA1p0GeV_file_list.txt
#h4g2018-mA1p2GeV_file_list.txt

#data2016-Run2016B
#data2016-Run2016C
#data2016-Run2016D
#data2016-Run2016E
#data2016-Run2016F
#data2016-Run2016G

#data2017-Run2017B
#data2017-Run2017C
#data2017-Run2017D
#data2017-Run2017E
#data2017-Run2017F
#h4g2017-mA0p1GeV
#h4g2017-mA0p2GeV
#h4g2017-mA0p4GeV
#h4g2017-mA0p6GeV
#h4g2017-mA0p8GeV
#h4g2017-mA1p0GeV
#h4g2017-mA1p2GeV
#bg2017-hgg
#bg2017-dy

import argparse
# Register command line options
parser = argparse.ArgumentParser(description='Run mass regression.')
parser.add_argument('-s', '--sample', required=True, type=str, help='Sample name.')
parser.add_argument('-t', '--magen_tgt', default=None, type=float, help='magen tgt in GeV, if doing an interpolation.')
args = parser.parse_args()

sample = args.sample
print('>> Sample:', sample)
assert len(sample.split('-')) == 2, '!! sample name invalid: %s'%sample
year = re.findall('(201[6-8])', sample.split('-')[0])[0]

magen_tgt = args.magen_tgt
print('>> magen_tgt:', magen_tgt)

# input ML model file
model = 'Models/model_epoch80_mae0.1906.pkl'
print('>> Model:', model)
assert os.path.isfile(model), '!! model file not found: %s'%img_list

# input img campaign [primary]
#img_campaign = 'Era06Sep2020_AOD-IMGv1' # h4g,hgg bad dipho trgs, data,dy: ok
#img_campaign = 'Era06Sep2020_AOD-IMGv6' # 2018A
#img_campaign = 'Era04Dec2020_AOD-IMGv1' # h4g,hgg dipho trgs fixed
#img_campaign = 'Era22Jun2021_AOD-IMGv1' # !! EB images only !! data, h4g, hgg: redo with mgg95 trgs.
img_campaign = 'Era22Jun2021_AOD-IMGv2' # !! EB images only !! h4g, hgg: do NOT apply HLT dipho trg--applied later using trg SFs instead
print('>> Input imgNtuple campaign:', img_campaign)
img_list = '../imgNtuples/%s/%s_file_list.txt'%(img_campaign, sample)
assert os.path.isfile(img_list), '!! img input list not found: %s'%img_list

# input gg skim campaign [secondary]
#gg_campaign = 'ggNtuples-Era24Sep2020v1_ggSkim-v2' # h4g,hgg bad dipho trgs, data,dy: ok
#gg_campaign = 'ggNtuples-Era04Dec2020v1_ggSkim-v1' # h4g,hgg dipho trgs fixed
#gg_campaign = 'ggNtuples-Era20May2021v1_ggSkim-v1' # data, h4g, hgg. mgg95 trgs
gg_campaign = 'ggNtuples-Era20May2021v1_ggSkim-v2' # h4g, hgg: do NOT apply HLT dipho trg--applied later using trg SFs instead
print('>> Input ggSkim campaign:', gg_campaign)
gg_list = '../ggSkims/%s/%s_file_list.txt'%(gg_campaign, sample)
assert os.path.isfile(gg_list), '!! gg input list not found: %s'%gg_list

# output mantuple campaign
#ma_campaign = 'maNtuples-Era04Dec2020v1' # gg:ggNtuples-Era24Sep2020v1_ggSkim-v2 + img:Era06Sep2020_AOD-IMGv1, re-labelled from maNtuples-Era03Dec2020v1
#ma_campaign = 'maNtuples-Era22Jun2021v1' # gg:ggNtuples-Era20May2021v1_ggSkim-v1 + img:Era22Jun2021_AOD-IMGv1
#ma_campaign = 'maNtuples-Era22Jun2021v2' # gg:ggNtuples-Era20May2021v1_ggSkim-v2 + img:Era22Jun2021_AOD-IMGv2. h4g, hgg w/o HLT
ma_campaign = 'maNtuples-Era22Jun2021v3' # gg:ggNtuples-Era20May2021v1_ggSkim-v2 + img:Era22Jun2021_AOD-IMGv2. h4g, hgg w/o HLT, add interpolated mass, otherwise copied from above v2
print('>> Output maNtuple campaign:', ma_campaign)

# mantuple output dir
eos_redir = 'root://cmseos.fnal.gov'
eos_basedir = '/store/user/lpchaa4g/mandrews'
eos_tgtdir = '%s/%s/%s/%s'%(eos_redir, eos_basedir, year, ma_campaign)
#eos_tgtdir = 'MAntuples/%s'%(ma_campaign)
eos_tgtdir = 'MAntuples'
if not os.path.isdir(eos_tgtdir):
    os.makedirs(eos_tgtdir)
print('>> EOS tgt dir:', eos_tgtdir)
#run_eosmkdir(eos_tgtdir, eos_redir)

# log file
log_dir = 'Logs/%s'%ma_campaign
#log_dir = 'Logs'
if not os.path.isdir(log_dir):
    os.makedirs(log_dir)
#log_file = '%s/%s.log'%(log_dir, sample)
log_file = '%s/%s%s.log'%(log_dir, sample, '' if magen_tgt is None else 'to%sGeV'%(str(magen_tgt).replace('.','p')))
print('>> Log file:', log_file)

# mass_eval_ntuples.py
#pyargs = 'regress_mass.py -s %s -g %s -i %s -m %s -o %s'%(sample, gg_list, img_list, model, eos_tgtdir)
pyargs = 'regress_mass.py -s %s -g %s -i %s -m %s -o %s -l %s'%(sample, gg_list, img_list, model, eos_tgtdir, log_file)
if magen_tgt is not None:
    pyargs += ' -t %f'%(magen_tgt)
print('>> Running:', pyargs)
os.system('python %s'%pyargs)
#os.system('python %s > %s'%(pyargs, log_file))
