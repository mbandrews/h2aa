import os
import subprocess

def get_ma_tree_name(sample):
    if 'Run2017' in sample:
        tree_name = 'Data'
    elif 'h24gamma_1j_1M' in sample:
        tree_name = 'h24g_ma%s'%sample.split('_')[-1]
    else:
        if 'GluGluH' in sample:
            tree_name = '%s_M125'%sample
        else:
            tree_name = '%s_MGG80'%sample
    return tree_name.replace('-','_')

def run_process(process):
    os.system('python %s'%process)


def replace_eosredir(eosdir):
    if '/eos/uscms' in eosdir:
        return eosdir.replace('/eos/uscms', 'root://cmseos.fnal.gov/')
    elif '/eos/cms' in eosdir:
        return eosdir.replace('/eos/cms', 'root://eoscms.cern.ch/')
    else:
        return eosdir

def run_eosfind(eos_basedir, sample, eos_redir='root://cmseos.fnal.gov'):

    eosfind = 'eos %s find'%eos_redir

    cmd = '%s %s'%(eosfind, eos_basedir)
    #print(cmd)
    # subprocess.check_output() returns a byte-string => decode into str then split into files
    file_list = subprocess.check_output(cmd, shell=True).decode("utf-8").split('\n')
    # only keep files for this sample
    file_list = [f for f in file_list if sample in f]
    # eosfind returns directories as well, keep only root files from correct sample and add eos redir
    file_list = [f for f in file_list if '.root' in f]
    file_list = [replace_eosredir(f) for f in file_list]
    # clean up empty elements:
    file_list = list(filter(None, file_list)) # for py2.7: use filter(None, file_list) without list()
    #print(len(file_list))

    return file_list
