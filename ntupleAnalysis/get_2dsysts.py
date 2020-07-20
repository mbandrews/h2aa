from __future__ import print_function
import ROOT
import numpy as np
from array import array
from hist_utils import *
from get_bkg_norm import *
from collections import OrderedDict 

wd, ht = int(800*1), int(680*1)
wd_wide = 1400

#apply_blinding = True
apply_blinding = False

def isnot_sg(ix, iy):
    #if abs(ix - iy) > int(200/25): # 200MeV blinding / 25MeV bin widths -> 8 bins
    #if abs(ix - iy) > int(200/25) or (ix <= 1) or (iy <= 1): # 200MeV blinding / 25MeV bin widths -> 8 bins
    #if abs(ix - iy) >= int(200/50) or (ix <= 1) or (iy <= 1): # 200MeV blinding / 50MeV bin widths
    if abs(ix - iy) >= int(200/dMa) or (ix <= 1) or (iy <= 1): # 200MeV blinding / 50MeV bin widths
        return True
    else:
        return False

def draw_hist_1dma_syst(ks, syst, ymax_=-1, blind_diag=False):

    hc = {}

    ksr, klo, knom, khi = ks
    sample = ksr.split('_')[0]
    blind = ksr.split('_')[2]
    sr = ksr.split('_')[1]
    sb = knom.split('_')[1]
    key = ksr.split('_')[-1]
    kc = '%s_%s_%s_%so%s_%s'%(sample, syst, blind, sr, sb, key)

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

    ksyst = knom+'_errband'
    h[ksyst] = ROOT.TGraphAsymmErrors()
    h[ksyst].SetName(ksyst)
    ibin = 1
    for ib in range(2, h[knom].GetNbinsX()+1):

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
    h[k] = set_hist(h[k], "m_{a,pred} [GeV]", "N_{a} / 25 MeV", "")
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

    k = sb2sr_k
    h[k].SetLineColor(9)
    h[k].SetFillStyle(0)
    h[k].Draw("hist same")
    hc[k] = h[k].Clone()
    hc[k].SetFillColor(9)
    hc[k].SetFillStyle(3002)
    hc[k].Draw("E2 same")
    h[ksyst].SetFillColor(3)
    h[ksyst].SetFillStyle(3001)
    h[ksyst].Draw("E2 same")

    k = sr_k
    hc[k] = h[k].Clone()
    hc[k].SetFillColor(9)
    hc[k].SetFillStyle(0)
    hc[k].SetMarkerStyle(20)
    hc[k].SetMarkerSize(0.85)
    hc[k].Draw("E same")

    k = sr_k
    #ymax = 1.2*max(h[k].GetMaximum(), h[sb2sr_k].GetMaximum())
    if ymax_ == -1 and hc[k].GetBinContent(2) > 0.:
        ymax = 1.2*max(np.max([hc[k].GetBinContent(ib) for ib in range(2, hc[k].GetNbinsX()+1)]),
                       np.max([hc[sb2sr_k].GetBinContent(ib) for ib in range(2, hc[sb2sr_k].GetNbinsX()+1)]))
    if ymax_ is not None and ymax_ > 0.:
        ymax = ymax_
    hc[k+'dummy'].GetYaxis().SetRangeUser(0.1, ymax)
    hc[k+'dummy'].GetXaxis().SetRangeUser(0., 1.2)

    l, l2, hatch = {}, {}, {}
    legend = {}

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

    #legend[k] = ROOT.TLegend(0.5,0.68,0.8,0.86) #(x1, y1, x2, y2)
    #legend[k].AddEntry(hc[k].GetName(),"Obs","l")
    #legend[k].AddEntry(hc['sb2sr_maxy'].GetName(),"Exp","l")
    #legend[k].SetBorderSize(0)
    #legend[k].Draw("same")

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

    dY = 0.199
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
    fUnity.SetLineWidth(1)
    fUnity.SetLineStyle(7)
    fUnity.SetTitle("")
    fUnity.Draw()

    k = sb2sr_k
    kr = k+'err'
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
            (h[k].GetBinError(ib)/h[k].GetBinContent(ib)),
            (h[k].GetBinError(ib)/h[k].GetBinContent(ib)),
            )
    h[kr].SetFillColor(9)
    h[kr].SetFillStyle(3002)
    h[kr].Draw("E2 same")

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
            1.- (yvals[i]-eylos[i])/yvals[i],
            (yvals[i]+eyhis[i])/yvals[i] - 1.
            )
    h[kr].SetFillColor(3)
    h[kr].SetFillStyle(3001)
    h[kr].Draw("E2 same")

    k = srosb2sr_k
    h[k] = h[sr_k].Clone()
    h[k].Reset()
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

    h[k].SetName(k)
    h[k].SetLineColor(1)
    #h[k].Sumw2()
    h[k].SetStats(0)

    h[k].SetMarkerStyle(20)
    h[k].SetMarkerSize(0.85)
    h[k].SetMarkerColor(1)
    h[k].Draw("ep same")

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
    c[kc].Print('Plots/Sys2D_%s.eps'%(kc))
    #c[k].Print('Plots/%s_blind_%s_%so%s.eps'%(sample, blind, ks[0], ks[1]))

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
    c[kc].Print('Plots/Sys2D_%s.eps'%k)


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
    #h[k].SetContour(50)
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

    c[k].Print('Plots/Sys2D_%s.eps'%(k))
    #c[k].Print('Plots/Sys2D_%s.png'%(k))

def plot_datavmc_flat(region, kplots, syst, nbins, yrange=None, colors=[3, 10], styles=[1001, 1001], titles=["im_{x}#timesim_{y} + im_{y}", "N_{evts}"]):

    xtitle, ytitle = titles
    kobs_nom, kbkg_dn, kbkg_nom, kbkg_up, kfit = kplots
    kshifts = [kbkg_up, kbkg_dn]

    print(kobs_nom)
    sample = kobs_nom.split('_')[1]
    blind = kobs_nom.split('_')[2]
    sr = kobs_nom[-3:]
    sb = kbkg_nom[-3:]
    kc = '%s_%s_%s_%so%s_2dmaflat'%(sample, syst, blind, sr, sb)

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
      #k = k_+'flat'
      #print(k)
      #h[k].Reset()
      h[k].SetTitle("")
      h[k].GetXaxis().SetTitle(xtitle)
      h[k].GetYaxis().SetTitle(ytitle)
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
          h[k].GetYaxis().SetRangeUser(yrange[0], yrange[1])
      #h[k].SetLineColor(colors[i])
      #h[k].SetFillColor(colors[i])
      #h[k].SetFillStyle(styles[i])
      h[k].SetLineColor(0)
      h[k].SetFillColor(0)
      if i == 0:
          h[k].Draw("LF2")
      else:
          h[k].Draw("LF2 same")
    h[kbkg_nom].SetLineColor(9)
    h[kbkg_nom].SetLineStyle(1)
    h[kbkg_nom].Draw("hist same")
    h[kfit].SetFillColor(3)
    h[kfit].SetFillStyle(3001)
    h[kfit].Draw("E2 same")
    h[kobs_nom].SetFillStyle(0)
    h[kobs_nom].SetMarkerStyle(20)
    h[kobs_nom].SetMarkerSize(0.85)
    h[kobs_nom].Draw("E same")

    pUp.RedrawAxis()

    ##### Ratio plots on lower pad #####
    pDn.cd()

    #'''
    fUnity = ROOT.TF1('fUnity',"[0]",0.,float(nbins))
    fUnity.SetParameter( 0,1. )

    fUnity.GetXaxis().SetTitle(xtitle)
    fUnity.GetXaxis().SetTickLength(0.1)
    fUnity.GetXaxis().SetTitleOffset(1.05)
    fUnity.GetXaxis().SetTitleSize(0.16)
    fUnity.GetXaxis().SetLabelSize(0.14)

    dY = 0.399
    fUnity.GetYaxis().SetTitle("Obs/Fit")
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

    #fUnity.SetLineColor(9)
    fUnity.SetLineColor(3)
    fUnity.SetLineWidth(1)
    fUnity.SetLineStyle(1)
    fUnity.SetTitle("")
    fUnity.Draw("L")

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
            1.- (yvals[i]-eylos[i])/yvals[i],
            (yvals[i]+eyhis[i])/yvals[i] - 1.
            )
    h[kr].SetFillColor(3)
    h[kr].SetFillStyle(3001)
    h[kr].Draw("E2 same")

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
      err_ = get_cplimits_sym(binc_num, binc_den, binerr_num, binerr_den)
      #print(i, binc_num, binc_den, binc_num/binc_den, binerr_num, binerr_den, err_)
      h[kr].SetBinContent(i, binc_num/binc_den)
      h[kr].SetBinError(i, err_)
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
    #c[kc].Print('Plots/Sys2D_flat_blind%s_syst%s_datavbkg.eps'%(region, syst))
    c[kc].Print('Plots/Sys2D_%s.eps'%(kc))

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

    print(ibin-1, nbins)
    assert ibin-1 == nbins

def get_datavmc_flat(ksrcs, ktgts, nbins):

    ksr, klo, knom, khi = ksrcs

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
                binnom = h[knom].GetBinContent(ix, iy)
                binhi = h[khi].GetBinContent(ix, iy)

                binerrsr = h[ksr].GetBinError(ix, iy)
                binerrlo = h[klo].GetBinError(ix, iy)
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

        print(ibin-1, nbins)
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

f, hf, = {}, {}
h = OrderedDict()
fLine = {}
hatch, hatch2 = {}, {}
ax, ay = {}, {}
c = {}

sample = 'Run2017B-F'
regions = ['sb2sr', 'sr']
#keys = ['ma0vma1']
#keys = ['ma0vma1', 'ma1']
keys = ['ma0vma1', 'ma0', 'ma1']
#valid_blind = 'sg'
valid_blind = 'diag_lo_hi'
limit_blind = 'offdiag_lo_hi'
blinds = [valid_blind, limit_blind]
#syst = 'ptrwgt_resample'
#syst = 'ptrwgt'
#syst = 'tempfrac'
#systs = ['ptrwgt', 'tempfrace1', 'tempfrace2']
systs = ['flo']
cr = 'a0noma1inv'
syst_shifts = {}
#syst_shifts['ptrwgt_resample'] = ['srsblo', 'nom', 'srsbhi']
#syst_shifts['ptrwgt_resample'] = ['srsblo0p20', 'nom', 'srsbhi0p20']
#syst_shifts['ptrwgt'] = ['sblo', 'nom', 'sbhi']
syst_shifts['ptrwgt'] = ['srsblo0p20', 'srsbhi0p20']
syst_shifts['flo'] = ['0p722', '0p790']
#syst_shifts['tempfrac'] = ['e0dn', 'nom', 'e0up']
syst_shifts['tempfrace1'] = ['dn', 'up']
syst_shifts['tempfrace2'] = ['dn', 'up']
#indir = 'Templates/%s/%s'%(syst, cr)
#indir = 'Templates/_prod_varptbinsxy/%s/'%(cr)
indir = 'Templates/scan_ptrwgt'

for b in blinds:
    # Nominals
    for r in regions:
        kidx = '%s_%s_%s'%(sample, r, b)
        hf[kidx] = ROOT.TFile("%s/%s/%s_%s_blind_%s_templates.root"%(indir, 'nom', sample, r, b),"READ")
        for k in keys:
            kidx_k = '%s_%s'%(kidx, k)
            h[kidx_k] = hf[kidx].Get(k)
            h[kidx_k].SetName(kidx_k)
            #print('Adding:',kidx_k)
    # Syst shifts, sb2sr only
    r = 'sb2sr'
    for syst in systs:
        for shift in syst_shifts[syst]:
            kidx = '%s_%s_%s_%s%s'%(sample, r, b, syst, shift)
            hf[kidx] = ROOT.TFile("%s/%s/%s_%s_blind_%s_templates.root"%(indir, '%s_%s'%(syst,shift), sample, r, b),"READ")
            for k in keys:
                kidx_k = '%s_%s'%(kidx, k)
                h[kidx_k] = hf[kidx].Get(k)
                h[kidx_k].SetName(kidx_k)
                #print('Adding:',kidx_k)

#dMa = 25
dMa = 50
#dMa = 100
ma_bins = list(range(0,1200+dMa,dMa))
ma_bins = [-400]+ma_bins
ma_bins = [float(m)/1.e3 for m in ma_bins]
#print(len(ma_bins))
ma_bins = array('d', ma_bins)

nbins = {valid_blind:420, limit_blind:196}
hvalid, hlimit = {}, {}

xtitle, ytitle, ztitle = "m_{a_{1},pred} [GeV]", "m_{a_{2},pred} [GeV]", "N_{evts} / %d MeV"%(dMa)
zrange = None
zrange = [1., 4100.]
zrange = [0., 650.]
do_trunc = True
do_log = False if do_trunc else True

for kidx in h.keys():

    key = kidx.split('_')[-1]
    if key != 'ma0vma1': continue

    k = kidx+'_rebin'
    if ma_bins is not None:
        h[k] = rebin2d(h[kidx], ma_bins)

    for ix in range(1, h[k].GetNbinsX()+1):
        for iy in range(1, h[k].GetNbinsY()+1):
            binc = h[k].GetBinContent(ix, iy)
            h[k].SetBinContent(ix, iy, binc)

    #plot_2dma(k, "", xtitle, ytitle, ztitle, zrange, do_trunc, do_log=do_log)
    #print(k)

for kidx in h.keys():

    #print(kidx)
    key = kidx.split('_')[-1]
    if key != 'ma0' and key != 'ma1': continue

    #print(kidx)
    #plot_1dma(kidx, "", yrange=None, new_canvas=True, color=1, titles=["m_{a,pred} [GeV]", "N_{evts} / 25 MeV"])

#keys_1d = ['ma0', 'ma1']
keys_1d = keys[1:]
for key in keys_1d:
    for blind in blinds:
        for syst in systs:

            ksrcs = [
                '%s_sr_%s'%(sample, blind),
                '%s_sb2sr_%s_%s%s'%(sample, blind, syst, syst_shifts[syst][0]),
                '%s_sb2sr_%s'%(sample, blind),
                '%s_sb2sr_%s_%s%s'%(sample, blind, syst, syst_shifts[syst][1])
                ]
            ksrcs = ['%s_%s'%(ksrc, key) for ksrc in ksrcs]
            #print(ksrcs)
            draw_hist_1dma_syst(ksrcs, syst)

'''
##########################
xtitle, ytitle, ztitle = "m_{a_{1},pred} [GeV]", "m_{a_{2},pred} [GeV]", "(Data/Bkg) / %d MeV"%(dMa)
zrange = [0., 2.]

sr_k = sample+'sr'+valid_blind+key
sb2sr_k = sample+'sb2sr'+valid_blind+key
key = keys[0]

#########################
yrange_flat = [0., 650.] # a0nom, a1inv
#yrange_flat = [0., 200.] # a0inv, a1inv
#yrange_flat = [0., 1100.] # a0nom, a1nom
for blind in blinds:

    nbin = nbins[blind]

    for syst in systs:

        ksrcs = [
            '%s_sr_%s'%(sample, blind),
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
        plot_datavmc_flat(blind, kplots, syst, nbin, yrange=yrange_flat)

for k in h.keys():
    pass
    #if 'flat' in k: print(k)

hout = OrderedDict()
file_out = ROOT.TFile('Fits/Bkgfits_flat_region%s.root'%'limit', "RECREATE")
#file_out = ROOT.TFile('Datacards/%s_hists.root'%'shape', "UPDATE")
for i,syst in enumerate(systs):
    ksysts = [k for k in h.keys() if syst in k]
    ksysts = [k for k in ksysts if 'flat' in k]
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
        for stat in ['Up', 'Down']:
            kout = 'bkg_bstat%s'%stat
            hout[kout] = hout['bkg'].Clone()
            hout[kout].SetName(kout)
            print(kout)
            for ib in range(1, hout[kout].GetNbinsX()+1):
                binc = hout[kout].GetBinContent(ib)
                binerr = hout[kout].GetBinError(ib)
                binout = binc + binerr if stat == 'Up' else binc - binerr
                if binout < 0.:print(ib, binc, binerr)
                hout[kout].SetBinContent(ib, binout)

file_out.Write()
file_out.Close()

#########################
sample = 'h24gamma_1j_1M_100MeV'
regions = ['sr']
blinds = [limit_blind]

systs = ['offset', 'scale']
syst_shifts['offset'] = ['Dn', 'Up']
syst_shifts['scale'] = ['Dn', 'Up']
indir = 'Templates/_prod_varptbinsxy/%s/massreg'%(cr)

norm = get_sg_norm(sample, xsec=50.*1.e0)
print('%s mc2data norm: %.4f'%(sample, norm))
keys = ['ma0vma1']
for b in blinds:
    # Nominals
    for r in regions:
        kidx = '%s_%s_%s'%(sample, r, b)
        hf[kidx] = ROOT.TFile("%s/%s/%s_%s_blind_%s_templates.root"%(indir, 'nom', sample, r, b),"READ")
        for k in keys:
            kidx_k = '%s_%s'%(kidx, k)
            h[kidx_k] = hf[kidx].Get(k)
            h[kidx_k].SetName(kidx_k)
            h[kidx_k].Scale(norm)
            print('Adding:',kidx_k)
        for syst in systs:
            for shift in syst_shifts[syst]:
                kidx = '%s_%s_%s_%s%s'%(sample, r, b, syst, shift)
                hf[kidx] = ROOT.TFile("%s/%s/%s_%s_blind_%s_templates.root"%(indir, '%s%s'%(syst,shift), sample, r, b),"READ")
                for k in keys:
                    kidx_k = '%s_%s'%(kidx, k)
                    h[kidx_k] = hf[kidx].Get(k)
                    h[kidx_k].SetName(kidx_k)
                    h[kidx_k].Scale(norm)
                    print('Adding:',kidx_k)

for kidx in h.keys():

    if sample not in kidx: continue
    key = kidx.split('_')[-1]
    if key != 'ma0vma1': continue

    k = kidx+'_rebin'
    if ma_bins is not None:
        h[k] = rebin2d(h[kidx], ma_bins)

    for ix in range(1, h[k].GetNbinsX()+1):
        for iy in range(1, h[k].GetNbinsY()+1):
            binc = h[k].GetBinContent(ix, iy)
            h[k].SetBinContent(ix, iy, binc)

    #plot_2dma(k, "", xtitle, ytitle, ztitle, zrange, do_trunc, do_log=do_log)

for blind in blinds:

    nbin = nbins[blind]

    for syst in systs:

        ksrcs = [
            '%s_sr_%s'%(sample, blind),
            '%s_sr_%s_%s%s'%(sample, blind, syst, syst_shifts[syst][0]),
            #'%s_sb2sr_%s'%(sample, blind),
            'Run2017B-F_sb2sr_%s'%(blind),
            '%s_sr_%s_%s%s'%(sample, blind, syst, syst_shifts[syst][1])
            ]
        ksrcs = ['%s_%s_rebin'%(ksrc, key) for ksrc in ksrcs]
        ktgts = ['Obs', 'Down', 'Nom', 'Up', 'Fit']
        ktgts = ['%s_%s_%s%s'%(sample, blind, syst, ktgt) for ktgt in ktgts]
        get_datavmc_flat(ksrcs, ktgts, nbin)
        kplots = ['flat_'+k for k in ktgts]
        #if i != 0: continue
        #plot_datavmc_flat(blind, kplots, syst, nbin, yrange=yrange_flat)

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
        kout = 'h4g_%s%s'%(syst, shift)
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
        kout = 'h4g'
        hout[kout] = h[ksyst_shift].Clone()
        hout[kout].SetName(kout)
        hout[kout].SetLineColor(1)
        print(kout)
        for stat in ['Up', 'Down']:
            kout = 'h4g_sstat%s'%stat
            hout[kout] = hout['h4g'].Clone()
            hout[kout].SetName(kout)
            print(kout)
            for ib in range(1, hout[kout].GetNbinsX()+1):
                binc = hout[kout].GetBinContent(ib)
                binerr = hout[kout].GetBinError(ib)
                binout = binc + binerr if stat == 'Up' else binc - binerr
                if binout < 0.:print(ib, binc, binerr)
                hout[kout].SetBinContent(ib, binout)
                #if ib < 10: print(ib, binc, binerr, np.sqrt(binc))

file_out.Write()
file_out.Close()

xtitle, ytitle, ztitle = "m_{a_{1},pred} [GeV]", "m_{a_{2},pred} [GeV]", "N_{evts} / %d MeV"%(dMa)
zrange = None
zrange = [1., 4100.]
for blind in blinds:
    for r in regions:

        kbkg = 'Run2017B-F'+'sb2sr'+blind+key+'rebin'
        kreg = sample+r+blind+key
        k = kreg+'rebin'

        if ma_bins is not None:
            h[k] = rebin2d(h[kreg], ma_bins)

        for ix in range(1, h[k].GetNbinsX()+1):
            for iy in range(1, h[k].GetNbinsY()+1):
                binc = h[k].GetBinContent(ix, iy)
                h[k].SetBinContent(ix, iy, binc)

        plot_2dma(k, "", xtitle, ytitle, ztitle, zrange, do_log=True)

        region = 'limit'

        ksrcs = [kbkg, k]
        ktgts = [sample+'_Obs']
        get_datavmc_flat(region, ksrcs, [None], ktgts, nbins[region])
        #yrange = [0., 600.]
        plot_1dma('flat_'+ktgts[0], color=4, yrange=yrange_flat)

        file_out = ROOT.TFile('Fits/Bkgfits_flat_region%s.root'%region, "UPDATE")
        #file_out = ROOT.TFile('Fits/Bkgfits_flat_region%s.root'%region, "RECREATE")
        hout = hvalid if region == 'valid' else hlimit
        #k_ = 'flat_%sh4g100MeV'%region
        k_ = 'flat_%sh4g'%region
        hout[k_] = h['flat_'+ktgts[0]].Clone()
        hout[k_].SetName(k_)
        #for shift in ['Up', 'Down']:
        #    k_shift = k_+'_stat'+shift
        #    hout[k_shift] = hout[k_].Clone()
        #    hout[k_shift].Reset()
        #    hout[k_shift].SetName(k_shift)
        #    for ib in range(1, hout[k_shift].GetNbinsX()+1):
        #        binc = hout[k_].GetBinContent(ib)
        #        binerr = hout[k_].GetBinError(ib)
        #        binout = binc + binerr if shift == 'Up' else binc - binerr
        #        hout[k_shift].SetBinContent(ib, binout)
        file_out.Write()
        file_out.Close()
'''
