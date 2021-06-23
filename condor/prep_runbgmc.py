from __future__ import print_function
import os, glob, shutil, re
import numpy as np

# Strings to replace in jdl template
EXEC = '__EXEC__'
INPUTS = '__INPUTS__'
ARGS = '__ARGS__'
MEM = '__MEM__'

# Input ntuple list
indir = '../ggNtuples'
input_campaign = 'Era06Sep2020_v1' # bkg mc ggntuples (i.e. no ma). NOTE: hgg list copied from Era04Dec2020_v1.
print('>> Input maNtuple campaign:',input_campaign)

# Define bg campaign
this_campaign = 'bgmc-Era06Dec2020v1' # miniaod bkg mc, ggntuples only (i.e. no ma)
print('>> Bkg selection campaign:',this_campaign)

#sel = 'nom'
sel = 'inv'
sub_campaign = 'bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-%s'%sel # bdt > -0.96, relChgIso < 0.07 !! optimal
print('>> Output sub-campaign:',sub_campaign)

# Define jdl exec, tar, etc
exec_file = 'run_bgmc.sh'
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
inlist = [l for l in inlist if 'bg' in l]
assert(len(inlist) >= 1)

# pt wgts (for SB re-weighting only)
eos_redir = 'root://cmseos.fnal.gov'
# Input pt wgts campaign
ptwgts_campaign = 'bkgNoPtWgts-Era04Dec2020v2' # 2016H+2018 failed lumis
print('>> Input pt wgts campaign: %s'%ptwgts_campaign)
ptwgts_indir = '/store/group/lpchaa4g/mandrews/Run2/%s/%s/Weights'%(ptwgts_campaign, sub_campaign)
print('   .. pt wgts indir:', ptwgts_indir)

mhregions = ['sblo', 'sr', 'sbhi']

for l in inlist:

    sample = l.split('/')[-1].split('_')[0]
    year = re.findall('(201[6-8])', sample.split('-')[0])[0]

    #if 'hgg' not in sample: continue

    print('>> For sample:',sample)

    # Output EOS tgt
    #eos_tgtdir = '/store/user/lpchaa4g/mandrews/%s/%s'%(year, this_campaign)
    eos_tgtdir = '/store/user/lpchaa4g/mandrews/%s/%s/%s'%(year, this_campaign, sub_campaign)
    print('   .. eos tgt:', eos_tgtdir)

    # Get input PU data ref
    #pu_data = '%s/PU/dataPU_%s.root'%(analysis_dir, year)
    pu_data = None
    print('   .. PU reference:', pu_data)
    if pu_data is not None:
        assert os.path.isfile(pu_data), '!! PU data ref file not found!'

    # Get input pho id syst file
    #syst_file = '%s/SF/SF%s_egammaEffi.txt_EGM2D.root'%(analysis_dir, year) if year == '2017' else None
    #syst_file = '%s/SF/SF%s_egammaEffi.txt_EGM2D.root'%(analysis_dir, year)
    syst_file = None
    print('   .. Photon ID syst reference:', syst_file)
    if syst_file is not None:
            assert os.path.isfile(syst_file), '!! Photon ID syst file not found: %s'%syst_file

    # Define jdl inputs
    #jdl_inputs = '%s, %s, %s, %s, %s, %s'%(cwd+exec_file, cwd+tar_file, cwd+l, cwd+xrdcp_py, cwd+xrdcp_util, pu_data)
    jdl_inputs = '%s, %s, %s, %s, %s'%(cwd+exec_file, cwd+tar_file, cwd+l, cwd+xrdcp_py, cwd+xrdcp_util)
    if pu_data is not None:
        jdl_inputs += ', %s'%(pu_data)
    if syst_file is not None:
        jdl_inputs += ', %s'%(syst_file)
    print(jdl_inputs)

    #################################
    # Split by mH-region
    for region in mhregions:

        print('   >> For mH-region:',region)

        # Do baseline without pt re-weighting first
        ptwgts_file = 'NONE'
        outdir = 'Templates'

        # Define jdl args
        jdl_args_ = '%s %s %s %s'%(sample, l.split('/')[-1], pu_data.split('/')[-1] if pu_data is not None else 'NONE', eos_tgtdir)
        jdl_args_ += ' %s'%(syst_file.split('/')[-1] if syst_file is not None else 'NONE')
        jdl_args_ += ' %s'%(tar_file)
        jdl_args_ += ' %s'%(region)
        jdl_args = '%s %s %s'%(jdl_args_, outdir, ptwgts_file)
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
        with open('%s/condor_runbgmc_%s_mh%s.jdl'%(jdl_folder, sample, region), "w") as sample_file:
            sample_file.write(file_data)

        #################################
        # Apply pt re-weighting
        # Re-weighting is only for sb->sr
        if 'sb' not in region: continue

        # Get f_SBlow scenarios and pt wgt files
        # Each scenario will use different pt wgts
        #flos = [None]
        flo_files = glob.glob('/eos/uscms/%s/*ptwgts.root'%ptwgts_indir)
        assert len(flo_files) >= 1
        # flo_dict: key: f_SBlow, value: LFN filepath to pt wgts file
        # e.g. flo_dict['0.6413'] = /store/.../..flo0.6413_ptwgts.root
        flo_dict = {flo.split('_')[-2].strip('flo'):flo.replace('/eos/uscms/','') for flo in flo_files}
        print('      .. found %d f_SBlow scenarios: %s'%(len(flo_dict), ' '.join(flo_dict.keys())))

        for flo in flo_dict:

            print('         >> For f_SBlow: %s'%flo)

            outdir = 'Templates_flo%s'%flo
            ptwgts_file = '%s/%s'%(eos_redir, flo_dict[flo])
            print('         .. using pt wgts: %s'%ptwgts_file)

            # Define jdl args
            jdl_args = '%s %s %s'%(jdl_args_, outdir, ptwgts_file)
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
            with open('%s/condor_runbgmc_%s_mh%s_flo%s.jdl'%(jdl_folder, sample, region, flo), "w") as sample_file:
                sample_file.write(file_data)

