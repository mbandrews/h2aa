from __future__ import print_function
import os, glob, shutil, re
import numpy as np

# Strings to replace in jdl template
EXEC = '__EXEC__'
INPUTS = '__INPUTS__'
ARGS = '__ARGS__'
MEM = '__MEM__'
MA = '$MA'
NCPU = '__NCPU__'

# Input ntuples
#indir = '../maNtuples'
#input_campaign = 'Era04Dec2020v1' # fixed mc diphoton trg
#print('>> Input maNtuple campaign:',input_campaign)

# Define bkg+sg campaign
#this_campaign = 'limits_bkg-bkgNoPtWgts-Era04Dec2020v2_sg-Era04Dec2020v3_v1' # use old (bdt+chgiso cuts) 2017 s+s for all yrs
#this_campaign = 'limits_bkg-bkgNoPtWgts-Era04Dec2020v2_sg-Era04Dec2020v4_v1' # add 2016+17+18 phoid, 2017+18 ss. 2016 ss missing: use 2017 ss
#this_campaign = 'limits_bkg-bkgNoPtWgts-Era04Dec2020v2_sg-Era04Dec2020v5_v1' # v4 + nominals use best-fit ss over full m_a, shifted uses best-fit ss over ele peak only.
this_campaign = 'limits_bkg-bkgNoPtWgts-Era04Dec2020v2_sg-Era04Dec2020v6_v1' # 2016-18 phoid, 2016-18 ss. ss implemented only for shifted syst (as in v4)
print('>> Limit setting campaign:',this_campaign)

#sub_campaign = 'bdtgtm0p98_relChgIsolt0p05_etalt1p44/nom-inv' # a0nom-a1inv
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p05_etalt1p44/nom-nom' # a0nom-a1nom
#sub_campaign = 'bdtgtm0p99_relChgIsolt0p05_etalt1p44/nom-nom' # bdt > -0.99
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p05_etalt1p44/nom-nom' # bdt > -0.96
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p03_etalt1p44/nom-nom' # relChgIso < 0.03
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p07_etalt1p44/nom-nom' # relChgIso < 0.07
#sub_campaign = 'bdtgtm0p99_relChgIsolt0p03_etalt1p44/nom-nom' # bdt > -0.99, relChgIso < 0.03
sub_campaign = 'bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-nom' # bdt > -0.96, relChgIso < 0.07 !! optimal
#sub_campaign = 'bdtgtm0p97_relChgIsolt0p06_etalt1p44/nom-nom' # bdt > -0.96, relChgIso < 0.07
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p09_etalt1p44/nom-nom' # bdt > -0.96, relChgIso < 0.09
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p08_etalt1p44/nom-nom' # bdt > -0.96, relChgIso < 0.08
#sub_campaign = '%s/bin100MeV'%sub_campaign
sub_campaign = '%s/bin25MeV'%sub_campaign
print('>> Output sub-campaign:',sub_campaign)

# Define jdl exec, tar, etc
tar_file = 'combineTool.tgz'
print('>> tar file:',tar_file)
assert os.path.isfile(tar_file), '!! input tar file %s not found!'%tar_file

## Define xrdcp utils
#xrdcp_py = 'xrdcpRecursive.py'
#assert os.path.isfile(xrdcp_py), '!! input xrdcpRecursive.py file not found!'
#xrdcp_util = 'recursiveFileList.py'
#assert os.path.isfile(xrdcp_util), '!! input recursiveFileList.py file not found!'

# Defin work dirs
cwd = os.getcwd()+'/'
analysis_dir = '%s../ntupleAnalysis'%cwd
combine_dir = '/uscms/home/mba2012/nobackup/h2aa/CMSSW_10_2_13/src'
jdl_folder = 'jdls/%s/%s/dcards'%(this_campaign, sub_campaign)
if not os.path.isdir(jdl_folder):
    os.makedirs(jdl_folder)
print('>> jdl folder:',jdl_folder)

dcard_path = '/uscms/home/mba2012/nobackup/h2aa/CMSSW_10_5_0/src/h2aa/ntupleAnalysis/Datacards/h4g_MA_.txt'
print('>> datacard template:',dcard_path)
assert os.path.isfile(dcard_path), '!! input datacard %s not found!'%dcard_path

# Define systs
systs = [
    'flo',
    'hgg',
    'pol2de0',
    'pol2de1',
    'pol2de2',
    'Lumi',
    'Scale',
    'Smear',
    'PhoIdSF',
    '* autoMCStats'
]

# Define mass pts
masses = ['0p1', '0p4', '1p0']

for m in masses:

    sample = 'h4g_%s'%m
    print('>> For sample:',sample)

    # Read in datacard template
    with open(dcard_path, "r") as dcard_file:
        dcard_data = dcard_file.read()

    dcard_data = dcard_data.replace(MA, m)

    # Write out mass-specific datacard, all systs
    dcard_tgt = cwd+'%s/%s.txt'%(jdl_folder, sample)
    with open(dcard_tgt, "w") as sample_card:
        sample_card.write(dcard_data)

    # Output EOS tgt
    eos_tgtdir = '/store/user/lpchaa4g/mandrews/Run2/%s/%s/%s'%(this_campaign, sub_campaign, sample)
    print('   .. eos tgt:', eos_tgtdir)

    # Get sg+bkg templates
    #model_file = '%s/Fits/Bkgfits_flat_regionlimit.root'%(analysis_dir)
    model_file = '%s/Fits/CMS_h4g_sgbg_shapes.root'%(analysis_dir)
    print('   .. sg+bkg model file:', model_file)
    assert os.path.isfile(model_file), '!! Model file %s not found!'%(model_file)

    # Define exec file
    # When running with all syst, run both impacts and limits
    exec_file = 'run_limits+impacts.sh'
    assert os.path.isfile(exec_file), '!! input exec file %s not found!'%exec_file

    # Define jdl inputs
    jdl_inputs = '%s, %s, %s, %s'%(cwd+exec_file, cwd+tar_file, model_file, dcard_tgt)

    # Define jdl args
    jdl_args = '%s %s %s %s %s'%(sample, model_file.split('/')[-1], dcard_tgt.split('/')[-1], eos_tgtdir, tar_file)
    assert sample+'.txt' == dcard_tgt.split('/')[-1] # required by exec_file

    # Read in jdl template
    with open('jdls/condor_setlimits.jdl', "r") as template_file:
        file_data = template_file.read()

    # Replace condor template strings with sample-specific values
    file_data = file_data.replace(EXEC,   cwd+exec_file)
    file_data = file_data.replace(INPUTS, jdl_inputs)
    file_data = file_data.replace(ARGS,   jdl_args)
    #file_data = file_data.replace(MEM,    '2800')
    file_data = file_data.replace(MEM,    '8000')
    file_data = file_data.replace(NCPU,   '10') #10

    # Write out sample-specific jdl
    with open('%s/../condor_setlimits_%s.jdl'%(jdl_folder, sample), "w") as sample_file:
        sample_file.write(file_data)

    #'''
    # Run N-1 limits only (i.e. no impacts)
    for syst in systs:

        syst_clean = syst.replace('* ','')
        sample = 'h4g_%s-%s'%(m, syst_clean)
        print('   >> Doing N-1 syst:',sample)
        assert syst in dcard_data

        # Read in datacard template
        with open(dcard_path, "r") as dcard_file:
            dcard_data = dcard_file.read()

        dcard_data = dcard_data.replace(MA,   m)
        dcard_data = dcard_data.replace(syst, '#'+syst)

        # Write out sample-specific datacard, N-1 systs
        dcard_tgt = cwd+'%s/%s.txt'%(jdl_folder, sample)
        with open(dcard_tgt, "w") as sample_card:
            sample_card.write(dcard_data)

        # Output EOS tgt
        eos_tgtdir = '/store/user/lpchaa4g/mandrews/Run2/%s/%s/%s/%s'%(this_campaign, sub_campaign, sample.split('-')[0], syst_clean)
        print('   .. eos tgt:', eos_tgtdir)

        # Define exec file
        # When running on N-1 systs, only run limits (i.e. no impacts)
        exec_file = 'run_limits.sh'
        assert os.path.isfile(exec_file), '!! input exec file %s not found!'%exec_file

        # Define jdl inputs
        jdl_inputs = '%s, %s, %s, %s'%(cwd+exec_file, cwd+tar_file, model_file, dcard_tgt)

        # Define jdl args
        jdl_args = '%s %s %s %s %s'%(sample, model_file.split('/')[-1], dcard_tgt.split('/')[-1], eos_tgtdir, tar_file)
        assert sample+'.txt' == dcard_tgt.split('/')[-1] # required by exec_file

        # Read in crabConfig template
        with open('jdls/condor_setlimits.jdl', "r") as template_file:
            file_data = template_file.read()

        # Replace condor template strings with sample-specific values
        file_data = file_data.replace(EXEC,   cwd+exec_file)
        file_data = file_data.replace(INPUTS, jdl_inputs)
        file_data = file_data.replace(ARGS,   jdl_args)
        file_data = file_data.replace(MEM,    '2800')
        file_data = file_data.replace(NCPU,   '1')

        # Write out sample-specific jdl
        with open('%s/../condor_setlimits_%s.jdl'%(jdl_folder, sample), "w") as sample_file:
            sample_file.write(file_data)

    #'''
