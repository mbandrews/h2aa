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
#input_campaign = 'Era24Sep2020_v1'
input_campaign = 'Era09Mar2021_v1' # DYToEE mc only

# Era24Sep2020_v1_ggSkimZee-v1 #dy only
# Era24Sep2020_v1_ggSkimZee-v2 #data only
# Era24Sep2020_v1_ggSkimZee-v3 #dy+data skim:nele+presel
# Era09Mar2021_v1_ggSkimZee-v1 #DYToEE mc, skim:nele+presel

# Define skim campaign
this_campaign = '%s-%s'%(indir.split('/')[-1], input_campaign.replace('_',''))
#this_campaign = '%s_%s'%(this_campaign, 'ggSkimZee-vTEST')
this_campaign = '%s_%s'%(this_campaign, 'ggSkimZee-v1')
#this_campaign = '%s_%s'%(this_campaign, 'ggSkimZee-v2')
#this_campaign = '%s_%s'%(this_campaign, 'ggSkimZee-v3')
print('ggSkim campaign:',this_campaign)

exec_file = 'run_skim-zee.sh'
tar_file = 'h2aa-zee.tgz'
assert os.path.isfile(tar_file), '!! input tar file not found!'

jdl_folder = 'jdls/%s'%this_campaign
if not os.path.isdir(jdl_folder):
    os.makedirs(jdl_folder)
print('jdl folder:',jdl_folder)

inlist = glob.glob('%s/%s/*file_list.txt'%(indir, input_campaign))
assert(len(inlist) >= 1)

cwd = os.getcwd()+'/'

for l in inlist:

    if 'dy' not in l: continue
    #if 'data' not in l: continue
    #if 'data' not in l and 'dy' not in l: continue

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
    file_data = file_data.replace(EXEC,   cwd+exec_file)
    file_data = file_data.replace(INPUTS, '%s, %s, %s'%(cwd+exec_file, cwd+tar_file, cwd+l))
    file_data = file_data.replace(ARGS,   '%s %s %s'%(lfile, eos_tgtdir, tar_file))
    #file_data = file_data.replace(MEM,    '6400')
    if 'Run2018D' in l:
        file_data = file_data.replace(MEM, '16000') #25600
    elif ('Run2018A' in l):
        file_data = file_data.replace(MEM, '16000') #12000
    elif ('Run2018' in l):
        file_data = file_data.replace(MEM, '8000') #4800
    #elif ('Run2016B' in l) or ('Run2016H' in l):
    #    file_data = file_data.replace(MEM, '4800')
    else:
        #file_data = file_data.replace(MEM, '2800')
        file_data = file_data.replace(MEM,    '6400')

    # Write out sample-specific crabConfig
    with open('%s/condor_skim_%s.jdl'%(jdl_folder, sample), "w") as sample_file:
        sample_file.write(file_data)
