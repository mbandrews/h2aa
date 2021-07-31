from __future__ import print_function
#import numpy as np
import ROOT
import os, glob, re
#from root_numpy import hist2array
from data_utils import *
from hist_utils import *

'''
Calculate 2d pt wgts to map data mH-SB 2d pt distn -> data mH-SR pt distn for a given f_SBlow `flo`.
If doing full run2, make sure to use bkg processing with full run2 stats as opposed to yr-by-yr stats
(as is used for making bkg templates, see mk_bkg_templates.py).
'''
eos_basedir = 'root://cmseos.fnal.gov//store/user/lpchaa4g/mandrews'

#sample = 'Run2017'
#campaign = 'Run2/runBkg_noptwgts_bdtgtm0p99-v1'
#in_campaign = 'bkgNoPtWgts-Era04Dec2020v1' # missing 2018A, 2016H+2018 failed lumis
#in_campaign = 'bkgNoPtWgts-Era04Dec2020v2' # 2016H+2018 failed lumis still
#in_campaign = 'bkgNoPtWgts-Era04Dec2020v3' # redo v2 with nVtx, PU plots
in_campaign = 'bkgNoPtWgts-Era22Jun2021v1' # data, h4g, hgg: redo with mgg95 trgs. [Note:new EB-only AOD skims]
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
#sel = 'nom'
sel = 'inv'

norm_scale = 150.e3
distn = 'pt0vpt1'
ma_blind = None
mh_regions = ['sblo', 'sr', 'sbhi']
#flo_ins = [0.504, None, 0.791] if sel == 'nom' else [0.406, None, 1.000]
# Calculated using: https://docs.google.com/spreadsheets/d/1D8ztbh1WtCnSGJ_E0KQC0I5CEN0g61HQU4-XcfSm3iQ/edit#gid=777269656 -> nom-*, mgg90v1
flo_ins = [0.6228, None, 0.6722] if sel == 'nom' else [0.5233, None, 0.8256]
#flo_in = None
#flo = 0.888
#ceil = 10.

#runs = ['2016', '2017', '2018']
runs = ['Run2'] # use full run2 stats
for r in runs:

    print('>> Doing run:',r)

    #if r != '2016': continue

    #sample = 'data%s'%r
    sample = 'data' if r == 'Run2' else 'data%s'%r
    campaign = '%s/%s/%s/nom-%s'%(r, in_campaign, sub_campaign, sel)

    indir = '%s/%s/Templates'%(eos_basedir, campaign)
    outdir = '%s/%s/Weights'%(eos_basedir, campaign)
    run_eosmkdir(outdir)

    h, hf = {}, {}
    s = sample
    k = distn
    tgt = 'sr'

    for flo_in in flo_ins:

        load_hists(h, hf, [sample], mh_regions, [distn], ma_blind, input_dir=indir)

        # Get "natural" flo if not user-specified
        if flo_in is None:
            flo = h['%s_sblo_%s'%(s, k)].Integral()/(h['%s_sblo_%s'%(s, k)].Integral()+h['%s_sbhi_%s'%(s, k)].Integral())
            print('Nsblo:%f, Nsbhi:%f, Nsr:%f'%(\
                    h['%s_sblo_%s'%(s, k)].Integral(),\
                    h['%s_sbhi_%s'%(s, k)].Integral(),\
                    h['%s_%s_%s'%(s, tgt, k)].Integral()))
        else:
            flo = flo_in

        print('   >> For flo:',flo)

        #s = sample
        #k = distn
        #tgt = 'sr'

        # Normalize histograms to norm_scale
        h['%s_%s_%s'%(s, tgt, k)].Scale(norm_scale/h['%s_%s_%s'%(s, tgt, k)].Integral())
        h['%s_sblo_%s'%(s, k)].Scale(norm_scale/h['%s_sblo_%s'%(s, k)].Integral())
        h['%s_sbhi_%s'%(s, k)].Scale(norm_scale/h['%s_sbhi_%s'%(s, k)].Integral())

        # Add normalized SB-lo,hi hists in fracs: flo, 1.-flo
        kcombo = '%s_sbcombo_%s'%(s, k)
        h[kcombo] = h['%s_sblo_%s'%(s, k)].Clone()
        #print('sb-lo integral, pre-scale:',h[kcombo].Integral())
        h[kcombo].Scale(flo)
        #print('sb-lo integral, post-scale:',h[kcombo].Integral())
        h[kcombo].Add(h['%s_sbhi_%s'%(s, k)], (1.-flo))
        #print('sb-lo+hi integral, post-scale:',h[kcombo].Integral())

        # SB->SR weights given by ratio SR/SB
        h[tgt+'%s_ratio'%k] = h['%s_%s_%s'%(s, tgt, k)].Clone()
        h[tgt+'%s_ratio'%k].Divide(h[kcombo])
        print(h[tgt+'%s_ratio'%k].GetMaximum())
        print(h[tgt+'%s_ratio'%k].GetMinimum())
        # NOTE: Apply ceiling during pt look-up in actual bkg event loop instead of here
        #for ix in range(1, h[tgt+'%s_ratio'%k].GetNbinsX()+1):
        #    for iy in range(1, h[tgt+'%s_ratio'%k].GetNbinsY()+1):
        #        binc = h[tgt+'%s_ratio'%k].GetBinContent(ix, iy)
        #        if binc > ceil:
        #            h[tgt+'%s_ratio'%k].SetBinContent(ix, iy, ceil)
        #print(h[tgt+'%s_ratio'%k].GetMaximum())
        #print(h[tgt+'%s_ratio'%k].GetMinimum())

        # Save all histograms for reference
        #flo_str = '%.3f'%flo if flo_in is not None else str(flo_in)
        flo_str = '%.4f'%flo
        outpath = "%s/%s_sb2%s_blind_%s_flo%s_ptwgts.root"%(outdir, s, tgt, ma_blind, flo_str)
        print('      .. output file:',outpath)
        hf[tgt+'ratios'] = ROOT.TFile.Open(outpath, "RECREATE")
        h['%s_%s_%s'%(s, tgt, k)].SetName('%s_%s_%s'%(s, tgt, k))
        h['%s_%s_%s'%(s, tgt, k)].Write()
        h['%s_sblo_%s'%(s, k)].SetName('%s_sblo_%s'%(s, k))
        h['%s_sblo_%s'%(s, k)].Write()
        h['%s_sbhi_%s'%(s, k)].SetName('%s_sbhi_%s'%(s, k))
        h['%s_sbhi_%s'%(s, k)].Write()
        h[kcombo].SetName(kcombo)
        h[kcombo].Write()
        h[tgt+'%s_ratio'%k].SetName('%s_ratio'%k)
        h[tgt+'%s_ratio'%k].Write()
        hf[tgt+'ratios'].Close()
