from __future__ import print_function
#import numpy as np
import ROOT
import os, glob, re
from data_utils import *
from hist_utils import *
from template_utils import *

'''
Make yr-by-yr data-driven + hgg bkg templates
NOTE: bkg template must be constructed yr-by-yr even for full run2!

For data component: construct from mH-SB events but re-weight to have same 2d-pt
distn as in mH-SR (derived in get_ptwgts.py). For full run2, pt wgts are derived
using full run2 stats BUT bkg templates MUST be first constructed using yr-by-yr stats
since need to be combined with hgg templates which must be normalized yr-by-yr.
Yr-by-yr bkg templates are combined for full run2 bkg template separately in
combine_bkg_templates.py.

For hgg MG component: for each yr, normalize hgg template to each yr's data mH-SR lumi.
Since only using gluon-fusion hgg MC, introduce normalization syst wrt total hgg inclusive xsec
vs glusion fusion xsec component only.
'''

#k2dpt = 'pt0vpt1'
k2dpt = 'nEvtsWgtd'
k2dma = 'ma0vma1'
distns = [k2dpt, k2dma]
ma_blind_input = None
ma_blind_norm = 'diag_lo_hi'
ma_blind_outputs = ['diag_lo_hi', 'offdiag_lo_hi']

doRun2 = True # use full run2 pt wgts
run2dir = 'Run2'
sel = 'nom'
#sel = 'inv'
#campaign_noptwgts = 'runBkg_noptwgts_bdtgtm0p99-v1'
#campaign_ptwgts = 'runBkg_ptwgts_bdtgtm0p99-v1'
#campaign_ptwgts = 'runBkg_ptwgts_bdtgtm0p99-v2noceil'
# no 2018A, 2016H+2018 failed lumis
#campaign_noptwgts = 'bkgNoPtWgts-Era04Dec2020v1/bdtgtm0p98_relChgIsolt0p05_etalt1p44/nom-%s'%sel
#campaign_ptwgts = 'bkgPtWgts-Era04Dec2020v1/bdtgtm0p98_relChgIsolt0p05_etalt1p44/nom-%s'%sel
# with 2018A. 2016H+2018 failed lumis
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
campaign_noptwgts = 'bkgNoPtWgts-Era22Jun2021v1/%s'%sub_campaign
#campaign_ptwgts = 'bkgPtWgts-Era04Dec2020v2/%s'%sub_campaign
campaign_ptwgts = 'bkgPtWgts-Era22Jun2021v1/%s'%sub_campaign
if doRun2: campaign_ptwgts += '/%s'%run2dir

br_hgg = 2.27e-3 # BR(h->gg)
nhgg = {
        '2016': 214099989.445038,
        '2017': 214099989.445038,
        '2018': 214099989.445038
        } # N wgt gen evts
# Official lumis: https://twiki.cern.ch/twiki/bin/view/CMS/TWikiLUM
#intlumi = {'2016': 36.33e3, #35.92e3,
#           '2017': 41.53e3,
#           '2018': 59.74e3} # /pb.
# Estimated lumis modulo missing lumis: https://docs.google.com/spreadsheets/d/1wmDcb88uJfgJakIE9BfKfHXU_sb1ldy6NArZZzr0fRk/edit#gid=0
# Calculated using:
#   [1] cmslpc:~mba2012/nobackup/h2aa/CMSSW_10_5_0/src/h2aa/crab/run_getLumis.py
#   [2] lxplus:~mandrews/work/h2aa/brilcalc_work/getLumis_byEra.sh
intlumi = {'2016': 36.25e3,
           '2017': 41.53e3,
           '2018': 58.75e3} # /pb. Run2: 136.53/pb

#flo_nom = 0.645897591246
#flo_ins = [0.5040, flo_nom, 0.7910]
# Input f_hggs. Calculated using get_fhgg.py
'''
fhggs = {
        '2016nom': [0.                       , 1.29409e-03, 1.29409e-03 + 2.71978e-0],
        '2016inv': [8.39948e-03 - 3.85741e-03, ]

        '2017nom': [1.24404e-02 - 5.74877e-03, 1.24404e-02, 1.24404e-02 + 5.74877e-03],
        '2017inv': [],

        '2018nom': [0.                       , 1.23262e-02, 1.23262e-02 + 4.81454e-02],
        '2018inv': [5.98173e-03 - 3.48104e-03, 5.98173e-03, 5.98173e-03 + 3.48104e-03]
         }
# Make sure f_hgg scenarios are in increasing order and positive-valued
for k in fhggs:
    assert (fhggs[k][1] > fhggs[k][0]) and (fhggs[k][1] < fhggs[k][2])
    if fhggs[k][0] < 0:
        fhggs[k][0] = 0.
    print(fhggs[k])
fhggs = {
        '2016nom': [1.29409e-03, 2.71978e-03],
        '2016inv': [8.39948e-03, 3.85741e-03],

        '2017nom': [1.24404e-02, 5.74877e-03],
        '2017inv': [5.26839e-03, 2.54058e-03],

        '2018nom': [1.23262e-02, 4.81454e-02],
        '2018inv': [5.98173e-03, 3.48104e-03]
         } # [nom fit value, fit uncert]
fhggs = {
        'nom': [3.28431e-03, 2.77196e-03],
        'inv': [1.92478e-03, 2.46728e-03]
         } # [nom fit value, fit uncert]
'''
fhggs = {
        'nom': [2.88903e-03, 2.78887e-03],
        'inv': [1.42361e-03, 1.22762e-03],
         } # [nom fit value, fit uncert]

runs = ['2016', '2017', '2018']

for r in runs:

    print('>> Doing Run:',r)

    #if r != '2016': continue
    #if r != '2017': continue
    #if r != '2018': continue

    eos_basedir = '/store/user/lpchaa4g/mandrews/%s'%r
    input_dir = '%s/%s'%(eos_redir, eos_basedir)
    outdir = '%s/%s/Templates_bkg'%(input_dir, campaign_ptwgts)
    run_eosmkdir(outdir)

    #sample_data = 'Run2017'
    #sample_hgg = 'GluGluHToGG'
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
    flo_nom = flo_ins[1]

    for flo_in in flo_ins:

        print('>> Doing flo_in:',flo_in)

        # --------------------------------------------------
        # Init
        # --------------------------------------------------
        hnorm, hblind = {}, {}
        c, h, hf = {}, {}, {}

        # raw mh-SR
        # dont use full run2 folder since getting mh-SR (unwgtd) counts per yr
        workdir = '%s/%s/Templates'%(input_dir, campaign_noptwgts)
        samples = [sample_data, sample_hgg]
        mh_regions = ['sr']
        load_hists(h, hf, samples, mh_regions, distns, ma_blind_input, workdir)

        # Get total hgg and mh-SR event yield
        nevts = {}
        for k in h:
            if k2dpt in k:
                nevts[k] = h[k].Integral()
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
        # --------------------------------------------------
        sb2sr_norm, sr_blind_yield = get_sb2sr_norm(h, hnorm, c, flo_in, flo_nom, sample_data, distns, to_blind=ma_blind_norm, k2dma=k2dma, k2dpt=k2dpt)

        # --------------------------------------------------
        # Make full data mh-SBlo+hi + hgg mh-SR bkg template
        # --------------------------------------------------

        # Combine pt re-weighted mh-SBlo+hi and normalize
        ksblo = '%s_sblo_%s'%(sample, k2dma)
        ksbhi = '%s_sbhi_%s'%(sample, k2dma)
        ksb2sr = '%s_sb2sr_%s'%(sample, k2dma)
        combine_sblohi(h, flo_in, flo_nom, ksblo, ksbhi, ksb2sr)
        h[ksb2sr].Scale(sb2sr_norm)
        print('.. h[%s].Integral(): %f'%(ksb2sr, h[ksb2sr].Integral()))

        # Calculate fhgg over full, unblinded (2d-pt) evt yields (same as for flo)
        # If only using blinded 2d-ma, can give skewed estimates of true hgg xsec yield
        khgg_2dpt = '%s_sr_%s'%(sample_hgg, k2dpt)
        ksr_2dpt = '%s_sr_%s'%(sample_data, k2dpt)

        '''
        # Loop over hgg xsecs: nom: total SM inclusive: 50.94, syst: gluglu-only: 43.92
        # If doing flo_nom, only need to do nom xsec
        #xs_nom, xs_syst = 50.94, 43.92 # [pb] gluglu only:48.58->43.92
        #xs_syst, xs_nom = 50.94, 43.92 # [pb] gluglu only:48.58->43.92
        #xsecs = [xs_nom, xs_syst] if flo_in == flo_nom else [xs_nom]
        #for xsec_hgg in xsecs:
        '''

        # Loop over f_hggs: nominal fit from get_fhgg +/- fit uncert
        # If varying f_sblo, only use nominal f_hgg, else loop over all f_hgg syst shifts
        #fhgg_nom = fhggs[r+sel][0] # nominal is 1st element
        #fhgg_err = fhggs[r+sel][1] # fit uncert is 2nd element
        fhgg_nom = fhggs[sel][0] # nominal is 1st element
        fhgg_err = fhggs[sel][1] # fit uncert is 2nd element
        if flo_in == flo_nom:
            fhggs_ = [fhgg_nom-fhgg_err if fhgg_nom > fhgg_err else 0., fhgg_nom, fhgg_nom+fhgg_err]
        else:
            fhggs_ = [fhgg_nom]
        for fhgg in fhggs_:

            assert fhgg >= 0.
            print('  >> Doing f_hgg:',fhgg)

            '''
            fhgg = br_hgg*xsec_hgg*intlumi[r]*nevts[khgg_2dpt]/nhgg[r]
            fhgg /= nevts[ksr_2dpt]
            print('  .. fhgg, 2017:', fhgg)
            if sel == 'nom':
                fhgg = 0.00395577246287 if xsec_hgg == xs_nom else 0.00458804756964
            else:
                fhgg = 3.84666817207e-05 if xsec_hgg == xs_nom else 4.46150447826e-05
            '''
            fsb = 1.-fhgg
            print('  .. fhgg:',fhgg)
            print('  .. fsb:',fsb)

            #'''
            # Normalize hgg template s.t. diag_lo_hi-blinded hgg yield matches corresponding yield in data(mh-SR)
            # Required to preserve norm of total SB+hgg template in diag_lo_hi-blinded 2d-ma
            khgg = '%s_sr_%s'%(sample_hgg, k2dma)
            khgg_blind = '%s-%s'%(khgg, ma_blind_norm)
            hblind[khgg_blind] = h[khgg].Clone()
            hblind[khgg_blind].SetName(khgg_blind)
            blind_hist(hblind[khgg_blind], to_blind=ma_blind_norm)
            hgg_norm = sr_blind_yield/hblind[khgg_blind].Integral()
            h[khgg].Scale(hgg_norm)

            # Combine existing mh-SBlo+hi template with hgg template:
            # fsb*data(mh-SBlo+hi) + fgg*hgg(mh-SR)
            ksb2sr_hgg = '%s_sb2sr+hgg_%s'%(sample_data, k2dma)
            h[ksb2sr_hgg] = h[ksb2sr].Clone()
            h[ksb2sr_hgg].SetName(ksb2sr_hgg)
            h[ksb2sr_hgg].Scale(fsb)
            h[ksb2sr_hgg].Add(h[khgg], fhgg)
            print('  .. h[%s].Integral(): %f'%(ksb2sr_hgg, h[ksb2sr_hgg].Integral()))

            # Draw
            c[ksb2sr_hgg] = ROOT.TCanvas(ksb2sr_hgg, ksb2sr_hgg, wd, ht)
            h[ksb2sr_hgg].Draw('COL Z')
            c[ksb2sr_hgg].SetLogz()
            c[ksb2sr_hgg].Draw()
            c[ksb2sr_hgg].Update()

            # Make blinded bkg templates
            # Note: bkg vs. data(mh-SR) yields must agree in diag_lo_hi-blinded 2d-ma!
            ksr = '%s_sr_%s'%(sample_data, k2dma)
            for k in [ksb2sr_hgg, ksr]:

                print('    >> doing mh-region:',k)

                for b in ma_blind_outputs:

                    print('      >> doing ma-blind:',b)
                    kblind = '%s-%s'%(k, b)

                    # Apply blinding
                    hblind[kblind] = h[k].Clone()
                    hblind[kblind].SetName(kblind)
                    blind_hist(hblind[kblind], to_blind=b)
                    print('      .. nevts[%s]: %f'%(kblind, hblind[kblind].Integral()))

                    # Draw
                    c[kblind] = ROOT.TCanvas(kblind, kblind, wd, ht)
                    hblind[kblind].GetXaxis().SetRangeUser(0., 1.2)
                    hblind[kblind].GetYaxis().SetRangeUser(0., 1.2)
                    hblind[kblind].Draw('COL Z')
                    #c[kblind].SetLogz()
                    c[kblind].Draw()
                    c[kblind].Update()

            # Get syst str
            syst_str = ''
            # f_sblo
            if flo_in < flo_nom:
                syst_str += '_floDn'
            elif flo_in > flo_nom:
                syst_str += '_floUp'
            # hgg yield
            if fhgg < fhgg_nom:
                syst_str += '_hggDn'
            elif fhgg > fhgg_nom:
                syst_str += '_hggUp'

            #print(hblind.keys())
            #print(hnorm.keys())

            # Write to file
            outpath = '%s/%s%s.root'%(outdir, ksb2sr_hgg.replace('_'+k2dma, ''), syst_str)
            print(' .. Writing to:',outpath)
            hfout = ROOT.TFile.Open(outpath, 'RECREATE')
            hfout.mkdir('hnorm/')
            hfout.cd('hnorm/')
            for k in hnorm:
                hnorm[k].Write()
            hfout.cd('')
            for k in hblind:
                hblind[k].Write()
            hfout.Close()
