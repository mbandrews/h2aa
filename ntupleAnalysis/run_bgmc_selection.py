from __future__ import print_function
#from multiprocessing import Pool
import os, glob, shutil
#import numpy as np
#import subprocess
from data_utils import *
#from plot_srvsb import plot_srvsb

import argparse
#from hist_utils import *
#from selection_utils import *
#from get_bkg_norm import *

#import ROOT

# Register command line options
parser = argparse.ArgumentParser(description='Run h2aa selection on bkg mc.')
parser.add_argument('-s', '--sample', default='bg2017-diphotonjets', type=str, help='Sample name.')
#parser.add_argument('-s', '--sample', default='bg2017-hgg', type=str, help='Sample name.')
#parser.add_argument('-s', '--sample', default='h4g2018-mA1p0GeV', type=str, help='Sample name.')
parser.add_argument('-r', '--region', default='sr', type=str, help='mH-region: sr, sb, sblo, sbhi, all')
#parser.add_argument('-r', '--region', default='sblo', type=str, help='mH-region: sr, sb, sblo, sbhi, all')
parser.add_argument('-i', '--inlist', default='../ggNtuples/Era20May2021_v2/bg2017-diphotonjets_file_list.txt', type=str, help='Input list of ggntuples.')
#parser.add_argument('-i', '--inlist', default='../ggNtuples/Era06Sep2020_v1/bg2017-diphotonjets_file_list.txt', type=str, help='Input list of ggntuples.')
#parser.add_argument('-i', '--inlist', default='../ggNtuples/Era06Sep2020_v1/bg2017-hgg_file_list.txt', type=str, help='Input list of ggntuples.')
#parser.add_argument('-i', '--inlist', default='../ggNtuples/Era20May2021_v1/h4g2018-mA1p0GeV_file_list.txt', type=str, help='Input list of ggntuples.')
#parser.add_argument('--pu_data', default='PU/dataPU_2017.root', type=str, help='PU data ref file.')
#parser.add_argument('--systPhoIdFile', default='SF/SF2017_egammaEffi.txt_EGM2D.root', type=str, help='Photon ID syst reweighting file if to be applied.')
#parser.add_argument('--systPhoIdFile', default=None, type=str, help='Photon ID syst reweighting file if to be applied.')
parser.add_argument('--pt_rwgt', default=None, type=str, help='pt re-weighting file.')
#parser.add_argument('--pt_rwgt', default='root://cmseos.fnal.gov//store/group/lpchaa4g/mandrews/Run2/bkgNoPtWgts-Era04Dec2020v2/bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-nom/Weights/data_sb2sr_blind_None_flo0.7910_ptwgts.root', type=str, help='pt re-weighting file.')
parser.add_argument('-o', '--outdir', default='Templates', type=str, help='Output directory.')
args = parser.parse_args()

sample = args.sample
print('>> Sample:', sample)
#assert len(sample.split('-')) == 2, '!! sample name invalid: %s'%sample
year = re.findall('(201[6-8])', sample.split('-')[0])[0]

# input ggNtuple list
# NOTE: these are ggNtuples without regressed mass for bkg MC!!
inlist = args.inlist
assert os.path.isfile(inlist), '!! gg input list not found: %s'%inlist
assert sample in inlist, '!! sample: %s mismatch to input file: %s'%(sample, inlist)

pt_rwgt = args.pt_rwgt
# wont work if root:// path passed:
#if pt_rwgt is not None:
#    assert os.path.isfile(pt_rwgt), '!! pt re-weight file not found: %s'%pt_rwgt
'''
# Get PU data ref distn
pu_data = args.pu_data
print('>> PU reference:', pu_data)
assert os.path.isfile(pu_data), '!! PU data ref file not found!'

# Get photon ID syst file
systPhoIdFile = args.systPhoIdFile
phoIdSF_nom = None
print('>> Photon ID syst reference:', systPhoIdFile)
if systPhoIdFile is not None:
    assert os.path.isfile(systPhoIdFile), '!! Photon ID syst file not found: %s'%systPhoIdFile
    phoIdSF_nom = 'nom'
'''

# mH-region: SR by default
region = args.region
print('>> mH-region:', region)

# Create output dirs
#output_basedir = mkoutdir('Templates/systTEST')
#output_basedir = mkoutdir('Templates')
output_basedir = mkoutdir(args.outdir)
#pu_dir = mkoutdir('PU')

#_________________________________

'''
# Get MC->Data PU weights
# Data pu created using pileupCalc: https://twiki.cern.ch/twiki/bin/viewauth/CMS/PileupJSONFileforData
# See e.g. https://github.com/tanmaymudholkar/STEALTH/blob/tanmay-devel/miscUtils/PUReweighting/makeDataPUDistributions.sh
# Output from Tanmay: https://github.com/tanmaymudholkar/STEALTH/tree/tanmay-devel/getMCSystematics/data
pu_file = '%s/puwgts_datao%s.root'%(pu_dir, sample)
pyargs = 'get_pu_distn.py -s %s --inlist %s -p %s -o %s'%(sample, inlist, pu_data, pu_file)
print('>> Deriving MC->Data PU wgts: %s'%pyargs)
os.system('python %s'%pyargs)
assert os.path.isfile(pu_file), '!! PU wgts file not found: %s'%pu_file
'''

# Nominal scenario
output_dir = mkoutdir('%s/systNom_nom'%(output_basedir))
pyargs = 'skim_select_events.py -s %s -r %s --inlist %s -o %s --do_ptomGG'\
        %(sample, region, inlist, output_dir)
if pt_rwgt is not None:
    pyargs += ' --pt_rwgt %s'%pt_rwgt
#if systPhoIdFile is not None:
#    pyargs += ' --systPhoIdSF nom --systPhoIdFile %s'%systPhoIdFile
print('>> Making nominal MC templates: %s'%pyargs)
os.system('python %s'%pyargs)
