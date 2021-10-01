from __future__ import print_function
import os, glob, shutil, re
import numpy as np

# Strings to replace in jdl template
EXEC = '__EXEC__'
INPUTS = '__INPUTS__'
ARGS = '__ARGS__'
MEM = '__MEM__'

# Input ntuples
indir = '../maNtuples'
#input_campaign = 'Era04Dec2020v1' # fixed mc diphoton trg
#input_campaign = 'Era22Jun2021v1' # data, h4g, hgg. mgg95 trgs. gg:ggNtuples-Era20May2021v1_ggSkim-v1 + img:Era22Jun2021_AOD-IMGv1 [EB-only AOD skims]
#input_campaign = 'Era22Jun2021v2' # h4g w/o HLT. gg:ggNtuples-Era20May2021v1_ggSkim-v2 + img:Era22Jun2021_AOD-IMGv2
input_campaign = 'Era22Jun2021v3' # Era22Jun2021v2 + interpolated mass samples
print('>> Input maNtuple campaign:',input_campaign)

# Define sg campaign
#this_campaign = 'sg-Era04Dec2020v1' #2016,2018: no phoid, ma scale+smear
#this_campaign = 'sg-Era04Dec2020v2' # sg selection + bdt/chgiso scans. 2016,2018: no phoid, ma scale+smear
#this_campaign = 'sg-Era04Dec2020v3' # use old (bdt+chgiso cuts) 2017 s+s for all yrs
#this_campaign = 'sg-Era04Dec2020v4' # add 2016+17+18 phoid, 2017+18 ss. 2016 ss missing: use 2017 ss
#this_campaign = 'sg-Era04Dec2020v5' # v4 + nominals use best-fit ss over full m_a, shifted uses best-fit ss over ele peak only.
#this_campaign = 'sg-Era04Dec2020v6' # 2016-18 phoid, 2016-18 ss. ss implemented only for shifted syst (as in v4)
#this_campaign = 'sg-Era04Dec2020v7' #  v6 + nVtx plots
#this_campaign = 'sg-Era22Jun2021v1' # h4g, hgg: redo with mgg95 trgs. [Note:new EB-only AOD skims], HLT applied, no trgSF
#this_campaign = 'sg-Era22Jun2021v2' # h4g w/o HLT applied, with trgSF
#this_campaign = 'sg-Era22Jun2021v3' # sg-Era22Jun2021v2 + interpolated mass samples
this_campaign = 'sg-Era22Jun2021v4' # sg-Era22Jun2021v3 + ss with SFs
print('>> Signal selection campaign:',this_campaign)

# If applying trg SFs, make sure HLT trigger was NOT applied
# trg SFs emulate trg eff already!
#do_trgSF = False # if HLT applied in skim
#do_trgSF = True # if HLT *not* applied in skim
#do_trgSF = False
do_trgSF = True
if this_campaign == 'sg-Era22Jun2021v2' or this_campaign == 'sg-Era22Jun2021v3' or this_campaign == 'sg-Era22Jun2021v4':
    do_trgSF = True

sel = 'nom'
sel = 'inv'
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p05_etalt1p44/nom-inv' # a0nom-a1inv
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p05_etalt1p44/nom-nom' # a0nom-a1nom
#sub_campaign = 'bdtgtm0p99_relChgIsolt0p05_etalt1p44/nom-nom' # bdt > -0.99
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p05_etalt1p44/nom-nom' # bdt > -0.96
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p03_etalt1p44/nom-nom' # relChgIso < 0.03
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p07_etalt1p44/nom-nom' # relChgIso < 0.07
#sub_campaign = 'bdtgtm0p99_relChgIsolt0p03_etalt1p44/nom-nom' # bdt > -0.99, relChgIso < 0.03
sub_campaign = 'bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-%s'%sel # bdt > -0.96, relChgIso < 0.07 !! optimal
#sub_campaign = 'bdtgtm0p97_relChgIsolt0p06_etalt1p44/nom-nom' # bdt > -0.96, relChgIso < 0.07
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p09_etalt1p44/nom-nom' # bdt > -0.96, relChgIso < 0.09
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p08_etalt1p44/nom-nom' # bdt > -0.96, relChgIso < 0.08
print('>> Output sub-campaign:',sub_campaign)

# Define jdl exec, tar, etc
exec_file = 'run_sg.sh'
assert os.path.isfile(exec_file), '!! input exec file not found!'
#tar_file = 'h2aa.tgz'
#tar_file = 'h2aa_%s.tgz'%sub_campaign.split('/')[-1]
#tar_file = 'h2aa_%s_%s.tgz'%(sub_campaign.split('/')[-1], sub_campaign.split('_')[0]) # bdt scan
#tar_file = 'h2aa_%s_%s.tgz'%(sub_campaign.split('/')[-1], sub_campaign.split('_')[1]) # relChgIso scan
tar_file = 'h2aa_%s_%s_%s.tgz'%(sub_campaign.split('/')[-1], sub_campaign.split('_')[0], sub_campaign.split('_')[1]) # bdt,relChgIso scan
print('>> tar file:',tar_file)
assert os.path.isfile(tar_file), '!! input tar file not found!'

# Define xrdcp utils
xrdcp_py = 'xrdcpRecursive.py'
assert os.path.isfile(xrdcp_py), '!! input xrdcpRecursive.py file not found!'
xrdcp_util = 'recursiveFileList.py'
assert os.path.isfile(xrdcp_util), '!! input recursiveFileList.py file not found!'

# Defin work dirs
cwd = os.getcwd()+'/'
analysis_dir = '%s../ntupleAnalysis'%cwd
#jdl_folder = 'jdls/%s'%this_campaign
jdl_folder = 'jdls/%s/%s'%(this_campaign, sub_campaign)
if not os.path.isdir(jdl_folder):
    os.makedirs(jdl_folder)
print('>> jdl folder:',jdl_folder)

# Define h4g+hgg input samples
inlist = glob.glob('%s/%s/*file_list.txt'%(indir, input_campaign))
inlist = [l for l in inlist if ('h4g' in l) or ('hgg' in l)]
assert(len(inlist) >= 1)

for l in inlist:

    sample = l.split('/')[-1].split('_')[0]
    year = re.findall('(201[6-8])', sample.split('-')[0])[0]
    print('>> For sample:',sample)

    #if 'hgg' not in sample: continue

    # Output EOS tgt
    #eos_tgtdir = '/store/user/lpchaa4g/mandrews/%s/%s'%(year, this_campaign)
    eos_tgtdir = '/store/user/lpchaa4g/mandrews/%s/%s/%s'%(year, this_campaign, sub_campaign)
    print('   .. eos tgt:', eos_tgtdir)

    # Get input PU data ref
    pu_data = '%s/PU/dataPU_%s.root'%(analysis_dir, year)
    print('   .. PU reference:', pu_data)
    assert os.path.isfile(pu_data), '!! PU data ref file not found!'

    # Get input pho id syst file
    #syst_file = '%s/SF/SF%s_egammaEffi.txt_EGM2D.root'%(analysis_dir, year) if year == '2017' else None
    syst_file = '%s/SF/SF%s_egammaEffi.txt_EGM2D.root'%(analysis_dir, year)
    print('   .. Photon ID syst reference:', syst_file)
    if syst_file is not None:
            assert os.path.isfile(syst_file), '!! Photon ID syst file not found: %s'%syst_file

    # Define jdl inputs
    #jdl_inputs = '%s, %s, %s, %s'%(cwd+exec_file, cwd+tar_file, cwd+l, pu_data)
    jdl_inputs = '%s, %s, %s, %s, %s, %s'%(cwd+exec_file, cwd+tar_file, cwd+l, cwd+xrdcp_py, cwd+xrdcp_util, pu_data)
    if syst_file is not None:
        jdl_inputs += ', %s'%(syst_file)
    print(jdl_inputs)

    # Define jdl args
    jdl_args = '%s %s %s %s'%(sample, l.split('/')[-1], pu_data.split('/')[-1], eos_tgtdir)
    jdl_args += ' %s'%(syst_file.split('/')[-1] if syst_file is not None else 'NONE')
    jdl_args += ' %s'%(tar_file)
    jdl_args += ' %s'%('TRUE' if do_trgSF else 'FALSE')
    #print(jdl_args)

    # Read in crabConfig template
    with open('jdls/condor_runsg.jdl', "r") as template_file:
        file_data = template_file.read()

    # Replace crabConfig template strings with sample-specific values
    file_data = file_data.replace(EXEC,   cwd+exec_file)
    file_data = file_data.replace(INPUTS, jdl_inputs)
    file_data = file_data.replace(ARGS,   jdl_args)
    file_data = file_data.replace(MEM, '2800')

    # Write out sample-specific crabConfig
    with open('%s/condor_runsg_%s.jdl'%(jdl_folder, sample), "w") as sample_file:
        sample_file.write(file_data)
