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
#campaign_noptwgts = 'bkgNoPtWgts-Era22Jun2021v1/%s'%sub_campaign
campaign_noptwgts = 'bkgNoPtWgts-Era22Jun2021v2/%s'%sub_campaign # v1 but with bin 50MeV [not used]
#campaign_noptwgts = 'bkgNoPtWgts-Era22Jun2021v3/%s'%sub_campaign # duplicate of v1 but with SFs on hgg template
#campaign_noptwgts = 'bkgNoPtWgts-Era22Jun2021v4/%s'%sub_campaign # duplicate of v3, but with fhgg derived from SM br(hgg)
#campaign_ptwgts = 'bkgPtWgts-Era04Dec2020v2/%s'%sub_campaign
#campaign_ptwgts = 'bkgPtWgts-Era22Jun2021v1/%s'%sub_campaign
campaign_ptwgts = 'bkgPtWgts-Era22Jun2021v2/%s'%sub_campaign # v1 but with bin 50MeV [not used]
#campaign_ptwgts = 'bkgPtWgts-Era22Jun2021v3/%s'%sub_campaign # duplicate of v1 but with SFs on hgg template
#campaign_ptwgts = 'bkgPtWgts-Era22Jun2021v4/%s'%sub_campaign # duplicate of v3, but with fhgg from SM br(hgg)
#campaign_ptwgts = 'bkgPtWgts-Era22Jun2021v5/%s'%sub_campaign # v4, but with addtl ptwgts shifted down/up by stat uncerts
#campaign_ptwgts = 'bkgPtWgts-Era22Jun2021v6/%s'%sub_campaign # v4, but with pt wgts smoothing (no shifting anymore)
if doRun2: campaign_ptwgts += '/%s'%run2dir

# f_hgg = ( intlumi * xs * br * N_hgg,sel / N_hgg,gen ) / N_sel,data
# where the above equality is assumed to hold identically for sel = evt sel + (mH-SR & ma-SB) and sel = evt sel + (mH-SR & ma-SR)
# so that we can derive it from (mH-SR & ma-SB) and use it for (mH-SR & ma-SR)
#hgg_campaign = 'sg-Era22Jun2021v4/%s'%sub_campaign # sg-Era22Jun2021v2 + interp masses (v3) + ss with SFs
hgg_campaign = 'sg-Era22Jun2021v6/%s'%sub_campaign # v4, but xs_sg = 1pb (v5) and 50MeV
skim_campaign = 'ggNtuples-Era20May2021v1_ggSkim-v2' # for getting mc nevtsgen
# https://twiki.cern.ch/twiki/bin/view/LHCPhysics/CERNYellowReportPageAt1314TeV2014
# total SM inclusive higgs prodn: 50.94, gluglu-only: 43.92
# Calculated using: https://docs.google.com/spreadsheets/d/1D8ztbh1WtCnSGJ_E0KQC0I5CEN0g61HQU4-XcfSm3iQ/edit#gid=368154701
xs_hgg = 51.04 # pb, SM total inclusive
xs_hgg_hi = 55.55 # pb, SM total inclusive + th uncerts
xs_hgg_lo = 39.56 # pb, gluglu only
nevtsgen = {}

br_hgg = 2.27e-3 # BR(h->gg)
#nhgg = {
#        '2016': 214099989.445038,
#        '2017': 214099989.445038,
#        '2018': 214099989.445038
#        } # N wgt gen evts
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

'''
[DEPRECATED]
# Input f_hggs. Calculated using get_fhgg.py
fhggs = {
        'nom': [2.88903e-03, 2.78887e-03],
        'inv': [1.42361e-03, 1.22762e-03],
         } # [nom fit value, fit uncert]
'''

#runs = ['2016']
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
    #flo_ins = [float(flo.split('_')[-2].strip('flo')) for flo in flo_files]
    flo_ins = [float(flo.split('_')[-2].strip('flo').strip('Down').strip('Up')) for flo in flo_files]
    flo_ins = np.sort(np.unique(flo_ins))
    flo_nom = flo_ins[1]

    #for flo_in in flo_ins[1:2]:
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
        #samples = [sample_data, sample_hgg]
        samples = [sample_data]
        mh_regions = ['sr']
        load_hists(h, hf, samples, mh_regions, distns, ma_blind_input, workdir)

        ## raw mh-SR, hgg
        # Use hgg template with phoid+trg SFs applied
        workdir = '%s/%s/Templates/systNom_nom'%(input_dir, hgg_campaign)
        samples = [sample_hgg]
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
        print('.. sblo', 3, 15, h[ksblo].GetBinContent(3, 15), h[ksblo].GetBinError(3, 15))
        print('.. sbhi', 3, 15, h[ksbhi].GetBinContent(3, 15), h[ksbhi].GetBinError(3, 15))
        print('.. sb2sr', 3, 15, h[ksb2sr].GetBinContent(3, 15), h[ksb2sr].GetBinError(3, 15))
        print('.. h[%s].Integral(): %f'%(ksb2sr, h[ksb2sr].Integral()))

        ## Get shifted bkg model
        #if flo_in == flo_nom:

        #    print('   >> Adding pt weight uncertainties')
        #    hshift, hfshift = {}, {}
        #    for shift in ['Down', 'Up']:

        #        print('   .. Getting shift:',shift)
        #        hshift[shift], hfshift[shift] = {}, {}
        #        load_hists(hshift[shift], hfshift[shift], [sample], mh_regions, distns, ma_blind_input, workdir+shift)
        #        #print('.. ',hshift[shift].keys())

        #    for ksb in [ksblo, ksbhi]:
        #        print('   .. Doing mhsb:',ksb)
        #        #kratio = tgt+'%s_ratioClone%s'%(k, shift)
        #        #h[kratio] = h[tgt+'%s_ratio'%k].Clone()
        #        #h[kratio].SetName(kratio)
        #        for ix in range(h[ksb].GetNbinsX()+2):
        #            for iy in range(h[ksb].GetNbinsY()+2):
        #                #if ix != 3: continue
        #                #if iy != 15: continue
        #                bincnom = h[ksb].GetBinContent(ix, iy)
        #                binerrnom = h[ksb].GetBinError(ix, iy)
        #                #bincup = hshift['Up'][ksb].GetBinContent(ix, iy)
        #                #bincdn = hshift['Down'][ksb].GetBinContent(ix, iy)
        #                bincup = abs(hshift['Up'][ksb].GetBinContent(ix, iy)-bincnom)
        #                bincdn = abs(hshift['Down'][ksb].GetBinContent(ix, iy)-bincnom)
        #                bincdiff = np.max([bincup, bincdn])
        #                binerrtot = np.sqrt(binerrnom*binerrnom + bincdiff*bincdiff)
        #                if bincnom = 0.:
        #                    binerrtot = 0.
        #                #print(ix, iy, bincnom, binerrnom, bincup, bincdn, bincdiff, binerrtot)
        #                h[ksb].SetBinError(ix, iy, binerrtot)
        #                #print(ix, iy, h[ksb].GetBinContent(ix, iy), h[ksb].GetBinError(ix, iy))

        #combine_sblohi(h, flo_in, flo_nom, ksblo, ksbhi, ksb2sr)
        #print('.. sblo', 3, 15, h[ksblo].GetBinContent(3, 15), h[ksblo].GetBinError(3, 15))
        #print('.. sbhi', 3, 15, h[ksbhi].GetBinContent(3, 15), h[ksbhi].GetBinError(3, 15))
        #print('.. sb2sr', 3, 15, h[ksb2sr].GetBinContent(3, 15), h[ksb2sr].GetBinError(3, 15))
        #print('.. h[%s].Integral(): %f'%(ksb2sr, h[ksb2sr].Integral()))

        h[ksb2sr].Scale(sb2sr_norm)
        print('.. h[%s].Integral(): %f'%(ksb2sr, h[ksb2sr].Integral()))

        '''
        [DEPRECATED]:
        # Calculate fhgg over full, unblinded (2d-pt) evt yields (same as for flo)
        # If only using blinded 2d-ma, can give skewed estimates of true hgg xsec yield
        khgg_2dpt = '%s_sr_%s'%(sample_hgg, k2dpt)
        ksr_2dpt = '%s_sr_%s'%(sample_data, k2dpt)
        '''

        # Get total hgg gen events for this sample/year
        nevtsgen[sample_hgg] = get_mcgenevents(sample_hgg, input_dir, hgg_campaign, skim_campaign)
        print('.. nevtsgen[%s]: %f'%(sample_hgg, nevtsgen[sample_hgg]))
        # Get hgg 2dma yield in diag_lo_hi-blinded region (mH-SR & ma-SB)
        khgg = '%s_sr_%s'%(sample_hgg, k2dma)
        khgg_blind = '%s-%s'%(khgg, ma_blind_norm)
        hblind[khgg_blind] = h[khgg].Clone()
        hblind[khgg_blind].SetName(khgg_blind)
        blind_hist(hblind[khgg_blind], to_blind=ma_blind_norm)

        # Loop over hgg xsecs:
        # If doing non-flo_nom, only need to do nom xsec
        xsecs = [xs_hgg_lo, xs_hgg, xs_hgg_hi] if flo_in == flo_nom else [xs_hgg]
        for xs in xsecs:

            '''
            [DEPRECATED]:
            fhgg = br_hgg*xsec_hgg*intlumi[r]*nevts[khgg_2dpt]/nhgg[r]
            fhgg /= nevts[ksr_2dpt]
            print('  .. fhgg, 2017:', fhgg)
            if sel == 'nom':
                fhgg = 0.00395577246287 if xsec_hgg == xs_nom else 0.00458804756964
            else:
                fhgg = 3.84666817207e-05 if xsec_hgg == xs_nom else 4.46150447826e-05
            '''
            print('  >> Doing xs_hgg:',xs)

            # Calculate fhgg using diag_lo_hi-blinded region:
            # f_hgg = ( intlumi * xs * br * N_hgg,sel / N_hgg,gen ) / N_sel,data
            # where N_sel,data = sr_blind_yield, for sel = (mH-SR & ma-SB)
            #print('nhgg_gen:',nevtsgen[sample_hgg])
            #print('hblind[ksr_blind].Integral():',sr_blind_yield)
            #print('nhggsel:',hblind[khgg_blind].Integral())
            #print('intlumi[r]:',intlumi[r])
            #print('xs_hgg:',xs)
            #print('br_hgg:',br_hgg)
            fhgg = ( intlumi[r] * xs * br_hgg * hblind[khgg_blind].Integral() ) / ( nevtsgen[sample_hgg] * sr_blind_yield )

            # fsb is then the complement
            fsb = 1.-fhgg
            print('  .. fhgg:',fhgg)
            print('  .. fsb:',fsb)

            # Now, normalize full 2dma hgg template
            # Normalize hgg template s.t. diag_lo_hi-blinded hgg yield matches corresponding yield in data(mh-SR & ma-SB)
            # Required to preserve norm of total SB+hgg template in diag_lo_hi-blinded 2d-ma
            hgg2sr_norm = sr_blind_yield/hblind[khgg_blind].Integral()
            #h[khgg].Scale(hgg2sr_norm) # will get overwritten!! apply as a scale when adding hgg to total bkg instead, as below

            # Combine existing full 2dma mh-SBlo+hi template with hgg template:
            # fsb*data(mh-SBlo+hi) + fgg*hgg(mh-SR)
            ksb2sr_hgg = '%s_sb2sr+hgg_%s'%(sample_data, k2dma)
            h[ksb2sr_hgg] = h[ksb2sr].Clone()
            h[ksb2sr_hgg].SetName(ksb2sr_hgg)
            h[ksb2sr_hgg].Scale(fsb)
            #h[ksb2sr_hgg].Add(h[khgg], fhgg)
            h[ksb2sr_hgg].Add(h[khgg], fhgg*hgg2sr_norm)
            print('  .. h[%s].Integral(): %f'%(ksb2sr_hgg, h[ksb2sr_hgg].Integral()))

            print('.. sb2sr+hgg', 3, 15, h[ksb2sr_hgg].GetBinContent(3, 15), h[ksb2sr_hgg].GetBinError(3, 15))

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
            #if fhgg < fhgg_nom:
            #    syst_str += '_hggDn'
            #elif fhgg > fhgg_nom:
            #    syst_str += '_hggUp'
            if xs < xs_hgg:
                syst_str += '_hggDn'
            elif xs > xs_hgg:
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
