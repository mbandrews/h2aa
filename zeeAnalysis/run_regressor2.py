from __future__ import print_function
import os, glob, re
from data_utils import *
#import numpy as np

# sample names
#bg2017-dy0

import argparse
# Register command line options
parser = argparse.ArgumentParser(description='Run mass regression.')
parser.add_argument('-s', '--sample', required=True, type=str, help='Sample name.')
args = parser.parse_args()

sample = args.sample
print('>> Sample:', sample)
assert len(sample.split('-')) == 2, '!! sample name invalid: %s'%sample
year = re.findall('(201[6-8])', sample.split('-')[0])[0]

# input ML model file
model = 'Models/model_epoch80_mae0.1906.pkl'
#model = 'Models/resnet/precise300/model_epoch90_val_mae0.1889.json' # for massreg paper
print('>> Model:', model)
assert os.path.isfile(model), '!! model file not found: %s'%img_list

# input img campaign [primary]
#img_campaign = 'Era06Sep2020_AOD-IMGZeev3' # dy+data zee skim(nele), with trg filter
#img_campaign = 'Era06Sep2020_AOD-IMGZeev4' # 2017: dy+data zee skim(nele+presel), with trg filter
#img_campaign = 'Era06Sep2020_AOD-IMGZeev5' # 2016: dy+data zee skim(nele+presel), with trg filter  -> wrong miniaodskim input
#img_campaign = 'Era16Feb2021_AOD-IMGZeev1' # fixed: use zee miniaod skim input. [data zee skim(nele+presel), dy(DYToLL) no good]
img_campaign = 'Era09Mar2021_AOD-IMGZeev1' # dy only:DYToEE [zee skim(nele+presel)]
print('>> Input imgNtuple campaign:', img_campaign)
img_list = '../imgNtuples/%s/%s_file_list.txt'%(img_campaign, sample)
assert os.path.isfile(img_list), '!! img input list not found: %s'%img_list

# input gg skim campaign [secondary]
#gg_campaign = 'ggNtuples-Era24Sep2020v1_ggSkimZee-v3' # data zee skim(nele+presel). dy(DYToLL) no good
gg_campaign = 'ggNtuples-Era09Mar2021v1_ggSkimZee-v1' # dy only:DYToEE zee skim(nele+presel)
print('>> Input ggSkim campaign:', gg_campaign)
gg_sample = sample
# for DYToEE: I miscalculated the splitting needed to have a reasonable regression time
# As a quick fix, I artifically split the IMG ntuple file lists: bg2017-dy0 -> bg2017-dy00,bg2017-dy01, ...
# but the gg ntuples are still with the original splitting, so make sure to get the one corresponding
# to the original splitting here:
if 'dy' in sample:
    dy_it = re.findall('dy([0-9]*)', sample.split('-')[-1])[0]
    gg_sample = sample[:-1] if len(dy_it) == 2 else sample
gg_list = '../ggSkims/%s/%s_file_list.txt'%(gg_campaign, gg_sample)
assert os.path.isfile(gg_list), '!! gg input list not found: %s'%gg_list

# output mantuple campaign
#ma_campaign = 'maNtuples-Era09Feb2021-Zeev1' # gg:ggNtuples-Era24Sep2020v1_ggSkimZee-v3 + img:Era06Sep2020_AOD-IMGZeev4/v5, model:Models/resnet/precise300/model_epoch90_val_mae0.1889.json
#ma_campaign = 'maNtuples-Era16Feb2021-Zeev1' # gg:ggNtuples-Era24Sep2020v1_ggSkimZee-v3 + img[data]:Era16Feb2021_AOD-IMGZeev1/img[dy]:Era09Mar2021_AOD-IMGZeev1, model:Models/resnet/precise300/model_epoch90_val_mae0.1889.json. for massreg paper only.
#ma_campaign = 'maNtuples-Era16Feb2021-Zeev2' # gg:ggNtuples-Era24Sep2020v1_ggSkimZee-v3 + img[data]:Era16Feb2021_AOD-IMGZeev1/img[dy]:Era09Mar2021_AOD-IMGZeev1, model:Models/model_epoch80_mae0.1906.pkl
ma_campaign = 'maNtuples-Era16Feb2021-Zeev3' # same as Era16Feb2021-Zeev2 but rotate 90deg CW: gg[data]:ggNtuples-Era24Sep2020v1_ggSkimZee-v3/gg[dy]:ggNtuples-Era09Mar2021v1_ggSkimZee-v1 + img[data]:Era16Feb2021_AOD-IMGZeev1/img[dy]:Era09Mar2021_AOD-IMGZeev1, model:Models/model_epoch80_mae0.1906.pkl
print('>> Output maNtuple campaign:', ma_campaign)

# mantuple output dir
eos_redir = 'root://cmseos.fnal.gov'
eos_basedir = '/store/user/lpchaa4g/mandrews'
eos_tgtdir = '%s/%s/%s/%s'%(eos_redir, eos_basedir, year, ma_campaign)
#eos_tgtdir = 'MAntuples/%s'%(ma_campaign)
#if not os.path.isdir(eos_tgtdir):
#    os.makedirs(eos_tgtdir)
print('>> EOS tgt dir:', eos_tgtdir)
run_eosmkdir(eos_tgtdir, eos_redir)

# log file
log_dir = 'Logs/%s'%ma_campaign
if not os.path.isdir(log_dir):
    os.makedirs(log_dir)
log_file = '%s/%s.log'%(log_dir, sample)
print('>> Log file:', log_file)

# mass_eval_ntuples.py
#pyargs = 'regress_mass.py -s %s -g %s -i %s -m %s -o %s'%(sample, gg_list, img_list, model, eos_tgtdir)
pyargs = 'regress_mass.py -s %s -g %s -i %s -m %s -o %s -l %s'%(sample, gg_list, img_list, model, eos_tgtdir, log_file)
print('>> Running:', pyargs)
os.system('python %s'%pyargs)
#os.system('python %s > %s'%(pyargs, log_file))
