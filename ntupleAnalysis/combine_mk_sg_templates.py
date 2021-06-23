from __future__ import print_function
#import numpy as np
import ROOT
import os, glob, re
from data_utils import *
from hist_utils import *
from template_utils import *

#eos_basedir = '/store/user/lpchaa4g/mandrews/Run2'
#eos_basedir = '/eos/uscms/store/user/lpchaa4g/mandrews/2017/sg-Era04Dec2020v2/Templates/systNom_nom'
#eos_basedir = '/eos/uscms/store/user/lpchaa4g/mandrews'
eos_basedir = '/store/user/lpchaa4g/mandrews'
#input_dir = '%s/%s'%(eos_redir, eos_basedir)
input_dir = 'Templates'
k2dma = 'ma0vma1'
distns = [k2dma]
ma_blind_input = None
ma_blind_output = 'offdiag_lo_hi'

# g/mandrews/2018/bkgNoPtWgts-Era04Dec2020v2/bdtgtm0p98_relChgIsolt0p05_etalt1p44/
#campaign = 'systTEST'
campaign = 'sg-Era04Dec2020v2'
print('>> Signal selection campaign:',campaign)

sub_campaign = '' # nominal
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p05_etalt1p44/nom-inv' # a0nom-a1inv
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p05_etalt1p44/nom-nom' # a0nom-a1nom
#sub_campaign = 'bdtgtm0p99_relChgIsolt0p05_etalt1p44/nom-nom' # bdt > -0.99
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p05_etalt1p44/nom-nom' # bdt > -0.96
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p03_etalt1p44/nom-nom' # relChgIso < 0.03
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p07_etalt1p44/nom-nom' # relChgIso < 0.07
print('>> sub-campaign:',sub_campaign)
#outdir = '%s/%s/Templates_sg'%(input_dir, campaign)
#run_eosmkdir(outdir)

#h24gamma_1j_1M_1GeV
#ksg = 'h4g'
ksg = 'h24gamma_1j_1M_'
#samples = {}
#samples[ksg+'2017'] = [
#        '1'
#        ]

#systs = {}
#systs['Nom'] = ['nom']
#systs['PhoIdSF'] = ['dn', 'up']
#systs['Scale'] = ['dn', 'up']
#systs['Smear'] = ['dn', 'up']
#mh_regions = ['sr']
mh_region = 'sr'

#make_plots = True
make_plots = False

r = '2017'

cwd = os.getcwd()+'/'

runs = ['2016', '2017', '2018']

for r in runs:

    print('>> Doing run:', r)

    workdir = '%s/%s/%s/%s/Templates'%(eos_basedir, r, campaign, sub_campaign)
    print('.. input dir:', workdir)

    systs = run_eosls(workdir) # returns dirs in relative path only
    assert(len(systs) >= 1)

    for syst in systs:

        print('   >> Doing syst:', syst)
        if 'TEST' in syst: continue

        # Get list of samples
        syst_dir = '%s/%s'%(workdir, syst)
        sample_files = run_eosls(syst_dir)
        sample_files = [s for s in sample_files if 'templates.root' in s]
        samples = set([s.split('_')[0] for s in sample_files]) # in case of multiple mH regions, get unique sample names
        samples = sorted(samples)
        #print(samples)
        #print('   .. Doing sample: Doing syst:', syst)

        #sample_list = samples[ksg+r]
        #sample_list = ['%s%sGeV'%(ksg, s) for s in sample_list]
        #print(sample_list)
        #workdir = '%s/%s/%s%s/syst%s_%s'%(input_dir, campaign, 'h4g', r, syst, shift)
        #print('    .. workdir:', workdir)

        for i,s in enumerate(samples):

            print('      >> Doing sample:', s)

            c, h, hblind, hf = {}, {}, {}, {}
            #load_hists(h, hf, [s], mh_regions, distns, ma_blind_input, '%s/%s'%(eos_redir, syst_dir))
            load_hists(h, hf, [s], [mh_region], distns, ma_blind_input, '%s/%s'%(eos_redir, syst_dir))
            #print(h.keys())

            #ksrc = '%s_sr_%s'%(s, k2dma)
            ksrc = '%s_%s_%s'%(s, mh_region, k2dma)
            print('      .. nevts[%s]: %f'%(ksrc, h[ksrc].Integral()))

            #kblind = '%s2017_sr_%s-%s'%(s, k2dma, ma_blind_output)
            kblind = '%s-%s'%(ksrc, ma_blind_output)
            hblind[kblind] = h[ksrc].Clone()
            hblind[kblind].SetName(kblind)
            hblind[kblind].SetTitle(kblind)
            blind_hist(hblind[kblind], to_blind=ma_blind_output)
            hblind[kblind].GetXaxis().SetRangeUser(0., 1.2)
            hblind[kblind].GetYaxis().SetRangeUser(0., 1.2)
            print('      .. nevts[%s]: %f'%(kblind, hblind[kblind].Integral()))

            if make_plots:
                c[kblind] = ROOT.TCanvas(kblind+'_', kblind+'_', wd, ht)
                hblind[kblind].Draw('COL Z')
                c[kblind].Draw()
                c[kblind].Update()

            # Write to file
            outpath = '%s/%s/%s'%(eos_redir, syst_dir, sample_files[i].replace(str(ma_blind_input), ma_blind_output))
            print('      .. writing to:',outpath)
            #hfout = ROOT.TFile.Open(outpath, 'RECREATE')
            #for k in hblind:
            #    hblind[k].Write()
            #hfout.Close()
#'''
