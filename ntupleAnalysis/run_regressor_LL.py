from __future__ import print_function
import os, glob, re
from data_utils import *
#import numpy as np

# sample names
#h4g2017-mA0p1GeV-ctau0-0ep00mm
#h4g2017-mA0p1GeV-ctau0-1ep00mm
#h4g2017-mA0p1GeV-ctau0-1ep01mm
#h4g2017-mA0p2GeV-ctau0-0ep00mm
#h4g2017-mA0p2GeV-ctau0-1ep00mm !
#h4g2017-mA0p2GeV-ctau0-1ep01mm
#h4g2017-mA0p4GeV-ctau0-0ep00mm
#h4g2017-mA0p4GeV-ctau0-1ep00mm
#h4g2017-mA0p4GeV-ctau0-1ep01mm

import argparse
# Register command line options
parser = argparse.ArgumentParser(description='Run mass regression.')
parser.add_argument('-s', '--sample', required=True, type=str, help='Sample name.')
parser.add_argument('-t', '--magen_tgt', default=None, type=float, help='magen tgt in GeV, if doing an interpolation.')
args = parser.parse_args()

sample = args.sample
print('>> Sample:', sample)
#assert len(sample.split('-')) == 2, '!! sample name invalid: %s'%sample
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
#img_campaign = 'Era22Jun2021_AOD-IMGv2' # !! EB images only !! h4g, hgg: do NOT apply HLT dipho trg--applied later using trg SFs instead
#img_campaign = 'Era18Nov2021_AOD-IMGv1' # !! EB images only !! h4g 2017 LL: do NOT apply HLT dipho trg--applied later using trg SFs instead
#img_campaign = 'Era18Nov2021_AOD-IMGv2' # includes dvtx [NOT USED!!]
img_campaign = 'Era18Nov2021_AOD-IMGv3' # fixed tau units, include dvtx
print('>> Input imgNtuple campaign:', img_campaign)
img_list = '../imgNtuples/%s/%s_file_list.txt'%(img_campaign, sample)
assert os.path.isfile(img_list), '!! img input list not found: %s'%img_list

# input gg skim campaign [secondary]
#gg_campaign = 'ggNtuples-Era24Sep2020v1_ggSkim-v2' # h4g,hgg bad dipho trgs, data,dy: ok
#gg_campaign = 'ggNtuples-Era04Dec2020v1_ggSkim-v1' # h4g,hgg dipho trgs fixed
#gg_campaign = 'ggNtuples-Era20May2021v1_ggSkim-v1' # data, h4g, hgg. mgg95 trgs
#gg_campaign = 'ggNtuples-Era20May2021v1_ggSkim-v2' # h4g, hgg: do NOT apply HLT dipho trg--applied later using trg SFs instead
#gg_campaign = 'ggNtuples-Era18Nov2021v1_ggSkim-v1' # h4g 2017 LL: do NOT apply HLT dipho trg--applied later using trg SFs instead
gg_campaign = 'ggNtuples-Era18Nov2021v2_ggSkim-v1' # fixed tau units
print('>> Input ggSkim campaign:', gg_campaign)
gg_list = '../ggSkims/%s/%s_file_list.txt'%(gg_campaign, sample)
assert os.path.isfile(gg_list), '!! gg input list not found: %s'%gg_list

# output mantuple campaign
#ma_campaign = 'maNtuples-Era04Dec2020v1' # gg:ggNtuples-Era24Sep2020v1_ggSkim-v2 + img:Era06Sep2020_AOD-IMGv1, re-labelled from maNtuples-Era03Dec2020v1
#ma_campaign = 'maNtuples-Era22Jun2021v1' # gg:ggNtuples-Era20May2021v1_ggSkim-v1 + img:Era22Jun2021_AOD-IMGv1
#ma_campaign = 'maNtuples-Era22Jun2021v2' # gg:ggNtuples-Era20May2021v1_ggSkim-v2 + img:Era22Jun2021_AOD-IMGv2. h4g, hgg w/o HLT
#ma_campaign = 'maNtuples-Era22Jun2021v3' # gg:ggNtuples-Era20May2021v1_ggSkim-v2 + img:Era22Jun2021_AOD-IMGv2. h4g, hgg w/o HLT, add interpolated mass, otherwise copied from above v2
#ma_campaign = 'maNtuples-Era18Nov2021v1' # gg:ggNtuples-Era18Nov2021v1_ggSkim-v1 + img:Era18Nov2021_AOD-IMGv1. h4g 2017 LL, w/o HLT
ma_campaign = 'maNtuples-Era18Nov2021v2' # gg:ggNtuples-Era18Nov2021v2_ggSkim-v1 + img:Era18Nov2021_AOD-IMGv3. h4g 2017 LL fixed tau units, w/o HLT
print('>> Output maNtuple campaign:', ma_campaign)

# mantuple output dir
eos_redir = 'root://cmseos.fnal.gov'
eos_basedir = '/store/user/lpchaa4g/mandrews'
eos_tgtdir = '%s/%s/%s/%s'%(eos_redir, eos_basedir, year, ma_campaign)
#eos_tgtdir = 'MAntuples/%s'%(ma_campaign)
#eos_tgtdir = 'MAntuples'
#if not os.path.isdir(eos_tgtdir):
#    os.makedirs(eos_tgtdir)
print('>> EOS tgt dir:', eos_tgtdir)
run_eosmkdir(eos_tgtdir, eos_redir)

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
pyargs = 'regress_mass_LL.py -s %s -g %s -i %s -m %s -o %s -l %s'%(sample, gg_list, img_list, model, eos_tgtdir, log_file)
if magen_tgt is not None:
    pyargs += ' -t %f'%(magen_tgt)
print('>> Running:', pyargs)
os.system('python %s'%pyargs)
#os.system('python %s > %s'%(pyargs, log_file))
