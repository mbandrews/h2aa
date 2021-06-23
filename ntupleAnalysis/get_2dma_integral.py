from __future__ import print_function
#import numpy as np
import ROOT
import os, glob, re
#from root_numpy import hist2array
from data_utils import *
from hist_utils import *

'''
Calculate integral over 2d-ma plane
'''
eos_basedir = 'root://cmseos.fnal.gov//store/user/lpchaa4g/mandrews'

#sample = 'Run2017'
#campaign = 'Run2/runBkg_noptwgts_bdtgtm0p99-v1'
#in_campaign = 'bkgNoPtWgts-Era04Dec2020v1' # missing 2018A, 2016H+2018 failed lumis
in_campaign = 'bkgNoPtWgts-Era04Dec2020v2' # 2016H+2018 failed lumis still
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p05_etalt1p44' # nominal
#sub_campaign = 'bdtgtm0p99_relChgIsolt0p05_etalt1p44' # bdt > -0.99
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p05_etalt1p44' # bdt > -0.96
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p03_etalt1p44' # relChgIso < 0.03
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p07_etalt1p44' # relChgIso < 0.07
#sub_campaign = 'bdtgtm0p99_relChgIsolt0p03_etalt1p44' # bdt > -0.99, relChgIso < 0.03
sub_campaign = 'bdtgtm0p96_relChgIsolt0p07_etalt1p44' # bdt > -0.96, relChgIso < 0.07 !! optimal
#sub_campaign = 'bdtgtm0p97_relChgIsolt0p06_etalt1p44' # bdt > -0.96, relChgIso < 0.07
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p09_etalt1p44' # bdt > -0.96, relChgIso < 0.09
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p08_etalt1p44' # bdt > -0.96, relChgIso < 0.08
sel = 'nom'
#sel = 'inv'

norm_scale = 150.e3
#distn = 'pt0vpt1'
distn = 'ma0vma1'
ma_blind = None
mh_regions = ['sblo', 'sr', 'sbhi']

runs = ['Run2'] # use full run2 stats
for r in runs:

    print('>> Doing run:',r)

    sample = 'data' if r == 'Run2' else 'data%s'%r
    campaign = '%s/%s/%s/nom-%s'%(r, in_campaign, sub_campaign, sel)

    indir = '%s/%s/Templates'%(eos_basedir, campaign)
    #outdir = '%s/%s/Weights'%(eos_basedir, campaign)
    #run_eosmkdir(outdir)

    h, hf = {}, {}

    s = sample
    k = distn
    tgt = 'sr'

    load_hists(h, hf, [sample], mh_regions, [distn], ma_blind, input_dir=indir)

    ilo = h['%s_sblo_%s'%(s, k)].GetXaxis().FindBin(0.)
    ihi = h['%s_sblo_%s'%(s, k)].GetXaxis().FindBin(1.2)

    print('Nsblo:%f, Nsbhi:%f, Nsr:%f'%(\
            h['%s_sblo_%s'%(s, k)].Integral(ilo, ihi, ilo, ihi),\
            h['%s_sbhi_%s'%(s, k)].Integral(ilo, ihi, ilo, ihi),\
            h['%s_%s_%s'%(s, tgt, k)].Integral(ilo, ihi, ilo, ihi)))

    print('Ntotal: %f'%(h['%s_sblo_%s'%(s, k)].Integral(ilo, ihi, ilo, ihi)\
            + h['%s_sbhi_%s'%(s, k)].Integral(ilo, ihi, ilo, ihi)\
            + h['%s_%s_%s'%(s, tgt, k)].Integral(ilo, ihi, ilo, ihi)))
