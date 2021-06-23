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
#CMS_lumi.lumi_sqrtS = "41.5 fb^{-1} (13 TeV)" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
CMS_lumi.lumi_sqrtS = "134 fb^{-1} (13 TeV)" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
iPos = 11
if( iPos==0 ): CMS_lumi.relPosX = 0.12
iPeriod = 0

wd, ht = int(800*1), int(680*1)
wd_wide = 1400

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
#nparams = 6
#nparams = 10

def pol2_2d_x_bkg(x, par):

    imx = h[kfitsrc].GetXaxis().FindBin(x[0])
    imy = h[kfitsrc].GetYaxis().FindBin(x[1])

    pol_val =  par[0] + par[1]*x[0] + par[2]*x[1]
    #pol_val =  par[0] + par[1]*x[0] + par[2]*x[1] + par[3]*x[0]*x[1]
    #pol_val =  par[0] + par[1]*x[0] + par[2]*x[1] + par[3]*x[0]*x[1] + par[4]*x[0]*x[0] + par[5]*x[1]*x[1]
    #pol_val =  par[0] + par[1]*x[0] + par[2]*x[1] + par[3]*x[0]*x[1] + par[4]*x[0]*x[0] + par[5]*x[1]*x[1]\
    #            + par[6]*x[0]*x[0]*x[0] + par[7]*x[1]*x[1]*x[1] + par[8]*x[0]*x[0]*x[1] + par[9]*x[0]*x[1]*x[1]
    hist_val = h[kfitsrc].GetBinContent(imx, imy)

    return pol_val*hist_val

def get_pol_hist(params, shift):

    pol2_2d = '[0] + [1]*x + [2]*y'
    #pol2_2d = '[0] + [1]*x + [2]*y +[3]*x*y'
    #pol2_2d = '[0] + [1]*x + [2]*y +[3]*x*y + [4]*x*x + [5]*y*y'
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
    h[k] = set_hist(h[k], "m_{a,pred} [GeV]", "N_{a} / %d MeV"%dMa, "")
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

    fUnity.GetXaxis().SetTitle("m_{a,pred} [GeV]")
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
    h[k] = set_hist(h[k], "m_{a,pred} [GeV]", "N_{a} / %d MeV"%dMa, "")
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
    legend[k].AddEntry(kobs+'errs', 'h #rightarrow aa #rightarrow 4#gamma' if is_h4g else "Obs", "lp")
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

    fUnity.GetXaxis().SetTitle("m_{a,pred} [GeV]")
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

sample_data = 'Run2017'
#sample_data = 'Run2017B-F'
sample = sample_data
keys = ['ma0vma1']
#keys = ['ma0vma1', 'ma1']
#keys = ['ma0vma1', 'ma0', 'ma1']
#valid_blind = 'sg'
valid_blind = 'diag_lo_hi'
limit_blind = 'offdiag_lo_hi'
blinds = [valid_blind, limit_blind]
#blinds = [valid_blind]
#syst = 'ptrwgt_resample'
#syst = 'ptrwgt'
#syst = 'tempfrac'
#systs = ['ptrwgt', 'tempfrace1', 'tempfrace2']
#systs = ['flo']
systs = ['flo', 'hgg']
#cr = 'a0noma1inv'
syst_shifts = {}
#syst_shifts['flo'] = ['0p406', '1p000']
#syst_shifts['flo'] = ['0p406', '0p758']
#syst_shifts['flo'] = ['0p504', '0p791']
#syst_shifts['flo_None_hgg'] = ['dn', 'up']
syst_shifts['flo'] = ['Dn', 'Up']
syst_shifts['hgg'] = ['Nom', 'Syst']
#indir = 'Templates/scan_ptrwgt'
#indir = 'Templates/scan_ptrwgt/nom-nom'
#indir = 'Templates/prod_normblind_diaglohi/nom-nom'
indir = 'Templates/prod_fixsb2srnorm/nom-nom'
apply_blinding = True
#apply_blinding = False
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
##campaign = 'runBkg_ptwgts_bdtgtm0p99-v2noceil/Templates_bkg'
##campaign = 'bkgPtWgts-Era04Dec2020v1/%s/nom-nom/Templates_bkg'%sub_campaign # no 2018A, 2016H+2018 failed lumis
##campaign = 'bkgPtWgts-Era04Dec2020v2/%s/nom-nom/Templates_bkg'%sub_campaign # 2016H+2018 failed lumis, run = '2017'
#campaign = 'bkgPtWgts-Era04Dec2020v2/%s/nom-nom/Run2/Templates_bkg'%sub_campaign # yr-by-yr with Run2 ptwgts, 2016H+2018 failed lumis, run = '2017'
campaign = 'bkgPtWgts-Era04Dec2020v2/%s/nom-nom/Templates_bkg'%sub_campaign # combined full Run2, 2016H+2018 failed lumis, run = 'Run2'
#2018/bkgPtWgts-Era04Dec2020v1/bdtgtm0p98_relChgIsolt0p05_etalt1p44/nom-nom/Templates_bkg/

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
    nbins = {valid_blind:420, limit_blind:196} #dM50
elif dMa == 100:
    nbins = {valid_blind:110, limit_blind:54} #dM100
else:
    #nbins = {valid_blind:1640, limit_blind:664} #dM25, blind_w = 200MeV
    nbins = {valid_blind:1332, limit_blind:972} #dM25, blind_w = 300MeV

hvalid, hlimit = {}, {}

xtitle, ytitle, ztitle = "m_{a_{1},pred} [GeV]", "m_{a_{2},pred} [GeV]", "N_{evts} / %d MeV"%(dMa)
#zrange = None
#zrange = [0., 650.]
if dMa == 100:
    #ymax_1d = 15.e3
    #ymax_flat = 4.e3
    # 2016
    #ymax_1d = 12.e3
    #ymax_flat = 5.e3
    # 2017
    #ymax_1d = 18.e3
    #ymax_flat = 6.e3
    # 2018
    #ymax_1d = 24.e3
    #ymax_flat = 8.e3
    # Run2
    ymax_1d = 54.e3
    ymax_flat = 18.e3
elif dMa == 50:
    # Run2
    ymax_1d = 30.e3
    ymax_flat = 5.4e3
else:
    # 25 MeV
    # 2017
    #ymax_1d = 4.e3
    #ymax_flat = 350
    # Run2
    ymax_1d = 14.e3 # 16.e3
    ymax_flat = 1.4e3
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
#    #plot_1dma(kidx, "", yrange=None, new_canvas=True, color=1, titles=["m_{a,pred} [GeV]", "N_{evts} / 25 MeV"])
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
#'bdtgtm0p98_relChgIsolt0p05_etalt1p44' # nominal
#'bdtgtm0p99_relChgIsolt0p05_etalt1p44' # bdt > -0.99
#'bdtgtm0p96_relChgIsolt0p05_etalt1p44' # bdt > -0.96
#'bdtgtm0p98_relChgIsolt0p03_etalt1p44' # relChgIso < 0.03
#'bdtgtm0p98_relChgIsolt0p07_etalt1p44' # relChgIso < 0.07
if dMa == 25:
    pass
#    h[k].FixParameter(0,  9.86310e-01)
#    h[k].FixParameter(1, -6.07111e-03)
#    h[k].FixParameter(2,  3.15883e-02)
#    h[k].FixParameter(0,  9.94601e-01)
#    h[k].FixParameter(1, -1.19847e-02)
#    h[k].FixParameter(2,  2.00016e-02)
#    h[k].FixParameter(0,  9.85770e-01)
#    h[k].FixParameter(1, -1.11777e-02)
#    h[k].FixParameter(2,  3.70487e-02)
#    h[k].FixParameter(0,  9.84844e-01)
#    h[k].FixParameter(1, -4.33492e-03)
#    h[k].FixParameter(2,  3.30299e-02)
#    h[k].FixParameter(0,  9.89707e-01)
#    h[k].FixParameter(1, -9.86390e-03)
#    h[k].FixParameter(2,  2.79949e-02)
#    h[k].FixParameter(0,  9.95226e-01)
#    h[k].FixParameter(1, -1.54637e-02)
#    h[k].FixParameter(2,  2.14290e-02)
#    h[k].FixParameter(0,  9.88623e-01)
#    h[k].FixParameter(1, -1.48400e-02)
#    h[k].FixParameter(2,  3.43419e-02)
#    h[k].FixParameter(0,  9.84700e-01)
#    h[k].FixParameter(1, -8.21132e-03)
#    h[k].FixParameter(2,  3.67385e-02)
elif dMa == 50:
    pass
#    h[k].FixParameter(0,  9.85385e-01)
#    h[k].FixParameter(1, -5.41274e-03)
#    h[k].FixParameter(2,  3.23650e-02)
#    h[k].FixParameter(0,  9.94127e-01)
#    h[k].FixParameter(1, -1.16004e-02)
#    h[k].FixParameter(2,  2.06105e-02)
#    h[k].FixParameter(0,  9.85292e-01)
#    h[k].FixParameter(1, -1.09174e-02)
#    h[k].FixParameter(2,  3.77911e-02)
#    h[k].FixParameter(0,  9.84141e-01)
#    h[k].FixParameter(1, -3.73403e-03)
#    h[k].FixParameter(2,  3.39289e-02)
#    h[k].FixParameter(0,  9.89025e-01)
#    h[k].FixParameter(1, -9.32034e-03)
#    h[k].FixParameter(2,  2.88988e-02)
#    h[k].FixParameter(0,  9.94628e-01)
#    h[k].FixParameter(1, -1.49709e-02)
#    h[k].FixParameter(2,  2.22029e-02)
#    h[k].FixParameter(0,  9.88039e-01)
#    h[k].FixParameter(1, -1.44068e-02)
#    h[k].FixParameter(2,  3.51611e-02)
#    h[k].FixParameter(0,  9.83916e-01)
#    h[k].FixParameter(1, -7.56216e-03)
#    h[k].FixParameter(2,  3.77678e-02)
elif dMa == 100:
    pass
#    h[k].FixParameter(0,  9.85385e-01)
#    h[k].FixParameter(1, -5.18422e-03)
#    h[k].FixParameter(2,  3.26524e-02)
else:
    raise Exception('Invalid dMa',dMa)
# 2016
#h[k].FixParameter(0, 9.60924e-01)
#h[k].FixParameter(1, 1.36569e-02)
#h[k].FixParameter(2, 6.80024e-02)
# 2017
#h[k].FixParameter(0, 9.75586e-01)
#h[k].FixParameter(1, 1.48966e-02)
#h[k].FixParameter(2, 3.55535e-02)
# 2018
#h[k].FixParameter(0, 1.00610e+00)
#h[k].FixParameter(1, -2.97482e-02)
#h[k].FixParameter(2, 1.17133e-02)

#fitResult = h[kfittgt].Fit(h[k], "LLIEMNS")
# Set fit tgt to have stat errs of bkg+tgt
# since TF2 fitting doesnt account for bkg (fitsrc) errs
kfittgt_stat = kfittgt+'_stat'
h[kfittgt_stat] = h[kfittgt].Clone()
h[kfittgt_stat].SetName(kfittgt_stat)
h[kfittgt_stat].SetTitle(kfittgt_stat)
for ix in range(1, h[kfittgt_stat].GetNbinsX()+1):
    for iy in range(1, h[kfittgt_stat].GetNbinsY()+1):
        binerr_tgt = h[kfittgt].GetBinError(ix, iy)
        binerr_src = h[kfitsrc].GetBinError(ix, iy)
        binerr = np.sqrt(binerr_tgt*binerr_tgt + binerr_src*binerr_src)
        h[kfittgt_stat].SetBinError(ix, iy, binerr)
fitResult = h[kfittgt_stat].Fit(h[k], "LLIEMNS")
chi2 = h[k].GetChisquare()
ndof = h[k].GetNDF()
pval = h[k].GetProb()
nDiag = nbins[limit_blind]
print('chi2 / ndf: %f / %f = %f'%(chi2, ndof, chi2/ndof))
print('chi2 / (ndf-nDiag): %f / %f = %f'%(chi2, ndof-nDiag, chi2/(ndof-nDiag)))
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
plot_2dma(k, "", xtitle, ytitle, 'pol2d', [1.-0.1, 1.+0.1], do_trunc=do_trunc)

# Eigenvariations from solving covariance matrix
# Must be hardcoded here
# a0 nom, a1 inv
#floNone, dM50
#np.sqrt(3.930942e-04) * np.array([ 0.603954327138,-0.56766240213,-0.559462749376 ]),
#np.sqrt(1.164696e-05) * np.array([ -0.778729579015,-0.270772601254,-0.565917344828 ]),
#np.sqrt(1.440589e-04) * np.array([ -0.169762815419,-0.777458420507,0.605589787631 ]),
#floNone, dM100
#np.sqrt(3.861450e-04) * np.array([ 0.607758680651,-0.560912162028,-0.562144939124 ]),
#np.sqrt(1.139487e-05) * np.array([ -0.777720829331,-0.27728825569,-0.564146731694 ]),
#np.sqrt(1.387601e-04) * np.array([ -0.16056057336,-0.780056901608,0.604757416272 ])
#flo0p756, dM50
#np.sqrt(3.861450e-04) * np.array([ 0.607758680651,-0.560912162028,-0.562144939124 ]),
#np.sqrt(1.139487e-05) * np.array([ -0.777720829331,-0.27728825569,-0.564146731694 ]),
#np.sqrt(1.387601e-04) * np.array([ -0.16056057336,-0.780056901608,0.604757416272 ])
# a0 nom, a1 nom
#'bdtgtm0p98_relChgIsolt0p05_etalt1p44' # nominal
#'bdtgtm0p99_relChgIsolt0p05_etalt1p44' # bdt > -0.99
#'bdtgtm0p96_relChgIsolt0p05_etalt1p44' # bdt > -0.96
#'bdtgtm0p98_relChgIsolt0p03_etalt1p44' # relChgIso < 0.03
#'bdtgtm0p98_relChgIsolt0p07_etalt1p44' # relChgIso < 0.07
if dMa == 25:
    pass
    varvec = np.array([
    # nominal
    #np.sqrt(1.066691e-04) * np.array([ 0.562404198284,-0.603508915393,-0.565224297774 ]),
    #np.sqrt(3.911051e-06) * np.array([ -0.823753446486,-0.349720460483,-0.44623520583 ]),
    #np.sqrt(3.639982e-05) * np.array([ -0.0716364233867,-0.71657001651,0.693826804241 ])
    #np.sqrt(1.066970e-04) * np.array([ 0.562141898226,-0.60363721573,-0.565348209553 ]),
    #np.sqrt(3.913354e-06) * np.array([ -0.823934361917,-0.349560657841,-0.446026359918 ]),
    #np.sqrt(3.640968e-05) * np.array([ -0.0716146180024,-0.716539920922,0.693860135916 ])
    #np.sqrt(9.274539e-05) * np.array([ 0.570464706512,-0.593332275499,-0.567914456124 ]),
    #np.sqrt(3.336513e-06) * np.array([ -0.818792763574,-0.356616170753,-0.449892561703 ]),
    #np.sqrt(3.157810e-05) * np.array([ -0.0644082987076,-0.721652075178,0.68925311276 ])
    #np.sqrt(1.244557e-04) * np.array([ 0.55434389349,-0.612662957566,-0.563335555576 ]),
    #np.sqrt(4.626777e-06) * np.array([ -0.828763080315,-0.344109493935,-0.44129402091 ]),
    #np.sqrt(4.222753e-05) * np.array([ -0.0765153870617,-0.711500356015,0.698507436562 ])
    #np.sqrt(1.356939e-04) * np.array([ 0.560020499389,-0.60721732788,-0.563617030427 ]),
    #np.sqrt(4.984923e-06) * np.array([ -0.82496478583,-0.346123745446,-0.446801359644 ]),
    #np.sqrt(4.659117e-05) * np.array([ -0.0762242901278,-0.715182123351,0.694769305621 ])
    #np.sqrt(9.261172e-05) * np.array([ 0.56436012354,-0.600305017641,-0.566684689005 ]),
    #np.sqrt(3.381959e-06) * np.array([ -0.822753383395,-0.352769101001,-0.4456801897 ]),
    #np.sqrt(3.139632e-05) * np.array([ -0.0676352058492,-0.717765872116,0.692991797755 ])
    #np.sqrt(1.183220e-04) * np.array([ 0.568722918788,-0.596219763873,-0.566635892627 ]),
    #np.sqrt(4.285811e-06) * np.array([ -0.819679317641,-0.353520679579,-0.450720473622 ]),
    #np.sqrt(4.054224e-05) * np.array([ -0.0684109485198,-0.720794785135,0.689764321957 ])
    #sub_campaign = 'bdtgtm0p96_relChgIsolt0p07_etalt1p44' # bdt > -0.96, relChgIso < 0.07 !! optimal
    #np.sqrt(1.088091e-04) * np.array([ 0.556336452982,-0.609615795254,-0.56467542293 ]),
    #np.sqrt(4.023956e-06) * np.array([ -0.827742255736,-0.346848222679,-0.44106583238 ]),
    #np.sqrt(3.664693e-05) * np.array([ -0.0730240313319,-0.712786709052,0.697569063424 ])
    #blind_w = 300MeV
    np.sqrt(1.776221e-04) * np.array([ 0.576481906876,-0.588928336931,-0.56642036069 ]),
    np.sqrt(4.943718e-06) * np.array([ -0.813627583437,-0.349795992221,-0.46438445204 ]),
    np.sqrt(3.837421e-05) * np.array([ -0.075357590955,-0.728564463713,0.680819400208 ])
    #np.sqrt(1.080694e-04) * np.array([ 0.558236081284,-0.607522628593,-0.565056398335 ]),
    #np.sqrt(3.984901e-06) * np.array([ -0.826546953893,-0.348064712515,-0.442347249243 ]),
    #np.sqrt(3.662565e-05) * np.array([ -0.0720597707699,-0.713979839806,0.696448259232 ])
    #np.sqrt(9.885980e-05) * np.array([ 0.558028565657,-0.607385726654,-0.565408435529 ]),
    #np.sqrt(3.643369e-06) * np.array([ -0.826814669823,-0.349014069259,-0.441097133549 ]),
    #np.sqrt(3.307683e-05) * np.array([ -0.0705806041089,-0.713632789687,0.696955249501 ])
    #np.sqrt(1.034312e-04) * np.array([ 0.557400973971,-0.608234618522,-0.565114858279 ]),
    #np.sqrt(3.823405e-06) * np.array([ -0.827139744297,-0.348024419126,-0.44126958551 ]),
    #np.sqrt(3.470536e-05) * np.array([ -0.0717216677156,-0.713393056123,0.697084177023 ])
    ])
elif dMa == 50:
    pass
    varvec = np.array([
    #np.sqrt(1.070820e-04) * np.array([ 0.562222554638,-0.603912346959,-0.56497404918 ]),
    #np.sqrt(3.911583e-06) * np.array([ -0.823884389223,-0.349914522139,-0.445841160493 ]),
    #np.sqrt(3.649641e-05) * np.array([ -0.0715563571648,-0.716135255651,0.694283791661 ])
    #np.sqrt(9.303974e-05) * np.array([ 0.570517131429,-0.593627532918,-0.56755312959 ]),
    #np.sqrt(3.348944e-06) * np.array([ -0.818751781792,-0.356856341245,-0.449776690732 ]),
    #np.sqrt(3.165132e-05) * np.array([ -0.0644648939956,-0.721290443494,0.689626256437 ])
    #np.sqrt(1.249070e-04) * np.array([ 0.554514743442,-0.612819235978,-0.562997320883 ]),
    #np.sqrt(4.623120e-06) * np.array([ -0.82864382312,-0.344367862079,-0.441316428395 ]),
    #np.sqrt(4.234983e-05) * np.array([ -0.0765690127254,-0.711240718451,0.698765931273 ])
    #np.sqrt(1.361485e-04) * np.array([ 0.560144404114,-0.607357365514,-0.56334294803 ]),
    #np.sqrt(4.982947e-06) * np.array([ -0.824883250176,-0.346391527098,-0.446744371575 ]),
    #np.sqrt(4.671853e-05) * np.array([ -0.0761962605302,-0.714933521742,0.69502819322 ])
    #np.sqrt(9.294303e-05) * np.array([ 0.564459255671,-0.600594398531,-0.566279186568 ]),
    #np.sqrt(3.388717e-06) * np.array([ -0.822695096421,-0.353205725027,-0.44544190882 ]),
    #np.sqrt(3.146825e-05) * np.array([ -0.0675168646492,-0.717308918292,0.693476307257 ])
    #np.sqrt(1.186929e-04) * np.array([ 0.568841942332,-0.596398319889,-0.566328428279 ]),
    #np.sqrt(4.275905e-06) * np.array([ -0.819585354896,-0.353670582687,-0.450773740341 ]),
    #np.sqrt(4.065121e-05) * np.array([ -0.0685469961677,-0.720573495887,0.689981989867 ])
    #np.sqrt(1.092173e-04) * np.array([ 0.556480124376,-0.609832874604,-0.564299332117 ]),
    #np.sqrt(4.019297e-06) * np.array([ -0.827654711325,-0.347258949718,-0.440906907025 ]),
    #np.sqrt(3.674336e-05) * np.array([ -0.0729215331464,-0.712400931283,0.697973755316 ])
    #np.sqrt(1.084577e-04) * np.array([ 0.558367153849,-0.607763066168,-0.564668200721 ]),
    #np.sqrt(3.990140e-06) * np.array([ -0.826465976577,-0.348467518347,-0.442181386105 ]),
    #np.sqrt(3.673217e-05) * np.array([ -0.0719729884273,-0.713578617995,0.696868312436 ])
    ])
elif dMa == 100:
    pass
    varvec = np.array([
    # nominal
    #np.sqrt(1.085777e-04) * np.array([ 0.56320956309,-0.604355907366,-0.563514795969 ]),
    #np.sqrt(3.906831e-06) * np.array([ -0.823166042651,-0.350883563225,-0.446406083387 ]),
    #np.sqrt(3.684545e-05) * np.array([ -0.0720600740395,-0.715286419758,0.695106238958 ])
    #np.sqrt(1.085660e-04) * np.array([ 0.562889609916,-0.604562017175,-0.563613390933 ]),
    #np.sqrt(3.909766e-06) * np.array([ -0.823396164029,-0.350816165202,-0.446034500118 ]),
    #np.sqrt(3.685422e-05) * np.array([ -0.0719308286576,-0.71514528987,0.695264820242 ])
    #sub_campaign = 'bdtgtm0p96_relChgIsolt0p07_etalt1p44' # bdt > -0.96, relChgIso < 0.07 !! optimal
    np.sqrt(1.108096e-04) * np.array([ 0.557303057842,-0.610185829298,-0.563104391249 ]),
    np.sqrt(4.015238e-06) * np.array([ -0.827102877713,-0.348432602205,-0.441016497877 ]),
    np.sqrt(3.710513e-05) * np.array([ -0.0728980891351,-0.711525105281,0.698869010013 ])
    ])
else:
    raise Exception('invalid dMa',dMa)
#varvec = np.array([
# 2016
#np.sqrt(4.787525e-04) * np.array([ 0.55001623775,-0.627928268382,-0.550625306337 ]),
#np.sqrt(1.721833e-05) * np.array([ -0.831546149018,-0.35053769438,-0.430876231501 ]),
#np.sqrt(1.601292e-04) * np.array([ -0.0775444405827,-0.694859276822,0.714952757285 ])
# 2017
#np.sqrt(3.248286e-04) * np.array([ 0.564048681007,-0.599969634809,-0.567349559584 ]),
#np.sqrt(1.176815e-05) * np.array([ -0.822505893027,-0.347457125189,-0.450286133576 ]),
#np.sqrt(1.114032e-04) * np.array([ -0.0730283601712,-0.720631655884,0.689461293438 ])
# 2018
#np.sqrt(2.480435e-04) * np.array([ 0.568880484219,-0.594577232667,-0.568201468731 ]),
#np.sqrt(8.869191e-06) * np.array([ -0.819680183314,-0.353558105642,-0.450689541722 ]),
#np.sqrt(8.399734e-05) * np.array([ -0.0670775056012,-0.722131968776,0.688495481404 ])
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
xtitle, ytitle, ztitle = "m_{a_{1},pred} [GeV]", "m_{a_{2},pred} [GeV]", "(Data/Bkg) / %d MeV"%(dMa)
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
    #sg = np.sqrt(sg_bkg*sg_bkg + sg_obs*sg_obs)
    sg = sg_bkg
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
file_out = ROOT.TFile('Fits/Bkgfits_flat_region%s.root'%'limit', "RECREATE")
#file_out = ROOT.TFile('Datacards/%s_hists.root'%'shape', "UPDATE")
for i,syst in enumerate(systs):
    ksysts = [k for k in h.keys() if syst in k]
    #print(ksysts)
    ksysts = [k for k in ksysts if 'flat' in k]
    #print(ksysts)
    ksysts = [k for k in ksysts if limit_blind in k]
    #print(ksysts)
    for shift in ['Down', 'Up']:
        ksyst_shift = [k for k in ksysts if shift in k][0]
        #print(ksyst_shift, h[ksyst_shift].Integral())
        kout = 'bkg_%s%s'%(syst, shift)
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
file_out.Close()

#########################
# Signal samples
#########################
regions = ['sr']
blinds = [limit_blind]
#sample_data = 'Run2017B-F'
#sample = sample_data
sample_sg = 'h4g'

#systs = ['offset', 'scale']
#systs = ['scale', 'smear']
#syst_shifts['smear'] = ['dn', 'up']
#syst_shifts['scale'] = ['dn', 'up']
#indir = 'Templates/prod_fixsb2srnorm/nom-nom/h4g'

#systs = ['PhoIdSF']
#systs = ['PhoIdSF', 'Scale', 'Smear']
systs = ['PhoIdSF', 'Scale', 'Smear', 'Lumi']
syst_shifts['PhoIdSF'] = ['dn', 'up']
syst_shifts['Scale'] = ['dn', 'up']
syst_shifts['Smear'] = ['dn', 'up']
#systs = ['TEST'] # dummy to force output of nominal sg plots
#syst_shifts['TEST'] = ['dn', 'up']
#systs = ['Lumi']
syst_shifts['Lumi'] = ['dn', 'up']
#systs = []
keys = ['ma0vma1']

#run = 'Run2'
#run = '2017'
indir = 'root://cmseos.fnal.gov//store/user/lpchaa4g/mandrews/%s'%run
#/eos/uscms/store/user/lpchaa4g/mandrews/Run2/sg-Era04Dec2020v2/bdtgtm0p98_relChgIsolt0p05_etalt1p44/nom-nom/Templates/systNom_nom/h4g_blind_offdiag_lo_hi_templates.root
#campaign = 'sg-Era04Dec2020v2/%s/nom-nom/Templates'%sub_campaign
#campaign = 'sg-Era04Dec2020v3/%s/nom-nom/Templates'%sub_campaign #old 2017 ss, SFs
#campaign = 'sg-Era04Dec2020v4/%s/nom-nom/Templates'%sub_campaign # 2016-18 SFs. 2017-18 ss. 2016 ss uses 2017.
#campaign = 'sg-Era04Dec2020v5/%s/nom-nom/Templates'%sub_campaign # v4 + nominals use best-fit ss over full m_a, shifted uses best-fit ss over ele peak only.
campaign = 'sg-Era04Dec2020v6/%s/nom-nom/Templates'%sub_campaign # 2016-18 phoid, 2016-18 ss. ss implemented only for shifted syst (as in v4)

ma_pts = ['0p1', '0p2', '0p4', '0p6', '0p8', '1p0', '1p2']
#ma_pts = ['0p1']
#for ma in ['100MeV', '400MeV', '1GeV']:
#for ma in ['0p1', '0p4', '1p0']:
for ma in ma_pts:

    #sample = 'h4g_%s'%ma
    sample = 'h4g-mA%sGeV'%ma if run == 'Run2' else 'h4g%s-mA%sGeV'%(run, ma)
    #norm = get_sg_norm(sample, xsec=50.*1.e-2)
    #norm = get_sg_norm(sample, xsec=1.)
    #print('%s mc2data norm: %.4f'%(sample, norm))
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

#'''
##########################
# Get total syst

syst_shifts['all'] = ['dn', 'up']

for ma in ma_pts:

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

for ma in ma_pts:

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
                    for shift in syst_shifts['all']:
                        kSystAll = '%s_%s_%s_all%s_ma0vma1_rebin_%s'%(sample, r, b, shift, key)
                        bincout = binc+qerrup if shift == syst_shifts['all'][1] else binc-qerrdn
                        h[kSystAll].SetBinContent(ib, bincout)

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

    file_out = ROOT.TFile('Fits/Bkgfits_flat_region%s.root'%'limit', "UPDATE")
    for i,syst in enumerate(systs):
        ksysts = [k for k in h.keys() if syst in k]
        ksysts = [k for k in ksysts if sample in k]
        ksysts = [k for k in ksysts if 'flat' in k]
        ksysts = [k for k in ksysts if limit_blind in k]
        print(ksysts)
        for shift in ['Down', 'Up']:
            ksyst_shift = [k for k in ksysts if shift in k][0]
            #print(ksyst_shift, h[ksyst_shift].Integral())
            #kout = 'h4g_%s%s'%(syst, shift)
            kout = 'h4g_%s_%s%s'%(ma, syst, shift)
            hout[kout] = h[ksyst_shift].Clone()
            hout[kout].SetName(kout)
            hout[kout].SetLineColor(1)
            #hout[kout].Write()
            #print(hout[kout].Integral())
            print(kout)
        if i != 0: continue
        for shift in ['Obs']:
            ksyst_shift = [k for k in ksysts if shift in k][0]
            #print(ksyst_shift, h[ksyst_shift].Integral())
            #kout = 'h4g'
            kout = 'h4g_%s'%ma
            hout[kout] = h[ksyst_shift].Clone()
            hout[kout].SetName(kout)
            hout[kout].SetLineColor(1)
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

    file_out.Write()
    file_out.Close()

#'''
#xtitle, ytitle, ztitle = "m_{a_{1},pred} [GeV]", "m_{a_{2},pred} [GeV]", "N_{evts} / %d MeV"%(dMa)
#zrange = None
#zrange = [1., 4100.]
#for blind in blinds:
#    for r in regions:
#
#        kbkg = 'Run2017B-F'+'sb2sr'+blind+key+'rebin'
#        kreg = sample+r+blind+key
#        k = kreg+'rebin'
#
#        if ma_bins is not None:
#            h[k] = rebin2d(h[kreg], ma_bins)
#
#        for ix in range(1, h[k].GetNbinsX()+1):
#            for iy in range(1, h[k].GetNbinsY()+1):
#                binc = h[k].GetBinContent(ix, iy)
#                h[k].SetBinContent(ix, iy, binc)
#
#        plot_2dma(k, "", xtitle, ytitle, ztitle, zrange, do_log=True)
#
#        region = 'limit'
#
#        ksrcs = [kbkg, k]
#        ktgts = [sample+'_Obs']
#        get_datavmc_flat(region, ksrcs, [None], ktgts, nbins[region])
#        #yrange = [0., 600.]
#        plot_1dma('flat_'+ktgts[0], color=4, yrange=yrange_flat)
#
#        file_out = ROOT.TFile('Fits/Bkgfits_flat_region%s.root'%region, "UPDATE")
#        #file_out = ROOT.TFile('Fits/Bkgfits_flat_region%s.root'%region, "RECREATE")
#        hout = hvalid if region == 'valid' else hlimit
#        #k_ = 'flat_%sh4g100MeV'%region
#        k_ = 'flat_%sh4g'%region
#        hout[k_] = h['flat_'+ktgts[0]].Clone()
#        hout[k_].SetName(k_)
#        #for shift in ['Up', 'Down']:
#        #    k_shift = k_+'_stat'+shift
#        #    hout[k_shift] = hout[k_].Clone()
#        #    hout[k_shift].Reset()
#        #    hout[k_shift].SetName(k_shift)
#        #    for ib in range(1, hout[k_shift].GetNbinsX()+1):
#        #        binc = hout[k_].GetBinContent(ib)
#        #        binerr = hout[k_].GetBinError(ib)
#        #        binout = binc + binerr if shift == 'Up' else binc - binerr
#        #        hout[k_shift].SetBinContent(ib, binout)
#        file_out.Write()
#        file_out.Close()
#'''
