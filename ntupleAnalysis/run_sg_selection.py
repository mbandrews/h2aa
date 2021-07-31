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
parser = argparse.ArgumentParser(description='Run h2aa sg selection.')
parser.add_argument('-s', '--sample', default='h4g2017-mA0p4GeV', type=str, help='Sample name.')
#parser.add_argument('-s', '--sample', default='bg2017-hgg', type=str, help='Sample name.')
parser.add_argument('-r', '--region', default='sr', type=str, help='mH-region: sr, sb, sblo, sbhi, all')
parser.add_argument('-i', '--inlist', default='../maNtuples/Era22Jun2021v1/h4g2017-mA0p4GeV_file_list.txt', type=str, help='Input list of mantuples.')
#parser.add_argument('-i', '--inlist', default='../maNtuples/Era22Jun2021v1/bg2016-hgg_file_list.txt', type=str, help='Input list of mantuples.')
parser.add_argument('--pu_data', default='PU/dataPU_2016.root', type=str, help='PU data ref file.')
parser.add_argument('--systPhoIdFile', default='SF/SF2016_egammaEffi.txt_EGM2D.root', type=str, help='Photon ID syst reweighting file if to be applied.')
#parser.add_argument('--systPhoIdFile', default=None, type=str, help='Photon ID syst reweighting file if to be applied.')
parser.add_argument('--do_systTrgSF', action='store_true', help='Apply trigger SFs.')
args = parser.parse_args()

## /eos/uscms/store/user/lpchaa4g/mandrews/2017/maNtuples-Era03Dec2020v1/h4g2017-mA0p1GeV_mantuple.root
#samples = [
#    '0p1',
#    '0p2',
#    '0p4',
#    '0p6',
#    '0p8',
#    '1p0',
#    '1p2',
#    ]
#samples = ['mA%sGeV'%s for s in samples]
#
#input_campaign = 'Era04Dec2020v1'
#campaign = 'templates-Era04Dec2020v1'
##campaign += '-eta1p2'

sample = args.sample
print('>> Sample:', sample)
assert len(sample.split('-')) == 2, '!! sample name invalid: %s'%sample
year = re.findall('(201[6-8])', sample.split('-')[0])[0]

# input maNtuple list
inlist = args.inlist
assert os.path.isfile(inlist), '!! ma input list not found: %s'%inlist
assert sample in inlist, '!! sample: %s mismatch to input file: %s'%(sample, inlist)

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

# mH-region: SR by default
region = args.region
print('>> mH-region:', region)

# SF scenarios
systPhoIdSFs = ['up', 'dn'] # photon ID SF syst shifts: nom, up, dn
systScales = ['up', 'dn'] # ma energy scale shifts: up, dn => dn: no scale applied
systSmears = ['up', 'dn'] # ma energy smearing shifts: up, dn => dn: no smear applied
systTrgSFs = ['up', 'dn'] # trg SF syst shifts: nom, up, dn

# If not applying trg SFs
do_systTrgSF = args.do_systTrgSF
print('>> Apply trg SFs?', do_systTrgSF)
if not do_systTrgSF:
    systTrgSFs = []

# energy scaling per year: [|eta|<0.5, 0.5<|eta|<1.0, 1.0<|eta|<1.4]
enScale = {'2016': [1.002, 0.976, 0.990],
           '2017': [1.046, 1.014, 1.056],
           '2018': [1.012, 1.016, 1.044],
           }
#enScale = {'2016': [1.046, 1.032, 1.056],
#           '2017': [1.046, 1.032, 1.056],
#           '2018': [1.012, 1.016, 1.044],
#           }
#enScaleShift = {'2016': [1.046, 1.014, 1.042],
#                '2017': [1.046, 1.014, 1.042],
#                '2018': [1.020, 1.028, 1.042],
#               }
# energy smearing per year: [|eta|<0.5, 0.5<|eta|<1.0, 1.0<|eta|<1.4]
enSmear = {'2016': [0., 0., 0.012],
           '2017': [0., 0., 0.],
           '2018': [0.002, 0., 0.],
           }
#enSmear = {'2016': [0., 0., 0.],
#           '2017': [0., 0., 0.],
#           '2018': [0.002, 0., 0.],
#           }
#enSmearShift = {'2016': [0., 0., 0.],
#                '2017': [0., 0., 0.004],
#                '2018': [0.010, 0., 0.],
#                }

# Create output dirs
#output_basedir = mkoutdir('Templates/systTEST')
output_basedir = mkoutdir('Templates')
pu_dir = mkoutdir('PU')

#_________________________________

# Get MC->Data PU weights
# Data pu created using pileupCalc: https://twiki.cern.ch/twiki/bin/viewauth/CMS/PileupJSONFileforData
# See e.g. https://github.com/tanmaymudholkar/STEALTH/blob/tanmay-devel/miscUtils/PUReweighting/makeDataPUDistributions.sh
# Output from Tanmay: https://github.com/tanmaymudholkar/STEALTH/tree/tanmay-devel/getMCSystematics/data
pu_file = '%s/puwgts_datao%s.root'%(pu_dir, sample)
pyargs = 'get_pu_distn.py -s %s --inlist %s -p %s -o %s'%(sample, inlist, pu_data, pu_file)
print('>> Deriving MC->Data PU wgts: %s'%pyargs)
os.system('python %s'%pyargs)
assert os.path.isfile(pu_file), '!! PU wgts file not found: %s'%pu_file

# Nominal scenario
output_dir = mkoutdir('%s/systNom_nom'%(output_basedir))
pyargs = 'select_events.py -s %s -r %s --inlist %s -o %s --do_ptomGG --pu_file %s'\
        %(sample, region, inlist, output_dir, pu_file)
if systPhoIdFile is not None:
    pyargs += ' --systPhoIdSF nom --systPhoIdFile %s'%systPhoIdFile
if do_systTrgSF:
    pyargs += ' --systTrgSF nom'
## apply nominal scale: chi2 fit over full m_a space
#pyargs += ' --systScale %s'%(' '.join(str(s) for s in enScale[year]))
## apply nominal smear: chi2 fit over full m_a space
#pyargs += ' --systSmear %s'%(' '.join(str(s) for s in enSmear[year]))
print('>> Making nominal MC templates: %s'%pyargs)
os.system('python %s'%pyargs)

'''
# Syst: trg SF
print('>> Doing systTrgSF...')
for systTrgSF in systTrgSFs:

    print('   .. systTrgSF:',systTrgSF)

    output_dir = mkoutdir('%s/systTrgSF_%s'%(output_basedir, systTrgSF))
    pyargs = 'select_events.py -s %s -r %s --inlist %s -o %s --do_ptomGG --pu_file %s'\
            %(sample, region, inlist, output_dir, pu_file)
    if systPhoIdFile is not None:
        pyargs += ' --systPhoIdSF nom --systPhoIdFile %s'%systPhoIdFile
    # apply trg SF shift:
    pyargs += ' --systTrgSF %s'% systTrgSF
    print('   >> Making templates: %s'%pyargs)
    os.system('python %s'%pyargs)
'''

# Syst: photon ID SFs
if systPhoIdFile is not None:

    print('>> Doing systPhoIdSF...')
    for systPhoIdSF in systPhoIdSFs:

        print('   .. systPhoIdSF:',systPhoIdSF)

        output_dir = mkoutdir('%s/systPhoIdSF_%s'%(output_basedir, systPhoIdSF))
        pyargs = 'select_events.py -s %s -r %s --inlist %s -o %s --do_ptomGG --pu_file %s --systPhoIdSF %s --systPhoIdFile %s'\
                %(sample, region, inlist, output_dir, pu_file, systPhoIdSF, systPhoIdFile)
        ## apply nominal scale: chi2 fit over full m_a space
        #pyargs += ' --systScale %s'%(' '.join(str(s) for s in enScale[year]))
        ## apply nominal smear: chi2 fit over full m_a space
        #pyargs += ' --systSmear %s'%(' '.join(str(s) for s in enSmear[year]))
        if do_systTrgSF:
            pyargs += ' --systTrgSF nom'
        print('   >> Making templates: %s'%pyargs)
        os.system('python %s'%pyargs)

# Syst: trg SF
print('>> Doing systTrgSF...')
for systTrgSF in systTrgSFs:

    print('   .. systTrgSF:',systTrgSF)

    output_dir = mkoutdir('%s/systTrgSF_%s'%(output_basedir, systTrgSF))
    pyargs = 'select_events.py -s %s -r %s --inlist %s -o %s --do_ptomGG --pu_file %s'\
            %(sample, region, inlist, output_dir, pu_file)
    if systPhoIdFile is not None:
        pyargs += ' --systPhoIdSF nom --systPhoIdFile %s'%systPhoIdFile
    # apply trg SF shift:
    pyargs += ' --systTrgSF %s'% systTrgSF
    print('   >> Making templates: %s'%pyargs)
    os.system('python %s'%pyargs)

# Syst: m_a energy scale
# NOTE: systScale:dn applies no scaling at all since scaling syst is 1-sided
# Since identical to nominal scenario, copy contents from there
print('>> Doing systScale...')
for systScale in systScales:

    print('   .. systScale:',systScale)

    output_dir = mkoutdir('%s/systScale_%s'%(output_basedir, systScale))
    if 'dn' in systScale:
        print('   .. copying systNom_nom')
        os.system('cp -r %s/systNom_nom/*root %s/systScale_dn/'%(output_basedir, output_basedir))
    elif 'up' in systScale:
        pyargs = 'select_events.py -s %s -r %s --inlist %s -o %s --do_ptomGG --pu_file %s'\
                %(sample, region, inlist, output_dir, pu_file)
        if systPhoIdFile is not None:
            pyargs += ' --systPhoIdSF nom --systPhoIdFile %s'%systPhoIdFile
        if do_systTrgSF:
            pyargs += ' --systTrgSF nom'
        # apply shifted scale
        pyargs += ' --systScale %s'%(' '.join(str(s) for s in enScale[year]))
        ## apply shifted scale: chi2 fit over m_a peak of electrons
        #pyargs += ' --systScale %s'%(' '.join(str(s) for s in enScaleShift[year]))
        ## apply nominal smear: chi2 fit over full m_a space
        #pyargs += ' --systSmear %s'%(' '.join(str(s) for s in enSmear[year]))
        print('   >> Making templates: %s'%pyargs)
        os.system('python %s'%pyargs)

# Syst: m_a energy smearing
print('>> Doing systSmear...')
# NOTE: systSmear:dn applies no smearing at all since smearing syst is 1-sided
# Since identical to nominal scenario, copy contents from there
for systSmear in systSmears:

    print('   .. systSmear:',systSmear)

    output_dir = mkoutdir('%s/systSmear_%s'%(output_basedir, systSmear))
    if 'dn' in systSmear:
        print('   .. copying systNom_nom')
        os.system('cp -r %s/systNom_nom/*root %s/systSmear_dn/'%(output_basedir, output_basedir))
    elif 'up' in systSmear:
        pyargs = 'select_events.py -s %s -r %s --inlist %s -o %s --do_ptomGG --pu_file %s'\
                %(sample, region, inlist, output_dir, pu_file)
                #%(sample, region, inlist, output_dir, pu_file, systSmear)
        if systPhoIdFile is not None:
            pyargs += ' --systPhoIdSF nom --systPhoIdFile %s'%systPhoIdFile
        if do_systTrgSF:
            pyargs += ' --systTrgSF nom'
        # apply shifted smear
        pyargs += ' --systSmear %s'%(' '.join(str(s) for s in enSmear[year]))
        ## apply nominal scale: chi2 fit over full m_a space
        #pyargs += ' --systScale %s'%(' '.join(str(s) for s in enScale[year]))
        ## apply shifted smear: chi2 fit over m_a peak of electrons
        #pyargs += ' --systSmear %s'%(' '.join(str(s) for s in enSmearShift[year]))
        print('   >> Making templates: %s'%pyargs)
        os.system('python %s'%pyargs)
