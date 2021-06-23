from __future__ import print_function
import os, glob, shutil, re
import numpy as np

# Strings to replace in jdl template
EXEC = '__EXEC__'
INPUTS = '__INPUTS__'
ARGS = '__ARGS__'
MEM = '__MEM__'

# Input maNtuple campaign
indir = '../maNtuples'
input_campaign = 'Era04Dec2020v1' # 2018A added later
print('>> Input campaign: maNtuples-%s'%input_campaign)

# Output bkg campaign
#this_campaign = 'bkgNoPtWgts-Era11Dec2020v1' # no eta cut applied, no 2018A, 2016H+2018 failed lumis
#this_campaign = 'bkgNoPtWgts-Era04Dec2020v1' # rename of Era11Dec2020v1
#this_campaign = 'bkgNoPtWgts-Era04Dec2020v2' # redo with 2018A
this_campaign = 'bkgNoPtWgts-Era04Dec2020v3' # redo v2 with nVtx, nPU plots
print('>> Output campaign:',this_campaign)

#sub_campaign = 'bdtgtm0p98_relChgIsolt0p05_etalt1p44/nom-inv' # a0nom-a1inv
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p05_etalt1p44/nom-nom' # a0nom-a1nom

#sub_campaign = 'bdtgtm0p99_relChgIsolt0p05_etalt1p44/nom-nom' # bdt > -0.99
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p05_etalt1p44/nom-nom' # bdt > -0.96
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p03_etalt1p44/nom-nom' # relChgIso < 0.03
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p07_etalt1p44/nom-nom' # relChgIso < 0.07

#sub_campaign = 'bdtgtm0p99_relChgIsolt0p03_etalt1p44/nom-nom' # bdt > -0.99, relChgIso < 0.03
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-nom' # bdt > -0.96, relChgIso < 0.07 !! optimal
#sub_campaign = 'bdtgtm0p97_relChgIsolt0p06_etalt1p44/nom-nom' # bdt > -0.97, relChgIso < 0.06
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p09_etalt1p44/nom-nom' # bdt > -0.96, relChgIso < 0.09
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p08_etalt1p44/nom-nom' # bdt > -0.96, relChgIso < 0.08

sub_campaign = 'bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-nom' # bdt > -0.96, relChgIso < 0.07 !! optimal
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-inv' # bdt > -0.96, relChgIso < 0.07 !! optimal
print('>> Output sub-campaign:',sub_campaign)

exec_file = 'run_bkg_noptwgts.sh'
#tar_file = 'h2aa_%s.tgz'%sub_campaign.split('/')[-1]
#tar_file = 'h2aa_%s_%s.tgz'%(sub_campaign.split('/')[-1], sub_campaign.split('_')[0]) # bdt scan
#tar_file = 'h2aa_%s_%s.tgz'%(sub_campaign.split('/')[-1], sub_campaign.split('_')[1]) # relChgIso scan
tar_file = 'h2aa_%s_%s_%s.tgz'%(sub_campaign.split('/')[-1], sub_campaign.split('_')[0], sub_campaign.split('_')[1]) # bdt,relChgIso scan
print('>> tar file:',tar_file)
assert os.path.isfile(tar_file), '!! input tar file not found!'

cwd = os.getcwd()+'/'
#jdl_folder = 'jdls/%s'%this_campaign
jdl_folder = 'jdls/%s/%s'%(this_campaign, sub_campaign)
if not os.path.isdir(jdl_folder):
    os.makedirs(jdl_folder)
print('>> jdl folder:',jdl_folder)

#runs = ['Run2'] # all years together--will only run on data
#runs = ['2016', '2017', '2018'] # run bkg yr-by-yr. required for MC

# For full Run2: bkg templates need to be created yr-by-yr
# since hgg MC are provided yr-by-yr and need to be normalized per yr
# However, derivation of pt wgts needs to be done over full Run2 stats
# so run both yr-by-yr and full run2 bkg processing
runs = ['2016', '2017', '2018', 'Run2'] # run all

for r in runs:

    print('>> For run:',r)
    #if r != '2016': continue

    doRun2 = True if r == 'Run2' else False

    # ntuple IO
    #eos_indir = '/store/group/lpchaa4g/mandrews/%s/maNtuples-Era04Dec2020v1'%('*' if doRun2 else r)
    #eos_tgtdir = '/store/user/lpchaa4g/mandrews/%s/%s'%(r, this_campaign)
    eos_tgtdir = '/store/user/lpchaa4g/mandrews/%s/%s/%s'%(r, this_campaign, sub_campaign)
    #print('   .. eos indir:', eos_indir)
    print('   .. eos tgtdir:', eos_tgtdir)

    # Define samples
    # NOTE: hgg mc is not actually used for deriving (data-only) pt wgts
    # but is included here since evt selection for hgg is never run with pt wgts
    # (pt wgts are applied to SB data only)
    # NOTE: hgg MC must be done year-by-year since each sample will
    # have diff lumi normalizations, depending on mc stats & tgt data lumi
    # data samples, on other hand, can be run together for full Run2

    # For data, run on each mH-SB/SR
    yr = '' if doRun2 else r
    samples = ['data%s'%yr]
    mhregions = {'data%s'%yr: ['sblo', 'sr', 'sbhi']}
    # If doing yr-by-yr, include hgg MC
    if not doRun2:
        samples.append('bg%s-hgg'%yr)
        mhregions['bg%s-hgg'%yr] = ['sr']

    for sample in samples:

        #if sample != 'GluGluHToGG': continue

        print('   >> For sample:',sample)

        in_list = '%s/%s/%s_file_list.txt'%(indir, input_campaign, sample)
        print('      .. using input list: %s'%(in_list))
        assert os.path.isfile(in_list), '      !! input maNtuple list not found!'

        for mhregion in mhregions[sample]:

            print('      >> For mhregion:',mhregion)

            # Read in condor config template
            with open('jdls/condor_runbkg.jdl', "r") as template_file:
                file_data = template_file.read()

            # Replace condor config template strings with sample-specific values
            file_data = file_data.replace(EXEC,   cwd+exec_file)
            file_data = file_data.replace(INPUTS, '%s, %s, %s'%(cwd+exec_file, cwd+tar_file, cwd+in_list))
            file_data = file_data.replace(ARGS,   '%s %s %s %s %s'
                                                   %(sample, mhregion, in_list.split('/')[-1], eos_tgtdir, tar_file))
            file_data = file_data.replace(MEM, '4800')

            # Write out sample-specific condor config
            with open('%s/condor_runbkg_%s_mh%s.jdl'%(jdl_folder, sample, mhregion), "w") as sample_file:
                sample_file.write(file_data)
