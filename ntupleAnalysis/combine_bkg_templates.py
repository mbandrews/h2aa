from __future__ import print_function
#import numpy as np
import ROOT
import os, glob, re
from collections import OrderedDict
from data_utils import *
from hist_utils import *
from template_utils import *

'''
Combine yr-by-yr bkg templates for full run2 bkg template
Required since data-driven + hgg template combination must
be done yr-by-yr (see mk_bkg_templates.py)
'''
k2dma = 'ma0vma1'
sample_data = 'data'
mh_regions = ['sb2sr+hgg', 'sr']
ma_blinds = ['diag_lo_hi', 'offdiag_lo_hi']
distns = ['%s-%s'%(k2dma, b) for b in ma_blinds]
print('>> Running script to combine bkg templates...')

sel = 'nom'
#sel = 'inv'
run2dir = 'Run2'
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
campaign_ptwgts = 'bkgPtWgts-Era04Dec2020v2/%s'%sub_campaign
print('.. input campaign: %s'%campaign_ptwgts)

# Output combined templates to lpchaa4g/mandrews/Run2/
eos_basedir = '/store/user/lpchaa4g/mandrews'
outdir = '%s/%s/%s/%s/Templates_bkg'%(eos_redir, eos_basedir, run2dir, campaign_ptwgts)
print('.. output dir: %s\n'%outdir)
run_eosmkdir(outdir)

def get_unique_key(k):
    ksplit = k.split('_')
    ksplit = ksplit[1:] # remove preceding `data<run>_` string
    kjoin = '_'.join(ksplit)
    return kjoin

def get_run_key(k, r, sample=sample_data):
    krun = '%s%s_%s'%(sample, r, k)
    return krun

#--------------
# Read in hists
#--------------
h = OrderedDict()
hf = OrderedDict()
runs = ['2016', '2017', '2018']

# Loop over run eras
for r in runs:

    print('>> Reading hists for run:', r)

    #if r != '2016': continue
    #if r != '2017': continue
    #if r != '2018': continue

    eos_basedir = '/store/user/lpchaa4g/mandrews'
    # If combining templates over runs, always use full run 2 ptwgts, i.e. read from <campaign>/Run2/Templates_bkg
    indir = '%s/%s/%s/%s/%s/Templates_bkg'%(eos_redir, eos_basedir, r, campaign_ptwgts, run2dir)
    print('.. input dir:', indir)

    samples = ['%s%s'%(sample_data, r)]

    # Get list of syst files for this run era.
    infiles = indir.replace(eos_redir, '/eos/uscms') + '/*root'
    print('.. inpath: %s'%infiles)
    syst_files = glob.glob(infiles)
    print('.. found %d syst files.'%(len(syst_files)))
    systs = [s.split('/')[-1].replace('.root','') for s in syst_files]

    h[r] = OrderedDict()
    hf[r] = OrderedDict()

    # Loop over systs file/scenarios
    for i,syst in enumerate(systs):

        print('.. Reading syst:', syst)

        h[r][syst] = OrderedDict()
        hf[r][syst] = OrderedDict()

        # Read in hists/templates for each run and syst
        load_hists_in_file(h[r][syst], hf[r][syst], samples, mh_regions, distns, syst_files[i])

#----------------------
# Do consistency checks
#----------------------
print('\n>> Doing hist consistency checks...')
#print(h.keys()) # lists runs
#print(h[r].keys()) # lists systs
#print(h[r][syst].keys()) # lists hists

# Check that systs are identical across runs
for i in runs:
    syst_keys_i = [get_unique_key(ki) for ki in h[i].keys()]
    #print(i, syst_keys_i)
    for j in runs:
        if i == j: continue
        syst_keys_j = [get_unique_key(kj) for kj in h[j].keys()]
        # Syst pairing
        assert syst_keys_i == syst_keys_j,\
               '!! systs do not match for run %d vs %d: %s vs %s'%(i, j, ','.join(syst_keys_i), ','.join(syst_keys_j))
        #print(j, syst_keys_j)
    break # only need to do first loop once to exhaust all pairings

# Store systs
ksysts = syst_keys_i
print('.. ksysts:', ksysts)

# Check that hist keys are identical
# First, check hist keys within run, across systs
hist_keys_run = OrderedDict()
for r in runs:

    # Hist keys within run, across systs
    for a in ksysts:
        hist_keys_a = [get_unique_key(ka) for ka in h[r][get_run_key(a,r)].keys()]
        #print(a, hist_keys_a)
        for b in ksysts:
            if a == b: continue
            hist_keys_b = [get_unique_key(kb) for kb in h[r][get_run_key(b,r)].keys()]
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
#print(h.keys()) # lists runs
#print(h[r].keys()) # lists systs
#print(h[r][syst].keys()) # lists hists
#print(type(h[r][syst].keys()[0])) # type
#htest = h[r][syst].keys()[0]
#print(type(h[r][syst][htest])) # hist
#print(h[r][syst][htest].GetName()) # hist

# Loop over syst scenarios (1 per file)
for syst in ksysts:
    print('.. for syst:', syst)

    # Initialize output file and hists
    outpath = '%s/data_%s.root'%(outdir, syst)
    print('.. outpath:', outpath)
    hfout = ROOT.TFile.Open(outpath, "RECREATE")
    hcombo = OrderedDict()

    # Loop over hists
    for hist in khists:
        htgt = '%s_%s'%(sample_data, hist)
        print('   .. for hist: %s -> %s'%(hist, htgt))

        # Loop over runs to sum over
        for i,r in enumerate(runs):
            print('      .. adding run:', r)
            rsyst = get_run_key(syst, r)
            rhist = get_run_key(hist, r)

            if i == 0:
                # Create combo histogram as clone of first hist
                hcombo[hist] = h[r][rsyst][rhist].Clone()
                hcombo[hist].SetName(htgt)
                hcombo[hist].SetTitle(htgt)
            else:
                # For subsequent hists, add to combo hist
                hcombo[hist].Add(h[r][rsyst][rhist])

            #print('      .. name: %s, integral: %.f'%(h[r][rsyst][rhist].GetName(), h[r][rsyst][rhist].Integral()))
            #print('      .. combo integral: %.f'%(hcombo[syst][hist].Integral()))

        print('   .. combo integral: %.f'%(hcombo[hist].Integral()))

    # Write out syst file
    hfout.Write()
    hfout.Close()
