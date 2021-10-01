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
#input_campaign = 'Era09Feb2021-Zeev1' # gg:ggNtuples-Era24Sep2020v1_ggSkimZee-v3 + img:Era06Sep2020_AOD-IMGZeev4, model:Models/resnet/precise300/model_epoch90_val_mae0.1889.json
#input_campaign = 'Era16Feb2021-Zeev1' # gg:ggNtuples-Era24Sep2020v1_ggSkimZee-v3 + img:Era16Feb2021_AOD-IMGZeev1, model:Models/resnet/precise300/model_epoch90_val_mae0.1889.json
input_campaign = 'Era16Feb2021-Zeev2' # gg:ggNtuples-Era24Sep2020v1_ggSkimZee-v3 + img:Era16Feb2021_AOD-IMGZeev1, model:Models/model_epoch80_mae0.1906.pkl
print('>> Input campaign: maNtuples-%s'%input_campaign)

# Output bkg campaign
#this_campaign = 'bkgNoPtWgts-Era04Dec2020v1' # rename of Era11Dec2020v1
#this_campaign = 'ZeeSel-Era09Feb2021v1' # dy+data zee skim(nele+presel)
#this_campaign = 'ZeeSel-Era16Feb2021-Zeev1' # zee(nele+presel[hoEPhoIDLoose]+tnp+mee[81-101GeV]+ptomee). For massreg paper only (no chgiso+bdt). model:Models/resnet/precise300/model_epoch90_val_mae0.1889.json
#this_campaign = 'ZeeSel-Era16Feb2021-Zeev2' # zee(nele+presel[hoEPhoIDLoose]+tnp+mee[81-101GeV]+ptomee+bdt+chgiso). For h4g analysis: Zee data v mc. model:Models/model_epoch80_mae0.1906.pkl
this_campaign = 'ZeeSel-Era16Feb2021-Zeev3' # ZeeSel-Era16Feb2021-Zeev2 + r9 for trg SFs: zee(nele+presel[hoEPhoIDLoose]+tnp+mee[81-101GeV]+ptomee+bdt+chgiso). For h4g analysis: Zee data v mc. model:Models/model_epoch80_mae0.1906.pkl
#this_campaign = 'ZeeSel-Era16Feb2021-Zeev4' # ZeeSel-Era16Feb2021-Zeev3 except hgg preselection. For hgg vs h4g trg SF comparison.
print('>> Output campaign:',this_campaign)

exec_file = 'run_sel-zee.sh'
assert os.path.isfile(exec_file), '!! input exec file not found!'

tar_file = 'h2aa-zee.tgz'
if input_campaign == 'Era16Feb2021-Zeev2':
    tar_file = 'h2aa-zee_bdtgtm0p96_relChgIsolt0p07.tgz'
if this_campaign == 'ZeeSel-Era16Feb2021-Zeev4':
    tar_file = 'h2aa-zee_hgg.tgz'
print('>> tar file:',tar_file)
assert os.path.isfile(tar_file), '!! input tar file not found!'

cwd = os.getcwd()+'/'
jdl_folder = 'jdls/%s'%this_campaign
if not os.path.isdir(jdl_folder):
    os.makedirs(jdl_folder)
print('>> jdl folder:',jdl_folder)

# Define xrdcp utils
xrdcp_py = 'xrdcpRecursive.py'
assert os.path.isfile(xrdcp_py), '!! input xrdcpRecursive.py file not found!'
xrdcp_util = 'recursiveFileList.py'
assert os.path.isfile(xrdcp_util), '!! input recursiveFileList.py file not found!'

inlist = glob.glob('%s/%s/*file_list.txt'%(cwd+indir, input_campaign))
assert(len(inlist) >= 1)

for l in inlist:

    #if 'Run2018D' not in l: continue
    #if 'h4g' not in l: continue
    #if 'hgg' not in l: continue
    #if 'dy' not in l: continue
    #if '2016' not in l: continue
    if '2016' in l: continue

    sample = l.split('/')[-1].split('_')[0]
    print('>> For sample:',sample)

    # ntuple IO
    year = re.findall('(201[6-8])', sample.split('-')[0])[0]
    eos_tgtdir = '/store/user/lpchaa4g/mandrews/%s/%s'%(year, this_campaign)
    print('   .. eos tgtdir:', eos_tgtdir)

    # PU info for data
    # passed for MC as well but will not be used by evt selection
    #pu_json = cwd+'../json/Collisions17_13TeV_PileUp_pileup_latest.txt' # TODO: change for each yr
    pu_json = cwd+'../json/Collisions%s_13TeV_PileUp_pileup_latest.txt'%year[-2:]
    assert os.path.isfile(pu_json), '!! input pu json file not found!'

    # Read in condor config template
    with open('jdls/condor_runbkg.jdl', "r") as template_file:
        file_data = template_file.read()

    # Replace condor config template strings with sample-specific values
    file_data = file_data.replace(EXEC,   cwd+exec_file)
    file_data = file_data.replace(INPUTS, '%s, %s, %s, %s, %s, %s'%(cwd+exec_file, cwd+tar_file, l, pu_json, cwd+xrdcp_py, cwd+xrdcp_util))
    file_data = file_data.replace(ARGS,   '%s %s %s %s %s'
                                           %(sample, l.split('/')[-1], eos_tgtdir, tar_file, pu_json.split('/')[-1]))
    file_data = file_data.replace(MEM, '4800')

    # Write out sample-specific condor config
    with open('%s/condor_runsel-zee_%s.jdl'%(jdl_folder, sample), "w") as sample_file:
        sample_file.write(file_data)
