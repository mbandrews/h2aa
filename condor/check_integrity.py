from __future__ import print_function
import os, re, glob

campaign = 'ggNtuples-Era24Sep2020v1_ggSkim-v2'

job_files = glob.glob('jdls/%s/job*.stdout'%campaign)
job_files.sort()
print('N job files:', len(job_files))

is_complete = True

for job in job_files:
    f = open(job).readlines()
    for l in f:
        if 'Sample name:' in l:
            sample = l.strip('\n')
            print(job, sample)
        if '!!! WARNING !!!' in l:
            print(l.strip('\n'))
            is_complete = False
