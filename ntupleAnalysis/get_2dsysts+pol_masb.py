from __future__ import print_function
import ROOT
import numpy as np
from array import array
from hist_utils import *
from get_bkg_norm import *
from collections import OrderedDict
import CMS_lumi, tdrstyle

#tdrstyle.setTDRStyle()
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
#change the CMS_lumi variables (see CMS_lumi.py)
CMS_lumi.lumi_7TeV = "4.8 fb^{-1}"
CMS_lumi.lumi_8TeV = "18.3 fb^{-1}"
CMS_lumi.writeExtraText = 1
CMS_lumi.extraText = "Preliminary"
CMS_lumi.cmsTextOffset = 0.
#CMS_lumi.lumi_sqrtS = "41.5 fb^{-1} (13 TeV)" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
CMS_lumi.lumi_sqrtS = "136 fb^{-1} (13 TeV)" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
iPos = 11
if( iPos==0 ): CMS_lumi.relPosX = 0.12
iPeriod = 0

wd, ht = int(800*1), int(680*1)
wd_wide = 1400

def dcard_syst(syst, run=None):
    dcard_syst = syst
    if syst == 'all':
        if run is None:
            dcard_syst = 'CMS_h4g_%s'%(syst)
        else:
            dcard_syst = '%s_CMS_h4g_%s_%s'%(run, syst, run)
    # signal
    #systs = ['PhoIdSF', 'Scale', 'Smear', 'TrgSF']
    elif syst == 'Scale':
        dcard_syst = '%s_CMS_h4g_mGamma_scale_%s'%(run, run)
    elif syst == 'Smear':
        dcard_syst = '%s_CMS_h4g_mGamma_smear_%s'%(run, run)
    elif syst == 'PhoIdSF':
        dcard_syst = '%s_CMS_h4g_preselSF_%s'%(run, run)
    elif syst == 'TrgSF':
        dcard_syst = '%s_CMS_h4g_hltSF_%s'%(run, run)
    # bkg
    #systs = ['flo', 'hgg'] + pol2de0,1,2
    elif syst == 'flo':
        dcard_syst = 'CMS_h4g_bgFracSBlo'
    elif syst == 'hgg':
        dcard_syst = 'CMS_h4g_bgFracHgg'
    elif 'pol2d' in syst:
        dcard_syst = 'CMS_h4g_bgRewgtPolEigen'+syst[-1]
    return dcard_syst

def isnot_sg(ix, iy):
    #if abs(ix - iy) > int(200/25): # 200MeV blinding / 25MeV bin widths -> 8 bins
    #if abs(ix - iy) > int(200/25) or (ix <= 1) or (iy <= 1): # 200MeV blinding / 25MeV bin widths -> 8 bins
    #if abs(ix - iy) >= int(200/50) or (ix <= 1) or (iy <= 1): # 200MeV blinding / 50MeV bin widths
    if abs(ix - iy) >= int(200/dMa) or (ix <= 1) or (iy <= 1): # 200MeV blinding / 50MeV bin widths
        return True
    else:
        return False

nparams = 3
#nparams = 4
nparams = 6
#nparams = 10

def pol2_2d_x_bkg(x, par):

    imx = h[kfitsrc].GetXaxis().FindBin(x[0])
    imy = h[kfitsrc].GetYaxis().FindBin(x[1])

    #pol_val =  par[0] + par[1]*x[0] + par[2]*x[1]
    #pol_val =  par[0] + par[1]*x[0] + par[2]*x[1] + par[3]*x[0]*x[1]
    pol_val =  par[0] + par[1]*x[0] + par[2]*x[1] + par[3]*x[0]*x[1] + par[4]*x[0]*x[0] + par[5]*x[1]*x[1]
    #pol_val =  par[0] + par[1]*x[0] + par[2]*x[1] + par[3]*x[0]*x[1] + par[4]*x[0]*x[0] + par[5]*x[1]*x[1]\
    #            + par[6]*x[0]*x[0]*x[0] + par[7]*x[1]*x[1]*x[1] + par[8]*x[0]*x[0]*x[1] + par[9]*x[0]*x[1]*x[1]
    hist_val = h[kfitsrc].GetBinContent(imx, imy)

    return pol_val*hist_val

def get_pol_hist(params, shift):

    #pol2_2d = '[0] + [1]*x + [2]*y'
    #pol2_2d = '[0] + [1]*x + [2]*y +[3]*x*y'
    pol2_2d = '[0] + [1]*x + [2]*y +[3]*x*y + [4]*x*x + [5]*y*y'
    #pol2_2d = '[0] + [1]*x + [2]*y +[3]*x*y + [4]*x*x + [5]*y*y + [6]*x*x*x + [7]*y*y*y + [8]*x*x*y + [9]*x*y*y'

    nparams = len(pol2_2d.split(']'))-1
    assert nparams == len(params)

    #gpol = ROOT.TF2('pol2_2d', pol2_2d, -0.4, 1.2, -0.4, 1.2)
    gpol = ROOT.TF2('pol2d_'+shift, pol2_2d, 0., 1.2, 0., 1.2)
    for i,p in enumerate(params):
        gpol.SetParameter(i, p)

    return gpol

def scale_bypol(k, gpol):

    for ix in range(1, h[k].GetNbinsX()+1):
        for iy in range(1, h[k].GetNbinsY()+1):
            binc = h[k].GetBinContent(ix, iy)
            ma_x, ma_y = h[k].GetXaxis().GetBinCenter(ix), h[k].GetYaxis().GetBinCenter(iy)
            pol_val = gpol.Eval(ma_x, ma_y)
            h[k].SetBinContent(ix, iy, pol_val*binc)

def var_params(params, varvec, side):

    if side == 'up':
        var_params = params + varvec
    elif side == 'dn':
        var_params = params - varvec
    else:
        raise Exception('Not a valid variation direction (up or dn): %s'%side)

    return var_params

def draw_hist_1dma_statsyst(ks, syst, ymax_=-1, blind_diag=False, plot_syst=True):

    assert syst == 'all'

    hc = {}

    #h4g_1GeV_sr_offdiag_lo_hi_scaleup_ma0vma1_rebin_ma1
    ksr, klo, knom, khi = ks

    assert 'h4g' not in ksr
    #is_h4g = True if 'h4g' in ksr else False
    sample = ksr.split('_')[0]
    blind = ksr.split('_')[2]
    sr = ksr.split('_')[1]
    sb = knom.split('_')[1]
    key = ksr.split('_')[-1]
    kc = '%s_%s_%s_%so%s_%s'%(sample, syst, blind, sr, sb, key)
    if 'rebin' in ksr:
        kc = kc+'_rebin'

    err_style = 'E2'
    fill_style = 3002
    wd, ht = int(640*1), int(680*1)
    #ROOT.TGaxis.fgMaxDigits = 3
    #ROOT.gStyle.SetErrorX(0)

    sr_k = ksr
    #print('num:',sr_k)
    sb2sr_k = knom
    #print('den:',sb2sr_k)
    srosb2sr_k = '%so%s'%(ksr, knom)

    # Syst err band
    ksyst = knom+'_errband'
    h[ksyst] = ROOT.TGraphAsymmErrors()
    h[ksyst].SetName(ksyst)
    ibin = 1
    for ib in range(2, h[knom].GetNbinsX()+1):

        # if h4g, syst up/dn is on binsr
        # if data, syst up/dn is on binnom
        binsr = h[ksr].GetBinContent(ib)
        binlo = h[klo].GetBinContent(ib)
        binnom = h[knom].GetBinContent(ib)
        binhi = h[khi].GetBinContent(ib)

        binup = binhi if binhi > binlo else binlo
        bindn = binlo if binhi > binlo else binhi
        if binnom > binup:
            binup = binnom
        if binnom < bindn:
            bindn = binnom
        h[ksyst].SetPoint(ibin-1, h[knom].GetBinCenter(ib), binnom)
        h[ksyst].SetPointError(
            ibin-1,
            h[knom].GetBinWidth(ib)/2.,
            h[knom].GetBinWidth(ib)/2.,
            binnom-bindn,
            binup-binnom
            )
        ibin += 1

    c[kc] = ROOT.TCanvas("c%s"%kc,"c%s"%kc,wd,ht)

    pUp = ROOT.TPad("upperPad", "upperPad",.005, .300, .995, .995) # (,,Double_t xlow, Double_t ylow, Double_t xup, Double_t yup,...)
    pDn = ROOT.TPad("lowerPad", "lowerPad",.005, .005, .995, .300)
    pUp.Draw()
    pDn.Draw()
    pUp.SetMargin(13.e-02,3.e-02,2.e-02,9.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pDn.SetMargin(13.e-02,3.e-02,36.e-02,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)

    pUp.cd()

    k = sr_k
    #h[k] = set_hist(h[k], "m_{a,pred} [GeV]", "N_{a} / %d MeV"%dMa, "")
    h[k] = set_hist(h[k], "m_{#Gamma,pred} [GeV]", "N_{#Gamma} / %d MeV"%dMa, "")
    hc[k+'dummy'] = h[k].Clone()

    k = k+'dummy'
    #hc[k].Reset()
    hc[k].GetXaxis().SetTitle('')
    hc[k].GetXaxis().SetLabelSize(0.)
    hc[k].GetYaxis().SetTitleOffset(0.9)
    hc[k].GetYaxis().SetTitleSize(0.07)
    hc[k].GetYaxis().SetLabelSize(0.06)
    hc[k].GetYaxis().SetMaxDigits(3)
    hc[k].Draw("E")

    # Plot stat band and stat+syst band separately
    # Need to plot stat+syst band first
    # Plot stat+syst as fill band
    # Note: stat+syst hist will be passed for `ksyst = all`
    if plot_syst:
        h[ksyst].SetLineColor(3)
        h[ksyst].SetFillColor(3)
        h[ksyst].SetFillStyle(3001)
        h[ksyst].Draw("E2 same")
    # Plot bkg + stat band
    k = sb2sr_k
    # Plot bkg as line
    h[k].SetLineColor(9)
    h[k].SetFillStyle(0)
    h[k].Draw("hist same")
    # Plot stat as fill band
    hc[k] = h[k].Clone()
    hc[k].SetName(k+'errs')
    hc[k].SetFillColor(9)
    hc[k].SetFillStyle(3002)
    hc[k].Draw("E2 same")

    # Plot obs data
    # For blinded data, sr_k = sb2sr_k
    # To prevent Clone from getting overwritten, use different key name
    kobs = sr_k+'obs'
    hc[kobs] = h[sr_k].Clone()
    hc[kobs].SetName(kobs+'errs')
    hc[kobs].SetLineColor(1)
    hc[kobs].SetFillColor(0)
    hc[kobs].SetFillStyle(0)
    hc[kobs].SetMarkerStyle(20)
    hc[kobs].SetMarkerSize(0.85)
    hc[kobs].Draw("E same")

    #k = sr_k
    k = kobs
    #ymax = 1.2*max(h[k].GetMaximum(), h[sb2sr_k].GetMaximum())
    if ymax_ == -1 and hc[k].GetBinContent(2) > 0.:
        ymax = 1.4*max(np.max([hc[k].GetBinContent(ib) for ib in range(2, hc[k].GetNbinsX()+1)]),
                       np.max([hc[sb2sr_k].GetBinContent(ib) for ib in range(2, hc[sb2sr_k].GetNbinsX()+1)]))
    if ymax_ is not None and ymax_ > 0.:
        ymax = ymax_

    k = sr_k
    hc[k+'dummy'].GetYaxis().SetRangeUser(0.1, ymax)
    hc[k+'dummy'].GetXaxis().SetRangeUser(0., 1.2)

    l, l2, hatch = {}, {}, {}
    legend = {}

    print('up line key:',k)
    l[k] = ROOT.TLine(0.135, 0., 0.135, ymax) # x0,y0, x1,y1
    l[k].SetLineColor(14)
    l[k].SetLineStyle(7)
    l[k].Draw("same")

    l2[k] = ROOT.TLine(0.55, 0., 0.55, ymax) # x0,y0, x1,y1
    l2[k].SetLineColor(14)
    l2[k].SetLineStyle(7)
    l2[k].Draw("same")

    hatch[k] = ROOT.TGraph(2, array('d',[0.,0.]), array('d',[0.,ymax]));
    hatch[k].SetLineColor(14)
    hatch[k].SetLineWidth(5001)
    #hatch[k].SetLineWidth(5)
    hatch[k].SetFillStyle(3004)
    hatch[k].SetFillColor(14)
    hatch[k].Draw("same")

    blindTextOffset = 0.4
    blindTextSize   = 0.65
    t_ = pUp.GetTopMargin()
    b_ = pUp.GetBottomMargin()
    r_ = pUp.GetRightMargin()
    l_ = pUp.GetLeftMargin()
    relPosX = 0.32#0.045
    relPosY = 0.035#0.235 #0.035
    posX_ =   l_ + relPosX*(1-l_-r_)
    posY_ = 1-t_ - relPosY*(1-t_-b_)
    #posY_ = 0.85
    print(posY_)

    blindText = 'm(a)-SR' if 'offdiag' in blind else 'm(a)-SB'
    #print(blind, blindText)
    ltx = ROOT.TLatex()
    ltx.SetNDC()
    ltx.SetTextFont(42)#bold:62
    ltx.SetTextAlign(13)
    ltx.SetTextSize(blindTextSize*t_)
    ltx.DrawLatex(posX_, posY_, blindText)

    legend[k] = ROOT.TLegend(0.62, posY_-0.2 if plot_syst else posY_-0.13, 0.92, posY_) #(x1, y1, x2, y2)
    #legend[k].AddEntry(hc[sr_k].GetName(), "Obs", "p")
    #legend[k].AddEntry(hc[sb2sr_k].GetName(), "Bkg, stat", "fel")
    legend[k].AddEntry(sr_k+'obserrs', "Obs", "lp")
    legend[k].AddEntry(sb2sr_k+'errs', "Bkg, stat", "fel")
    if plot_syst:
        legend[k].AddEntry(h[ksyst].GetName(), 'Bkg, stat+syst', "fel")
    legend[k].SetBorderSize(0)
    legend[k].Draw("same")

    CMS_lumi.CMS_lumi(pUp, iPeriod, iPos)

    ##### Ratio plots on lower pad #####
    pDn.cd()
    pDn.SetTicky()
    pDn.SetGridy()

    #fUnity = ROOT.TF1("fUnity","[0]",-0.4,1.2)
    fUnity = ROOT.TF1("fUnity","[0]",-0.,1.2)
    fUnity.SetParameter( 0,1. )

    fUnity.GetXaxis().SetTitle("m_{#Gamma,pred} [GeV]")
    fUnity.GetXaxis().SetTickLength(0.1)
    fUnity.GetXaxis().SetTitleOffset(1.05)
    fUnity.GetXaxis().SetTitleSize(0.16)
    fUnity.GetXaxis().SetLabelSize(0.14)

    #dY = 0.199
    dY = 0.399
    #fUnity.GetYaxis().SetTitle("SB/SR")
    fUnity.GetYaxis().SetTitle("Obs/Bkg")
    #fUnity.GetYaxis().SetRangeUser(1.-dY,1.+dY)
    fUnity.SetMaximum(1.+dY)
    fUnity.SetMinimum(1.-dY)
    fUnity.GetYaxis().SetNdivisions(305)
    fUnity.GetYaxis().SetTickLength(0.04)
    fUnity.GetYaxis().SetLabelFont(62)
    fUnity.GetYaxis().SetTitleFont(62)
    fUnity.GetYaxis().SetTitleOffset(.4)
    fUnity.GetYaxis().SetTitleSize(0.16)
    fUnity.GetYaxis().SetLabelSize(0.14)

    fUnity.SetLineColor(9)
    #fUnity.SetLineWidth(1)
    fUnity.SetLineWidth(0)
    fUnity.SetLineStyle(7)
    fUnity.SetTitle("")
    fUnity.Draw()

    if plot_syst:
        # For bkg plots, `ksyst` will containt stat+syst errs
        # which will need to be plotted first
        # Plot stat+syst ratio err bands
        k = sr_k
        kr = ksyst+'ratio'
        h[kr] = ROOT.TGraphAsymmErrors()
        h[kr].SetName(kr)
        yvals = h[ksyst].GetY()
        eyhis = h[ksyst].GetEYhigh()
        eylos = h[ksyst].GetEYlow()
        for i in range(h[ksyst].GetN()):
            ib = i+2
            h[kr].SetPoint(i, h[k].GetBinCenter(ib), 1.)
            h[kr].SetPointError(
                i,
                h[k].GetBinWidth(ib)/2.,
                h[k].GetBinWidth(ib)/2.,
                1.- (yvals[i]-eylos[i])/yvals[i] if yvals[i] > 0. else 0.,
                (yvals[i]+eyhis[i])/yvals[i] - 1 if yvals[i] > 0. else 0.
                )
        h[kr].SetFillColor(3)
        h[kr].SetFillStyle(3001)
        h[kr].Draw("E2 same")

    # Plot bkg stat ratio err bands
    k = sb2sr_k
    kr = k+'ratioerr'
    h[kr] = ROOT.TGraphAsymmErrors()
    h[kr].SetName(kr)
    for i in range(h[k].GetNbinsX()-1):
        ib = i+2
        h[kr].SetPoint(i, h[k].GetBinCenter(ib), 1.)
        h[kr].SetPointError(
            i,
            h[k].GetBinWidth(ib)/2.,
            h[k].GetBinWidth(ib)/2.,
            #0.,#1. - (h[k].GetBinError(ib)/h[k].GetBinContent(ib)),
            #0.# (h[k].GetBinError(ib)/h[k].GetBinContent(ib)) - 1.,
            (h[k].GetBinError(ib)/h[k].GetBinContent(ib)) if h[k].GetBinContent(ib) > 0. else 0.,
            (h[k].GetBinError(ib)/h[k].GetBinContent(ib)) if h[k].GetBinContent(ib) > 0. else 0.
            )
    h[kr].SetFillColor(9)
    #h[kr].SetFillStyle(3001)
    h[kr].SetFillStyle(3002)
    h[kr].Draw("E2 same")

    # Plot obs/bkg as points with err bars
    k = srosb2sr_k
    h[k] = h[sr_k].Clone()
    h[k].Reset()
    h[k].SetName(k)
    for ib in range(1, h[k].GetNbinsX()+1):
        obs = h[sr_k].GetBinContent(ib)
        obs_err = h[sr_k].GetBinError(ib)
        bkg = h[sb2sr_k].GetBinContent(ib)
        #if bkg == 0.: print(ib, obs, bkg)
        if bkg == 0.: continue
        bkg_err = h[sb2sr_k].GetBinError(ib)
        h[k].SetBinContent(ib, obs/bkg)
        #h[k].SetBinError(ib, get_cplimits_sym(obs, bkg, obs_err, bkg_err))
        h[k].SetBinError(ib, obs_err/obs)
    h[k].SetLineColor(1)
    h[k].SetStats(0)
    h[k].SetMarkerStyle(20)
    h[k].SetMarkerSize(0.85)
    h[k].SetMarkerColor(1)
    h[k].Draw("ep same")

    k = srosb2sr_k
    l[k] = ROOT.TLine(0.135, 1.-dY, 0.135, 1.+dY) # x0,y0, x1,y1
    l[k].SetLineColor(14)
    l[k].SetLineStyle(7)
    l[k].Draw("same")

    l2[k] = ROOT.TLine(0.55, 1.-dY, 0.55, 1.+dY) # x0,y0, x1,y1
    l2[k].SetLineColor(14)
    l2[k].SetLineStyle(7)
    l2[k].Draw("same")

    hatch[k] = ROOT.TGraph(2, array('d',[0.,0.]), array('d',[1.-dY,1.+dY]));
    hatch[k].SetLineColor(14)
    hatch[k].SetLineWidth(5001)
    #hatch[k].SetLineWidth(5)
    hatch[k].SetFillStyle(3004)
    hatch[k].SetFillColor(14)
    hatch[k].Draw("same")
    #h[k].SetLineColor(2)
    #h[k].SetLineWidth(1)
    #h[k].SetLineStyle(4)
    #h[k].SetTitle("")

    c[kc].Draw()
    c[kc].Update()
    c[kc].Print('Plots/Sys2D_%s.pdf'%(kc))
    #c[k].Print('Plots/%s_blind_%s_%so%s.pdf'%(sample, blind, ks[0], ks[1]))

def draw_hist_1dma_syst(ks, syst, ymax_=-1, blind_diag=False, plot_syst=True):

    hc = {}

    #h4g_1GeV_sr_offdiag_lo_hi_scaleup_ma0vma1_rebin_ma1
    ksr, klo, knom, khi = ks

    is_h4g = True if 'h4g' in ksr else False
    sample = ksr.split('_')[0]
    blind = ksr.split('_')[2]
    sr = ksr.split('_')[1]
    sb = knom.split('_')[1]
    key = ksr.split('_')[-1]
    kc = '%s_%s_%s_%so%s_%s'%(sample, syst, blind, sr, sb, key)
    if 'rebin' in ksr:
        kc = kc+'_rebin'

    err_style = 'E2'
    fill_style = 3002
    wd, ht = int(640*1), int(680*1)
    #ROOT.TGaxis.fgMaxDigits = 3
    #ROOT.gStyle.SetErrorX(0)

    sr_k = ksr
    #print('num:',sr_k)
    sb2sr_k = knom
    #print('den:',sb2sr_k)
    srosb2sr_k = '%so%s'%(ksr, knom)

    # Syst err band
    ksyst = knom+'_errband'
    h[ksyst] = ROOT.TGraphAsymmErrors()
    h[ksyst].SetName(ksyst)
    ibin = 1
    for ib in range(2, h[knom].GetNbinsX()+1):

        # if h4g, syst up/dn is on binsr
        # if data, syst up/dn is on binnom
        binsr = h[ksr].GetBinContent(ib)
        binlo = h[klo].GetBinContent(ib)
        binnom = h[knom].GetBinContent(ib) if not is_h4g else binsr
        binhi = h[khi].GetBinContent(ib)

        binup = binhi if binhi > binlo else binlo
        bindn = binlo if binhi > binlo else binhi
        if binnom > binup:
            binup = binnom
        if binnom < bindn:
            bindn = binnom
        h[ksyst].SetPoint(ibin-1, h[knom].GetBinCenter(ib), binnom)
        h[ksyst].SetPointError(
            ibin-1,
            h[knom].GetBinWidth(ib)/2.,
            h[knom].GetBinWidth(ib)/2.,
            binnom-bindn,
            binup-binnom
            )
        ibin += 1

    c[kc] = ROOT.TCanvas("c%s"%kc,"c%s"%kc,wd,ht)

    pUp = ROOT.TPad("upperPad", "upperPad",.005, .300, .995, .995) # (,,Double_t xlow, Double_t ylow, Double_t xup, Double_t yup,...)
    pDn = ROOT.TPad("lowerPad", "lowerPad",.005, .005, .995, .300)
    pUp.Draw()
    pDn.Draw()
    pUp.SetMargin(13.e-02,3.e-02,2.e-02,9.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pDn.SetMargin(13.e-02,3.e-02,36.e-02,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)

    pUp.cd()

    k = sr_k
    h[k] = set_hist(h[k], "m_{#Gamma,pred} [GeV]", "N_{#Gamma} / %d MeV"%dMa, "")
    hc[k+'dummy'] = h[k].Clone()

    k = k+'dummy'
    #hc[k].Reset()
    hc[k].GetXaxis().SetTitle('')
    hc[k].GetXaxis().SetLabelSize(0.)
    hc[k].GetYaxis().SetTitleOffset(0.9)
    hc[k].GetYaxis().SetTitleSize(0.07)
    hc[k].GetYaxis().SetLabelSize(0.06)
    hc[k].GetYaxis().SetMaxDigits(3)
    hc[k].Draw("E")

    # Plot bkg model + stat band + syst band in order
    k = sb2sr_k
    # Plot bkg as line
    h[k].SetLineColor(9)
    h[k].SetFillStyle(0)
    h[k].Draw("hist same")
    # Plot stat as fill band
    hc[k] = h[k].Clone()
    hc[k].SetName(k+'errs')
    hc[k].SetFillColor(9)
    hc[k].SetFillStyle(3002)
    hc[k].Draw("E2 same")
    # Plot syst as fill band
    if plot_syst:
        h[ksyst].SetLineColor(3)
        h[ksyst].SetFillColor(3)
        h[ksyst].SetFillStyle(3001)
        h[ksyst].Draw("E2 same")

    # Plot obs data
    # For blinded data, sr_k = sb2sr_k
    # To prevent Clone from getting overwritten, use different key name
    kobs = sr_k+'obs'
    hc[kobs] = h[sr_k].Clone()
    hc[kobs].SetName(kobs+'errs')
    if is_h4g:
        # If h4g plot sg model + stat band instead
        # Plot sg model as shaded area
        hc[kobs].SetLineColor(1)
        hc[kobs].SetFillColor(1)
        #hc[kobs].SetMarkerColor(0)
        hc[kobs].SetFillStyle(3003)
        #hc[kobs].SetMarkerSize(0.)
        #hc[kobs].Draw("hist E2 same")
        hc[kobs].SetMarkerStyle(20)
        hc[kobs].SetMarkerSize(0.85)
        hc[kobs].Draw("hist E same")
    else:
        # Otherwise plot obs data pts
        hc[kobs].SetLineColor(1)
        hc[kobs].SetFillColor(0)
        hc[kobs].SetFillStyle(0)
        hc[kobs].SetMarkerStyle(20)
        hc[kobs].SetMarkerSize(0.85)
        hc[kobs].Draw("E same")

    #k = sr_k
    k = kobs
    #ymax = 1.2*max(h[k].GetMaximum(), h[sb2sr_k].GetMaximum())
    if ymax_ == -1 and hc[k].GetBinContent(2) > 0.:
        ymax = 1.4*max(np.max([hc[k].GetBinContent(ib) for ib in range(2, hc[k].GetNbinsX()+1)]),
                       np.max([hc[sb2sr_k].GetBinContent(ib) for ib in range(2, hc[sb2sr_k].GetNbinsX()+1)]))
    if ymax_ is not None and ymax_ > 0.:
        ymax = ymax_

    k = sr_k
    hc[k+'dummy'].GetYaxis().SetRangeUser(0.1, ymax)
    hc[k+'dummy'].GetXaxis().SetRangeUser(0., 1.2)

    l, l2, hatch = {}, {}, {}
    legend = {}

    print('up line key:',k)
    l[k] = ROOT.TLine(0.135, 0., 0.135, ymax) # x0,y0, x1,y1
    l[k].SetLineColor(14)
    l[k].SetLineStyle(7)
    l[k].Draw("same")

    l2[k] = ROOT.TLine(0.55, 0., 0.55, ymax) # x0,y0, x1,y1
    l2[k].SetLineColor(14)
    l2[k].SetLineStyle(7)
    l2[k].Draw("same")

    hatch[k] = ROOT.TGraph(2, array('d',[0.,0.]), array('d',[0.,ymax]));
    hatch[k].SetLineColor(14)
    hatch[k].SetLineWidth(5001)
    #hatch[k].SetLineWidth(5)
    hatch[k].SetFillStyle(3004)
    hatch[k].SetFillColor(14)
    hatch[k].Draw("same")

    blindTextOffset = 0.4
    blindTextSize   = 0.65
    t_ = pUp.GetTopMargin()
    b_ = pUp.GetBottomMargin()
    r_ = pUp.GetRightMargin()
    l_ = pUp.GetLeftMargin()
    relPosX = 0.32#0.045
    relPosY = 0.035#0.235 #0.035
    posX_ =   l_ + relPosX*(1-l_-r_)
    posY_ = 1-t_ - relPosY*(1-t_-b_)
    #posY_ = 0.85
    print(posY_)

    blindText = 'm(a)-SR' if 'offdiag' in blind else 'm(a)-SB'
    #print(blind, blindText)
    ltx = ROOT.TLatex()
    ltx.SetNDC()
    ltx.SetTextFont(42)#bold:62
    ltx.SetTextAlign(13)
    ltx.SetTextSize(blindTextSize*t_)
    ltx.DrawLatex(posX_, posY_, blindText)

    legend[k] = ROOT.TLegend(0.62, posY_-0.2 if plot_syst else posY_-0.13, 0.92, posY_) #(x1, y1, x2, y2)
    #legend[k].AddEntry(hc[sr_k].GetName(), 'h #rightarrow aa #rightarrow 4#gamma' if is_h4g else "Obs", "lp" if is_h4g else 'p')
    #legend[k].AddEntry(hc[sb2sr_k].GetName(), "Bkg, stat", "fel")
    legend[k].AddEntry(kobs+'errs', 'H #rightarrow aa #rightarrow 4#gamma' if is_h4g else "Obs", "lp")
    legend[k].AddEntry(sb2sr_k+'errs', "Bkg, stat", "fel")
    if plot_syst:
        legend[k].AddEntry(h[ksyst].GetName(), 'Sg, syst' if is_h4g else 'Bkg, syst', "fel")
    legend[k].SetBorderSize(0)
    legend[k].Draw("same")

    CMS_lumi.CMS_lumi(pUp, iPeriod, iPos)

    ##### Ratio plots on lower pad #####
    pDn.cd()
    pDn.SetTicky()
    pDn.SetGridy()

    #fUnity = ROOT.TF1("fUnity","[0]",-0.4,1.2)
    fUnity = ROOT.TF1("fUnity","[0]",-0.,1.2)
    fUnity.SetParameter( 0,1. )

    fUnity.GetXaxis().SetTitle("m_{#Gamma,pred} [GeV]")
    fUnity.GetXaxis().SetTickLength(0.1)
    fUnity.GetXaxis().SetTitleOffset(1.05)
    fUnity.GetXaxis().SetTitleSize(0.16)
    fUnity.GetXaxis().SetLabelSize(0.14)

    #dY = 0.199
    dY = 0.399
    #fUnity.GetYaxis().SetTitle("SB/SR")
    fUnity.GetYaxis().SetTitle("Obs/Bkg")
    #fUnity.GetYaxis().SetRangeUser(1.-dY,1.+dY)
    fUnity.SetMaximum(1.+dY)
    fUnity.SetMinimum(1.-dY)
    fUnity.GetYaxis().SetNdivisions(305)
    fUnity.GetYaxis().SetTickLength(0.04)
    fUnity.GetYaxis().SetLabelFont(62)
    fUnity.GetYaxis().SetTitleFont(62)
    fUnity.GetYaxis().SetTitleOffset(.4)
    fUnity.GetYaxis().SetTitleSize(0.16)
    fUnity.GetYaxis().SetLabelSize(0.14)

    fUnity.SetLineColor(9)
    #fUnity.SetLineWidth(1)
    fUnity.SetLineWidth(0)
    fUnity.SetLineStyle(7)
    fUnity.SetTitle("")
    fUnity.Draw()

    # If h4g, plot sg stat ratio err bands first since have largest magnitude in tails
    if is_h4g:
        k = ksr
        kr = k+'ratioerr'
        h[kr] = ROOT.TGraphAsymmErrors()
        h[kr].SetName(kr)
        for i in range(h[k].GetNbinsX()-1):
            ib = i+2
            h[kr].SetPoint(i, h[k].GetBinCenter(ib), 1.)
            h[kr].SetPointError(
                i,
                h[k].GetBinWidth(ib)/2.,
                h[k].GetBinWidth(ib)/2.,
                #0.,#1. - (h[k].GetBinError(ib)/h[k].GetBinContent(ib)),
                #0.# (h[k].GetBinError(ib)/h[k].GetBinContent(ib)) - 1.,
                (h[k].GetBinError(ib)/h[k].GetBinContent(ib)) if h[k].GetBinContent(ib) > 0. else 0.,
                (h[k].GetBinError(ib)/h[k].GetBinContent(ib)) if h[k].GetBinContent(ib) > 0. else 0.
                )
        h[kr].SetFillColor(1)
        h[kr].SetFillStyle(3003)
        h[kr].Draw("E2 same")

    # Plot bkg stat ratio err bands
    k = sb2sr_k
    kr = k+'ratioerr'
    h[kr] = ROOT.TGraphAsymmErrors()
    h[kr].SetName(kr)
    for i in range(h[k].GetNbinsX()-1):
        ib = i+2
        h[kr].SetPoint(i, h[k].GetBinCenter(ib), 1.)
        h[kr].SetPointError(
            i,
            h[k].GetBinWidth(ib)/2.,
            h[k].GetBinWidth(ib)/2.,
            #0.,#1. - (h[k].GetBinError(ib)/h[k].GetBinContent(ib)),
            #0.# (h[k].GetBinError(ib)/h[k].GetBinContent(ib)) - 1.,
            (h[k].GetBinError(ib)/h[k].GetBinContent(ib)) if h[k].GetBinContent(ib) > 0. else 0.,
            (h[k].GetBinError(ib)/h[k].GetBinContent(ib)) if h[k].GetBinContent(ib) > 0. else 0.
            )
    h[kr].SetFillColor(9)
    h[kr].SetFillStyle(3002)
    h[kr].Draw("E2 same")

    # Plot syst err bands
    if plot_syst:
        k = sr_k
        kr = ksyst+'ratio'
        h[kr] = ROOT.TGraphAsymmErrors()
        h[kr].SetName(kr)
        yvals = h[ksyst].GetY()
        eyhis = h[ksyst].GetEYhigh()
        eylos = h[ksyst].GetEYlow()
        for i in range(h[ksyst].GetN()):
            ib = i+2
            h[kr].SetPoint(i, h[k].GetBinCenter(ib), 1.)
            h[kr].SetPointError(
                i,
                h[k].GetBinWidth(ib)/2.,
                h[k].GetBinWidth(ib)/2.,
                1.- (yvals[i]-eylos[i])/yvals[i] if yvals[i] > 0. else 0.,
                (yvals[i]+eyhis[i])/yvals[i] - 1 if yvals[i] > 0. else 0.
                )
        h[kr].SetFillColor(3)
        h[kr].SetFillStyle(3001)
        h[kr].Draw("E2 same")

    # If not h4g, plot obs/bkg as points with err bars
    if not is_h4g:
        k = srosb2sr_k
        h[k] = h[sr_k].Clone()
        h[k].Reset()
        h[k].SetName(k)
        for ib in range(1, h[k].GetNbinsX()+1):
            obs = h[sr_k].GetBinContent(ib)
            obs_err = h[sr_k].GetBinError(ib)
            bkg = h[sb2sr_k].GetBinContent(ib)
            #if bkg == 0.: print(ib, obs, bkg)
            if bkg == 0.: continue
            bkg_err = h[sb2sr_k].GetBinError(ib)
            h[k].SetBinContent(ib, obs/bkg)
            #h[k].SetBinError(ib, get_cplimits_sym(obs, bkg, obs_err, bkg_err))
            h[k].SetBinError(ib, obs_err/obs)
        h[k].SetLineColor(1)
        h[k].SetStats(0)
        h[k].SetMarkerStyle(20)
        h[k].SetMarkerSize(0.85)
        h[k].SetMarkerColor(1)
        h[k].Draw("ep same")

    k = srosb2sr_k
    l[k] = ROOT.TLine(0.135, 1.-dY, 0.135, 1.+dY) # x0,y0, x1,y1
    l[k].SetLineColor(14)
    l[k].SetLineStyle(7)
    l[k].Draw("same")

    l2[k] = ROOT.TLine(0.55, 1.-dY, 0.55, 1.+dY) # x0,y0, x1,y1
    l2[k].SetLineColor(14)
    l2[k].SetLineStyle(7)
    l2[k].Draw("same")

    hatch[k] = ROOT.TGraph(2, array('d',[0.,0.]), array('d',[1.-dY,1.+dY]));
    hatch[k].SetLineColor(14)
    hatch[k].SetLineWidth(5001)
    #hatch[k].SetLineWidth(5)
    hatch[k].SetFillStyle(3004)
    hatch[k].SetFillColor(14)
    hatch[k].Draw("same")
    #h[k].SetLineColor(2)
    #h[k].SetLineWidth(1)
    #h[k].SetLineStyle(4)
    #h[k].SetTitle("")

    c[kc].Draw()
    c[kc].Update()
    c[kc].Print('Plots/Sys2D_%s.pdf'%(kc))
    #c[k].Print('Plots/%s_blind_%s_%so%s.pdf'%(sample, blind, ks[0], ks[1]))

def plot_1dma(k, title='', yrange=[0., 600.], new_canvas=True, color=1, titles=["im_{x}#timesim_{y} + im_{y}", "N_{evts}"]):

    xtitle, ytitle = titles
    kc = k
    if new_canvas:
        #c[k] = ROOT.TCanvas("c%s"%k, "c%s"%k, wd_wide, ht)
        c[kc] = ROOT.TCanvas(kc, kc, wd_wide, ht)
        ROOT.gStyle.SetOptStat(0)
        ROOT.gPad.SetRightMargin(0.02)
        ROOT.gPad.SetLeftMargin(0.1)
        ROOT.gPad.SetTopMargin(0.05)
        ROOT.gPad.SetBottomMargin(0.14)
        h[k].SetTitle("")
        h[k].GetXaxis().SetTitle(xtitle)
        h[k].GetYaxis().SetTitle(ytitle)
        h[k].GetYaxis().SetTitleOffset(0.7)
        h[k].GetXaxis().SetTitleOffset(1.)
        h[k].GetXaxis().SetTitleSize(0.06)
        h[k].GetYaxis().SetTitleSize(0.06)
        h[k].GetXaxis().SetLabelFont(62)
        h[k].GetXaxis().SetTitleFont(62)
        h[k].GetYaxis().SetLabelFont(62)
        h[k].GetYaxis().SetTitleFont(62)

    h[k].SetLineColor(color)
    if yrange is not None:
        h[k].GetYaxis().SetRangeUser(yrange[0], yrange[1])

    c[kc].cd()
    if new_canvas:
        #h[k].SetMarkerStyle(20)
        #h[k].SetMarkerSize(0.85)
        #h[k].Draw("Ep same")
        h[k].Draw("hist E same")
        #h[k].Draw("hist")
        c[kc].Draw()
    else:
        h[k].Draw("hist same")
        c[kc].Update()
    c[kc].Print('Plots/Sys2D_%s.pdf'%k)


def plot_2dma(k, title, xtitle, ytitle, ztitle, zrange=None, do_trunc=False, do_log=False):

    assert k in h.keys()
    print(h[k].GetMinimum(), h[k].GetMaximum(), h[k].Integral())

    c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
    if do_log: c[k].SetLogz()
    ROOT.gStyle.SetOptStat(0)
    ROOT.gPad.SetRightMargin(0.19)
    ROOT.gPad.SetLeftMargin(0.14)
    ROOT.gPad.SetTopMargin(0.05)
    ROOT.gPad.SetBottomMargin(0.14)
    ROOT.gStyle.SetPalette(55)#53
    h[k].SetTitle("")
    h[k].GetXaxis().SetTitle(xtitle)
    h[k].GetYaxis().SetTitle(ytitle)
    h[k].GetYaxis().SetTitleOffset(1.)
    h[k].GetZaxis().SetTitle(ztitle)
    h[k].GetZaxis().SetTitleOffset(1.3)
    h[k].GetZaxis().SetTitleSize(0.05)
    h[k].GetZaxis().SetTitleFont(62)
    h[k].GetZaxis().SetLabelSize(0.04)
    h[k].GetZaxis().SetLabelFont(62)
    h[k].GetXaxis().SetTitleOffset(1.)
    h[k].GetXaxis().SetTitleSize(0.06)
    h[k].GetYaxis().SetTitleSize(0.06)
    h[k].GetXaxis().SetLabelFont(62)
    h[k].GetXaxis().SetTitleFont(62)
    h[k].GetYaxis().SetLabelFont(62)
    h[k].GetYaxis().SetTitleFont(62)
    h[k].SetContour(50)
    h[k].Draw("COLZ")
    if zrange is not None:
        h[k].SetMaximum(zrange[1])
        h[k].SetMinimum(zrange[0])
    else:
        h[k].SetMaximum(h[k].GetMaximum())
    c[k].Draw()

    if do_trunc:
        h[k].GetXaxis().SetRangeUser(0., 1.2)
        h[k].GetYaxis().SetRangeUser(0., 1.2)
    else:
        ax[k] = h[k].GetXaxis()
        ax[k].ChangeLabel(1,-1, 0,-1,-1,-1,"")
        ax[k].ChangeLabel(2,-1,-1,-1,-1,-1,"#font[22]{#gamma_{veto}}")
        ay[k] = h[k].GetYaxis()
        ay[k].ChangeLabel(1,-1, 0,-1,-1,-1,"")
        ay[k].ChangeLabel(2,-1,-1,-1,-1,-1,"#font[22]{#gamma_{veto}}")

        hatch[k] = ROOT.TGraph(2, array('d',[0.,0.]), array('d',[-0.4,1.2])) # n, x[n], y[2]
        hatch[k].SetLineColor(14)
        #hatch[k].SetLineWidth(5001)
        hatch[k].SetLineWidth(3401) # [+/-]ffll, where ff=fill width, ll=line width, +/-=which side of line hatching is drawn on
        #hatch[k].SetLineWidth(5)
        hatch[k].SetFillStyle(3004)
        hatch[k].SetFillColor(14)
        hatch[k].Draw("same")

        hatch2[k] = ROOT.TGraph(2, array('d',[-0.4,1.2]), array('d',[0.,0.])) # n, x[n], y[2]
        hatch2[k].SetLineColor(14)
        hatch2[k].SetLineWidth(-3401) # [+/-]ffll, where ff=fill width, ll=line width, +/-=which side of line hatching is drawn on
        #hatch2[k].SetLineWidth(5)
        hatch2[k].SetFillStyle(3004)
        hatch2[k].SetFillColor(14)
        hatch2[k].Draw("same")

    c[k].Draw()
    c[k].Update()

    c[k].Print('Plots/Sys2D_%s.pdf'%(k))
    #c[k].Print('Plots/Sys2D_%s.png'%(k))

def plot_datavmc_flat_statsyst(blind, kplots, syst, nbins, yrange=None, colors=[3, 10], styles=[1001, 1001], titles=["im_{1} #times im_{2} + im_{2}", "N_{evts}"], plot_syst=True):

    assert syst == 'all'

    hc = {}
    legend = {}
    xtitle, ytitle = titles
    kobs_nom, kbkg_dn, kbkg_nom, kbkg_up, kfit = kplots
    kshifts = [kbkg_up, kbkg_dn]

    print(kobs_nom)
    #is_h4g = True if 'h4g' in kobs_nom else False
    assert 'h4g' not in kobs_nom

    sample = kobs_nom.split('_')[1]
    blind = kobs_nom.split('_')[2]
    sr = kobs_nom[-3:]
    sb = kbkg_nom[-3:]
    kc = '%s_%s_%s_%so%s_2dmaflat'%(sample, syst, blind, sr, sb)
    #print('>> Flat plot name: [sample, syst, blind, sr o sb]',kc, sample, syst, blind)
    #print('>> Flat plot kobs_nom:',kobs_nom)

    c[kc] = ROOT.TCanvas('c'+kc, 'c'+kc, wd_wide, ht)

    ROOT.gStyle.SetOptStat(0)
    #ROOT.gStyle.SetErrorX(0)

    pUp = ROOT.TPad("upperPad", "upperPad",.005, .300, .995, .995) # (,, xlow, ylow, xup, yup)
    pDn = ROOT.TPad("lowerPad", "lowerPad",.005, .005, .995, .300)
    pUp.Draw()
    pDn.Draw()
    #pUp.SetMargin(14.e-02,3.e-02,5.e-03,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pUp.SetMargin(8.e-02,1.e-02,2.e-02,9.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pDn.SetMargin(8.e-02,1.e-02,36.e-02,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)

    pUp.cd()

    for i,k in enumerate(kshifts):
        # Dummy plots (workaround)
        #k = k_+'flat'
        #print(k)
        #h[k].Reset()
        h[k].SetTitle("")
        h[k].GetXaxis().SetTitle(xtitle)
        h[k].GetYaxis().SetTitle(ytitle+' / %d MeV'%dMa)
        h[k].GetYaxis().SetTitleOffset(0.5)
        h[k].GetXaxis().SetTitleOffset(1.)
        h[k].GetXaxis().SetTitleSize(0.06)
        h[k].GetYaxis().SetTitleSize(0.075)
        h[k].GetXaxis().SetLabelFont(62)
        h[k].GetXaxis().SetLabelSize(0)
        h[k].GetYaxis().SetLabelSize(0.055)
        h[k].GetXaxis().SetTitleFont(62)
        h[k].GetYaxis().SetLabelFont(62)
        h[k].GetYaxis().SetTitleFont(62)
        if yrange is not None:
            #h[k].GetYaxis().SetRangeUser(yrange[0], yrange[1])
            h[k].GetYaxis().SetRangeUser(yrange[0]+1.e-1, yrange[1])
        #h[k].SetLineColor(colors[i])
        #h[k].SetFillColor(colors[i])
        #h[k].SetFillStyle(styles[i])
        h[k].SetLineColor(0)
        h[k].SetFillColor(0)
        if i == 0:
            h[k].Draw("LF2")
        else:
            h[k].Draw("LF2 same")
    # Plot stat+syst as fill
    if plot_syst:
        h[kfit].SetLineColor(3)
        h[kfit].SetFillColor(3)
        h[kfit].SetFillStyle(3001)
        h[kfit].Draw("E2 same")
    # Plot bkg hist line
    h[kbkg_nom].SetLineColor(9)
    h[kbkg_nom].SetLineStyle(1)
    h[kbkg_nom].Draw("hist same")
    # Plot bkg err bands
    hc[kbkg_nom] = h[kbkg_nom].Clone()
    hc[kbkg_nom].SetName(kbkg_nom+'errs')
    hc[kbkg_nom].SetLineColor(9)
    hc[kbkg_nom].SetFillColor(9)
    hc[kbkg_nom].SetFillStyle(3002)
    hc[kbkg_nom].Draw("E2 same")
    # Plot obs as points
    h[kobs_nom].SetFillStyle(0)
    h[kobs_nom].SetMarkerStyle(20)
    h[kobs_nom].SetMarkerSize(0.85)
    h[kobs_nom].Draw("E same")

    pUp.RedrawAxis()

    blindTextSize     = 0.65
    blindTextOffset   = 0.4
    t_ = pUp.GetTopMargin()
    b_ = pUp.GetBottomMargin()
    r_ = pUp.GetRightMargin()
    l_ = pUp.GetLeftMargin()
    relPosX    = 0.35#0.045
    relPosY    = 0.035#0.235 #0.035
    posX_ =   l_ + relPosX*(1-l_-r_)
    posY_ = 1-t_ - relPosY*(1-t_-b_)
    #posY_ = 0.85
    print(posY_)

    blindText = 'm(a)-SR' if 'offdiag' in blind else 'm(a)-SB'
    #blindText = 'h #rightarrow'
    ltx = ROOT.TLatex()
    ltx.SetNDC()
    #ltx.SetTextColor(ROOT.kBlack)
    ltx.SetTextFont(42)#bold:62
    ltx.SetTextAlign(13)
    ltx.SetTextSize(blindTextSize*t_)
    ltx.DrawLatex(posX_, posY_, blindText)
    ch2odof = '#chi^{2}/dof = %3.2f'%(chi2/ndofoff)
    if 'offdiag' not in blind:
        ltx.DrawLatex(0.66, posY_-0.25, ch2odof)

    k = kobs_nom
    #legend[k] = ROOT.TLegend(0.65,0.65,0.95,0.85) #(x1, y1, x2, y2)
    #legend[k] = ROOT.TLegend(0.65,0.65 if plot_syst else 0.71,0.95,0.85) #(x1, y1, x2, y2)
    legend[k] = ROOT.TLegend(0.65, posY_-0.20 if plot_syst else posY_-0.13, 0.95, posY_) #(x1, y1, x2, y2)
    legend[k].AddEntry(h[kobs_nom].GetName(), "Obs", "lp")
    legend[k].AddEntry(hc[kbkg_nom].GetName(), "Bkg, stat", "fl")
    if plot_syst:
        legend[k].AddEntry(h[kfit].GetName(), 'Bkg, stat+syst', "fl")
    legend[k].SetBorderSize(0)
    legend[k].Draw("same")

    CMS_lumi.CMS_lumi(pUp, iPeriod, iPos)


    ##### Ratio plots on lower pad #####
    pDn.cd()

    #'''
    fUnity = ROOT.TF1('fUnity',"[0]",0.,float(nbins))
    fUnity.SetParameter( 0,1. )

    fUnity.GetXaxis().SetTitle(xtitle)
    print(xtitle)
    fUnity.GetXaxis().SetTickLength(0.1)
    fUnity.GetXaxis().SetTitleOffset(1.05)
    fUnity.GetXaxis().SetTitleSize(0.16)
    fUnity.GetXaxis().SetLabelSize(0.14)

    #dY = 0.399
    dY = 0.75
    fUnity.GetYaxis().SetTitle("Obs/Bkg")
    #fUnity.GetYaxis().SetRangeUser(1.-dY,1.+dY)
    fUnity.SetMaximum(1.+dY)
    fUnity.SetMinimum(1.-dY)
    fUnity.GetYaxis().SetNdivisions(305)
    fUnity.GetYaxis().SetTickLength(0.04)
    fUnity.GetYaxis().SetLabelFont(62)
    fUnity.GetYaxis().SetTitleFont(62)
    fUnity.GetYaxis().SetTitleOffset(.25)
    fUnity.GetYaxis().SetTitleSize(0.15)
    fUnity.GetYaxis().SetLabelSize(0.12)

    fUnity.SetLineColor(9)
    #fUnity.SetLineColor(3)
    #fUnity.SetLineWidth(1)
    fUnity.SetLineWidth(0)
    fUnity.SetLineStyle(1)
    fUnity.SetTitle("")
    fUnity.Draw("L")

    # Plot stat+syst ratio err bands
    if plot_syst:
        kr = kfit+'ratio'
        h[kr] = ROOT.TGraphAsymmErrors()
        h[kr].SetName(kr)
        yvals = h[kfit].GetY()
        eyhis = h[kfit].GetEYhigh()
        eylos = h[kfit].GetEYlow()
        for i in range(h[kfit].GetN()):
            h[kr].SetPoint(i, i+0.5, 1.)
            h[kr].SetPointError(
                i,
                0.5,
                0.5,
                1.- (yvals[i]-eylos[i])/yvals[i] if yvals[i] > 0. else 0.,
                (yvals[i]+eyhis[i])/yvals[i] - 1 if yvals[i] > 0. else 0.
                )
        h[kr].SetFillColor(3)
        h[kr].SetFillStyle(3001)
        h[kr].Draw("E2 same")

    # Plot bkg err bands
    k = kbkg_nom
    kr = k+'err'
    h[kr] = ROOT.TGraphAsymmErrors()
    h[kr].SetName(kr)
    for i in range(h[k].GetNbinsX()-1):
        ib = i+1
        #print(ib, k, h[k].GetBinContent(ib), h[k].GetBinContent(ib+1))
        h[kr].SetPoint(i, h[k].GetBinCenter(ib), 1.)
        h[kr].SetPointError(
            i,
            h[k].GetBinWidth(ib)/2.,
            h[k].GetBinWidth(ib)/2.,
            #0.,#1. - (h[k].GetBinError(ib)/h[k].GetBinContent(ib)),
            #0.# (h[k].GetBinError(ib)/h[k].GetBinContent(ib)) - 1.,
            (h[k].GetBinError(ib)/h[k].GetBinContent(ib)) if h[k].GetBinContent(ib) > 0. else 0.,
            (h[k].GetBinError(ib)/h[k].GetBinContent(ib)) if h[k].GetBinContent(ib) > 0. else 0.
            )
    h[kr].SetFillColor(9)
    h[kr].SetFillStyle(3002)
    h[kr].Draw("E2 same")

    # Plot obs/bkg err as points with error bars
    kr = kobs_nom+'ratio'
    h[kr] = h[kobs_nom].Clone()
    h[kr].Reset()
    ##h[kr].Divide(h[kbkg_nom])
    for i in range(1, h[kr].GetNbinsX()+1):
      #binc = h[kobs_nom].GetBinContent(i)
      #h[kr].SetBinError(i, 1./np.sqrt(binc) if binc != 0 else 0.)
      binc_num = h[kobs_nom].GetBinContent(i)
      binc_den = h[kbkg_nom].GetBinContent(i)
      binerr_num = h[kobs_nom].GetBinError(i)
      binerr_den = h[kbkg_nom].GetBinError(i)
      #err_ = get_cplimits_sym(binc_num, binc_den, binerr_num, binerr_den)
      #print(i, binc_num, binc_den, binc_num/binc_den, binerr_num, binerr_den, err_)
      h[kr].SetBinContent(i, binc_num/binc_den if binc_den > 0. else 0.)
      #h[kr].SetBinError(i, err_)
      h[kr].SetBinError(i, binerr_num/binc_num if binc_num > 0. else 0.)
      #if i<10: print(kr, binc_num/binc_den)
    #h[kr].SetFillStyle(0)
    h[kr].SetMarkerStyle(20)
    h[kr].SetMarkerSize(0.85)
    h[kr].Draw("Ep same")

    #fUnityUp = ROOT.TF1('fUnityUp',"[0]",0., float(nbins))
    #fUnityUp.SetParameter( 0, 1.2 )
    #fUnityUp.SetLineWidth(1)
    #fUnityUp.SetLineStyle(2)
    #fUnityUp.Draw("L same")
    #fUnityDn = ROOT.TF1('fUnityDn',"[0]",0., float(nbins))
    #fUnityDn.SetParameter( 0, 0.8 )
    #fUnityDn.SetLineWidth(1)
    #fUnityDn.SetLineStyle(2)
    #fUnityDn.Draw("L same")

    pDn.SetGridy()
    pDn.Update()
    #pDn.RedrawAxis()
    #fUnity.Draw("axis same")
    #'''
    c[kc].Draw()
    #c[kc].Update()
    c[kc].Print('Plots/Sys2D_%s.pdf'%(kc))

def plot_datavmc_flat(blind, kplots, syst, nbins, yrange=None, colors=[3, 10], styles=[1001, 1001], titles=["im_{1} #times im_{2} + im_{2}", "N_{evts}"], plot_syst=True):

    hc = {}
    legend = {}
    xtitle, ytitle = titles
    kobs_nom, kbkg_dn, kbkg_nom, kbkg_up, kfit = kplots
    kshifts = [kbkg_up, kbkg_dn]

    print(kobs_nom)
    is_h4g = True if 'h4g' in kobs_nom else False

    sample = kobs_nom.split('_')[1]
    blind = kobs_nom.split('_')[2]
    sr = kobs_nom[-3:]
    sb = kbkg_nom[-3:]
    kc = '%s_%s_%s_%so%s_2dmaflat'%(sample, syst, blind, sr, sb)
    #print('>> Flat plot name: [sample, syst, blind, sr o sb]',kc, sample, syst, blind)
    #print('>> Flat plot kobs_nom:',kobs_nom)

    c[kc] = ROOT.TCanvas('c'+kc, 'c'+kc, wd_wide, ht)

    ROOT.gStyle.SetOptStat(0)
    #ROOT.gStyle.SetErrorX(0)

    pUp = ROOT.TPad("upperPad", "upperPad",.005, .300, .995, .995) # (,, xlow, ylow, xup, yup)
    pDn = ROOT.TPad("lowerPad", "lowerPad",.005, .005, .995, .300)
    pUp.Draw()
    pDn.Draw()
    #pUp.SetMargin(14.e-02,3.e-02,5.e-03,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pUp.SetMargin(8.e-02,1.e-02,2.e-02,9.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pDn.SetMargin(8.e-02,1.e-02,36.e-02,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)

    pUp.cd()

    for i,k in enumerate(kshifts):
        # Dummy plots (workaround)
        #k = k_+'flat'
        #print(k)
        #h[k].Reset()
        h[k].SetTitle("")
        h[k].GetXaxis().SetTitle(xtitle)
        h[k].GetYaxis().SetTitle(ytitle+' / %d MeV'%dMa)
        h[k].GetYaxis().SetTitleOffset(0.5)
        h[k].GetXaxis().SetTitleOffset(1.)
        h[k].GetXaxis().SetTitleSize(0.06)
        h[k].GetYaxis().SetTitleSize(0.075)
        h[k].GetXaxis().SetLabelFont(62)
        h[k].GetXaxis().SetLabelSize(0)
        h[k].GetYaxis().SetLabelSize(0.055)
        h[k].GetXaxis().SetTitleFont(62)
        h[k].GetYaxis().SetLabelFont(62)
        h[k].GetYaxis().SetTitleFont(62)
        if yrange is not None:
            #h[k].GetYaxis().SetRangeUser(yrange[0], yrange[1])
            h[k].GetYaxis().SetRangeUser(yrange[0]+1.e-1, yrange[1])
        #h[k].SetLineColor(colors[i])
        #h[k].SetFillColor(colors[i])
        #h[k].SetFillStyle(styles[i])
        h[k].SetLineColor(0)
        h[k].SetFillColor(0)
        if i == 0:
            h[k].Draw("LF2")
        else:
            h[k].Draw("LF2 same")
    # Plot bkg hist line
    h[kbkg_nom].SetLineColor(9)
    h[kbkg_nom].SetLineStyle(1)
    h[kbkg_nom].Draw("hist same")
    # Plot bkg err bands
    hc[kbkg_nom] = h[kbkg_nom].Clone()
    hc[kbkg_nom].SetName(kbkg_nom+'errs')
    hc[kbkg_nom].SetLineColor(9)
    hc[kbkg_nom].SetFillColor(9)
    hc[kbkg_nom].SetFillStyle(3002)
    hc[kbkg_nom].Draw("E2 same")
    # Plot syst up/dn
    if plot_syst:
        h[kfit].SetLineColor(3)
        h[kfit].SetFillColor(3)
        h[kfit].SetFillStyle(3001)
        h[kfit].Draw("E2 same")
    # Plot obs err bars
    if is_h4g:
        h[kobs_nom].SetLineColor(1)
        h[kobs_nom].SetFillColor(1)
        h[kobs_nom].SetFillStyle(3003)
        h[kobs_nom].SetMarkerColor(1)
        h[kobs_nom].SetMarkerStyle(20)
        h[kobs_nom].SetMarkerSize(0.85)
        h[kobs_nom].Draw("hist E2 same")
    else:
        h[kobs_nom].SetFillStyle(0)
        h[kobs_nom].SetMarkerStyle(20)
        h[kobs_nom].SetMarkerSize(0.85)
        h[kobs_nom].Draw("E same")

    pUp.RedrawAxis()

    blindTextSize     = 0.65
    blindTextOffset   = 0.4
    t_ = pUp.GetTopMargin()
    b_ = pUp.GetBottomMargin()
    r_ = pUp.GetRightMargin()
    l_ = pUp.GetLeftMargin()
    relPosX    = 0.35#0.045
    relPosY    = 0.035#0.235 #0.035
    posX_ =   l_ + relPosX*(1-l_-r_)
    posY_ = 1-t_ - relPosY*(1-t_-b_)
    #posY_ = 0.85
    print(posY_)

    blindText = 'm(a)-SR' if 'offdiag' in blind else 'm(a)-SB'
    #blindText = 'h #rightarrow'
    ltx = ROOT.TLatex()
    ltx.SetNDC()
    #ltx.SetTextColor(ROOT.kBlack)
    ltx.SetTextFont(42)#bold:62
    ltx.SetTextAlign(13)
    ltx.SetTextSize(blindTextSize*t_)
    ltx.DrawLatex(posX_, posY_, blindText)
    ch2odof = '#chi^{2}/dof = %3.2f'%(chi2/ndofoff)
    if 'offdiag' not in blind:
        ltx.DrawLatex(0.66, posY_-0.25, ch2odof)

    k = kobs_nom
    #legend[k] = ROOT.TLegend(0.65,0.65,0.95,0.85) #(x1, y1, x2, y2)
    #legend[k] = ROOT.TLegend(0.65,0.65 if plot_syst else 0.71,0.95,0.85) #(x1, y1, x2, y2)
    legend[k] = ROOT.TLegend(0.65, posY_-0.20 if plot_syst else posY_-0.13, 0.95, posY_) #(x1, y1, x2, y2)
    legend[k].AddEntry(h[kobs_nom].GetName(), 'H #rightarrow aa #rightarrow 4#gamma' if is_h4g else "Obs", "lp")
    legend[k].AddEntry(hc[kbkg_nom].GetName(), "Bkg, stat", "fl")
    if plot_syst:
        legend[k].AddEntry(h[kfit].GetName(), 'Sg, syst' if is_h4g else 'Bkg, syst', "fl")
    legend[k].SetBorderSize(0)
    legend[k].Draw("same")

    CMS_lumi.CMS_lumi(pUp, iPeriod, iPos)


    ##### Ratio plots on lower pad #####
    pDn.cd()

    #'''
    fUnity = ROOT.TF1('fUnity',"[0]",0.,float(nbins))
    fUnity.SetParameter( 0,1. )

    fUnity.GetXaxis().SetTitle(xtitle)
    print(xtitle)
    fUnity.GetXaxis().SetTickLength(0.1)
    fUnity.GetXaxis().SetTitleOffset(1.05)
    fUnity.GetXaxis().SetTitleSize(0.16)
    fUnity.GetXaxis().SetLabelSize(0.14)

    #dY = 0.399
    dY = 0.75
    fUnity.GetYaxis().SetTitle("Obs/Bkg")
    #fUnity.GetYaxis().SetRangeUser(1.-dY,1.+dY)
    fUnity.SetMaximum(1.+dY)
    fUnity.SetMinimum(1.-dY)
    fUnity.GetYaxis().SetNdivisions(305)
    fUnity.GetYaxis().SetTickLength(0.04)
    fUnity.GetYaxis().SetLabelFont(62)
    fUnity.GetYaxis().SetTitleFont(62)
    fUnity.GetYaxis().SetTitleOffset(.25)
    fUnity.GetYaxis().SetTitleSize(0.15)
    fUnity.GetYaxis().SetLabelSize(0.12)

    fUnity.SetLineColor(9)
    #fUnity.SetLineColor(3)
    #fUnity.SetLineWidth(1)
    fUnity.SetLineWidth(0)
    fUnity.SetLineStyle(1)
    fUnity.SetTitle("")
    fUnity.Draw("L")

    # For h4g: sg err bands
    if is_h4g:
        k = kobs_nom
        kr = k+'err'
        h[kr] = ROOT.TGraphAsymmErrors()
        h[kr].SetName(kr)
        for i in range(h[k].GetNbinsX()-1):
            ib = i+1
            #print(ib, k, h[k].GetBinContent(ib), h[k].GetBinContent(ib+1))
            h[kr].SetPoint(i, h[k].GetBinCenter(ib), 1.)
            h[kr].SetPointError(
                i,
                h[k].GetBinWidth(ib)/2.,
                h[k].GetBinWidth(ib)/2.,
                #0.,#1. - (h[k].GetBinError(ib)/h[k].GetBinContent(ib)),
                #0.# (h[k].GetBinError(ib)/h[k].GetBinContent(ib)) - 1.,
                (h[k].GetBinError(ib)/h[k].GetBinContent(ib)) if h[k].GetBinContent(ib) > 0. else 0.,
                (h[k].GetBinError(ib)/h[k].GetBinContent(ib)) if h[k].GetBinContent(ib) > 0. else 0.
                )
        h[kr].SetFillColor(1)
        h[kr].SetFillStyle(3003)
        h[kr].Draw("E2 same")

    # Plot bkg err bands
    k = kbkg_nom
    kr = k+'err'
    h[kr] = ROOT.TGraphAsymmErrors()
    h[kr].SetName(kr)
    for i in range(h[k].GetNbinsX()-1):
        ib = i+1
        #print(ib, k, h[k].GetBinContent(ib), h[k].GetBinContent(ib+1))
        h[kr].SetPoint(i, h[k].GetBinCenter(ib), 1.)
        h[kr].SetPointError(
            i,
            h[k].GetBinWidth(ib)/2.,
            h[k].GetBinWidth(ib)/2.,
            #0.,#1. - (h[k].GetBinError(ib)/h[k].GetBinContent(ib)),
            #0.# (h[k].GetBinError(ib)/h[k].GetBinContent(ib)) - 1.,
            (h[k].GetBinError(ib)/h[k].GetBinContent(ib)) if h[k].GetBinContent(ib) > 0. else 0.,
            (h[k].GetBinError(ib)/h[k].GetBinContent(ib)) if h[k].GetBinContent(ib) > 0. else 0.
            )
    h[kr].SetFillColor(9)
    h[kr].SetFillStyle(3002)
    h[kr].Draw("E2 same")

    # Plot syst up/dn
    if plot_syst:
        kr = kfit+'ratio'
        h[kr] = ROOT.TGraphAsymmErrors()
        h[kr].SetName(kr)
        yvals = h[kfit].GetY()
        eyhis = h[kfit].GetEYhigh()
        eylos = h[kfit].GetEYlow()
        for i in range(h[kfit].GetN()):
            h[kr].SetPoint(i, i+0.5, 1.)
            h[kr].SetPointError(
                i,
                0.5,
                0.5,
                1.- (yvals[i]-eylos[i])/yvals[i] if yvals[i] > 0. else 0.,
                (yvals[i]+eyhis[i])/yvals[i] - 1 if yvals[i] > 0. else 0.
                )
        h[kr].SetFillColor(3)
        h[kr].SetFillStyle(3001)
        h[kr].Draw("E2 same")

    # Plot obs/bkg err bars
    if not is_h4g:
        kr = kobs_nom+'ratio'
        h[kr] = h[kobs_nom].Clone()
        h[kr].Reset()
        ##h[kr].Divide(h[kbkg_nom])
        for i in range(1, h[kr].GetNbinsX()+1):
          #binc = h[kobs_nom].GetBinContent(i)
          #h[kr].SetBinError(i, 1./np.sqrt(binc) if binc != 0 else 0.)
          binc_num = h[kobs_nom].GetBinContent(i)
          binc_den = h[kbkg_nom].GetBinContent(i)
          binerr_num = h[kobs_nom].GetBinError(i)
          binerr_den = h[kbkg_nom].GetBinError(i)
          #err_ = get_cplimits_sym(binc_num, binc_den, binerr_num, binerr_den)
          #print(i, binc_num, binc_den, binc_num/binc_den, binerr_num, binerr_den, err_)
          h[kr].SetBinContent(i, binc_num/binc_den if binc_den > 0. else 0.)
          #h[kr].SetBinError(i, err_)
          h[kr].SetBinError(i, binerr_num/binc_num if binc_num > 0. else 0.)
          #if i<10: print(kr, binc_num/binc_den)

        #h[kr].SetFillStyle(0)
        h[kr].SetMarkerStyle(20)
        h[kr].SetMarkerSize(0.85)
        h[kr].Draw("Ep same")

    #fUnityUp = ROOT.TF1('fUnityUp',"[0]",0., float(nbins))
    #fUnityUp.SetParameter( 0, 1.2 )
    #fUnityUp.SetLineWidth(1)
    #fUnityUp.SetLineStyle(2)
    #fUnityUp.Draw("L same")
    #fUnityDn = ROOT.TF1('fUnityDn',"[0]",0., float(nbins))
    #fUnityDn.SetParameter( 0, 0.8 )
    #fUnityDn.SetLineWidth(1)
    #fUnityDn.SetLineStyle(2)
    #fUnityDn.Draw("L same")

    pDn.SetGridy()
    pDn.Update()
    #pDn.RedrawAxis()
    #fUnity.Draw("axis same")
    #'''
    c[kc].Draw()
    #c[kc].Update()
    c[kc].Print('Plots/Sys2D_%s.pdf'%(kc))

def get_data_flat(region, ksrc, ktgt, nbins):

    k_flat = 'flat_'+ktgt
    h[k_flat] = ROOT.TH1F(k_flat, k_flat, nbins, 0., nbins)

    ibin = 1
    for ix in range(2, h[ksrc].GetNbinsX()+1):
        for iy in range(2, h[ksrc].GetNbinsY()+1):

            if h[ksrc].GetBinContent(ix, iy) == 0: continue

            binc = h[ksrc].GetBinContent(ix, iy)
            h[k_flat].SetBinContent(ibin, binc)
            ibin += 1

    #print(ibin-1, nbins)
    assert ibin-1 == nbins

def get_datavmc_flat(ksrcs, ktgts, nbins):

    ksr, klo, knom, khi = ksrcs

    is_h4g = True if 'h4g' in ksr else False

    for k in ktgts:

        kflat = 'flat_'+k

        if 'Fit' in k:
            h[kflat] = ROOT.TGraphAsymmErrors()
            h[kflat].SetName(kflat)
        else:
            h[kflat] = ROOT.TH1F(kflat, kflat, nbins, 0., nbins)

        ibin = 1
        for ix in range(2, h[knom].GetNbinsX()+1):
            for iy in range(2, h[knom].GetNbinsY()+1):

                if h[knom].GetBinContent(ix, iy) == 0: continue

                binsr = h[ksr].GetBinContent(ix, iy)
                binlo = h[klo].GetBinContent(ix, iy)
                #binnom = h[knom].GetBinContent(ix, iy) if not is_h4g else binsr
                binnom = h[knom].GetBinContent(ix, iy)
                binhi = h[khi].GetBinContent(ix, iy)

                binerrsr = h[ksr].GetBinError(ix, iy)
                binerrlo = h[klo].GetBinError(ix, iy)
                #binerrnom = h[knom].GetBinError(ix, iy) if not is_h4g else binerrsr
                binerrnom = h[knom].GetBinError(ix, iy)
                binerrhi = h[khi].GetBinError(ix, iy)

                if 'Obs' in k:
                    h[kflat].SetBinContent(ibin, binsr)
                    h[kflat].SetBinError(ibin, binerrsr)
                elif 'Down' in k:
                    h[kflat].SetBinContent(ibin, binlo)
                    h[kflat].SetBinError(ibin, binerrlo)
                elif 'Nom' in k:
                    h[kflat].SetBinContent(ibin, binnom)
                    h[kflat].SetBinError(ibin, binerrnom)
                elif 'Up' in k:
                    h[kflat].SetBinContent(ibin, binhi)
                    h[kflat].SetBinError(ibin, binerrhi)
                else:
                    # For 'Fit' use TGraphAsymmErrors
                    # For a given syst lo/hi, set upper (lower) error
                    # to correspond to syst with higher (lower) bin value
                    # since syst lo (hi) doesnt necessarily give lowest (highest)
                    # content for all bins

                    # For h4g, binnom is the bkg so syst up/dn
                    # must be taken wrt binsr to get h4g nom value
                    if is_h4g:
                        binnom = binsr
                    binup = binhi if binhi > binlo else binlo
                    bindn = binlo if binhi > binlo else binhi
                    if binnom > binup:
                        binup = binnom
                    if binnom < bindn:
                        bindn = binnom
                    #assert binup > binnom
                    #assert binnom > bindn
                    h[kflat].SetPoint(ibin-1, ibin-0.5, binnom)
                    h[kflat].SetPointError(
                        ibin-1,
                        0.5,
                        0.5,
                        binnom-bindn,
                        binup-binnom
                        )
                ibin += 1

        #print(ibin-1, nbins)
        print('>> Bin count, actual: %d vs expected: %d'%(ibin-1, nbins))
        assert ibin-1 == nbins
        #print(kflat, h[kflat].Integral(), type(h[kflat]))

def rebin2d(h, ma_bins):

    nbins = len(ma_bins)-1
    #print(h.GetName())
    name = h.GetName()+'_rebin'
    #print(name)
    hrebin = ROOT.TH2F(name, name, nbins, ma_bins, nbins, ma_bins)
    #hrebin.Sumw2()

    for ix in range(0, h.GetNbinsX()+2):
        ma_x = h.GetXaxis().GetBinCenter(ix)
        #ma_x = h.GetXaxis().GetBinLowEdge(ix)
        ix_rebin = hrebin.GetXaxis().FindBin(ma_x)
        for iy in range(0, h.GetNbinsY()+2):
            ma_y = h.GetYaxis().GetBinCenter(iy)
            #ma_y = h.GetYaxis().GetBinLowEdge(iy)
            iy_rebin = hrebin.GetYaxis().FindBin(ma_y)
            binc = h.GetBinContent(ix, iy)

            ixy_rebin = hrebin.GetBin(ix_rebin, iy_rebin)
            hrebin.AddBinContent(ixy_rebin, binc)
            #if ix == 2: print(iy, ma_y, iy_rebin, binc)

    return hrebin.Clone()
    #return hrebin

f, hf, = {}, {}
h = OrderedDict()
fLine = {}
hatch, hatch2 = {}, {}
ax, ay = {}, {}
c = {}

keys = ['ma0vma1']
#valid_blind = 'sg'
valid_blind = 'diag_lo_hi'
limit_blind = 'offdiag_lo_hi'
blinds = [valid_blind, limit_blind]
#blinds = [valid_blind]
systs = ['flo', 'hgg']
#systs = []
#cr = 'a0noma1inv'
syst_shifts = {}
syst_shifts['flo'] = ['Dn', 'Up']
#syst_shifts['hgg'] = ['Nom', 'Syst']
syst_shifts['hgg'] = ['Dn', 'Up']
apply_blinding = True
apply_blinding = False
plot_syst = False
plot_syst = True

#run = '2016'
#run = '2017'
#run = '2018'
run = 'Run2'
sample_data = 'data' if run == 'Run2' else 'data%s'%run
sample = sample_data
r_sb2sr, r_sr = 'sb2sr+hgg', 'sr'
regions = [r_sb2sr, r_sr]
indir = 'root://cmseos.fnal.gov//store/user/lpchaa4g/mandrews/%s'%run
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p05_etalt1p44' # nominal
#sub_campaign = 'bdtgtm0p99_relChgIsolt0p05_etalt1p44' # bdt > -0.99
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p05_etalt1p44' # bdt > -0.96
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p03_etalt1p44' # relChgIso < 0.03
#sub_campaign = 'bdtgtm0p98_relChgIsolt0p07_etalt1p44' # relChgIso < 0.07
#sub_campaign = 'bdtgtm0p99_relChgIsolt0p03_etalt1p44' # bdt > -0.99, relChgIso < 0.03
sub_campaign = 'bdtgtm0p96_relChgIsolt0p07_etalt1p44' # bdt > -0.96, relChgIso < 0.07 !! optimal
#sub_campaign = 'bdtgtm0p97_relChgIsolt0p06_etalt1p44' # bdt > -0.97, relChgIso < 0.06
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p09_etalt1p44' # bdt > -0.96, relChgIso < 0.09
#sub_campaign = 'bdtgtm0p96_relChgIsolt0p08_etalt1p44' # bdt > -0.96, relChgIso < 0.08
#campaign = 'bkgPtWgts-Era04Dec2020v2/%s/nom-nom/Templates_bkg'%sub_campaign # combined full Run2, 2016H+2018 failed lumis, run = 'Run2'
#campaign = 'bkgPtWgts-Era22Jun2021v1/%s/nom-nom/Templates_bkg'%sub_campaign # combined full Run2, mgg95
#campaign = 'bkgPtWgts-Era22Jun2021v3/%s/nom-nom/Templates_bkg'%sub_campaign # combined full Run2, mgg95, hgg template with SFs
campaign = 'bkgPtWgts-Era22Jun2021v4/%s/nom-nom/Templates_bkg'%sub_campaign # combined full Run2, mgg95, hgg template with SFs, fhgg from br(hgg)

# Nominals
inpath = '%s/%s/%s_sb2sr+hgg.root'%(indir, campaign, sample)
print('>> Reading file:', inpath)
hf['nom'] = ROOT.TFile.Open(inpath, "READ")
for b in blinds:
    for r in regions:
        kidx = '%s_%s_%s'%(sample, r, b)
        kidx = kidx.replace('+hgg', '')
        for k in keys:
            kidx_k = '%s_%s'%(kidx, k)
            hname = '%s_%s_%s-%s'%(sample, r, k, b)
            h[kidx_k] = hf['nom'].Get(hname)
            h[kidx_k].SetName(kidx_k)
            #print('Adding:',kidx_k, hname, h[kidx_k].GetName(), h[kidx_k].Integral())

# Syst shifts, sb2sr only
for syst in systs:
    for shift in syst_shifts[syst]:
        if syst == 'hgg' and shift == 'Nom':
            inpath = '%s/%s/%s_sb2sr+hgg.root'%(indir, campaign, sample)
        else:
            inpath = '%s/%s/%s_sb2sr+hgg_%s%s.root'%(indir, campaign, sample, syst, shift)
        print('>> Reading file:', inpath)
        hf[syst+shift] = ROOT.TFile.Open(inpath, "READ")
        for b in blinds:
            for r in [r_sb2sr]:
                kidx = '%s_%s_%s_%s%s'%(sample, r, b, syst, shift)
                kidx = kidx.replace('+hgg', '')
                # hgg shift range is (Nom, Up)
                for k in keys:
                    kidx_k = '%s_%s'%(kidx, k)
                    hname = '%s_%s_%s-%s'%(sample, r, k, b)
                    h[kidx_k] = hf[syst+shift].Get(hname)
                    h[kidx_k].SetName(kidx_k)
                    #print('Adding:',kidx_k, h[kidx_k].Integral())

dMa = 25
#dMa = 50
#dMa = 100
ma_bins = list(range(0,1200+dMa,dMa))
ma_bins = [-400]+ma_bins
ma_bins = [float(m)/1.e3 for m in ma_bins]
#print(len(ma_bins))
ma_bins = array('d', ma_bins)

if dMa == 50:
    #nbins = {valid_blind:420, limit_blind:196} #dM50, blind_w=200MeV
    nbins = {valid_blind:342, limit_blind:270} #dM50, blind_w=300MeV
elif dMa == 100:
    #nbins = {valid_blind:110, limit_blind:54} #dM100, blind_w = 200MeV
    nbins = {valid_blind:90, limit_blind:72} #dM100, blind_w = 300MeV
else:
    #nbins = {valid_blind:1640, limit_blind:664} #dM25, blind_w = 200MeV
    nbins = {valid_blind:1332, limit_blind:972} #dM25, blind_w = 300MeV

hvalid, hlimit = {}, {}

#xtitle, ytitle, ztitle = "m_{a_{1},pred} [GeV]", "m_{a_{2},pred} [GeV]", "N_{evts} / %d MeV"%(dMa)
xtitle, ytitle, ztitle = "m_{#Gamma_{1},pred} [GeV]", "m_{#Gamma_{2},pred} [GeV]", "N_{evts} / %d MeV"%(dMa)
#zrange = None
#zrange = [0., 650.]
if dMa == 100:
    # Run2
    ymax_1d = 54.e3
    ymax_flat = 18.e3
elif dMa == 50:
    # Run2
    ymax_1d = 30.e3
    ymax_flat = 5.4e3
else:
    # Run2
    ymax_1d = 18.e3 # 16.e3
    ymax_flat = 1.6e3
zrange = [0., ymax_flat]
do_trunc = True
do_log = False if do_trunc else True

for kidx in h:

    key = kidx.split('_')[-1]
    if key != 'ma0vma1': continue

    k = kidx+'_rebin'
    if ma_bins is None: continue
    h[k] = rebin2d(h[kidx], ma_bins)

    for ix in range(1, h[k].GetNbinsX()+1):
        for iy in range(1, h[k].GetNbinsY()+1):
            binc = h[k].GetBinContent(ix, iy)
            binerr = h[k].GetBinError(ix, iy)
            h[k].SetBinContent(ix, iy, binc)
            h[k].SetBinError(ix, iy, binerr)

    #plot_2dma(k, "", xtitle, ytitle, ztitle, zrange, do_trunc, do_log=do_log)
    #print(k, h[k].GetName(), h[k].Integral())

#for kidx in h.keys():
#
#    #print(kidx)
#    key = kidx.split('_')[-1]
#    if key != 'ma0' and key != 'ma1': continue
#
#    #print(kidx)
#    #plot_1dma(kidx, "", yrange=None, new_canvas=True, color=1, titles=["m_{#Gamma,pred} [GeV]", "N_{evts} / 25 MeV"])
#
##keys_1d = ['ma0', 'ma1']
#keys_1d = keys[1:]
#for key in keys_1d:
#    for blind in blinds:
#        for syst in systs:
#
#            ksr = '%s_sr_%s'%(sample, blind)
#            if apply_blinding and blind == limit_blind:
#                ksr = '%s_sb2sr_%s'%(sample, blind)
#            ksrcs = [
#                ksr,
#                '%s_sb2sr_%s_%s%s'%(sample, blind, syst, syst_shifts[syst][0]),
#                '%s_sb2sr_%s'%(sample, blind),
#                '%s_sb2sr_%s_%s%s'%(sample, blind, syst, syst_shifts[syst][1])
#                ]
#            ksrcs = ['%s_%s'%(ksrc, key) for ksrc in ksrcs]
#            #print(ksrcs)
#            draw_hist_1dma_syst(ksrcs, syst, ymax_=ymax_1d, plot_syst=plot_syst)
#
##########################
kfitpol = 'pol2_2d_x_bkg'
#kfitsrc = '%s_sb2sr_%s_%s'%(sample, valid_blind, keys[0])
#kfittgt = '%s_sr_%s_%s'%(sample, valid_blind, keys[0])
kfitsrc = '%s_sb2sr_%s_%s_rebin'%(sample, valid_blind, keys[0])
kfittgt = '%s_sr_%s_%s_rebin'%(sample, valid_blind, keys[0])
print('fitsrc:',h[kfitsrc].Integral())
print('fittgt:',h[kfittgt].Integral())

k = kfitpol
#h[k] = ROOT.TF2(k, pol2_2d_x_bkg, -0.4, 1.2, -0.4, 1.2, nparams)
h[k] = ROOT.TF2(k, pol2_2d_x_bkg, 0., 1.2, 0., 1.2, nparams)
## Run2, nom-nom
if dMa == 25:
    pass
#    h[k].FixParameter(0,  9.86310e-01)
#    h[k].FixParameter(1, -6.07111e-03)
#    h[k].FixParameter(2,  3.15883e-02)
elif dMa == 50:
    pass
#    h[k].FixParameter(0,  9.85385e-01)
#    h[k].FixParameter(1, -5.41274e-03)
#    h[k].FixParameter(2,  3.23650e-02)
elif dMa == 100:
    pass
#    h[k].FixParameter(0,  9.85385e-01)
#    h[k].FixParameter(1, -5.18422e-03)
#    h[k].FixParameter(2,  3.26524e-02)
else:
    raise Exception('Invalid dMa',dMa)

#fitResult = h[kfittgt].Fit(h[k], "LLIEMNS")
# Set fit tgt to have stat errs of bkg+tgt
# since TF2 fitting doesnt account for bkg (fitsrc) errs
kfittgt_stat = kfittgt+'_stat'
h[kfittgt_stat] = h[kfittgt].Clone()
h[kfittgt_stat].SetName(kfittgt_stat)
h[kfittgt_stat].SetTitle(kfittgt_stat)
#nbinsall = 0
#nbinsnonzero = 0
for ix in range(1, h[kfittgt_stat].GetNbinsX()+1):
    for iy in range(1, h[kfittgt_stat].GetNbinsY()+1):
        binerr_tgt = h[kfittgt].GetBinError(ix, iy)
        binerr_src = h[kfitsrc].GetBinError(ix, iy)
        binerr = np.sqrt(binerr_tgt*binerr_tgt + binerr_src*binerr_src)
        h[kfittgt_stat].SetBinError(ix, iy, binerr)
        #if h[kfittgt_stat].GetBinContent(ix, iy) == 0:
        #    pass
        #    #print(ix, iy, binerr)
        #else:
        #    nbinsnonzero += 1
        #nbinsall += 1
#print(nbinsall, nbinsnonzero)
fitResult = h[kfittgt_stat].Fit(h[k], "LLIEMNS")
chi2 = h[k].GetChisquare()
ndof = h[k].GetNDF()
pval = h[k].GetProb()
nDiag = nbins[limit_blind]
ndofoff = ndof-nDiag
print('chi2 / ndf: %f / %f = %f'%(chi2, ndof, chi2/ndof))
print('chi2 / (ndf-nDiag): %f / %f = %f'%(chi2, ndofoff, chi2/ndofoff))
print('p-val:',pval)
#cor = fitResult.GetCorrelationMatrix()
cov = fitResult.GetCovarianceMatrix()
#cor.Print()
cov.Print()

########################
# Get pol2d nom params
gpol = {}
params = {}
params['nom'] = [h[kfitpol].GetParameter(i) for i in range(nparams)]
gpol['nom'] = get_pol_hist(params['nom'], 'nom')
# Plot
k = 'pol2dnom'
h[k] = h[kfitsrc].Clone()
h[k].SetName(k)
h[k].Reset()
for ix in range(1, h[kfitsrc].GetNbinsX()+1):
    for iy in range(1, h[kfitsrc].GetNbinsY()+1):
        ma_x, ma_y = h[kfitsrc].GetXaxis().GetBinCenter(ix), h[kfitsrc].GetYaxis().GetBinCenter(iy)
        pol_val = gpol['nom'].Eval(ma_x, ma_y)
        h[k].SetBinContent(ix, iy, pol_val)
print('pol_hist:%s, min:%f, max:%f'%(k, h[k].GetMinimum(), h[k].GetMaximum()))
#plot_2dma(k, "", xtitle, ytitle, 'pol2d', [1.-0.05, 1.+0.05])
#plot_2dma(k, "", xtitle, ytitle, 'pol2d', [1.-0.1, 1.+0.1], do_trunc=do_trunc)
plot_2dma(k, "", xtitle, ytitle, 'pol2d', [1.-0.04, 1.+0.04], do_trunc=do_trunc)

# Eigenvariations from solving covariance matrix
# Must be hardcoded here
if dMa == 25:
    pass
    varvec = np.array([
    # nominal
    #blind_w = 300MeV
    #np.sqrt(1.083130e-04) * np.array([ 0.587484331363,-0.571860187163,-0.572571468675 ]),
    #np.sqrt(3.032697e-06) * np.array([ -0.807475967646,-0.367619503654,-0.461344190607 ]),
    #np.sqrt(2.450429e-05) * np.array([ -0.0533359360665,-0.733370184062,0.677734056288 ])
    #fhggv2
    #np.sqrt(1.083969e-04) * np.array([ 0.586567939731,-0.572481966161,-0.572889562219 ]),
    #np.sqrt(3.039681e-06) * np.array([ -0.808148208137,-0.367222218812,-0.460482698584 ]),
    #np.sqrt(2.453346e-05) * np.array([ -0.0532402644964,-0.733084060959,0.678051055456 ])
    #fhggv3
    # no neg
    #np.sqrt(1.083035e-04) * np.array([ 0.58764846401,-0.571807582417,-0.572455562849 ]),
    #np.sqrt(3.036732e-06) * np.array([ -0.807346534633,-0.36761639508,-0.461573135142 ]),
    #np.sqrt(2.449972e-05) * np.array([ -0.0534869681563,-0.733412758792,0.677676080055 ])
    # bkg v3
    #np.sqrt(1.083035e-04) * np.array([ 0.58764846401,-0.571807582417,-0.572455562849 ]),
    #np.sqrt(3.036732e-06) * np.array([ -0.807346534633,-0.36761639508,-0.461573135142 ]),
    #np.sqrt(2.449972e-05) * np.array([ -0.0534869681563,-0.733412758792,0.677676080055 ])
    # bkg v4
    #np.sqrt(1.082743e-04) * np.array([ 0.587870556337,-0.571620914571,-0.572413957741 ]),
    #np.sqrt(3.040593e-06) * np.array([ -0.80718115531,-0.367654312892,-0.461832100145 ]),
    #np.sqrt(2.449512e-05) * np.array([ -0.0535424271403,-0.733539253371,0.677534775683 ])
    # pol2d-O2
    np.sqrt(3.872762e-03) * np.array([ 0.246124760675,-0.54404331697,-0.559281238542,0.366783778543,0.307224203898,0.318946572321 ]),
    np.sqrt(6.286036e-04) * np.array([ -0.0251465634086,-0.524142068299,0.525699952524,0.021672111431,0.492943075944,-0.452570155853 ]),
    np.sqrt(3.822890e-04) * np.array([ -0.0652114848391,-0.0620881465061,-0.0833354479468,-0.830511748144,0.396794192027,0.371150013865 ]),
    np.sqrt(4.397047e-05) * np.array([ 0.651568293652,-0.234956213449,-0.195019698082,-0.388950232115,-0.384425568921,-0.427967700564 ]),
    np.sqrt(2.315713e-06) * np.array([ 0.712050006088,0.340168922439,0.41635258376,0.15133205257,0.257972374664,0.338333094463 ]),
    np.sqrt(1.125893e-05) * np.array([ -0.0546009369358,-0.504497478222,0.438767709162,-0.0326579604567,-0.539297707636,0.508011190534 ])
    ])
elif dMa == 50:
    pass
    # bkgv4
    varvec = np.array([
    np.sqrt(1.086348e-04) * np.array([ 0.587992304358,-0.571797807927,-0.572112154098 ]),
    np.sqrt(3.024985e-06) * np.array([ -0.807083314216,-0.367802804655,-0.46188485665 ]),
    np.sqrt(2.455026e-05) * np.array([ -0.053680293692,-0.733326914642,0.677753688541 ])
    ])
elif dMa == 100:
    pass
    varvec = np.array([
    # !! dummy values !!
    np.sqrt(1.083035e-04) * np.array([ 0.58764846401,-0.571807582417,-0.572455562849 ]),
    np.sqrt(3.036732e-06) * np.array([ -0.807346534633,-0.36761639508,-0.461573135142 ]),
    np.sqrt(2.449972e-05) * np.array([ -0.0534869681563,-0.733412758792,0.677676080055 ])
    ])
else:
    raise Exception('invalid dMa',dMa)
varvec *= 1.
for v in varvec:
    print(v)

key = keys[0]
# Shift nominal bkg model (without pol2d corr) by each of pol2d param uncertainties
# Do not use pol2d corr bkg model as pol2d+/-shift should be applied on same hist
# as was used to derive the fit
for i in range(nparams):

    # Add a new syst for each pol2d param
    pol_syst = 'pol2de'+str(i)
    systs.append(pol_syst)
    syst_shifts[pol_syst] = []

    # Derive shifted bkg model for each syst shift
    for shift in ['dn', 'up']:

        v = 'e%d%s'%(i, shift)
        # Calculate shifted pol2d fn from shifted params
        params[v] = var_params(params['nom'], varvec[i], shift)
        gpol[v] = get_pol_hist(params[v], v)
        # Add this shift to syst_shift list for this pol_syst
        syst_shifts[pol_syst].append(shift)

        # Apply shift over all input blinded regions
        for blind in blinds:
            # src bkg model
            ksrc = '%s_sb2sr_%s_%s_rebin'%(sample, blind, key)
            ktgt = '%s_sb2sr_%s_%s%s_%s_rebin'%(sample, blind, pol_syst, shift, key)
            print(ktgt)
            h[ktgt] = h[ksrc].Clone()
            h[ktgt].SetName(ktgt)
            scale_bypol(ktgt, gpol[v])

polfile_out = ROOT.TFile('Fits/bkgxpol.root', "RECREATE")
# Scale all non-pol2d syst bkg models by nom pol2d shape
for kidx in h.keys():

    if 'pol2d' in kidx: continue
    if 'rebin' not in kidx: continue
    kidx_split = kidx.split('_')
    if kidx_split[1] != 'sb2sr': continue
    if kidx_split[-2] != 'ma0vma1': continue

    k = kidx
    '''
    for ix in range(1, h[k].GetNbinsX()+1):
        for iy in range(1, h[k].GetNbinsY()+1):
            binc = h[k].GetBinContent(ix, iy)
            h[k].SetBinContent(ix, iy, binc)
    '''
    print('>> scale by pol2d, before: k:%s, min:%f, max:%f'%(k, h[k].GetMinimum(), h[k].GetMaximum()))
    scale_bypol(k, gpol['nom'])
    print('>> scale by pol2d, after: k:%s, min:%f, max:%f'%(k, h[k].GetMinimum(), h[k].GetMaximum()))
    h[k].Write()

polfile_out.Close()

##########################
# Get total syst
syst_shifts['all'] = ['dn', 'up']

# Initialize hists
for b in blinds:
    for k in h.keys():
        if '%s_sb2sr_%s_ma0vma1_rebin'%(sample, b) == k:
            #print('matched:',k)
            for shift in syst_shifts['all']:
                kSystAll = '%s_sb2sr_%s_all%s_ma0vma1_rebin'%(sample, b, shift)
                h[kSystAll] = h[k].Clone()
                h[kSystAll].SetName(kSystAll)
                h[kSystAll].SetTitle(kSystAll)

# Fill with total err (stat+syst) in quadrature
for b in blinds:
    kNom = '%s_sb2sr_%s_ma0vma1_rebin'%(sample, b)
    for ix in range(1, h[kNom].GetNbinsX()+1):
        for iy in range(1, h[kNom].GetNbinsY()+1):
            binc = h[kNom].GetBinContent(ix, iy)
            binerr = h[kNom].GetBinError(ix, iy)
            errlos = binc-np.array([h['%s_sb2sr_%s_%s%s_ma0vma1_rebin'%(sample, b, syst, syst_shifts[syst][0])].GetBinContent(ix,iy) for syst in systs])
            errlos = np.append(errlos, [binerr]) # included stat uncert
            errhis = np.array([h['%s_sb2sr_%s_%s%s_ma0vma1_rebin'%(sample,b, syst, syst_shifts[syst][1])].GetBinContent(ix,iy) for syst in systs])-binc
            errhis = np.append(errhis, [binerr]) # include stat uncert
            errs = np.array([[lo,hi]  if (lo >= 0.) and (hi >= 0.) else [abs(hi),abs(lo)] for lo,hi in zip(errlos, errhis)])
            #print(errs.shape)
            errdns = errs[:,0]
            errups = errs[:,1]
            qerrdn = np.sqrt(np.sum(errdns*errdns))
            qerrup = np.sqrt(np.sum(errups*errups))
            if ix <= 2:
                if iy <= 2:
                    pass
                    #print(ix, iy, binc, binerr, np.sqrt(binc))
                    #print(ix, iy, errlos)
                    #print(ix, iy, np.append(errlos, [binerr]))
                    #print(ix, iy, errdns)
                    #print(ix, iy, qerrdn)
                    #print(ix, iy, errups)
                    #print(ix, iy, qerrup)
            for shift in syst_shifts['all']:
                kSystAll = '%s_sb2sr_%s_all%s_ma0vma1_rebin'%(sample, b, shift)
                bincout = binc+qerrup if shift == syst_shifts['all'][1] else binc-qerrdn
                #print(ix, iy, shift, bincout)
                h[kSystAll].SetBinContent(ix, iy, bincout)
                #print(ix, iy, shift, h[kSystAll].GetBinContent(ix, iy))

# Add `all` to list of systs
systs.append('all')

##########################
# Redo 1d with pol correction
for kidx in h.keys():
    #if 'pol2d' in kidx: continue
    if 'rebin' not in kidx: continue
    print('rebinned:',kidx)
    ktgt = kidx+'_ma0'
    h[ktgt] = h[kidx].ProjectionX(ktgt)
    ktgt = kidx+'_ma1'
    h[ktgt] = h[kidx].ProjectionY(ktgt)

# Re-calculate 1d quadrature errors for `all` syst
keys_1d = ['ma0', 'ma1']
for key in keys_1d:
    for b in blinds:
        kNom = '%s_sb2sr_%s_ma0vma1_rebin_%s'%(sample, b, key)
        for ib in range(1, h[kNom].GetNbinsX()+1):
            binc = h[kNom].GetBinContent(ib)
            binerr = h[kNom].GetBinError(ib)
            errlos = binc-np.array([h['%s_sb2sr_%s_%s%s_ma0vma1_rebin_%s'%(\
                                       sample, b, syst, syst_shifts[syst][0], key)].GetBinContent(ib) for syst in systs if syst != 'all'])
            errlos = np.append(errlos, [binerr]) # included stat uncert
            errhis = np.array([h['%s_sb2sr_%s_%s%s_ma0vma1_rebin_%s'%(\
                                  sample,b, syst, syst_shifts[syst][1], key)].GetBinContent(ib) for syst in systs if syst != 'all'])-binc
            errhis = np.append(errhis, [binerr]) # include stat uncert
            errs = np.array([[lo,hi]  if (lo >= 0.) and (hi >= 0.) else [abs(hi),abs(lo)] for lo,hi in zip(errlos, errhis)])
            #print(errs.shape)
            errdns = errs[:,0]
            errups = errs[:,1]
            qerrdn = np.sqrt(np.sum(errdns*errdns))
            qerrup = np.sqrt(np.sum(errups*errups))
            #if ib < 2:
            #    print(ix, iy, errlos)
            #    print(ix, iy, errdns)
            #    print(ix, iy, qerrdn)
            #    print(ix, iy, binc)
            #    print(ix, iy, errlos)
            #    print(ix, iy, errups)
            #    print(ix, iy, qerrup)
            for shift in syst_shifts['all']:
                kSystAll = '%s_sb2sr_%s_all%s_ma0vma1_rebin_%s'%(sample, b, shift, key)
                bincout = binc+qerrup if shift == syst_shifts['all'][1] else binc-qerrdn
                h[kSystAll].SetBinContent(ib, bincout)

key_2d = 'ma0vma1'
#keys_1d = keys[1:]
for key in keys_1d:
    for blind in blinds:
        for syst in systs:

            #k:Run2017B-F_sb2sr_diag_lo_hi_ma0vma1_rebin, min:0.000000, max:1563.674316
            #'''
            ksr = '%s_sr_%s'%(sample, blind)
            if apply_blinding and blind == limit_blind:
                ksr = '%s_sb2sr_%s'%(sample, blind)
            ksrcs = [
                ksr,
                '%s_sb2sr_%s_%s%s'%(sample, blind, syst, syst_shifts[syst][0]),
                '%s_sb2sr_%s'%(sample, blind),
                '%s_sb2sr_%s_%s%s'%(sample, blind, syst, syst_shifts[syst][1])
                ]
            ksrcs = ['%s_%s_rebin_%s'%(ksrc, key_2d, key) for ksrc in ksrcs]
            #for ksrc in ksrcs:
            #    print(ksrc)
            #    assert ksrc in h.keys()
            #print('>> 1D-mA, ksrcs',ksrcs)
            if syst == 'all':
                draw_hist_1dma_statsyst(ksrcs, syst, ymax_=ymax_1d, plot_syst=plot_syst)
            else:
                draw_hist_1dma_syst(ksrcs, syst, ymax_=ymax_1d, plot_syst=plot_syst)
            #'''

k1dmas = [k for k in h.keys() if '_ma1' in k]
k1dmas = [k for k in k1dmas if 'offdiag' in k]
#k1dmas = [k for k in k1dmas if 'offdiag' in k]
print('>> 1D-mA, all offdiag ks:',k1dmas)

##########################
#xtitle, ytitle, ztitle = "m_{a_{1},pred} [GeV]", "m_{a_{2},pred} [GeV]", "(Data/Bkg) / %d MeV"%(dMa)
xtitle, ytitle, ztitle = "m_{#Gamma_{1},pred} [GeV]", "m_{#Gamma_{2},pred} [GeV]", "(Data/Bkg) / %d MeV"%(dMa)
zrange = [0., 2.]

sr_k = sample+'sr'+valid_blind+key
sb2sr_k = sample+'sb2sr'+valid_blind+key
key = keys[0]

#########################
# Flatten 2d-ma distns
yrange_flat = [0., ymax_flat] # a0nom, a1nom, dM=100MeV
#yrange_flat = [0., 4.e3] # a0nom, a1nom, dM=100MeV
#yrange_flat = [0., 2.4e3] # a0nom, a1inv
#yrange_flat = [0., 650.] # a0nom, a1inv
#yrange_flat = [0., 200.] # a0inv, a1inv
#yrange_flat = [0., 1100.] # a0nom, a1nom
for blind in blinds:

    nbin = nbins[blind]

    for syst in systs:

        ksr = '%s_sr_%s'%(sample, blind)
        if apply_blinding and blind == limit_blind:
            ksr = '%s_sb2sr_%s'%(sample, blind)
        ksrcs = [
            #'%s_sr_%s'%(sample, blind),
            ksr,
            '%s_sb2sr_%s_%s%s'%(sample, blind, syst, syst_shifts[syst][0]),
            '%s_sb2sr_%s'%(sample, blind),
            '%s_sb2sr_%s_%s%s'%(sample, blind, syst, syst_shifts[syst][1])
            ]
        ksrcs = ['%s_%s_rebin'%(ksrc, key) for ksrc in ksrcs]
        ktgts = ['Obs', 'Down', 'Nom', 'Up', 'Fit']
        ktgts = ['%s_%s_%s%s'%(sample, blind, syst, ktgt) for ktgt in ktgts]
        get_datavmc_flat(ksrcs, ktgts, nbin)
        kplots = ['flat_'+k for k in ktgts]
        #if i != 0: continue
        if syst == 'all':
            plot_datavmc_flat_statsyst(blind, kplots, syst, nbin, yrange=yrange_flat, plot_syst=plot_syst)
        else:
            plot_datavmc_flat(blind, kplots, syst, nbin, yrange=yrange_flat, plot_syst=plot_syst)

for k in h.keys():
    pass
    if 'flat' in k: print('>> flat hist:',k)

## Make pull plots
#>> flat hist: flat_data_diag_lo_hi_floObs
#>> flat hist: flat_data_diag_lo_hi_floNom
kpullbkg = 'flat_%s_%s_%sNom'%(sample_data, valid_blind, systs[0]) # all Obs and Nom syst histograms are identical so take 1st
kpullobs = 'flat_%s_%s_%sObs'%(sample_data, valid_blind, systs[0]) # all Obs and Nom syst histograms are identical so take 1st
kpull = 'pull_%s_%s'%(valid_blind, keys[0])
ROOT.gStyle.SetOptFit(1)
c[kpull] = ROOT.TCanvas(kpull, kpull, wd, ht)
h[kpull] = ROOT.TH1F(kpull, kpull, 50, -10., 10.)
count = 0
for ib in range(1, h[kpullobs].GetNbinsX()+1):
    if h[kpullobs].GetBinContent(ib) == 0.: continue
    diff = h[kpullobs].GetBinContent(ib) - h[kpullbkg].GetBinContent(ib)
    #sg = h[kpullbkg].GetBinError(ib)
    sg_bkg = h[kpullbkg].GetBinError(ib)
    sg_obs = h[kpullobs].GetBinError(ib)
    sg = np.sqrt(sg_bkg*sg_bkg + sg_obs*sg_obs)
    #sg = sg_bkg
    pull = diff/sg
    h[kpull].Fill(pull)
    #if count < 10:
    #    print('>> pull:',diff, sg, diff/sg)
    count += 1
print('>> Pull, nentries:',count)
#ROOT.gStyle.SetOptStat(1)
gfit = ROOT.TF1("gfit","gaus",-10.,10.)
fit_xmax = 4. #if region =='valid' else 3.
h[kpull].Fit('gfit','L', '', -fit_xmax, fit_xmax)
h[kpull].SetMarkerStyle(20)
h[kpull].SetMarkerSize(0.85)
h[kpull].Draw('Ep')
gfit.SetLineColor(2)
gfit.Draw('same')
c[kpull].Draw()
c[kpull].Update()
c[kpull].Print('Plots/Sys2D_pull_obsvnom_%s_%s_rebin-flat.pdf'%(valid_blind, keys[0]))
chi2 = gfit.GetChisquare()
ndof = gfit.GetNDF()
print('chi2 / ndf: %f / %f = %f'%(chi2, ndof, chi2/ndof))

#'''
hout = OrderedDict()
file_out = ROOT.TFile('Fits/CMS_h4g_sgbg_shapes.root', "RECREATE")
#file_out = ROOT.TFile('Fits/Bkgfits_flat_region%s.root'%'limit', "RECREATE")
#file_out = ROOT.TFile('Datacards/%s_hists.root'%'shape', "UPDATE")
for i,syst in enumerate(systs):
    ksysts = [k for k in h.keys() if syst in k]
    #print(ksysts)
    ksysts = [k for k in ksysts if 'flat' in k]
    #print(ksysts)
    #ksysts = [k for k in ksysts if limit_blind in k]
    ksysts = [k for k in ksysts if valid_blind in k]
    #print(ksysts)
    for shift in ['Down', 'Up']:
        ksyst_shift = [k for k in ksysts if shift in k][0]
        #print(ksyst_shift, h[ksyst_shift].Integral())
        #kout = 'bkg_%s%s'%(syst, shift)
        kout = 'bkg_%s%s'%(dcard_syst(syst), shift)
        hout[kout] = h[ksyst_shift].Clone()
        hout[kout].SetName(kout)
        hout[kout].SetLineColor(1)
        #hout[kout].Write()
        #print(hout[kout].Integral())
        print(kout)
    if i != 0: continue
    for shift in ['Nom', 'Obs']:
        ksyst_shift = [k for k in ksysts if shift in k][0]
        #print(ksyst_shift, h[ksyst_shift].Integral())
        kout = 'data_obs' if shift == 'Obs' else 'bkg'
        hout[kout] = h[ksyst_shift].Clone()
        hout[kout].SetName(kout)
        hout[kout].SetLineColor(1)
        print(kout)
        if shift != 'Nom': continue
        #for stat in ['Up', 'Down']:
        #    kout = 'bkg_bstat%s'%stat
        #    hout[kout] = hout['bkg'].Clone()
        #    hout[kout].SetName(kout)
        #    print(kout)
        #    for ib in range(1, hout[kout].GetNbinsX()+1):
        #        binc = hout[kout].GetBinContent(ib)
        #        binerr = hout[kout].GetBinError(ib)
        #        binout = binc + binerr if stat == 'Up' else binc - binerr
        #        if binout < 0.:print(ib, binc, binerr)
        #        hout[kout].SetBinContent(ib, binout)

file_out.Write()
#file_out.Close()

#########################
# Signal samples
#########################
regions = ['sr']
blinds = [limit_blind]
#blinds = [valid_blind]
sample_sg = 'h4g'

#systs = ['PhoIdSF', 'Scale', 'Smear', 'Lumi']
#systs = ['PhoIdSF', 'Scale', 'Smear', 'Lumi', 'TrgSF']
systs = ['PhoIdSF', 'Scale', 'Smear', 'TrgSF']
#systs = ['Lumi']
#systs = ['Scale']
syst_shifts['PhoIdSF'] = ['dn', 'up']
syst_shifts['Scale'] = ['dn', 'up']
syst_shifts['Smear'] = ['dn', 'up']
syst_shifts['Lumi'] = ['dn', 'up']
syst_shifts['TrgSF'] = ['dn', 'up']
#systs = ['TEST'] # dummy to force output of nominal sg plots
#syst_shifts['TEST'] = ['dn', 'up']
keys = ['ma0vma1']

#run = 'Run2'
#run = '2017'
#indir = 'root://cmseos.fnal.gov//store/user/lpchaa4g/mandrews/%s'%run
#campaign = 'sg-Era04Dec2020v6/%s/nom-nom/Templates'%sub_campaign # 2016-18 phoid, 2016-18 ss. ss implemented only for shifted syst (as in v4)
#campaign = 'sg-Era22Jun2021v2/%s/nom-nom/Templates'%sub_campaign # phoid+trg SFs. mgg95. no HLT applied.
#campaign = 'sg-Era22Jun2021v3/%s/nom-nom/Templates'%sub_campaign # phoid+trg SFs. mgg95. no HLT applied.
#campaign = 'sg-Era22Jun2021v4/%s/nom-nom/Templates'%sub_campaign # ss with SFs
campaign = 'sg-Era22Jun2021v5/%s/nom-nom/Templates'%sub_campaign # ss with SFs

#runs = ['Run2']
#runs = ['2018', '2017']
runs = ['2016', '2017', '2018']

#ma_pts = ['0p1', '0p2', '0p4', '0p6', '0p8', '1p0', '1p2']
ma_pts = (np.arange(12)+1.)/10.
ma_pts = [str(m_).replace('.','p') for m_ in ma_pts]
#ma_pts = ['0p1']
#ma_pts = ['1p0']
#ma_pts = ['0p4']
#ma_pts = ['0p1', '0p4', '1p0']
#for ma in ['100MeV', '400MeV', '1GeV']:
for ma in ma_pts:

    for run in runs:

        #sample = 'h4g_%s'%ma
        sample = 'h4g-mA%sGeV'%ma if run == 'Run2' else 'h4g%s-mA%sGeV'%(run, ma)
        #norm = get_sg_norm(sample, xsec=50.*1.e-2)
        #norm = get_sg_norm(sample, xsec=1.)
        #print('%s mc2data norm: %.4f'%(sample, norm))
        indir = 'root://cmseos.fnal.gov//store/user/lpchaa4g/mandrews/%s'%run

        for b in blinds:
            for r in regions:
                # Nominals
                kidx = '%s_%s_%s'%(sample, r, b)
                #hf[kidx] = ROOT.TFile("%s/%s/%s_%s_blind_%s_templates.root"%(indir, 'nom', sample, r, b),"READ")
                inpath = "%s/%s/syst%s/%s_%s_blind_%s_templates.root"%(indir, campaign, 'Nom_nom', sample, r, b)
                print('>> Reading:', inpath)
                hf[kidx] = ROOT.TFile.Open(inpath, "READ")
                for k in keys:
                    kidx_k = '%s_%s'%(kidx, k)
                    kidx_h = '%s_%s_%s-%s'%(sample, r, k, b)
                    print('   .. input key:',kidx_h)
                    #h[kidx_k] = hf[kidx].Get(k)
                    h[kidx_k] = hf[kidx].Get(kidx_h)
                    h[kidx_k].SetName(kidx_k)
                    #h[kidx_k].Scale(norm)
                    print('   .. adding: %s, integral: %.f'%(kidx_k, h[kidx_k].Integral()))

                # Syst shifts
                for syst in systs:
                    for shift in syst_shifts[syst]:
                        kidx = '%s_%s_%s_%s%s'%(sample, r, b, syst, shift)
                        #hf[kidx] = ROOT.TFile("%s/%s/%s_%s_blind_%s_templates.root"%(indir, '%s_%s'%(syst,shift), sample, r, b),"READ")
                        inpath = "%s/%s/syst%s/%s_%s_blind_%s_templates.root"%(indir, campaign, '%s_%s'%(syst, shift), sample, r, b)
                        print('>> Reading:', inpath)
                        hf[kidx] = ROOT.TFile.Open(inpath, "READ")
                        for k in keys:
                            kidx_k = '%s_%s'%(kidx, k)
                            kidx_h = '%s_%s_%s-%s'%(sample, r, k, b)
                            print('   .. input key:',kidx_h)
                            #h[kidx_k] = hf[kidx].Get(k)
                            h[kidx_k] = hf[kidx].Get(kidx_h)
                            h[kidx_k].SetName(kidx_k)
                            #h[kidx_k].Scale(norm)
                            #print('Adding:',kidx_k)
                            print('   .. adding: %s, integral: %.f'%(kidx_k, h[kidx_k].Integral()))

        # Rebin
        for kidx in h.keys():
            if sample not in kidx: continue
            key = kidx.split('_')[-1]
            if key != key_2d: continue

            k = kidx+'_rebin'
            if ma_bins is not None:
                h[k] = rebin2d(h[kidx], ma_bins)

            for ix in range(1, h[k].GetNbinsX()+1):
                for iy in range(1, h[k].GetNbinsY()+1):
                    binc = h[k].GetBinContent(ix, iy)
                    h[k].SetBinContent(ix, iy, binc)

            #plot_2dma(k, "", xtitle, ytitle, ztitle, zrange, do_trunc, do_log=do_log)
#print(h.keys())

##########################
# Get total syst

syst_shifts['all'] = ['dn', 'up']

for ma in ma_pts:

    for run in runs:

        sample = 'h4g-mA%sGeV'%ma if run == 'Run2' else 'h4g%s-mA%sGeV'%(run, ma)

        # Initialize hists
        for b in blinds:
            for r in regions:
                k = '%s_%s_%s_ma0vma1_rebin'%(sample, r, b)
                for shift in syst_shifts['all']:
                    kSystAll = '%s_%s_%s_all%s_ma0vma1_rebin'%(sample, r, b, shift)
                    h[kSystAll] = h[k].Clone()
                    h[kSystAll].SetName(kSystAll)
                    h[kSystAll].SetTitle(kSystAll)

        # Fill with total err in quadrature
        for b in blinds:
            for r in regions:
                kNom = '%s_%s_%s_ma0vma1_rebin'%(sample, r, b)
                for ix in range(1, h[kNom].GetNbinsX()+1):
                    for iy in range(1, h[kNom].GetNbinsY()+1):
                        binc = h[kNom].GetBinContent(ix, iy)
                        errlos = binc-np.array([h['%s_%s_%s_%s%s_ma0vma1_rebin'%(\
                                                   sample, r, b, syst, syst_shifts[syst][0])].GetBinContent(ix,iy) for syst in systs])
                        errhis = np.array([h['%s_%s_%s_%s%s_ma0vma1_rebin'%(\
                                              sample, r, b, syst, syst_shifts[syst][1])].GetBinContent(ix,iy) for syst in systs])-binc
                        errs = np.array([[lo,hi]  if (lo >= 0.) and (hi >= 0.) else [abs(hi),abs(lo)] for lo,hi in zip(errlos, errhis)])
                        #print(errs.shape)
                        errdns = errs[:,0]
                        errups = errs[:,1]
                        qerrdn = np.sqrt(np.sum(errdns*errdns))
                        qerrup = np.sqrt(np.sum(errups*errups))
                        #print(ix, iy, errlos)
                        #print(ix, iy, binc)
                        #print(ix, iy, errhis)
                        #print(ix, iy, errs)
                        #print(ix, iy, errdns)
                        #print(ix, iy, qerrdn)
                        #print(ix, iy, errups)
                        #print(ix, iy, qerrup)
                        for shift in syst_shifts['all']:
                            kSystAll = '%s_%s_%s_all%s_ma0vma1_rebin'%(sample, r, b, shift)
                            bincout = binc+qerrup if shift == syst_shifts['all'][1] else binc-qerrdn
                            #print(ix, iy, shift, bincout)
                            h[kSystAll].SetBinContent(ix, iy, bincout)
                            #print(ix, iy, shift, h[kSystAll].GetBinContent(ix, iy))
                        #if iy > 2: break
                    #if ix > 2: break

# Add `all` to list of systs
systs.append('all')
#'''

#file_out = ROOT.TFile('Fits/Bkgfits_flat_region%s.root'%'limit', "UPDATE")
#file_out = ROOT.TFile('Fits/CMS_h4g_sgbg_shapes.root', "UPDATE")
file_out.cd()
for ma in ma_pts:

    for run in runs:

        sample = 'h4g-mA%sGeV'%ma if run == 'Run2' else 'h4g%s-mA%sGeV'%(run, ma)

        ##########################
        # Redo 1d with pol correction
        for kidx in h.keys():
            #if 'pol2d' in kidx: continue
            if 'rebin' not in kidx: continue
            if sample not in kidx: continue
            print('rebinned:',kidx)
            ktgt = kidx+'_ma0'
            h[ktgt] = h[kidx].ProjectionX(ktgt)
            ktgt = kidx+'_ma1'
            h[ktgt] = h[kidx].ProjectionY(ktgt)

        # Re-calculate 1d quadrature errors for `all` syst
        for key in keys_1d:
            for b in blinds:
                for r in regions:
                    kNom = '%s_%s_%s_ma0vma1_rebin_%s'%(sample, r, b, key)
                    for ib in range(1, h[kNom].GetNbinsX()+1):
                        binc = h[kNom].GetBinContent(ib)
                        errlos = binc-np.array([h['%s_%s_%s_%s%s_ma0vma1_rebin_%s'%(\
                                               sample, r, b, syst, syst_shifts[syst][0], key)].GetBinContent(ib) for syst in systs if syst != 'all'])
                        errhis = np.array([h['%s_%s_%s_%s%s_ma0vma1_rebin_%s'%(\
                                          sample, r, b, syst, syst_shifts[syst][1], key)].GetBinContent(ib) for syst in systs if syst != 'all'])-binc
                        errs = np.array([[lo,hi]  if (lo >= 0.) and (hi >= 0.) else [abs(hi),abs(lo)] for lo,hi in zip(errlos, errhis)])
                        #print(errs.shape)
                        errdns = errs[:,0]
                        errups = errs[:,1]
                        qerrdn = np.sqrt(np.sum(errdns*errdns))
                        qerrup = np.sqrt(np.sum(errups*errups))
                        #if ib < 2:
                        #    print(ix, iy, errlos)
                        #    print(ix, iy, errdns)
                        #    print(ix, iy, qerrdn)
                        #    print(ix, iy, binc)
                        #    print(ix, iy, errlos)
                        #    print(ix, iy, errups)
                        #    print(ix, iy, qerrup)
                        #for shift in syst_shifts['all']:
                        #    kSystAll = '%s_%s_%s_all%s_ma0vma1_rebin_%s'%(sample, r, b, shift, key)
                        #    bincout = binc+qerrup if shift == syst_shifts['all'][1] else binc-qerrdn
                        #    h[kSystAll].SetBinContent(ib, bincout)

        for key in keys_1d:
            for blind in blinds:
                for syst in systs:

                    ksrcs = [
                        '%s_sr_%s'%(sample, blind),
                        '%s_sr_%s_%s%s'%(sample, blind, syst, syst_shifts[syst][0]),
                        '%s_sb2sr_%s'%(sample_data, blind),
                        '%s_sr_%s_%s%s'%(sample, blind, syst, syst_shifts[syst][1])
                        ]
                    ksrcs = ['%s_%s_rebin_%s'%(ksrc, key_2d, key) for ksrc in ksrcs]
                    for ksrc in ksrcs:
                        print(ksrc)
                        assert ksrc in h.keys(), ksrc
                    #print(ksrcs)
                    draw_hist_1dma_syst(ksrcs, syst, ymax_=ymax_1d, plot_syst=plot_syst)
                    #'''

        # Flatten 2d -> 1d
        for blind in blinds:

            nbin = nbins[blind]

            for syst in systs:

                ksrcs = [
                    '%s_sr_%s'%(sample, blind),
                    '%s_sr_%s_%s%s'%(sample, blind, syst, syst_shifts[syst][0]),
                    #'%s_sb2sr_%s'%(sample, blind),
                    '%s_sb2sr_%s'%(sample_data, blind),
                    '%s_sr_%s_%s%s'%(sample, blind, syst, syst_shifts[syst][1])
                    ]
                ksrcs = ['%s_%s_rebin'%(ksrc, key_2d) for ksrc in ksrcs]
                ktgts = ['Obs', 'Down', 'Nom', 'Up', 'Fit']
                ktgts = ['%s_%s_%s%s'%(sample, blind, syst, ktgt) for ktgt in ktgts]
                get_datavmc_flat(ksrcs, ktgts, nbin)
                kplots = ['flat_'+k for k in ktgts]
                #if i != 0: continue
                plot_datavmc_flat(blind, kplots, syst, nbin, yrange=yrange_flat, plot_syst=plot_syst)

        #file_out = ROOT.TFile('Fits/Bkgfits_flat_region%s.root'%'limit', "UPDATE")
        for i,syst in enumerate(systs):
            ksysts = [k for k in h.keys() if syst in k]
            ksysts = [k for k in ksysts if sample in k]
            ksysts = [k for k in ksysts if 'flat' in k]
            #ksysts = [k for k in ksysts if limit_blind in k]
            ksysts = [k for k in ksysts if valid_blind in k]
            print(ksysts)
            for shift in ['Down', 'Up']:
                #print('shift:',shift)
                ksyst_shift = [k for k in ksysts if shift in k][0]
                print(ksyst_shift)#, h[ksyst_shift].Integral())
                #kout = 'h4g_%s%s'%(syst, shift)
                #kout = 'h4g_%s_%s%s'%(ma, syst, shift)
                kout = 'h4g_%s_%s%s'%(ma, dcard_syst(syst, run), shift)
                #hout[kout] = h[ksyst_shift].Clone()
                hout[kout] = hout['bkg'].Clone()
                hout[kout].Reset()
                hout[kout].SetName(kout)
                for ib in range(1, h[ksyst_shift].GetNbinsX()+1):
                    binc = h[ksyst_shift].GetBinContent(ib)
                    hout[kout].SetBinContent(ib, binc)
                hout[kout].SetLineColor(1)
                hout[kout].Write()
                #print(hout[kout].Integral())
                print(kout)
            if i != 0: continue
            for shift in ['Obs']:
                #print('shift:',shift)
                ksyst_shift = [k for k in ksysts if shift in k][0]
                #print(ksyst_shift, h[ksyst_shift].Integral())
                #kout = 'h4g'
                #kout = 'h4g_%s'%ma
                kout = 'h4g_%s_%s'%(ma, run)
                #hout[kout] = h[ksyst_shift].Clone()
                hout[kout] = hout['bkg'].Clone()
                hout[kout].Reset()
                hout[kout].SetName(kout)
                for ib in range(1, h[ksyst_shift].GetNbinsX()+1):
                    binc = h[ksyst_shift].GetBinContent(ib)
                    #ib_off = 0 #if ma != '1p0' else 360
                    #hout[kout].SetBinContent(ib+ib_off, binc)
                    hout[kout].SetBinContent(ib, binc)
                hout[kout].SetLineColor(1)
                hout[kout].Write()
                print(kout)
                #for stat in ['Up', 'Down']:
                #    kout = 'h4g_sstat%s'%stat
                #    hout[kout] = hout['h4g'].Clone()
                #    hout[kout].SetName(kout)
                #    print(kout)
                #    for ib in range(1, hout[kout].GetNbinsX()+1):
                #        binc = hout[kout].GetBinContent(ib)
                #        binerr = hout[kout].GetBinError(ib)
                #        binout = binc + binerr if stat == 'Up' else binc - binerr
                #        if binout < 0.:print(ib, binc, binerr)
                #        hout[kout].SetBinContent(ib, binout)
                #        #if ib < 10: print(ib, binc, binerr, np.sqrt(binc))

    #file_out.Write() # will write all hists created after initialization of `file_out`
file_out.Close()
