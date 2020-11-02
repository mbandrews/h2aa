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
input_campaign = 'Era24Sep2020_v1'

# Define skim campaign
this_campaign = '%s-%s'%(indir.split('/')[-1], input_campaign.replace('_',''))
#this_campaign = '%s_%s'%(this_campaign, 'ggSkim-vTEST')
#this_campaign = '%s_%s'%(this_campaign, 'ggSkim-v1') # hoePhoIDloose_mgg100_ptomGG_bdgtm0p99
this_campaign = '%s_%s'%(this_campaign, 'ggSkim-v2') # hoePhoIDloose_mgg100_ptomGG_bdgtm0p99
print('ggSkim campaign:',this_campaign)

exec_file = 'run_skim.sh'
tar_file = 'h2aa.tgz'

out_folder = 'jdls/%s'%this_campaign
if not os.path.isdir(out_folder):
    os.makedirs(out_folder)

inlist = glob.glob('%s/%s/*file_list.txt'%(indir, input_campaign))
assert(len(inlist) >= 1)

cwd = os.getcwd()+'/'

for l in inlist:

    if 'Run201' not in l: continue

    sample = l.split('/')[-1].split('_')[0]
    print('For sample:',sample)

    year = re.findall('(201[6-8])', sample.split('-')[0])[0]
    eos_tgt = '/store/user/lpchaa4g/mandrews/%s/%s'%(year, this_campaign)
    print('eos tgt:', eos_tgt)

    # Read in crabConfig template
    with open('jdls/condor_skim.jdl', "r") as template_file:
        file_data = template_file.read()

    # Replace crabConfig template strings with sample-specific values
    lfile = l.split('/')[-1]
    file_data = file_data.replace(EXEC,   cwd+exec_file)
    file_data = file_data.replace(INPUTS, '%s, %s, %s'%(cwd+exec_file, cwd+tar_file, cwd+l))
    file_data = file_data.replace(ARGS,   '%s %s'%(lfile, eos_tgt))
    if 'Run2018D' in l:
        file_data = file_data.replace(MEM, '25600')
    elif ('Run2018A' in l):
        file_data = file_data.replace(MEM, '16000') #12000
    elif ('Run2018' in l) or ('Run2016H' in l):
        file_data = file_data.replace(MEM, '8000') #4800
    elif ('Run2016B' in l):
        file_data = file_data.replace(MEM, '4800')
    else:
        file_data = file_data.replace(MEM, '2800')

    # Write out sample-specific crabConfig
    with open('%s/condor_skim_%s.jdl'%(out_folder, sample), "w") as sample_file:
        sample_file.write(file_data)
