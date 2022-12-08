from __future__ import print_function
import glob, os, re
import subprocess

#eosfind = 'eos root://cmseos.fnal.gov find'
#eosfind = '/usr/bin/eos root://cmseos.fnal.gov find'
#eosfind = 'xrdfs root://cmseos.fnal.gov find'
#eosfind = 'xrdfs root://cmseos.fnal.gov ls'
eos_redir = 'root://cmseos.fnal.gov'

def eosls(eos_redir):
    #return 'xrdfs %s ls'%eos_redir
    return 'eos %s ls'%eos_redir

# Recursive version
def eosfind(eos_redir):
    #eosfind = 'eos %s find'%eos_redir
    #eosfind = '/usr/bin/eos %s find'%eos_redir
    #eosfind = 'xrdfs %s find'%eos_redir
    #eosfind = 'xrdfs %s ls'%eos_redir
    #eosfind = 'xrdfs %s ls -R'%eos_redir
    return 'xrdfs %s ls -R'%eos_redir

def eosmkdir(eos_redir):
    return 'xrdfs %s mkdir -p'%eos_redir

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

def replace_eosredir(eosdir, eos_redir):
    if '/eos/uscms' in eosdir:
        return eosdir.replace('/eos/uscms', 'root://cmseos.fnal.gov/')
    elif '/eos/cms' in eosdir:
        return eosdir.replace('/eos/cms', 'root://eoscms.cern.ch/')
    else:
        #return eosdir
        return '%s/%s'%(eos_redir, eosdir)

def run_eosmkdir(eos_tgtdir, eos_redir='root://cmseos.fnal.gov'):

    if eos_redir in eos_tgtdir:
        eos_tgtdir = eos_tgtdir.replace(eos_redir+'/', '')

    cmd = '%s %s'%(eosmkdir(eos_redir), eos_tgtdir)
    #print(cmd)
    _ = subprocess.check_output(cmd, shell=True)

def run_eosls(eos_indir, eos_redir='root://cmseos.fnal.gov'):

    cmd = '%s %s'%(eosls(eos_redir), eos_indir)
    #print(cmd)
    # subprocess.check_output() returns a byte-string => decode into str then split into files
    file_list = subprocess.check_output(cmd, shell=True).decode("utf-8").split('\n')
    file_list = [str(f) for f in file_list]
    #print(file_list)
    # clean up empty elements:
    file_list = list(filter(None, file_list)) # for py2.7: use filter(None, file_list) without list()
    #print(file_list)
    #print(len(file_list))
    #'''

    return file_list

def run_eosfind(eos_basedir, sample, eos_redir='root://cmseos.fnal.gov'):

    cmd = '%s %s'%(eosfind(eos_redir), eos_basedir)
    #print(cmd)
    # subprocess.check_output() returns a byte-string => decode into str then split into files
    file_list = subprocess.check_output(cmd, shell=True).decode("utf-8").split('\n')
    # only keep files for this sample
    #print(len(file_list))
    #for i,f in enumerate(file_list):
    #    print(f, sample in f)
    #    if i > 20: break
    file_list = [f for f in file_list if sample in f]
    #print(sample, len(file_list))
    if 'lpcsusystealth' in eos_basedir:
        file_list = [f for f in file_list if ('JetHT' not in f) and ('ntuplizedOct2019' in f)]
    #'''
    # eosfind returns directories as well, keep only root files from correct sample and add eos redir
    file_list = [f for f in file_list if '.root' in f]
    file_list = [f for f in file_list if 'failed' not in f]
    #file_list = [replace_eosredir(f) for f in file_list]
    file_list = [replace_eosredir(f, eos_redir) for f in file_list]
    # clean up empty elements:
    file_list = list(filter(None, file_list)) # for py2.7: use filter(None, file_list) without list()
    #print(len(file_list))
    #'''

    return file_list

#def get_mantuples(sample, eos_basedir='/store/group/lpchaa4g/mandrews/2017/MAntuples'):
def get_mantuples(sample, eos_redir='root://cmseos.fnal.gov', eos_basedir='/store/group/lpchaa4g/mandrews/2017/MAntuples'):

    cmd = '%s %s/'%(eosfind(eos_redir), eos_basedir) # H4G ntuple same for miniaod or aod IMG ntuple
    print(cmd)
    ma_inputs = subprocess.check_output(cmd, shell=True)
    # subprocess.check_output() returns a byte-string => decode into str then split into files
    ma_inputs = ma_inputs.decode("utf-8").split('\n')
    # eosfind returns directories as well, keep only root files from correct sample and add fnal redir
    ma_inputs = [f for f in ma_inputs if 'mantuple.root' in f]
    ma_inputs = [f for f in ma_inputs if 'ARCHIVE/' not in f]
    #ma_inputs = [f.replace('/eos/uscms','root://cmseos.fnal.gov/') for f in ma_inputs] # eosfind
    ma_inputs = ['root://cmseos.fnal.gov/%s'%f for f in ma_inputs] # xrdfs ls
    ma_inputs = [f for f in ma_inputs if re.search(sample, f) is not None]
    # clean up empty elements:
    ma_inputs = list(filter(None, ma_inputs)) # for py2.7: use filter(None, ma_inputs) without list()
    print(ma_inputs[0])
    print('len(ma_inputs):',len(ma_inputs))
    assert len(ma_inputs) > 0

    #ma_inputs = glob.glob('MAntuples/%s_mantuple.root'%sample)
    #print('len(ma_inputs):',len(ma_inputs))
    #assert len(ma_inputs) > 0

    return ma_inputs

def mkoutdir(s):
    if not os.path.isdir(s):
        os.makedirs(s)
    return s
