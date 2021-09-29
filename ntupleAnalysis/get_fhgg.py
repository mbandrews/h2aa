from __future__ import print_function
#import numpy as np
import ROOT
import os, glob, re
from data_utils import *
from hist_utils import *
from template_utils import *

# DEPRECATED: fhgg now determined using theory+MC, not using fit to data
# fitting to data can absorb a potential sg contribution into defintion of bkg model
'''
Calculate f_hgg for each year/sel combo
'''
import argparse
parser = argparse.ArgumentParser(description='Run h2aa bkg model.')
parser.add_argument('-s', '--sel', default='nom', type=str, help='Event selection: nom or inv.')
parser.add_argument('-r', '--run', default='2017', type=str, help='Run era: 2016, 2017, 2018.')
parser.add_argument('--nonegs', action='store_true', help='Remove negative bins.')
parser.add_argument('--fit', action='store_true', help='Do template frac fit.')
parser.add_argument('--norm', action='store_true', help='Set fit normalization to 1.e6.')
args = parser.parse_args()

#k2dpt = 'pt0vpt1'
k2dpt = 'nEvtsWgtd'
k2dma = 'ma0vma1'
distns = [k2dpt, k2dma]
ma_blind_input = None
ma_blind_norm = 'diag_lo_hi' # nominal blinding
#ma_blind_norm = 'diag_hi' # if allowing negative masses: does not give reasonable results. Could be due to using a single large occ negative mass bin.

remove_negs = args.nonegs
do_fit = args.fit
modify_norm = args.norm

doRun2 = True # use full run2 pt wgts
run2dir = 'Run2'
#sel = 'nom'
#sel = 'inv'
sel = args.sel
print('>> Selection:', sel)
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
#campaign_noptwgts = 'bkgNoPtWgts-Era04Dec2020v2/%s'%sub_campaign
campaign_noptwgts = 'bkgNoPtWgts-Era22Jun2021v1/%s'%sub_campaign # bin25MeV
#campaign_noptwgts = 'bkgNoPtWgts-Era22Jun2021v2/%s'%sub_campaign # bin50MeV
#campaign_ptwgts = 'bkgPtWgts-Era04Dec2020v2/%s'%sub_campaign
campaign_ptwgts = 'bkgPtWgts-Era22Jun2021v1/%s'%sub_campaign # bin25MeV
#campaign_ptwgts = 'bkgPtWgts-Era22Jun2021v2/%s'%sub_campaign # bin50MeV
if doRun2: campaign_ptwgts += '/%s'%run2dir

# N_hgg,sel,data-norm  = intlumi * xs * br * N_hgg,sel / N_hgg,gen
# NOTE: The above equality holds whether `sel` is defined as events passing evt sel only
# or passing evt sel and diag_lo_hi blinding
#hgg_campaign = 'sg-Era22Jun2021v2/%s'%sub_campaign # for getting mc templates
#hgg_campaign = 'sg-Era22Jun2021v4/%s'%sub_campaign # sg-Era22Jun2021v2 + interp masses (v3) + bin50MeV [overwritten]
hgg_campaign = 'sg-Era22Jun2021v4/%s'%sub_campaign # sg-Era22Jun2021v2 + interp masses (v3) + ss with SFs
skim_campaign = 'ggNtuples-Era20May2021v1_ggSkim-v2' # for getting mc nevtsgen
# https://twiki.cern.ch/twiki/bin/view/LHCPhysics/CERNYellowReportPageAt1314TeV2014
# total SM inclusive higgs prodn: 50.94, gluglu-only: 43.92
xs_hgg = 50.94
intlumi = {'2016': 36.25e3,
           '2017': 41.53e3,
           '2018': 58.75e3} # /pb. Run2: 136.53/pb

hsum = {}
hblind = {}
hnorm = {}
nevtsgen = {}
nevts = {}
#c, h, hf = {}, {}, {}
h, hf = {}, {}
runs = ['2016', '2017', '2018']

for i,r in enumerate(runs):

    #if r != '2016': continue
    #if r != '2017': continue
    #if r != '2018': continue
    #if r != args.run: continue

    print('>> Doing Run:',r)

    eos_basedir = '/store/user/lpchaa4g/mandrews/%s'%r
    input_dir = '%s/%s'%(eos_redir, eos_basedir)
    outdir = '%s/%s/Templates_bkg'%(input_dir, campaign_ptwgts)
    run_eosmkdir(outdir)

    sample_data = 'data%s'%r
    sample_hgg = 'bg%s-hgg'%r

    # Get list of fSB-lows from names of ptwgt files
    # NOTE: For full Run2, get ptwgt files from Run2 folder?? Does that make sense wrt how fSBlows are derived?
    # there should only be 1 set of systs for full Run2 data, right?
    inpath = '/eos/uscms/%s/%s/Weights/*ptwgts.root'%(eos_basedir, campaign_noptwgts)
    if doRun2: inpath = inpath.replace('/%s'%r, '/%s/'%run2dir)
    print('.. inpath: %s'%inpath)
    flo_files = glob.glob(inpath)
    print('.. found %d f_SBlows'%(len(flo_files)))
    flo_ins = [float(flo.split('_')[-2].strip('flo')) for flo in flo_files]
    flo_nom = flo_ins[1] # nominal is middle element

    flo_in = flo_nom
    print('>> Doing flo_in:',flo_in)

    # --------------------------------------------------
    # Init
    # --------------------------------------------------
    #hnorm, hblind = {}, {}
    #hnorm = {}
    #c, h, hf = {}, {}, {}
    c = {}

    # raw mh-SR, data
    # dont use full run2 folder since we are getting mh-SR (unwgtd) counts per yr
    workdir = '%s/%s/Templates'%(input_dir, campaign_noptwgts)
    #samples = [sample_data, sample_hgg]
    samples = [sample_data]
    mh_regions = ['sr']
    load_hists(h, hf, samples, mh_regions, distns, ma_blind_input, workdir)

    # raw mh-SR, hgg
    # Use hgg template with phoid+trg SFs applied
    workdir = '%s/%s/Templates/systNom_nom'%(input_dir, hgg_campaign)
    samples = [sample_hgg]
    mh_regions = ['sr']
    load_hists(h, hf, samples, mh_regions, distns, ma_blind_input, workdir)

    # Get total hgg and mh-SR event yield
    #nevts = {}
    for k in h:
        if r not in k: continue
        if k2dpt in k:
            #nevts[k] = h[k].Integral()
            nevts[k] = h[k].GetBinContent(2) # bin for filled event
            print('total nevts[%s]: %f'%(k, nevts[k]))
        else:
            print('total nevts[%s]: %f'%(k, h[k].Integral()))

    # pt rwgtd mh-SBs
    sample = sample_data
    mh_regions = ['sblo', 'sbhi']
    workdir = '%s/%s/Templates_flo%s'%(input_dir, campaign_ptwgts, '%.4f'%flo_in)
    load_hists(h, hf, [sample], mh_regions, distns, ma_blind_input, workdir)

    # --------------------------------------------------
    # Get sb->sr norm
    # Calculated using diag_lo_hi blinded
    # --------------------------------------------------
    sb2sr_norm, sr_blind_yield = get_sb2sr_norm(h, hnorm, c, flo_in, flo_nom, sample_data, distns, to_blind=ma_blind_norm, k2dma=k2dma, k2dpt=k2dpt)

    # --------------------------------------------------
    # Make blinded data mhSR, mh-SBlo+hi, and hgg mh-SR templates
    # --------------------------------------------------

    # Make blinded mh-SR template
    ksr = '%s_sr_%s'%(sample_data, k2dma)
    ksr_blind = '%s-%s'%(ksr, ma_blind_norm)
    hblind[ksr_blind] = h[ksr].Clone()
    hblind[ksr_blind].SetName(ksr_blind)
    blind_hist(hblind[ksr_blind], to_blind=ma_blind_norm)
    print('.. nevts[%s]: %f'%(ksr_blind, hblind[ksr_blind].Integral()))

    # Combine pt re-weighted mh-SBlo+hi and normalize
    # Note: bkg vs. data(mh-SR) yields must agree in diag_lo_hi-blinded 2d-ma!
    ksblo = '%s_sblo_%s'%(sample, k2dma)
    ksbhi = '%s_sbhi_%s'%(sample, k2dma)
    ksb2sr = '%s_sb2sr_%s'%(sample, k2dma)
    combine_sblohi(h, flo_in, flo_nom, ksblo, ksbhi, ksb2sr)
    h[ksb2sr].Scale(sb2sr_norm)
    print('.. h[%s].Integral(): %f'%(ksb2sr, h[ksb2sr].Integral()))
    # Make blinded SB-derived bkg templates
    ksb2sr_blind = '%s-%s'%(ksb2sr, ma_blind_norm)
    hblind[ksb2sr_blind] = h[ksb2sr].Clone()
    hblind[ksb2sr_blind].SetName(ksb2sr_blind)
    blind_hist(hblind[ksb2sr_blind], to_blind=ma_blind_norm)
    print('.. nevts[%s]: %f'%(ksb2sr_blind, hblind[ksb2sr_blind].Integral()))

    # Get total gen events for this sample/year
    nevtsgen[sample_hgg] = get_mcgenevents(sample_hgg, input_dir, hgg_campaign, skim_campaign)
    print('.. nevtsgen[%s]: %f'%(sample_hgg, nevtsgen[sample_hgg]))
    # Get raw mc template, then blind
    khgg = '%s_sr_%s'%(sample_hgg, k2dma)
    khgg_blind = '%s-%s'%(khgg, ma_blind_norm)
    hblind[khgg_blind] = h[khgg].Clone()
    hblind[khgg_blind].SetName(khgg_blind)
    blind_hist(hblind[khgg_blind], to_blind=ma_blind_norm)
    print('.. nevts[%s]: %f'%(khgg_blind, hblind[khgg_blind].Integral()))

    # Sum templates over years
    # Want to do template fraction fit using full run2 stats
    if i == 0:

        # Initialize hists on first iteration

        # sb2sr
        ksb2sr_blind_run2 = ksb2sr_blind.replace(r, '')
        hsum[ksb2sr_blind_run2] = hblind[ksb2sr_blind].Clone()
        hsum[ksb2sr_blind_run2].SetName(ksb2sr_blind_run2)

        # sr
        ksr_blind_run2 = ksr_blind.replace(r, '')
        hsum[ksr_blind_run2] = hblind[ksr_blind].Clone()
        hsum[ksr_blind_run2].SetName(ksr_blind_run2)

        # Hgg templates need to be summed over yrs before being normalized to data
        # This is done to maximize stats available for fit to data
        # At this point, only normalize to intlumi/N_gen for each yr so that
        # the different yrs can be combined correctly.
        # This is needed to get relative normalization between different years correct
        khgg_blind_run2 = khgg_blind.replace(r, '')
        hsum[khgg_blind_run2] = hblind[khgg_blind].Clone()
        hsum[khgg_blind_run2].SetName(khgg_blind_run2)
        # Scale to intlumi/nevtsgen (histogram will originally sum to N_hgg,sel)
        hsum[khgg_blind_run2].Scale(intlumi[r]/nevtsgen[sample_hgg])

        #print('!! nevts[%s]: %f'%(ksb2sr_blind_run2, hsum[ksb2sr_blind_run2].Integral()))
        #print(hsum.keys())
        #print(type(hsum[khgg_blind_run2]))
    else:

        # Add contributions from succeeding years
        #print(hsum.keys())
        #print(type(hsum[khgg_blind_run2]))

        # sb2sr
        hsum[ksb2sr_blind_run2].Add(hblind[ksb2sr_blind])
        # sr
        hsum[ksr_blind_run2].Add(hblind[ksr_blind])
        # hgg
        hsum[khgg_blind_run2].Add(hblind[khgg_blind], intlumi[r]/nevtsgen[sample_hgg])

        #print('!! nevts[%s]: %f'%(ksb2sr_blind_run2, hsum[ksb2sr_blind_run2].Integral()))

norm = 1.e6
if modify_norm:
    hsum[ksb2sr_blind_run2].Scale(norm/hsum[ksb2sr_blind_run2].Integral())
    hsum[ksr_blind_run2].Scale(norm/hsum[ksr_blind_run2].Integral())
print('>> total run2 events[%s]: %f'%(ksb2sr_blind_run2, hsum[ksb2sr_blind_run2].Integral()))
print('>> total run2 events[%s]: %f'%(ksr_blind_run2, hsum[ksr_blind_run2].Integral()))
print('>> total run2 events[%s]: %f'%(khgg_blind_run2, hsum[khgg_blind_run2].Integral()))

if remove_negs:
    print('>> Removing negative bins...')
    # set negative bins to zero
    for ix in range(hsum[khgg_blind_run2].GetNbinsX()+2):
        for iy in range(hsum[khgg_blind_run2].GetNbinsX()+2):
            binc = hsum[khgg_blind_run2].GetBinContent(ix, iy)
            if binc < 0:
                hsum[khgg_blind_run2].SetBinContent(ix, iy, 0.)

# Normalize combined hgg template to data here
print('>> Scaling hgg to data...')
hsum[khgg_blind_run2].Scale(hsum[ksr_blind_run2].Integral()/hsum[khgg_blind_run2].Integral())
print('>> total run2 events[%s]: %f'%(khgg_blind_run2, hsum[khgg_blind_run2].Integral()))

if do_fit:
    print('>> Doing template fraction fit')
    bgfracs = ROOT.TObjArray()
    bgfracs.Add(hsum[khgg_blind_run2])
    bgfracs.Add(hsum[ksb2sr_blind_run2])
    fit = ROOT.TFractionFitter(hsum[ksr_blind_run2], bgfracs)
    fit.Constrain(0, 0., 1.)
    fit.Constrain(1, 0., 1.)
    status = fit.Fit() # seg faults at deconstruction (not supported in PyROOT)
    print('   .. fit status:', int(status))
    print('   .. X^2 / ndf = %f / %d = %f'%(fit.GetChisquare(), fit.GetNDF(), fit.GetChisquare()/fit.GetNDF()))
    print('   .. p-val:', fit.GetProb())
    print(hsum[khgg_blind_run2].Integral())
else:
    #'''
    # Calculate BR from f_hgg
    # br = N_hgg,gen * N_hgg,sel,data-norm / (N_hgg,sel * intlumi * xs)
    if sel == 'nom':
        # nom selection
        # with neg
        #fhgg = 4.15379e-03
        #fhgg_err = 4.78402e-03
        # no neg
        fhgg = 2.88903e-03
        fhgg_err = 2.78887e-03
        #fhgg = 0.000909422776646
    else:
        # inv selection
        # no neg
        #fhgg = 1.56042e-03
        #fhgg_err = 9.26691e-04 #1.23826e-01
        # no neg, with norm
        fhgg = 1.42361e-03
        fhgg_err = 1.22762e-03

    print('>> Calculating BR(h->gg)...')
    print('.. br = N_hgg,gen * N_hgg,sel,data-norm / (N_hgg,sel * intlumi * xs)')
    #for frac in [fhgg]:
    for frac in [fhgg-fhgg_err, fhgg, fhgg+fhgg_err]:

        if frac < 0.: frac = 0.
        print('>> For fhgg: %E'%(frac))

        brs = {}
        for r in runs:
            print('   >> For run:',r)
            # Get keys
            sample_hgg = 'bg%s-hgg'%r
            khgg = '%s_sr_%s'%(sample_hgg, k2dma)
            khgg_blind = '%s-%s'%(khgg, ma_blind_norm)
            sample_data = 'data%s'%r
            ksr = '%s_sr_%s'%(sample_data, k2dma)
            ksr_blind = '%s-%s'%(ksr, ma_blind_norm)
            # Get nevts
            nhgg_gen = nevtsgen[sample_hgg]
            nhggsel = hblind[khgg_blind].Integral()
            nhggsel_datanorm = hblind[ksr_blind].Integral()*frac
            # Get br
            #print('   .. %.f * %.f / ( %.f * %E * %f )'%(nhgg_gen, nhggsel_datanorm, nhggsel, intlumi[r], xs_hgg))
            #print('nhgg_gen:',nhgg_gen)
            ##print('nhggsel_datanorm:',nhggsel_datanorm)
            #print('hblind[ksr_blind].Integral():',hblind[ksr_blind].Integral())
            #print('nhggsel:',nhggsel)
            #print('intlumi[r]:',intlumi[r])
            #print('xs_hgg:',xs_hgg)
            #print('fhgg:',frac)
            brs[r] = ( nhgg_gen * nhggsel_datanorm ) / ( nhggsel * intlumi[r] * xs_hgg )
            print('      .. BR[%s]: %E'%(r, brs[r]))

        # Get wgtd ave br
        br_ave = 0
        for r in runs:
            br_ave += brs[r]*intlumi[r]
        br_ave /= sum(intlumi[r] for r in intlumi)
        print('   .. Run2 est BR: %E'%br_ave)
    #'''
