from __future__ import print_function
import os, glob, shutil
import numpy as np
from data_utils import *
from get_bkg_norm import *

eras = ['Run2017']

do_pt_reweight = True
do_ptomGG = True # `do_ptomGG` swtich applies to SB only, SR always has this True

#for flo_ in [None, 0.504, 0.791]:
#for flo_ in [0.791]:
for flo_ in [None]:

    sample = 'Run2017'
    output_dir = 'Templates_tmp'

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    ma_inputs = get_mantuples(sample)
    print(ma_inputs)
    #s = 'Run2017B-F'
    # r = ['sblo', 'sbhi', 'sr']
    bkg_process(sample=sample,
                mh_region='sblo',
                ma_blind=None,
                ma_inputs=ma_inputs,
                output_dir=output_dir,
                do_ptomGG=True, #do_ptomGG if 'sb' in r else True,
                write_pts=True)



