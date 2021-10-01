from __future__ import print_function
import os, glob, shutil, re
import numpy as np

# Strings to replace in jdl template
EXEC = '__EXEC__'
INPUTS = '__INPUTS__'
ARGS = '__ARGS__'
MEM = '__MEM__'

# Input ntuples
indir = '../ggNtuples'
#input_campaign = 'Era24Sep2020_v1' # data only ok
#input_campaign = 'Era04Dec2020_v1' # fixed mc diphoton trg
#input_campaign = 'Era04May2021_v1' # Updated 2018 low-mass trgs
input_campaign = 'Era20May2021_v1' # Add mgg95 trgs for data, h4g, hgg

# Era24Sep2020_v1_ggSkim-v1: hoePhoIDloose_mgg100_ptomGG_bdgtm0p99, bad total Nevts, bad dipho h4g,hgg trgs
# Era24Sep2020_v1_ggSkim-v2: hoePhoIDloose_mgg100-180_ptomGG_bdgtm0p99, fixed total Nevts, bad dipho h4g,hgg trgs
# Era24Sep2020_v1_ggSkim-v3: test bad dipho h4g,hgg trgs
# Era04Dec2020_v1_ggSkim-v1: fixed dipho h4g,hgg trgs
# Era24Sep2020_v1_ggSkim-v4: data pi0 skim: trg-npho-presel(hgg hoe)

# Define skim campaign
# ggNtuples-Era24Sep2020v1_ggSkim-v4: data skim, lowmass trgs, wrong 2018 trg
# ggNtuples-Era04Dec2020v1_ggSkim-v1: h4g+hgg skim, lowmass trgs, wrong 2018 trg
# ggNtuples-Era04May2021v1_ggSkim-v1: h4g skim, 2018 only, fixed 2018 trg
# mgg90
# [CANCELLED-wrong 2017 mgg90 trg] ggNtuples-Era04Dec2020v1_ggSkim-v2: h4g+hgg skim, mgg90 trgs
# [CANCELLED-wrong 2017 mgg90 trg] ggNtuples-Era24Sep2020v1_ggSkim-v5: data skim, mgg90 trgs
# mgg95
# ggNtuples-Era20May2021v1_ggSkim-v1: data, h4g, hgg. mgg95 trgs
# ggNtuples-Era20May2021v1_ggSkim-v2: h4g, hgg: do NOT apply HLT dipho trg--applied later using trg SFs instead
this_campaign = '%s-%s'%(indir.split('/')[-1], input_campaign.replace('_',''))
#this_campaign = '%s_%s'%(this_campaign, 'ggSkim-vTEST')
#this_campaign = '%s_%s'%(this_campaign, 'ggSkim-v1')
this_campaign = '%s_%s'%(this_campaign, 'ggSkim-v2')
print('ggSkim campaign:',this_campaign)

exec_file = 'run_skim.sh'
tar_file = 'h2aa.tgz'
#tar_file = 'h2aa-pi0.tgz'
assert os.path.isfile(tar_file), '!! input tar file not found!'

jdl_folder = 'jdls/%s'%this_campaign
if not os.path.isdir(jdl_folder):
    os.makedirs(jdl_folder)
print('jdl folder:',jdl_folder)

inlist = glob.glob('%s/%s/*file_list.txt'%(indir, input_campaign))
assert(len(inlist) >= 1)

cwd = os.getcwd()+'/'

for l in inlist:

    #if 'data' not in l: continue
    #if 'Run2018D' not in l: continue
    #if 'Run2016' in l: continue
    #if 'Run2016' not in l: continue
    #if 'Run2016G' not in l: continue
    #if 'h4g' not in l: continue
    if 'hgg' not in l: continue
    #if 'dy' in l: continue

    sample = l.split('/')[-1].split('_')[0]
    print('For sample:',sample)

    year = re.findall('(201[6-8])', sample.split('-')[0])[0]
    eos_tgtdir = '/store/user/lpchaa4g/mandrews/%s/%s'%(year, this_campaign)
    print('eos tgt:', eos_tgtdir)

    # Read in crabConfig template
    with open('jdls/condor_skim.jdl', "r") as template_file:
        file_data = template_file.read()

    # Replace crabConfig template strings with sample-specific values
    lfile = l.split('/')[-1]
    skip_trg = 'TRUE' if 'h4g' in sample else 'FALSE'
    file_data = file_data.replace(EXEC,   cwd+exec_file)
    file_data = file_data.replace(INPUTS, '%s, %s, %s'%(cwd+exec_file, cwd+tar_file, cwd+l))
    file_data = file_data.replace(ARGS,   '%s %s %s %s'%(lfile, eos_tgtdir, tar_file, skip_trg))
    if 'Run2018D' in l:
        file_data = file_data.replace(MEM, '16000') #25600
    elif ('Run2018A' in l):
        file_data = file_data.replace(MEM, '16000') #12000
    elif ('Run2018' in l):
        file_data = file_data.replace(MEM, '8000') #4800
    elif ('Run2016B' in l) or ('Run2016H' in l):
        file_data = file_data.replace(MEM, '4800')
    else:
        file_data = file_data.replace(MEM, '2800')

    # Write out sample-specific crabConfig
    with open('%s/condor_skim_%s.jdl'%(jdl_folder, sample), "w") as sample_file:
        sample_file.write(file_data)
