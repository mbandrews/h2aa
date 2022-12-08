from __future__ import print_function
import ROOT
import numpy as np
from array import array
from hist_utils import *
from data_utils import *
import CMS_lumi

# Plot nVtx
# For reference comparison, see: https://twiki.cern.ch/twiki/bin/viewauth/CMS/PileupJSONFileforData

ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
#change the CMS_lumi variables (see CMS_lumi.py)
CMS_lumi.lumi_7TeV = "4.8 fb^{-1}"
CMS_lumi.lumi_8TeV = "18.3 fb^{-1}"
CMS_lumi.writeExtraText = 1
#CMS_lumi.extraText = "Simulation"
CMS_lumi.extraText = "Preliminary"
#CMS_lumi.lumi_sqrtS = "41.9 fb^{-1} (13 TeV)" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
#iPos = 11 # CMS in frame
iPos = 0 # CMS above frame
if iPos == 0:
    CMS_lumi.relPosX = 0.15
iPeriod = 0

def get_proc(k):
    proc = k.split('_')[0].split('-')[-1].replace(run, '')
    return proc

def get_proc(key):
    if 'qcd' in key:
        proc = 'dijet + #gamma+jet'
    elif 'diphoton' in key:
        proc = '#gamma#gamma'
    elif 'hgg' in key:
        proc = 'H#rightarrow#gamma#gamma'
    else:
        proc = 'data'
    return proc

def draw_hist_1dptstacked(ks, mh_region, ymax=None, range_minmax=[25., 125.], scale_qcd=False):

    kdata = [k for k in ks if 'data' in k]
    assert len(kdata) == 1
    kdata = kdata[0]

    kqcd = [k for k in ks if 'qcd' in k]
    assert len(kqcd) == 1
    kqcd = kqcd[0]

    # scale up qcd only
    #nevts = {}
    #for k in ks:
    #    print('.. %s, integral: %.f'%(k, hProc[k].Integral()))
    #    #proc = k.split('_')[0].split('-')[-1].replace(run, '')
    #    #print(proc)
    #    nevts[proc] = hProc[k].Integral()
    nDataNotQCD = hProc[kdata].Integral() - sum(hProc[k].Integral() for k in ks if (k is not kdata) and (k is not kqcd))
    #print(nDataNotQCD, hProc[kqcd].Integral())
    norm_qcd = nDataNotQCD/hProc[kqcd].Integral()
    print('.. norm qcd2data:',norm_qcd)
    hProc[kqcd].Scale(norm_qcd)

    err_style = 'E2'
    fill_style = 3002
    #wd, ht = int(440*1), int(400*1)
    #wd, ht = int(640*1), int(580*1)
    wd, ht = int(640*1), int(680*1)
    #ROOT.TGaxis.fgMaxDigits = 3
    #ROOT.gStyle.SetErrorX(0)

    k = kdata
    #c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
    c[k+'stack'] = ROOT.TCanvas("c%s_stacked"%k,"c%s_stacked"%k,wd,ht)

    pUp = ROOT.TPad("upperPad", "upperPad",.005, .300, .995, .995) # (,,Double_t xlow, Double_t ylow, Double_t xup, Double_t yup,...)
    pDn = ROOT.TPad("lowerPad", "lowerPad",.005, .005, .995, .300)
    pUp.Draw()
    pDn.Draw()
    #pUp.SetMargin(13.e-02,3.e-02,2.e-02,9.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pUp.SetMargin(15.e-02,3.e-02,2.e-02,9.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pDn.SetMargin(15.e-02,3.e-02,36.e-02,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)

    pUp.cd()

    hdummy = hProc[k].Clone()
    hdummy.Reset()
    hdummy = set_hist(hdummy, "p_{T}", "N_{a} / 25 GeV", "")
    hdummy.GetXaxis().SetTitle('')
    hdummy.GetXaxis().SetLabelSize(0.)
    #hdummy.GetYaxis().SetTitleOffset(0.9)
    hdummy.GetYaxis().SetTitleOffset(1.1)
    hdummy.GetYaxis().SetTitleSize(0.07)
    hdummy.GetYaxis().SetLabelSize(0.06)
    hdummy.GetYaxis().SetMaxDigits(3)
    #hdummy.SetLineColor(0)
    hdummy.Draw("hist")

    hstack = ROOT.THStack("hs","hs")
    hmc = hProc[kqcd].Clone()
    hmc.Reset()
    hmc.SetName('mc')
    hmc.SetTitle('mc')
    for i,key in enumerate(ks):
        if key == kdata: continue
        print('Stacking:',key)
        hProc[key].SetFillStyle(3002)
        hProc[key].SetFillColor(colorByProc(key))
        hProc[key].SetLineColor(colorByProc(key))
        hstack.Add(hProc[key])
        hmc.Add(hProc[key])
    hstack.Draw("hist same")
    #hstack.Draw("hist nostack same")

    #hProc[k] = set_hist(hProc[k], "p_{T}", "N_{a}", "")
    hc[k] = hProc[k].Clone()
    hc[k].SetFillStyle(0)
    hc[k].SetMarkerStyle(20)
    hc[k].SetMarkerSize(0.85)
    #hc[k].GetXaxis().SetTitle('')
    #hc[k].GetXaxis().SetLabelSize(0.)
    #hc[k].GetYaxis().SetTitleOffset(0.9)
    #hc[k].GetYaxis().SetTitleSize(0.07)
    #hc[k].GetYaxis().SetLabelSize(0.06)
    #hc[k].GetYaxis().SetMaxDigits(3)
    ##hc[k].Draw("hist same")
    hc[k].Draw("E same")

    '''
    # SB
    #k = 'sb2sr_%s'%k_
    k = kmc
    print('kmc:',kmc, mcnorm)
    h[k].Scale(hc[kdata].Integral()/h[kmc].Integral())
    #h[k].Scale(mcnorm)
    print(h[k].Integral())
    h[k].SetLineColor(9)
    #h[k].Draw("hist SAME")
    h[k].SetFillColor(9)
    h[k].SetFillStyle(fill_style)
    h[k].Draw("%s same"%err_style)
    hc[k] = h[k].Clone()
    hc[k].SetLineColor(9)
    hc[k].SetFillStyle(0)
    hc[k].Draw("hist same")
    '''

    k = kdata
    '''
    ymax = 1.2*max(h[kdata].GetMaximum(), h[kmc].GetMaximum())
    if ymax_ == -1 and hc[k].GetBinContent(2) > 0.:
        #ymax = 1.2*hc[k].GetBinContent(2)
        ymax = 1.2*max(np.max([hc[kdata].GetBinContent(ib) for ib in range(2, hc[kdata].GetNbinsX()+2)]),
                       np.max([hc[kmc].GetBinContent(ib) for ib in range(2, hc[kmc].GetNbinsX()+2)]))
        #ymax = 1.2*np.max([hc[k].GetBinContent(ib) for ib in range(2, hc[k].GetNbinsX()+2)])
        #print(np.max([hc[k].GetBinContent(ib) for ib in range(2, hc[k].GetNbinsX()+2)]))
    #if ymax_ is not None and ymax_ > 0.:
    #    ymax = ymax_
    '''
    if ymax is None:
        ymax = 1.2*hProc[k].GetMaximum()
        #hdummy.GetYaxis().SetRangeUser(0.1, ymax)
        hdummy.GetYaxis().SetRangeUser(0., ymax)
    #if range_minmax is not None:
    hdummy.GetXaxis().SetRangeUser(range_minmax[0], range_minmax[1])
    ROOT.gPad.RedrawAxis()

    legend[k] = ROOT.TLegend(0.68, 0.62, 0.92, 0.86) #(x1, y1, x2, y2)
    for i,key in enumerate(ks):
        leg_marker = 'lep' if key == kdata else 'f'
        legend[k].AddEntry(key , get_proc(key), leg_marker)
    #legend[k].AddEntry(hc[kmc].GetName(),"Exp","l")
    legend[k].SetBorderSize(0)
    legend[k].Draw("same")

    CMS_lumi.cmsTextOffset = 0.1
    CMS_lumi.CMS_lumi(pUp, iPeriod, iPos)

    ##### Ratio plots on lower pad #####
    pDn.cd()
    pDn.SetTicky()
    pDn.SetGridy()

    fUnity = ROOT.TF1("fUnity","[0]",range_minmax[0], range_minmax[1])
    fUnity.SetParameter( 0,1. )

    fUnity.GetXaxis().SetTitle('p_{T}')
    fUnity.GetXaxis().SetTickLength(0.1)
    fUnity.GetXaxis().SetTitleOffset(1.05)
    fUnity.GetXaxis().SetTitleSize(0.16)
    fUnity.GetXaxis().SetLabelSize(0.14)

    dY = 0.199
    dY = 0.399
    dY = 0.99
    #fUnity.GetYaxis().SetTitle("SB/SR")
    fUnity.GetYaxis().SetTitle("Data/MC")
    #fUnity.GetYaxis().SetRangeUser(1.-dY,1.+dY)
    #fUnity.SetMaximum(1.+dY)
    #fUnity.SetMinimum(1.-dY)
    fUnity.SetMaximum(1.+dY)
    fUnity.SetMinimum(0.)
    fUnity.GetYaxis().SetNdivisions(305)
    fUnity.GetYaxis().SetTickLength(0.04)
    fUnity.GetYaxis().SetLabelFont(62)
    fUnity.GetYaxis().SetTitleFont(62)
    #fUnity.GetYaxis().SetTitleOffset(.4)
    fUnity.GetYaxis().SetTitleOffset(.5)
    fUnity.GetYaxis().SetTitleSize(0.16)
    fUnity.GetYaxis().SetLabelSize(0.14)

    fUnity.SetLineColor(9)
    fUnity.SetLineWidth(1)
    fUnity.SetLineStyle(7)
    fUnity.SetTitle("")
    fUnity.Draw()

    #'''
    k = kdata
    kr = kdata+'ratio'
    kstat = 'mcratiostat'
    hRatio[kr] = hProc[k].Clone()
    hRatio[kr].SetName(kr)
    hRatio[kstat] = hProc[k].Clone()
    hRatio[kstat].SetName(kstat)
    for ib in range(1, hRatio[kr].GetNbinsX()+1):
        binc_data = hRatio[kr].GetBinContent(ib)
        binerr_data = hRatio[kr].GetBinError(ib)
        binc_mc = hmc.GetBinContent(ib)
        binerr_mc = hmc.GetBinError(ib)
        # Data ratio pts
        if binc_mc > 0.:
            hRatio[kr].SetBinContent(ib, binc_data/binc_mc)
            hRatio[kr].SetBinError(ib, binerr_data/binc_data)
        # MC stat band
        hRatio[kstat].SetBinContent(ib, 1.)
        hRatio[kstat].SetBinError(ib, binerr_mc/binc_mc)
        #print(binerr_mc/binc_mc)
    #hRatio[kr].Divide(hmc)
    #hRatio[kr].Divide(hstack)
    # MC stat band
    hRatio[kstat].SetFillColor(9)
    hRatio[kstat].SetFillStyle(fill_style)
    hRatio[kstat].Draw("E2 same")
    # Data ratio pts
    hRatio[kr].SetLineColor(1)
    hRatio[kr].SetStats(0)
    hRatio[kr].SetMarkerStyle(20)
    hRatio[kr].SetMarkerSize(0.85)
    hRatio[kr].SetMarkerColor(1)
    hRatio[kr].Draw("ep same")
    #'''

    k = kdata+'stack'
    c[k].Draw()
    c[k].Update()
    #samples_str = '_'.join(samples)
    #c[k].Print('Plots/%s_dataomc_blind_%s_%s.eps'%(samples_str, blind, k))
    #c[k].Print('Plots/ptstack/%s_sb2srvsr_blind_%.eps'%('datavmc', 'pt'))
    #c[k].Print('Plots/ptstack/%s-%s_%s_mH-srv%s%s_sel-%s.pdf'%(distn, run, '-'.join(samplesByProc), mh_region, '2sr-flo%s'%flo if do_ptrwgt else '', sel))

# Plot pt

hf, h, hc = {}, {}, {}
hSample, hProc, hType = {}, {}, {}
c = {}
legend = {}
hRatio = {}

#run = 'Run2'
run = '2017'
eos_redir = 'root://cmseos.fnal.gov'
indir = '/store/user/lpchaa4g/mandrews/%s'%run
sub_campaign = 'bdtgtm0p96_relChgIsolt0p07_etalt1p44' # bdt > -0.96, relChgIso < 0.07 !! optimal

#bkgPtWgts_campaign = 'bkgPtWgts-Era04Dec2020v3' # only if using pt re-wgtd templates
#bkgNoPtWgts_campaign = 'bkgNoPtWgts-Era04Dec2020v2' #v3
bkgNoPtWgts_campaign = 'bkgNoPtWgts-Era22Jun2021v1'
#bgmc_campaign = 'bgmc-Era06Dec2020v1'
bgmc_campaign = 'bgmc-Era20May2021v1'
mablind = None
sel = 'nom'
sel = 'inv'
do_ptrwgt = False
#flo = '0.6437' # nominal

#distn = 'ptxy'
distn = 'nEvtsWgtd'
regions = ['sblo', 'sr', 'sbhi']
regionsByType = ['sblo', 'sr', 'sbhi']
#regionsByType = ['sb', 'sr']
samples = [
    'data',
    'hgg',
    'diphotonjets',
    'gjetPt20to40',
    'gjetPt40toInf',
    'qcdPt30to40',
    'qcdPt40toInf'
    ]
intlumi = {
    '2017': 41.53e3
    } # /pb
# define qcd to be either gjet or qcd
samplesByProc = [
    'data',
    'hgg',
    'diphotonjets',
    #'pho',
    'gjet',
    'qcd',
    ]
def qcdtype(k):
    #if 'gjet' in k:
    #    k = k.replace('gjet', 'qcd')
    #if 'hgg' in k or 'diphotonjets' in k:
    #    k = 'pho'
    return k
def colorByProc(key):
    if 'qcd' in key:
        return 2 #red
    #elif 'GJet' in key:
    #    return 4 #blue
    elif 'diphoton' in key:
        return 3 #green
    elif 'hgg' in key:
        return 5 # yellow
    else:
        return 1 # black
samplesByType = [
    'data',
    'bg'
    ]
xsec = {
    #'hgg': 33.14*2.27e-3, # gluon fusion hgg only
    'hgg': 50.94*2.27e-3, # total inclusive hgg
    'diphotonjets': 134.3,
    'gjetPt20to40': 232.8,#*0.0029,
    'gjetPt40toInf': 872.8,#*0.0558,
    'qcdPt30to40': 24750.0,#*0.0004*100.,
    'qcdPt40toInf': 117400.0,#*0.0026*100.,
    } #pb

#/eos/uscms/store/user/lpchaa4g/mandrews/2017/bgmc-Era06Dec2020v1/bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-nom/Templates/systNom_nom/

def get_ksr(run, s, r):
    if 'data' in s:
        ksr = '%s%s_%s'%(s, run, r)
    else:
        ksr = 'bg%s-%s_%s'%(run, s, r)
    return ksr

for s in samples:
    print('   >> sample:',s)
    for r in regions:

        # Get files
        # For data sample, if doing pt rwgt get re-wgtd SB templates from bkgPtWgts campaign
        if 'data' in s:
            '''
            if do_ptrwgt and 'sb' in r:
                # strictly only for data-SB
                # bkgPtWgts-Era04Dec2020v3/bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-nom/Run2/Templates_flo0.6437/
                campaign = '%s/%s/nom-%s/Run2/Templates_flo%s'%(bkgPtWgts_campaign, sub_campaign, sel, flo) # data, pt rwgt
            else:
                campaign = '%s/%s/nom-%s/Templates'%(bkgNoPtWgts_campaign, sub_campaign, sel) # data
            '''
            campaign = '%s/%s/nom-%s/Templates'%(bkgNoPtWgts_campaign, sub_campaign, sel) # data
        else:
            '''
            if do_ptrwgt and 'sb' in r:
                campaign = '%s/%s/nom-%s/Templates_flo%s/systNom_nom'%(bgmc_campaign, sub_campaign, sel, flo) # bgmc
            else:
                campaign = '%s/%s/nom-%s/Templates/systNom_nom'%(bgmc_campaign, sub_campaign, sel) # bgmc
            '''
            campaign = '%s/%s/nom-%s/Templates/systNom_nom'%(bgmc_campaign, sub_campaign, sel) # bgmc
        fs = run_eosls('%s/%s'%(indir, campaign))
        fs = [f for f in fs if 'templates.root' in f]
        fs_s = [f for f in fs if s in f]

        print('      >> mh-region:',r)
        ksr = get_ksr(run, s, r)
        print('      .. ksr:',ksr)
        fs_r = [f for f in fs_s if r in f]
        for i,f in enumerate(fs_r):
            print('         >> file:',f)
            pass
            inpath = "%s/%s/%s/%s"%(eos_redir, indir, campaign, f)
            print('         .. reading:',inpath)
            ksrf = '_'.join(f.split('.')[0].split('_')[:2])
            #ksrf = '%s_%s'%(run, sample)
            print('         .. ksrf:',ksrf)
            #print('ksrf:', ksrf)
            hf[ksrf] = ROOT.TFile.Open(inpath)
            h[ksrf] = hf[ksrf].Get(distn)
            h[ksrf].SetName(ksrf)
            h[ksrf].SetTitle(ksrf)
            if 'data' in s: print('!!!',ksrf)
            print('         .. %s, entries: %.f, integral: %f, max: %f'%(ksrf, h[ksrf].GetEntries(), h[ksrf].Integral(), h[ksrf].GetMaximum()))
            if 'data' not in s:
                #scale
                inpath = "%s/%s/%s/%s_cut_hists.root"%(eos_redir, indir, campaign, ksrf)
                print('         .. reading:',inpath)
                hf['nEvtsWgtd'] = ROOT.TFile.Open(inpath)
                h['nEvtsWgtd'] = hf['nEvtsWgtd'].Get('None/None_nEvtsWgtd')
                ib = h['nEvtsWgtd'].GetXaxis().FindBin(1.)
                nEvtsGenTot = h['nEvtsWgtd'].GetBinContent(ib)
                h[ksrf].Scale(intlumi[run]*xsec[s]/nEvtsGenTot)
                print('         .. %s, ib: %d, xs: %f, nEvtsGenTot: %.f'%(ksrf, ib, xsec[s], nEvtsGenTot))
                print('         .. %s, entries: %.f, integral: %f, max: %f'%(ksrf, h[ksrf].GetEntries(), h[ksrf].Integral(), h[ksrf].GetMaximum()))
            #if i == 0:
            #    hSample[ksr] = h[ksrf].Clone()
            #    hSample[ksr].SetName(ksr)
            #    hSample[ksr].SetTitle(ksr)
            #    print(type(hSample[ksr]))
            #else:
            #    print(type(hSample[ksr]))
            #    hSample[ksr].Add(h[ksrf])
            #print('      .. %s, entries: %.f, integral: %.f, max: %.f'%(ksr, hSample[ksr].GetEntries(), hSample[ksr].Integral(), hSample[ksr].GetMaximum()))

for s in samplesByProc:
    print('   >> sampleByProc:',s)
    #ks_s = [k for k in h.keys() if s in k]
    ks_s = [k for k in h.keys() if s in qcdtype(k)]
    #print(ks_s)
    #for r in regions:
    for r in regionsByType:
        print('      >> mh-region:',r)
        ks_r = [k for k in ks_s if r in k]
        #print(ks_r)
        ksr = get_ksr(run, s, r)
        print('      .. ksr:',ksr)
        hProc[ksr] = h[ks_r[0]].Clone()
        hProc[ksr].Reset()
        hProc[ksr].SetName(ksr)
        hProc[ksr].SetTitle(ksr)
        for k in ks_r:
            hProc[ksr].Add(h[k])
        ib = hProc[ksr].GetXaxis().FindBin(1.)
        print('      .. %s, entries: %.f, integral: %f, err: %f, max: %f'%(ksr, hProc[ksr].GetEntries(), hProc[ksr].Integral(), hProc[ksr].GetBinError(ib), hProc[ksr].GetMaximum()))

'''
#print(hProc.keys())
#for r in regionsByType:
r = regionsByType[1]
#r = regionsByType[0]
print('   >> mh-region:',r)
ks_r = [k for k in hProc.keys() if r in k]
# for mH-SB, want to compare effect of pt rwgting on MC-SB to tgt mH-SR
# So compare to data-SR + hgg-SR by swapping out data- and hgg-SB with -SR counterpart
# Note: pt rwgt data-SB identical to data-SR by construction
if 'sb' in r:
    ks_r = [k.replace('sb', 'sr') if ('data' in k) or ('hgg' in k) else k for k in ks_r]
#print(ks_r)
#print('   .. ksr:',ksr)

# Draw
draw_hist_1dptstacked(ks_r, r)
'''
