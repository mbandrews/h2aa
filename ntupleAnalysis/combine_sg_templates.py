from __future__ import print_function
#import numpy as np
import ROOT
import os, glob, re
from collections import OrderedDict
from data_utils import *
from hist_utils import *
from template_utils import *

k2dma = 'ma0vma1'
sample_sg = 'h4g'
mh_region = 'sr'
#ma_blinds = ['diag_lo_hi', 'offdiag_lo_hi']
ma_blind = 'offdiag_lo_hi'
#ma_blind = 'diag_lo_hi' # for making unblinded plots in plot_2dma.py: both offdiag+diag blinding needed
#ma_blind = None
distns = ['%s-%s'%(k2dma, ma_blind)]
#distn = '%s'%(k2dma)
print('>> Running script to combine bkg templates...')

sel = 'nom'
#sel = 'inv'
run2dir = 'Run2'
#campaign = 'bkgPtWgts-Era04Dec2020v2/bdtgtm0p98_relChgIsolt0p05_etalt1p44/nom-%s'%sel
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p05_etalt1p44/nom-%s'%sel # nominal
#sub_campaign = 'bdtgtm0p99_relChgIsolt0p05_etalt1p44/nom-%s'%sel # bdt > -0.99
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p05_etalt1p44/nom-%s'%sel # bdt > -0.96
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p03_etalt1p44/nom-%s'%sel # relChgIso < 0.03
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p07_etalt1p44/nom-%s'%sel # relChgIso < 0.07
#sub_campaign = 'bdtgtm0p99_relChgIsolt0p03_etalt1p44/nom-%s'%sel # bdt > -0.99, relChgIso < 0.03
sub_campaign = 'bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-%s'%sel # bdt > -0.96, relChgIso < 0.07 !! optimal
#sub_campaign = 'bdtgtm0p97_relChgIsolt0p06_etalt1p44/nom-%s'%sel # bdt > -0.97, relChgIso < 0.06
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p09_etalt1p44/nom-%s'%sel # bdt > -0.96, relChgIso < 0.09
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p08_etalt1p44/nom-%s'%sel # bdt > -0.96, relChgIso < 0.08
#campaign = 'sg-Era04Dec2020v2/%s'%sub_campaign # sg selection + bdt/chgiso scans. 2016,2018: no phoid, ma scale+smear
#campaign = 'sg-Era04Dec2020v3/%s'%sub_campaign # use old (bdt+chgiso cuts) 2017 s+s for all yrs
#campaign = 'sg-Era04Dec2020v3/%s'%sub_campaign # use old (bdt+chgiso cuts) 2017 s+s for all yrs
#campaign = 'sg-Era04Dec2020v4/%s'%sub_campaign # 2016-18 SFs. 2017-18 ss. 2016 ss uses 2017.
#campaign = 'sg-Era04Dec2020v5/%s'%sub_campaign # v4 + nominals use best-fit ss over full m_a, shifted uses best-fit ss over ele peak only.
#campaign = 'sg-Era04Dec2020v6/%s'%sub_campaign # 2016-18 phoid, 2016-18 ss. ss implemented only for shifted syst (as in v4)
#campaign = 'sg-Era22Jun2021v2/%s'%sub_campaign # h4g, hgg: w/o HLT applied, with trgSF. gg:ggNtuples-Era20May2021v1_ggSkim-v2 + img:Era22Jun2021_AOD-IMGv2
#campaign = 'sg-Era22Jun2021v3/%s'%sub_campaign # v2 + interpolated masses
#campaign = 'sg-Era22Jun2021v4/%s'%sub_campaign # duplicate of v3 + ss with SFs + (xs_sg = 0.05pb for by era but xs_sg = 1pb for run2 for making plots)
#campaign = 'sg-Era22Jun2021v5/%s'%sub_campaign # duplicate of v3 + ss with SFs + (xs_sg = 0.05104pb for by era but xs_sg = 1pb for run2 for making plots)
campaign = 'sg-Era22Jun2021v6/%s'%sub_campaign # v5 but with 50MeV
print('.. input campaign: %s'%campaign)

# Define ggnutple campaign for mc normalization
#ggntuple_campaign = 'Era04Dec2020v1_ggSkim-v1' # fixed h4g mc triggers

eos_basedir = '/store/user/lpchaa4g/mandrews'
outdir = '%s/%s/%s/%s/Templates'%(eos_redir, eos_basedir, run2dir, campaign)
print('.. output dir: %s\n'%outdir)
run_eosmkdir(outdir)

def get_unique_key(k):
    #ksplit = k.split('_')
    ksplit = k.split('-')
    ksplit = ksplit[1:] # remove preceding `data<run>_` string
    #kjoin = '_'.join(ksplit)
    kjoin = '-'.join(ksplit)
    return kjoin

def get_run_key(k, r, sample=sample_sg):
    #krun = '%s%s_%s'%(sample, r, k)
    krun = '%s%s-%s'%(sample, r, k)
    return krun

#--------------
# Read in hists
#--------------
h = OrderedDict()
hf = OrderedDict()
runs = ['2016', '2017', '2018']
#xs_sg = 1. #pb
# DEPRECATED: implemented in mk_sg_templates.py
#tgt_lumis = {'2016': (2./3.)*41.9e3,
#             '2017': 41.9e3,
#             '2018': (4./3.)*41.9e3} # /pb

# Loop over run eras
for r in runs:

    print('>> Reading hists for run:', r)

    #if r != '2016': continue
    #if r != '2017': continue
    #if r != '2018': continue

    eos_basedir = '/store/user/lpchaa4g/mandrews'
    indir = '%s/%s/%s/%s/Templates'%(eos_redir, eos_basedir, r, campaign)
    print('.. input dir:', indir)

    # Get list of syst files for this run era.
    indirs = indir.replace(eos_redir, '/eos/uscms') + '/syst*'
    #print('.. inpath: %s'%indirs)
    syst_paths = glob.glob(indirs)
    #print('.. syst files.',syst_paths)
    print('.. found %d syst files.'%(len(syst_paths)))
    systs = [s.split('/')[-1].replace('.root','') for s in syst_paths]

    h[r] = OrderedDict()
    hf[r] = OrderedDict()

    # Loop over systs file
    for i,syst in enumerate(systs):

        print('.. Reading syst:', syst)

        h[r][syst] = OrderedDict()
        hf[r][syst] = OrderedDict()

        sample_path = '%s/%s%s-*_blind_%s_templates.root'%(syst_paths[i], sample_sg, r, ma_blind)
        #print(sample_path)
        sample_files = glob.glob(sample_path)
        #print(sample_files)
        samples = [s.split('/')[-1].split('_')[0] for s in sample_files]
        #print(samples)

        # Loop over sg samples
        for j,sample in enumerate(samples):

            print('   .. Reading sample:', sample)

            # Read in hists/templates for each run and syst
            #print(' sample_file:',sample_files[j].replace('/eos/uscms', eos_redir))
            load_hists_in_file(h[r][syst], hf[r][syst], [sample], [mh_region], distns, sample_files[j].replace('/eos/uscms', eos_redir))

#----------------------
# Do consistency checks
#----------------------
print('\n>> Doing hist consistency checks...')
print(h.keys()) # lists runs
print(h[r].keys()) # lists systs
print(h[r][syst].keys()) # lists hists

# Check that systs are identical across runs
ksysts = []
for i in runs:
    #syst_keys_i = [get_unique_key(ki) for ki in h[i].keys()]
    syst_keys_i = [ki for ki in h[i].keys()]
    print(i, syst_keys_i)
    for j in runs:
        if i == j: continue
        #syst_keys_j = [get_unique_key(kj) for kj in h[j].keys()]
        syst_keys_j = [kj for kj in h[j].keys()]
        # Syst pairing
        #assert syst_keys_i == syst_keys_j,\
        #       '!! systs do not match for run %d vs %d: %s vs %s'%(i, j, ','.join(syst_keys_i), ','.join(syst_keys_j))
        print(j, syst_keys_j)
        ksysts_ = [s for s in syst_keys_i if s in syst_keys_j]
        for s_ in ksysts_:
            if s_ not in ksysts:
                ksysts.append(s_)
    break # only need to do first loop once to exhaust all pairings

# Store systs
#ksysts = syst_keys_i
print('.. ksysts:', ksysts)

# Check that hist keys are identical
# First, check hist keys within run, across systs
hist_keys_run = OrderedDict()
for r in runs:

    # Hist keys within run, across systs
    for a in ksysts:
        #hist_keys_a = [get_unique_key(ka) for ka in h[r][get_run_key(a,r)].keys()]
        hist_keys_a = [get_unique_key(ka) for ka in h[r][syst].keys()]
        #print(a, hist_keys_a)
        for b in ksysts:
            if a == b: continue
            #hist_keys_b = [get_unique_key(kb) for kb in h[r][get_run_key(b,r)].keys()]
            hist_keys_b = [get_unique_key(kb) for kb in h[r][syst].keys()]
            #print(b, hist_keys_b)
            assert hist_keys_a == hist_keys_b,\
                   '!! hists do not match for syst %s vs %s: %s vs %s'%(a, b, ','.join(hist_keys_a), ','.join(hist_keys_b))
        break # only need to do first loop once to exhaust all pairings

    # Store uniqe keys
    hist_keys_run[r] = hist_keys_a

# Then, check unique hist keys across runs
for i in runs:
    #print(i, hist_keys_run[i])
    for j in runs:
        if i == j: continue
        assert hist_keys_run[i] == hist_keys_run[j]
        #print(j, hist_keys_run[j])
        assert hist_keys_run[i] == hist_keys_run[j],\
               '!! hists do not match for run %d vs %d: %s vs %s'%(i, j, ','.join(hist_keys_run[i]), ','.join(hist_keys_run[i]))
    break # only need to do first loop once to exhaust all pairings

# Store systs
khists = hist_keys_run[runs[0]]
print('.. khists:', khists)

#----------------------
# Combine hists over runs for each syst
#----------------------
print('\n>> Combining hists...')
print(h.keys()) # lists runs
print(h[r].keys()) # lists systs
print(h[r][syst].keys()) # lists hists
print(type(h[r][syst].keys()[0])) # type
htest = h[r][syst].keys()[0]
print(type(h[r][syst][htest])) # hist
print(h[r][syst][htest].GetName()) # hist

# Loop over syst scenarios (1 per file)
for syst in ksysts:
    print('.. for syst:', syst)

    # Initialize output file and hists
    syst_outdir = '%s/%s'%(outdir, syst)
    run_eosmkdir(syst_outdir)
    #outpath = '%s/%s_blind_%s_templates.root'%(syst_outdir, sample_sg, ma_blind)
    #print('.. outpath:', outpath)
    #hfout = ROOT.TFile.Open(outpath, "RECREATE")
    hcombo = OrderedDict()

    # Loop over hists
    for hist in khists:
        #htgt = '%s_%s'%(sample_sg, hist)
        htgt = '%s-%s'%(sample_sg, hist)
        print('   .. for hist: %s -> %s'%(hist, htgt))

        sample_str = htgt.split('_')[0]
        outpath = '%s/%s_%s_blind_%s_templates.root'%(syst_outdir, sample_str, mh_region, ma_blind)
        print('.. outpath:', outpath)
        hfout = ROOT.TFile.Open(outpath, "RECREATE")

        # Loop over runs to sum over
        for i,r in enumerate(runs):
            print('      .. adding run:', r)
            #rsyst = get_run_key(syst, r)
            rsyst = syst
            rhist = get_run_key(hist, r)
            #print('      .. adding rsyst:', rsyst)
            print('      .. adding rhist:', rhist)

            # [DEPRECATED] implemented at mk_sg_templates.py so each year's templates are properly normalized
            # and can be used individually for systematics studies
            #print('      .. name: %s, integral: %.f'%(h[r][rsyst][rhist].GetName(), h[r][rsyst][rhist].Integral()))
            #mcnorm = get_mc2data_norm(rhist.split('_')[0], ggntuple_campaign, tgt_lumis[r], xsec=xs_sg)
            #h[r][rsyst][rhist].Scale(mcnorm)

            if i == 0:
                # Create combo histogram as clone of first hist
                hcombo[hist] = h[r][rsyst][rhist].Clone()
                hcombo[hist].SetName(htgt)
                hcombo[hist].SetTitle(htgt)
            else:
                # For subsequent hists, add to combo hist
                hcombo[hist].Add(h[r][rsyst][rhist])

            print('      .. name: %s, integral: %.f'%(h[r][rsyst][rhist].GetName(), h[r][rsyst][rhist].Integral()))
            print('      .. combo integral: %.f'%(hcombo[hist].Integral()))

        print('   .. combo integral: %.f'%(hcombo[hist].Integral()))
        # only needed if applying [DEPRECATED] mc normalization
        #hfout.cd()
        #hcombo[hist].Write()

        # Write out syst file
        hfout.Write()
        hfout.Close()
'''
'''
