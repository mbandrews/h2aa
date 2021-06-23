from __future__ import print_function
import ROOT
import numpy as np
from array import array
from hist_utils import *
import CMS_lumi

# Plot nVtx
# For reference comparison, see: https://twiki.cern.ch/twiki/bin/viewauth/CMS/PileupJSONFileforData

ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
#change the CMS_lumi variables (see CMS_lumi.py)
CMS_lumi.lumi_7TeV = "4.8 fb^{-1}"
CMS_lumi.lumi_8TeV = "18.3 fb^{-1}"
CMS_lumi.writeExtraText = 1
CMS_lumi.extraText = "Simulation"
#CMS_lumi.lumi_sqrtS = "41.9 fb^{-1} (13 TeV)" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
iPos = 11 # CMS in frame
#iPos = 0 # CMS above frame
CMS_lumi.cmsTextOffset = 0.01
if( iPos==0 ): CMS_lumi.relPosX = 0.12
iPeriod = 0

def draw_hist_1dma_overlay(k_, h, hc, c, l, hatch, legend, it, ymax_=None):

    #hc = {}
    print('key:%s, it:%d'%(k_, it))

    err_style = 'E2'
    fill_style = 3002
    #wd, ht = int(440*1), int(400*1)
    #wd, ht = int(640*1), int(580*1)
    wd, ht = int(640*1), int(680*1)
    #ROOT.gStyle.SetErrorX(0)

    #k = 'sb_%s'%k_
    #k = 'sblo_'+k_
    #k = region+'_'+k_
    k = k_
    if it == 0:
        #c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
        c.SetLeftMargin(0.16)
        c.SetRightMargin(0.04)
        c.SetBottomMargin(0.14)
        c.SetTopMargin(0.06)
        ROOT.gStyle.SetOptStat(0)
    else:
        c.cd()

    h[k].GetXaxis().SetLabelSize(0.08)
    h[k].GetXaxis().SetLabelFont(62)
    h[k].GetXaxis().SetTitleOffset(0.09)
    h[k].GetXaxis().SetTitleSize(0.08)
    h[k].GetXaxis().SetTitleFont(62)

    h[k].GetYaxis().SetLabelSize(0.06)
    h[k].GetYaxis().SetLabelFont(62)
    h[k].GetYaxis().SetTitleOffset(1.2)
    h[k].GetYaxis().SetTitleSize(0.06)
    h[k].GetYaxis().SetTitleFont(62)

    h[k] = set_hist(h[k], "m_{#Gamma,pred} [GeV]", "f_{events} / 25 MeV", "")
    #h[k].GetXaxis().SetTitleOffset(0.9)
    #h[k].GetXaxis().SetTitleSize(0.06)
    #h[k].SetLineColor(9)
    #h[k].SetFillColor(9)
    h[k].SetLineColor(it+1)
    h[k].SetFillColor(it+1)
    h[k].SetFillStyle(fill_style)
    #h[k].Draw("hist")
    if it == 0:
        h[k].Draw("%s"%err_style)
    else:
        h[k].Draw("%s same"%err_style)
    hc[k] = h[k].Clone()
    hc[k].SetName(k+'line')
    #hc[k].SetLineColor(9)
    hc[k].SetFillStyle(0)
    hc[k].SetMarkerStyle(20)
    hc[k].SetMarkerSize(0.85)

    #h[k].GetXaxis().SetTitle('')
    #h[k].GetXaxis().SetLabelSize(0.)
    #h[k].GetYaxis().SetTitleOffset(0.9)
    h[k].GetYaxis().SetTitleSize(0.06)
    h[k].GetYaxis().SetLabelSize(0.04)
    h[k].GetYaxis().SetMaxDigits(3)
    h[k].GetXaxis().SetTitleSize(0.06)
    h[k].GetXaxis().SetLabelSize(0.04)
    h[k].GetXaxis().SetTitleOffset(1.)
    hc[k].Draw("hist same")
    #hc[k].Draw("E")

    if ymax_ is None:
        ymax = 1.2*h[k].GetMaximum()
    elif ymax_ == -1:
        ima_low = h[k].GetXaxis().FindBin(0.)
        ymax = 1.2*np.max([h[k].GetBinContent(ib) for ib in range(ima_low, h[k].GetNbinsX()+2)])
    else:
        ymax = ymax_
    #print('>> ymax: %f -> %f'%(h[k].GetMaximum(), ymax))
    #ymax = 4.2e3
    #ymax = 3.4e3

    if it == 0:
        pass
        print('>> ymax[%d]: %f'%(it, ymax))
        #hc[k].GetYaxis().SetRangeUser(0.1, ymax)
        #hc[k].GetXaxis().SetRangeUser(0., 1.2)
        h[k].GetYaxis().SetRangeUser(1.e-5 if normalize else 0.1, ymax)
        h[k].GetXaxis().SetRangeUser(0., 1.2)
        #hc[k].GetYaxis().SetRangeUser(0.1, ymax)

    if it == nit - 1:
        mass = float(k.split('_')[1].replace('p','.'))
        print('>> mass: %f'%mass)
        print('>> ymax[%d]: %f'%(it, ymax))
        #l[k] = ROOT.TLine(0.135, 0., 0.135, ymax) # x0,y0, x1,y1
        #l[k].SetLineColor(14)
        #l[k].SetLineStyle(7)
        #l[k].Draw("same")

        #l[k+'550'] = ROOT.TLine(0.55, 0., 0.55, ymax) # x0,y0, x1,y1
        #l[k+'550'].SetLineColor(14)
        #l[k+'550'].SetLineStyle(7)
        #l[k+'550'].Draw("same")

        l[k] = ROOT.TLine(mass, 0., mass, ymax) # x0,y0, x1,y1
        l[k].SetLineColor(14)
        l[k].SetLineStyle(7)
        l[k].Draw("same")

        hatch[k] = ROOT.TGraph(2, array('d',[0.,0.]), array('d',[0.,ymax]));
        hatch[k].SetLineColor(14)
        hatch[k].SetLineWidth(5001)
        #hatch[k].SetLineWidth(5)
        hatch[k].SetFillStyle(3004)
        hatch[k].SetFillColor(14)
        hatch[k].Draw("same")

    if it == 0:
        c.Draw()
        CMS_lumi.CMS_lumi(c, iPeriod, iPos)
    c.Update()
    if it == nit-1:

        #print(h.keys())
        legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.88) #(x1, y1, x2, y2)
        for r in runs:
            rmek = '%s_%s'%(r, '_'.join(k_.split('_')[1:]))
            legend.AddEntry(rmek, r, "lef")
        legend.SetBorderSize(0)
        legend.Draw("same")

        outfile = 'Plots/mAvRun_%s.pdf'%(k)
        #outfile = 'Plots/mAvEtaCut_%s_norm_%s.eps'%(k, normalize)
        c.Print(outfile)
        #c.Print('Plots/mA_%.eps'%(k))

def draw_nvtx(k, h, c, ymax=None):

    err_style = 'E2'
    fill_style = 3002
    #wd, ht = int(440*1), int(400*1)
    #wd, ht = int(640*1), int(580*1)
    wd, ht = int(640*1), int(680*1)
    #ROOT.gStyle.SetErrorX(0)

    c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)

    h[k] = set_hist(h[k], "N_{vtx}", "f_{events}", "")

    c[k].SetLeftMargin(0.17)
    c[k].SetRightMargin(0.04)
    c[k].SetBottomMargin(0.14)
    c[k].SetTopMargin(0.06)
    ROOT.gStyle.SetOptStat(0)

    h[k].GetYaxis().SetTitleSize(0.06)
    h[k].GetYaxis().SetLabelSize(0.04)
    h[k].GetYaxis().SetMaxDigits(3)
    h[k].GetYaxis().SetTitleOffset(1.3)

    h[k].GetXaxis().SetTitleSize(0.06)
    h[k].GetXaxis().SetLabelSize(0.04)
    h[k].GetXaxis().SetTitleOffset(1.)

    h[k].SetLineColor(9)
    h[k].SetFillColor(9)
    h[k].SetFillStyle(fill_style)
    h[k].Draw("%s"%err_style)

    hc[k] = h[k].Clone()
    hc[k].SetFillStyle(0)
    hc[k].SetMarkerStyle(20)
    hc[k].SetMarkerSize(0.85)
    hc[k].Draw("hist same")

    #hc[k].Draw("E")

    if ymax is not None:
        h[k].GetYaxis().SetRangeUser(0., ymax)
    #h[k].GetXaxis().SetRangeUser(0., 1.2)

    #legend[k] = ROOT.TLegend(0.5,0.68,0.8,0.86) #(x1, y1, x2, y2)
    #legend[k].AddEntry(hc[k].GetName(),"Obs","l")
    #legend[k].AddEntry(hc['sb2sr_maxy'].GetName(),"Exp","l")
    #legend[k].SetBorderSize(0)
    #legend[k].Draw("same")

    c[k].Draw()

    CMS_lumi.CMS_lumi(c[k], iPeriod, iPos)

    c[k].Update()
    #c[k].Print('Plots/%s_sb2srvsr_blind_%s.eps'%(sample, blind))
    #c[k].Print('Plots/%s_sb2srvsr_blind_%.eps'%(sample, blind))
    #c[k].Print('Plots/%s_sb_blind_%s_%s.eps'%(sample, blind, k))

def draw_nvtx_ratio(ks, h, c, ymax=None):

    err_style = 'E2'
    fill_style = 3002
    wd, ht = int(640*1), int(680*1)
    #ROOT.TGaxis.fgMaxDigits = 3
    #ROOT.gStyle.SetErrorX(0)
    #ROOT.gStyle.SetErrorX(1.)

    kdata, kmc = ks
    assert 'data' in kdata
    assert 'h4g' in kmc

    k = kdata

    c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)

    pUp = ROOT.TPad("upperPad", "upperPad",.005, .300, .995, .995) # (,,Double_t xlow, Double_t ylow, Double_t xup, Double_t yup,...)
    pDn = ROOT.TPad("lowerPad", "lowerPad",.005, .005, .995, .300)
    pUp.Draw()
    pDn.Draw()
    pUp.SetMargin(15.e-02,3.e-02,2.e-02,9.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pDn.SetMargin(15.e-02,3.e-02,36.e-02,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)

    pUp.cd()
    #h[k], c[k] = set_hist(h[k], c[k], "m_{a,pred} [GeV]", "N_{a}", "")
    h[k] = set_hist(h[k], "N_{vtx}", "f_{events}", "")

    # Plot data

    h[k].GetXaxis().SetTitle('')
    h[k].GetXaxis().SetLabelSize(0.)

    h[k].GetYaxis().SetTitleOffset(1.1)
    h[k].GetYaxis().SetTitleSize(0.07)
    h[k].GetYaxis().SetLabelSize(0.06)
    #h[k].GetYaxis().SetMaxDigits(3)

    ROOT.gStyle.SetOptStat(0)

    h[k].SetFillStyle(0)
    h[k].SetMarkerStyle(20)
    h[k].SetMarkerSize(0.85)
    h[k].Draw("E")

    # Plot MC
    k = kmc
    # Plot stat errs
    h[k].SetLineColor(9)
    h[k].SetFillColor(9)
    h[k].SetFillStyle(fill_style)
    h[k].Draw("%s same"%err_style)
    # Plot line
    hc[k] = h[k].Clone()
    hc[k].SetName(k+'line')
    hc[k].SetLineColor(9)
    hc[k].SetFillStyle(0)
    hc[k].Draw("hist same")

    k = kdata
    if ymax is not None:
        h[k].GetYaxis().SetRangeUser(0., ymax)
    #hc[k].GetXaxis().SetRangeUser(0., 1.2)

    print(kdata, kmc)
    #kmc = 2017_h4g2017-mA0p1GeV_nVtx
    ma_ = float(kmc.split('_')[1].split('-')[-1].replace('mA','').replace('GeV','').replace('p','.'))
    #print(ma_)
    ma_str = '%.f MeV'%(ma_*1.e3) if ma_ < 1. else '%.f GeV'%ma_
    legend[k] = ROOT.TLegend(0.5,0.65,0.85,0.82) #(x1, y1, x2, y2)
    legend[k].AddEntry(kdata, "Data, %s"%run, "lpe")
    #legend[k].AddEntry(kmc, "H #rightarrow aa #rightarrow, m_{a} = %s"%ma_str, "lf")
    legend[k].AddEntry(kmc, "Sg, m_{a} = %s"%ma_str, "lf")
    legend[k].SetBorderSize(0)
    legend[k].Draw("same")

    CMS_lumi.CMS_lumi(pUp, iPeriod, iPos)

    ##### Ratio plots on lower pad #####
    pDn.cd()
    pDn.SetTicky()
    pDn.SetGridy()

    fUnity = ROOT.TF1("fUnity", "[0]", 0., 120.)
    fUnity.SetParameter( 0,1. )

    fUnity.GetXaxis().SetTitle("N_{vtx}")
    fUnity.GetXaxis().SetTickLength(0.1)
    fUnity.GetXaxis().SetTitleOffset(1.05)
    fUnity.GetXaxis().SetTitleSize(0.16)
    fUnity.GetXaxis().SetLabelSize(0.14)

    #dY = 0.399
    dY = 0.99
    fUnity.GetYaxis().SetTitle("Data/MC")
    #fUnity.GetYaxis().SetRangeUser(1.-dY,1.+dY)
    fUnity.SetMaximum(1.+dY)
    #fUnity.SetMinimum(1.-dY)
    fUnity.SetMinimum(0.01)
    fUnity.GetYaxis().SetNdivisions(305)
    fUnity.GetYaxis().SetTickLength(0.04)
    fUnity.GetYaxis().SetLabelFont(62)
    fUnity.GetYaxis().SetTitleFont(62)
    fUnity.GetYaxis().SetTitleOffset(.4)
    fUnity.GetYaxis().SetTitleSize(0.16)
    fUnity.GetYaxis().SetLabelSize(0.14)

    fUnity.SetLineColor(9)
    fUnity.SetLineWidth(1)
    fUnity.SetLineStyle(7)
    fUnity.SetTitle("")
    fUnity.Draw()

    # Plot data ratios as points with stat err
    kratio = kdata+'o'+kmc
    k = kratio
    h[k] = h[kdata].Clone()
    h[k].Reset()
    h[k].SetName(k)
    for ib in range(1, h[k].GetNbinsX()+1):
        obs = h[kdata].GetBinContent(ib)
        bkg = h[kmc].GetBinContent(ib)
        #if bkg == 0.: print(ib, obs, bkg)
        if obs == 0. or bkg == 0.: continue
        obs_err = h[kdata].GetBinError(ib)
        bkg_err = h[kmc].GetBinError(ib)
        #print(ib, obs/bkg)
        h[k].SetBinContent(ib, obs/bkg)
        h[k].SetBinError(ib, obs_err/obs if obs > 0. else 1.)
    h[k].SetLineColor(9)
    h[k].Sumw2()
    h[k].SetStats(0)
    h[k].SetMarkerStyle(20)
    h[k].SetMarkerSize(0.85)
    h[k].SetMarkerColor(1)#9
    h[k].Draw("ep same")

    # Plot mc stat err band
    kmc_ratiostat = kmc+'ratiostat'
    k = kmc_ratiostat
    h[k] = h[kmc].Clone()
    h[k].Reset()
    h[k].SetName(k)
    for ib in range(1, h[k].GetNbinsX()+1):
        bkg = h[kmc].GetBinContent(ib)
        if bkg == 0.: continue
        bkg_err = h[kmc].GetBinError(ib)
        #print(ib, obs/bkg)
        h[k].SetBinContent(ib, 1.)
        h[k].SetBinError(ib, bkg_err/bkg if bkg > 0. else 1.)
    h[k].Sumw2()
    h[k].SetStats(0)
    h[k].SetFillColor(9)
    h[k].SetFillStyle(fill_style)
    h[k].SetFillStyle(fill_style)
    h[k].Draw("E2 same")

    k = kdata
    c[k].Draw()
    c[k].Update()
    c[k].Print('Plots/nVtx/run%sorun%s.pdf'%(kdata, kmc))

# Plot nVtx
# For reference comparison, see: https://twiki.cern.ch/twiki/bin/viewauth/CMS/PileupJSONFileforData

l, hatch = {}, {}
legend = {}

hf, h, hc = {}, {}, {}
c = {}

#run = 'Run2'
run = '2016'
#run = '2017'
#run = '2018'
r_sb2sr, r_sr = 'sb2sr+hgg', 'sr'
valid_blind = 'diag_lo_hi'
limit_blind = 'offdiag_lo_hi'
indir = 'root://cmseos.fnal.gov//store/user/lpchaa4g/mandrews/%s'%run
sub_campaign = 'bdtgtm0p96_relChgIsolt0p07_etalt1p44' # bdt > -0.96, relChgIso < 0.07 !! optimal

#'''
# Sg model
# /eos/uscms/store/user/lpchaa4g/mandrews/2017/sg-Era04Dec2020v7/bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-nom/Templates/systNom_nom/h4g2017-mA0p1GeV_sr_blind_None_templates.root
CMS_lumi.extraText = "Simulation"
sel = 'nom'
campaign = 'sg-Era04Dec2020v7/%s/nom-%s/Templates/systNom_nom'%(sub_campaign, sel) # 2016-18 phoid, 2016-18 ss. ss implemented only for shifted syst (as in v4)

#nit = len(runs)*len(expts)
#normalize = False
normalize = True
if normalize:
    ymax_norm = 0.18 if '2016' in run else 0.12

mhregion = r_sr
mablind = None
keys = ['nVtx']
ma_pts = ['0p1', '0p4', '1p0']
#ma_pts = ['0p1']

#'''
for ma in ma_pts:

    sample = 'h4g-mA%sGeV'%ma if run == 'Run2' else 'h4g%s-mA%sGeV'%(run, ma)

    inpath = "%s/%s/%s_%s_blind_%s_templates.root"%(indir, campaign, sample, mhregion, mablind)
    print('>> Reading:', inpath)

    rs = '%s_%s'%(run, sample)
    print('rs:', rs)

    hf[rs] = ROOT.TFile.Open(inpath)
    for k in keys:
        rsk = '%s_%s'%(rs, k)
        print('rsk:', rsk)
        h[rsk] = hf[rs].Get(k)
        if normalize:
            h[rsk].Scale(1./h[rsk].GetEntries())
            h[rsk].SetName(rsk)
            h[rsk].SetTitle(rsk)
        print('>> %s: maximum: %f'%(rsk, h[rsk].GetMaximum()))
        print('>> %s: GetEntries: %f, Integral: %f'%(rsk, h[rsk].GetEntries(), h[rsk].Integral()))

        #draw_nvtx(rsk, h, c, ymax=ymax_norm)
#'''

# Bkg model
sample = 'data'
#/eos/uscms/store/user/lpchaa4g/mandrews/2017/bkgPtWgts-Era04Dec2020v3/bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-nom/Run2/Templates_flo0.6437/data2017_sblo_blind_None_templates.root
#/eos/uscms/store/user/lpchaa4g/mandrews/2017/bkgNoPtWgts-Era04Dec2020v3/bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-nom/Templates/
#campaign = 'bkgPtWgts-Era04Dec2020v3/%s/nom-%s/Run2/Templates_flo0.6437'%(sub_campaign, sel) # combined full Run2, 2016H+2018 failed lumis, run = 'Run2'
campaign = 'bkgNoPtWgts-Era04Dec2020v3/%s/nom-%s/Templates'%(sub_campaign, sel) # combined full Run2, 2016H+2018 failed lumis, run = 'Run2'
CMS_lumi.extraText = "Preliminary"

mhregion = 'sr'
inpath = "%s/%s/%s_%s_blind_%s_templates.root"%(indir, campaign, sample if run == 'Run2' else sample+run, mhregion, mablind)
print('>> Reading:', inpath)

rs = '%s_%s'%(run, sample)
print('rs:', rs)

hf[rs] = ROOT.TFile.Open(inpath)
for k in keys:
    rsk = '%s_%s'%(rs, k)
    print('rsk:', rsk)
    h[rsk] = hf[rs].Get(k)
    if normalize:
        h[rsk].Scale(1./h[rsk].GetEntries())
        h[rsk].SetName(rsk)
        h[rsk].SetTitle(rsk)
    print('>> %s: maximum: %f'%(rsk, h[rsk].GetMaximum()))
    print('>> %s: GetEntries: %f, Integral: %f'%(rsk, h[rsk].GetEntries(), h[rsk].Integral()))

    #draw_nvtx(rsk, h, c, ymax=ymax_norm)

    for ksg in h.keys():
        if 'h4g' not in ksg: continue
        print(ksg)
        draw_nvtx_ratio([rsk, ksg], h, c, ymax=ymax_norm)

'''
it = {}
wd, ht = int(640*1), int(680*1)
for k in keys:
    for m in mas:
        it[k+m] = 0
        c[k+m] = ROOT.TCanvas("c%s"%(k+m), "c%s"%(k+m), wd, ht)
        ymax_ = ymaxs[m]
        #ymax_ = -1
        for r in runs:
            for e in expts:
                rmek = '%s_%s_%s_%s'%(r, m, e, k)
                for ix in range(0, h[rmek].GetNbinsX()+2):
                    pass
                    #print('%d: %f'%(ix, h[rmek].GetBinContent(ix)))
                draw_hist_1dma_overlay(rmek, h, hc, c[k+m], l, hatch, legend, it[k+m], ymax_)
                it[k+m] += 1
        #c[k+m].Print('Plots/mA_%.eps'%(k))
'''
