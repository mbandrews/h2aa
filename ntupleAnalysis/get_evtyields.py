from __future__ import print_function
import numpy as np
import os, re, glob

year = '2016'
campaign = 'ggNtuples-Era20May2021v1_ggSkim-v1'
#inpath = '/eos/uscms/store/user/lpchaa4g/mandrews/%s/%s/ggSkims/data%s-Run%s*_cut_stats.txt'%(year, campaign, year, year)
inpath = '/eos/uscms/store/user/lpchaa4g/mandrews/%s/%s/ggSkims/h4g%s-mA*_cut_stats.txt'%(year, campaign, year)
infiles = glob.glob(inpath)
'''
data2017-Run2017F0_cut_stats.txt
..       None | Npassed: 37626984 | f_prev: 1.000 | f_total: 1.000
..        trg | Npassed: 11211445 | f_prev: 0.298 | f_total: 0.298
..       npho | Npassed: 10261383 | f_prev: 0.915 | f_total: 0.273
..     presel | Npassed: 1225198 | f_prev: 0.119 | f_total: 0.033
..        mgg | Npassed:  643514 | f_prev: 0.525 | f_total: 0.017
..     ptomGG | Npassed:  486114 | f_prev: 0.755 | f_total: 0.013
..        bdt | Npassed:  483729 | f_prev: 0.995 | f_total: 0.013
'''
nevts = {}
for infile in infiles:
    print('>> file:', infile)
    f = open(infile)
    nevts[infile] = []
    for l in f:
        nevts_ = l.split('|')[1].split(':')[-1].strip()
        if nevts_ != '':
            nevts[infile].append(int(nevts_))
            print(nevts[infile][-1])

ncuts = len(nevts[infile])
print('>> ncuts:',ncuts)
for k in nevts.keys():
    assert len(nevts[k]) == ncuts

nevtstot = np.zeros(ncuts)
print('>> Summing...')
for i in range(ncuts):
    nevtstot_ = 0
    for k in nevts.keys():
        nevtstot_ += nevts[k][i]
    nevtstot[i] = nevtstot_
    print(nevtstot[i])
