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
input_campaign = 'Era04Dec2020v1' # updated later with 2018A
print('>> Input campaign: maNtuples-%s'%input_campaign)

# Input pt wgts campaign
#ptwgts_campaign = 'bkgNoPtWgts-Era04Dec2020v1' # no 2018A, 2016H+2018 failed lumis
#ptwgts_campaign = 'bkgNoPtWgts-Era04Dec2020v2' # 2016H+2018 failed lumis
ptwgts_campaign = 'bkgNoPtWgts-Era04Dec2020v3' # redo v2 with nVtx, nPU plots
print('>> Input pt wgts campaign: %s'%ptwgts_campaign)

#ptwgts_subcampaign = 'bdtgtm0p98_relChgIsolt0p05_etalt1p44/nom-nom' # a0nom-a1nom
#ptwgts_subcampaign = 'bdtgtm0p98_relChgIsolt0p05_etalt1p44/nom-inv' # a0nom-a1nom
#ptwgts_subcampaign = 'bdtgtm0p99_relChgIsolt0p05_etalt1p44/nom-nom' # bdt > -0.99
#ptwgts_subcampaign = 'bdtgtm0p96_relChgIsolt0p05_etalt1p44/nom-nom' # bdt > -0.96
#ptwgts_subcampaign = 'bdtgtm0p98_relChgIsolt0p03_etalt1p44/nom-nom' # relChgIso < 0.03
#ptwgts_subcampaign = 'bdtgtm0p98_relChgIsolt0p07_etalt1p44/nom-nom' # relChgIso < 0.07
#ptwgts_subcampaign = 'bdtgtm0p99_relChgIsolt0p03_etalt1p44/nom-nom' # bdt > -0.99, relChgIso < 0.03
#ptwgts_subcampaign = 'bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-nom' # bdt > -0.96, relChgIso < 0.07 !! optimal
#ptwgts_subcampaign = 'bdtgtm0p97_relChgIsolt0p06_etalt1p44/nom-nom' # bdt > -0.96, relChgIso < 0.07
#ptwgts_subcampaign = 'bdtgtm0p96_relChgIsolt0p09_etalt1p44/nom-nom' # bdt > -0.96, relChgIso < 0.09
#ptwgts_subcampaign = 'bdtgtm0p96_relChgIsolt0p08_etalt1p44/nom-nom' # bdt > -0.96, relChgIso < 0.08

ptwgts_subcampaign = 'bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-nom' # bdt > -0.96, relChgIso < 0.07 !! optimal
#ptwgts_subcampaign = 'bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-inv' # bdt > -0.96, relChgIso < 0.07 !! optimal
print('>> Input pt wgts sub-campaign: %s'%ptwgts_subcampaign)

# Output bkg campaign
#this_campaign = 'bkgPtWgts-Era04Dec2020v1' # using bkgNoPtWgts-Era04Dec2020v1/bdtgtm0p98_relChgIsolt0p05_etalt1p44
#this_campaign = 'bkgPtWgts-Era04Dec2020v2' # using bkgNoPtWgts-Era04Dec2020v2/bdtgtm0p98_relChgIsolt0p05_etalt1p44
this_campaign = 'bkgPtWgts-Era04Dec2020v3' # using bkgNoPtWgts-Era04Dec2020v3/bdtgtm0p98_relChgIsolt0p05_etalt1p44 [same as v2 + nVtx, nPU plots]
print('>> Output campaign:',this_campaign)

exec_file = 'run_bkg_ptwgts.sh'
#tar_file = 'h2aa.tgz'
#tar_file = 'h2aa-inv.tgz'
#tar_file = 'h2aa_%s.tgz'%ptwgts_subcampaign.split('/')[-1]
#tar_file = 'h2aa_%s_%s.tgz'%(ptwgts_subcampaign.split('/')[-1], ptwgts_subcampaign.split('_')[0]) # bdt scan
#tar_file = 'h2aa_%s_%s.tgz'%(ptwgts_subcampaign.split('/')[-1], ptwgts_subcampaign.split('_')[1]) # relChgIso scan
tar_file = 'h2aa_%s_%s_%s.tgz'%(ptwgts_subcampaign.split('/')[-1], ptwgts_subcampaign.split('_')[0], ptwgts_subcampaign.split('_')[1]) # bdt,relChgIso scan
assert os.path.isfile(tar_file), ' !! input tarfile not found: %s'%tar_file

doRun2 = True
run2dir = 'Run2'

# Output jdl directory
cwd = os.getcwd()+'/'
#jdl_folder = 'jdls/%s'%this_campaign
jdl_folder = 'jdls/%s/%s'%(this_campaign, ptwgts_subcampaign)
if doRun2: jdl_folder += '/%s'%run2dir
if not os.path.isdir(jdl_folder):
    os.makedirs(jdl_folder)
print('>> jdl folder:',jdl_folder)

runs = ['2016', '2017', '2018'] # Full Run2 bkg should still by yr-by-yr except using full Run2 pt wgts.

for r in runs:

    print('>> For run:',r)
    #if r != '2016': continue

    # pt weights
    ptwgts_indir = '/store/group/lpchaa4g/mandrews/%s/%s/%s/Weights'%(run2dir if doRun2 else r, ptwgts_campaign, ptwgts_subcampaign)
    print('   .. pt wgts indir:', ptwgts_indir)

    # ntuple IO
    eos_tgtdir = '/store/user/lpchaa4g/mandrews/%s/%s/%s'%(r, this_campaign, ptwgts_subcampaign)
    if doRun2: eos_tgtdir += '/%s'%run2dir
    print('   .. eos tgtdir:', eos_tgtdir)

    # Define samples
    # pt reweighting only applied to data mH-SBlo, mH-SBhi
    #yr = '' if doRun2 else r
    yr = r
    samples = ['data%s'%yr]
    mhregions = {'data%s'%yr: ['sblo', 'sbhi']}

    for sample in samples:

        print('   >> For sample:',sample)

        in_list = '%s/%s/%s_file_list.txt'%(indir, input_campaign, sample)
        print('      .. using input list: %s'%(in_list))
        assert os.path.isfile(in_list), '      !! input maNtuple list not found!'

        for mhregion in mhregions[sample]:

            print('      >> For mhregion:',mhregion)

            # Get f_SBlow scenarios and pt wgt files
            # Each scenario will use different pt wgts
            #flos = [None]
            flo_files = glob.glob('/eos/uscms/%s/*ptwgts.root'%ptwgts_indir)
            # flo_dict: key: f_SBlow, value: LFN filepath to pt wgts file
            # e.g. flo_dict['0.6413'] = /store/.../..flo0.6413_ptwgts.root
            flo_dict = {flo.split('_')[-2].strip('flo'):flo.replace('/eos/uscms/','') for flo in flo_files}
            print('      .. found %d f_SBlow scenarios: %s'%(len(flo_dict), ' '.join(flo_dict.keys())))

            for flo in flo_dict:

                print('         >> For f_SBlow: %s'%flo)
                #flo_str = '%.3f'%flo if flo is not None else str(flo)
                flo_str = flo
                #input_ptwgts = '%s_sb2sr_blind_None_flo%s_ptwgts'%(sample, flo_str)
                #ptwgts_file = '%s/%s.root'%(ptwgts_indir, input_ptwgts)
                #print('         .. using pt wgts: %s'%ptwgts_file)
                ptwgts_file = flo_dict[flo]
                print('         .. using pt wgts: %s'%flo_dict[flo])

                #'''
                # Read in condor config template
                with open('jdls/condor_runbkg.jdl', "r") as template_file:
                    file_data = template_file.read()

                # Replace condor config template strings with sample-specific values
                file_data = file_data.replace(EXEC,   cwd+exec_file)
                file_data = file_data.replace(INPUTS, '%s, %s, %s'%(cwd+exec_file, cwd+tar_file, cwd+in_list))
                file_data = file_data.replace(ARGS,   '%s %s %s %s %s %s %s'
                                                       %(sample, mhregion, in_list.split('/')[-1], eos_tgtdir, flo_str, ptwgts_file, tar_file))
                file_data = file_data.replace(MEM,    '4800')

                # Write out sample-specific condor config
                with open('%s/condor_runbkg_%s_mh%s_flo%s.jdl'%(jdl_folder, sample, mhregion, flo_str), "w") as sample_file:
                    sample_file.write(file_data)
                #'''
