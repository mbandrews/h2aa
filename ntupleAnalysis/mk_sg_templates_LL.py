from __future__ import print_function
#import numpy as np
import ROOT
import os, glob, re
from data_utils import *
from hist_utils import *
from template_utils import *

'''
Construct 2d-ma signal templates
Applyind 2d-ma blinding as specified by `ma_blind_output`
Normalize to appropriate yr's data lumi
Introduce syst wrt data lumi uncert.
'''
#eos_basedir = '/store/user/lpchaa4g/mandrews/Run2'
#eos_basedir = '/eos/uscms/store/user/lpchaa4g/mandrews/2017/sg-Era04Dec2020v2/Templates/systNom_nom'
#eos_basedir = '/eos/uscms/store/user/lpchaa4g/mandrews'
eos_basedir = '/store/user/lpchaa4g/mandrews'
#input_dir = '%s/%s'%(eos_redir, eos_basedir)
input_dir = 'Templates'
k2dma = 'ma0vma1'
distns = [k2dma]
#distns = [k2dma, 'ma0', 'ma0']
ma_blind_input = None
ma_blind_output = 'offdiag_lo_hi'
#ma_blind_output = 'diag_lo_hi' # for making unblinded plots in plot_2dma.py: both offdiag+diag blinding needed

# g/mandrews/2018/bkgNoPtWgts-Era04Dec2020v2/bdtgtm0p98_relChgIsolt0p05_etalt1p44/
#campaign = 'systTEST'
#campaign = 'sg-Era04Dec2020v2' # sg selection + bdt/chgiso scans. 2016,2018: no phoid, ma scale+smear
#campaign = 'sg-Era04Dec2020v3' # use old (bdt+chgiso cuts) 2017 s+s for all yrs
#campaign = 'sg-Era04Dec2020v4' # 2016-18 SFs. 2017-18 ss. 2016 ss uses 2017.
#campaign = 'sg-Era04Dec2020v5' # v4 + nominals use best-fit ss over full m_a, shifted uses best-fit ss over ele peak only.
#campaign = 'sg-Era04Dec2020v6' # 2016-18 phoid, 2016-18 ss. ss implemented only for shifted syst (as in v4)
#campaign = 'sg-Era22Jun2021v1' # h4g, hgg: mgg95 trgs, w/ HLT, no trgSF. gg:ggNtuples-Era20May2021v1_ggSkim-v1 + img:Era22Jun2021_AOD-IMGv1
#campaign = 'sg-Era22Jun2021v2' # h4g, hgg: w/o HLT applied, with trgSF. gg:ggNtuples-Era20May2021v1_ggSkim-v2 + img:Era22Jun2021_AOD-IMGv2
#campaign = 'sg-Era22Jun2021v3' # v2 + interpolated masses
#campaign = 'sg-Era22Jun2021v4' # duplicate of v3 + ss with SFs + (xs_sg = 0.05pb for by era but xs_sg = 1pb for run2 for making plots)
#campaign = 'sg-Era22Jun2021v5' # duplicate of v3 + ss with SFs + (xs_sg = 1pb for all)
#campaign = 'sg-Era22Jun2021v6' # v5 but with 50MeV
#campaign = 'sg-Era18Nov2021v1' # h4g 2017 LL, w/o HLT
campaign = 'sg-Era18Nov2021v2' # h4g 2017 LL fixed tau units, w/o HLT
print('>> Signal selection campaign:',campaign)

sel = 'nom'
#sel = 'inv'
#sub_campaign = '' # nominal
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p05_etalt1p44/nom-inv' # a0nom-a1inv
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p05_etalt1p44/nom-nom' # a0nom-a1nom
#sub_campaign = 'bdtgtm0p99_relChgIsolt0p05_etalt1p44/nom-nom' # bdt > -0.99
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p05_etalt1p44/nom-nom' # bdt > -0.96
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p03_etalt1p44/nom-nom' # relChgIso < 0.03
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p07_etalt1p44/nom-nom' # relChgIso < 0.07
#sub_campaign = 'bdtgtm0p99_relChgIsolt0p03_etalt1p44/nom-nom' # bdt > -0.99, relChgIso < 0.03
sub_campaign = 'bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-%s'%sel # bdt > -0.96, relChgIso < 0.07 !! optimal
#sub_campaign = 'bdtgtm0p97_relChgIsolt0p06_etalt1p44/nom-nom' # bdt > -0.97, relChgIso < 0.06
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p09_etalt1p44/nom-nom' # bdt > -0.96, relChgIso < 0.09
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p08_etalt1p44/nom-nom' # bdt > -0.96, relChgIso < 0.08

print('>> sub-campaign:',sub_campaign)

# ggSkim campaign
# For mc->data normalization
#ggntuple_campaign = 'Era04Dec2020v1_ggSkim-v1' # fixed h4g mc triggers
#ggntuple_campaign = 'Era20May2021v1_ggSkim-v1' # h4g, hgg: mgg95 trgs, w/ HLT req
#ggntuple_campaign = 'Era20May2021v1_ggSkim-v2' # h4g, hgg: mgg95 trgs, no HLT req
#ggntuple_campaign = 'Era20May2021v1_ggSkim-v'+campaign[-1]
#ggntuple_campaign = 'Era20May2021v1_ggSkim-v2'
#ggntuple_campaign = 'Era18Nov2021v1_ggSkim-v1' # h4g 2017, LL
ggntuple_campaign = 'Era18Nov2021v2_ggSkim-v1' # h4g 2017, LL fixed tau units
xs_sg = 1. #pb
#xs_sg = 0.05 #pb
#xs_sg = 0.05104 #pb
# Official lumis: https://twiki.cern.ch/twiki/bin/view/CMS/TWikiLUM
#tgt_lumis = {'2016': 36.33e3, #35.92e3,
#             '2017': 41.53e3,
#             '2018': 59.74e3} # /pb.
# Estimated lumis modulo missing lumis: https://docs.google.com/spreadsheets/d/1wmDcb88uJfgJakIE9BfKfHXU_sb1ldy6NArZZzr0fRk/edit#gid=0
# Calculated using:
#   [1] cmslpc:~mba2012/nobackup/h2aa/CMSSW_10_5_0/src/h2aa/crab/run_getLumis.py
#   [2] lxplus:~mandrews/work/h2aa/brilcalc_work/getLumis_byEra.sh
tgt_lumis = {'2016': 36.25e3,
             '2017': 41.53e3,
             '2018': 58.75e3} # /pb. Run2: 136.53/pb
lumi_uncerts = {'2016': 0.012, #0.025,
                '2017': 0.023,
                '2018': 0.025} # f_lumi

mh_region = 'sr'

#make_plots = True
make_plots = False

syst_nom = 'systNom_nom'
syst_lumi = 'systLumi'
cwd = os.getcwd()+'/'

runs = ['2016', '2017', '2018']
runs = ['2017']

for r in runs:

    #if r != '2018': continue
    print('>> Doing run:', r)

    workdir = '%s/%s/%s/%s/Templates'%(eos_basedir, r, campaign, sub_campaign)
    print('.. input dir:', workdir)

    systs = run_eosls(workdir) # returns dirs in relative path only
    assert(len(systs) >= 1)
    for syst in systs:

        #if syst != syst_nom: continue # DEBUG: for printing out ma-ROI only
        if 'TEST' in syst: continue
        if 'Lumi' in syst: continue # lumi syst derived separately by shifting sytNom_nom
        print('   >> Doing syst:', syst)

        # Get list of samples
        syst_dir = '%s/%s'%(workdir, syst)
        sample_files = run_eosls(syst_dir)
        sample_files = [s for s in sample_files if 'templates.root' in s]
        samples = set([s.split('_')[0] for s in sample_files]) # in case of multiple mH regions, get unique sample names
        samples = sorted(samples)
        #print(samples)

        for i,s in enumerate(samples):

            #if 'mA0p1GeV' not in s: continue
            #if 'mA0p2GeV' not in s: continue
            #if 'mA0p4GeV' not in s: continue
            #if ('mA1p2GeV' not in s) and ('mA1p1GeV' not in s) and ('mA1p0GeV' not in s): continue # DEBUG: for verifying interpolation
            #if ('mA0p2GeV' not in s) and ('mA0p3GeV' not in s) and ('mA0p4GeV' not in s): continue # DEBUG: for verifying interpolation
            #if ('mA0p5GeV' not in s) and ('mA0p4GeV' not in s) and ('mA0p6GeV' not in s): continue # DEBUG: for verifying interpolation
            #if ('mA0p1GeV' not in s) and ('mA0p4GeV' not in s) and ('mA1p0GeV' not in s): continue # DEBUG: for printing out ma-ROI only
            if 'hgg' in s: continue
            print('      >> Doing sample:', s)

            c, h, hblind, hf = {}, {}, {}, {}
            #load_hists(h, hf, [s], mh_regions, distns, ma_blind_input, '%s/%s'%(eos_redir, syst_dir))
            load_hists(h, hf, [s], [mh_region], distns, ma_blind_input, '%s/%s'%(eos_redir, syst_dir))
            #print(h.keys())

            #ksrc = '%s_sr_%s'%(s, k2dma)
            ksrc = '%s_%s_%s'%(s, mh_region, k2dma)
            print('      .. nevts[%s]: %f'%(ksrc, h[ksrc].Integral()))

            # Apply 2d-ma blinding
            #kblind = '%s2017_sr_%s-%s'%(s, k2dma, ma_blind_output)
            kblind = '%s-%s'%(ksrc, ma_blind_output)
            hblind[kblind] = h[ksrc].Clone()
            hblind[kblind].SetName(kblind)
            hblind[kblind].SetTitle(kblind)
            blind_hist(hblind[kblind], to_blind=ma_blind_output)
            hblind[kblind].GetXaxis().SetRangeUser(0., 1.2)
            hblind[kblind].GetYaxis().SetRangeUser(0., 1.2)
            print('      .. nevts[%s]: %f'%(kblind, hblind[kblind].Integral()))

            # Get mc->data lumi normalization
            #mcnorm = get_mc2data_norm(s, ggntuple_campaign, tgt_lumis[r], xsec=xs_sg)
            #mcnorm = get_mc2data_norm_interp(s, ggntuple_campaign, tgt_lumis[r], xsec=xs_sg)
            s_edit = s.replace('ctau', 'tau').strip('mm') # forgot to fix names in ggntuples
            mcnorm = get_mc2data_norm_interp(s_edit, ggntuple_campaign, tgt_lumis[r], xsec=xs_sg)
            hblind[kblind].Scale(mcnorm)
            print('      .. nevts[%s], mc2data: %f'%(kblind, hblind[kblind].Integral()))

            if make_plots:
                c[kblind] = ROOT.TCanvas(kblind+'_', kblind+'_', wd, ht)
                hblind[kblind].Draw('COL Z')
                c[kblind].Draw()
                c[kblind].Update()

            #''' # comment below if DEBUG: for printout out ma-ROI only
            # Write to file
            outpath = '%s/%s/%s_%s_blind_%s_templates.root'%(eos_redir, syst_dir, s, mh_region, ma_blind_output)
            print('      .. writing to:',outpath)

            hfout = ROOT.TFile.Open(outpath, 'RECREATE')
            for k in hblind:
                hblind[k].Write()
            hfout.Close()

            # Do lumi shifts of nominal template
            if syst == syst_nom:
                print('         >> Doing lumi syst...')

                hlumi = {}
                for shift in ['up', 'dn']:

                    print('         .. doing shift:', shift)
                    hlumi[shift] = hblind[kblind].Clone()
                    # lumi_uncert = total 1sg band => shift = `lumi_uncert`/2.
                    lumi_scale = lumi_uncerts[r]/2.
                    lumi_scale = 1. + lumi_scale if shift == 'up' else 1. - lumi_scale
                    hlumi[shift].Scale(lumi_scale)
                    print('         .. nevts[%s]: %f (%f)'%(hlumi[shift].GetName(),
                                                            hlumi[shift].Integral(),
                                                            (hlumi[shift].Integral()/hblind[kblind].Integral())-1.))
                    #outdir = '%s/%s/Templates_sg'%(input_dir, campaign)
                    #run_eosmkdir(outdir)

                    # Write to file
                    lumi_dir = '%s/%s_%s'%(workdir, syst_lumi, shift)
                    run_eosmkdir(lumi_dir)
                    outpath = '%s/%s/%s_%s_blind_%s_templates.root'%(eos_redir, lumi_dir, s, mh_region, ma_blind_output)
                    print('         .. writing to:', outpath)

                    hfout = ROOT.TFile.Open(outpath, 'RECREATE')
                    hlumi[shift].Write()
                    hfout.Close()

            #''' # end of DEBUG
#'''
