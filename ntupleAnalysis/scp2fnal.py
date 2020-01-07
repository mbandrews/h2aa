import os
import glob as glob
import subprocess

input_dirs = [
        #'DoubleEG_Run2017-slimv2',
        #'h24g_bkgMC2017v2',
        'h24gamma_01Nov2019-rhECAL_v6-exo'
        ]

tgt_eos = '/store/user/lpcml/mandrews/2017'
tgt_campaign = 'Era2017_18Nov2019_H4Gv2'

fnaleos = 'root://cmseos.fnal.gov'
eosls = 'eos %s ls'%(fnaleos)
eosmkdir = 'eos %s mkdir -p'%(fnaleos)

FNULL = open(os.devnull, 'w')
retcode = subprocess.call(['echo', 'foo'], stdout=FNULL, stderr=subprocess.STDOUT)

def create_eosdir(tgt_dir):

    # Check if EOS dir exists
    cmd = '%s %s'%(eosls, tgt_dir)
    ret = subprocess.call(cmd, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

    # Create dir if not
    if ret != 0:
        print('Creating dir: %s'%tgt_dir)
        cmd = '%s %s'%(eosmkdir, tgt_dir)
        ret = subprocess.call(cmd, shell=True)

    # Double-check dir exists
    cmd = '%s %s'%(eosls, tgt_dir)
    ret = subprocess.call(cmd, shell=True, stdout=FNULL)
    assert ret == 0

for d in input_dirs:

    print('For H4G ntuples in %s:'%d)

    tgt_dir = '%s/%s/%s'%(tgt_eos, tgt_campaign, d)
    create_eosdir(tgt_dir)

    h4g_inputs = glob.glob('%s/output*root'%d)
    assert len(h4g_inputs) > 0
    print('N input files: %d'%len(h4g_inputs))

    for f in h4g_inputs:
        #cmd = 'xrdcp %s %s/%s/'%(f, fnaleos, tgt_dir)
        cmd = 'xrdcopy -f %s %s/%s/'%(f, fnaleos, tgt_dir) #xrdcp does not support force overwrite that `xrdcopy -f` does
        ret = subprocess.call(cmd, shell=True)
        if ret != 0:
            raise Exception('File %s failed to copy'%f)

    # Do an ls of tgt_dir to make sure all files were copied
    cmd = '%s %s/'%(eosls, tgt_dir)
    h4g_outputs = subprocess.check_output(cmd, shell=True).decode("utf-8").split('\n')
    h4g_outputs = [f for f in h4g_outputs if '.root' in f]
    print('N copied files: %d'%len(h4g_outputs))
    assert len(h4g_inputs) == len(h4g_outputs)
