from __future__ import print_function
import ROOT
import numpy as np
from array import array
from hist_utils import *
from get_bkg_norm import *
from collections import OrderedDict
import CMS_lumi, tdrstyle

for_thesis = True

#tdrstyle.setTDRStyle()
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
#change the CMS_lumi variables (see CMS_lumi.py)
CMS_lumi.lumi_7TeV = "4.8 fb^{-1}"
CMS_lumi.lumi_8TeV = "18.3 fb^{-1}"
CMS_lumi.writeExtraText = 1
#CMS_lumi.extraText = "Preliminary" # for PAS
CMS_lumi.extraText = "" # for PRL
CMS_lumi.cmsTextOffset = 0.
#CMS_lumi.lumi_sqrtS = "41.5 fb^{-1} (13 TeV)" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
CMS_lumi.lumi_sqrtS = "136 fb^{-1} (13 TeV)" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
iPos = 11
if( iPos==0 ):
    CMS_lumi.relPosX = 0.12
CMS_lumi.relPosY = 0.048
iPeriod = 0

wd, ht = int(800*1), int(680*1)
wd_wide = 1400

def draw_hist_1dma_postfit_sg(kplots, yrange=None, idx=None, ksgs=[]):

    kbkg, kobs = kplots

    hc = {}
    legend = {}

    txtFont = 42
    mrkstyle = 20 #24 #20 #20
    mrksize = 0.75 #0.6 #75 #6
    err_style = 'E2'
    fill_style = 3002
    #wd, ht = int(640*1), int(680*1)
    wd, ht = int(640*1), int(720*1)
    #ROOT.TGaxis.fgMaxDigits = 3
    ROOT.gStyle.SetErrorX(0)

    icols = {}
    icols['red'] =    1180 #ROOT.TColor.GetFreeColorIndex()
    icols['blue'] =   1181 #ROOT.TColor.GetFreeColorIndex()
    icols['green'] =  1182 #ROOT.TColor.GetFreeColorIndex()
    icols['purple'] = 1183 #ROOT.TColor.GetFreeColorIndex()
    icols['orange'] = 1184 #ROOT.TColor.GetFreeColorIndex()
    tcols = {}
    tcols['red'] = ROOT.TColor(icols['red'],       228./255.,  26./255.,  28./255.)
    tcols['blue'] = ROOT.TColor(icols['blue'],      55./255., 126./255., 184./255.)
    tcols['green'] = ROOT.TColor(icols['green'],    77./255., 175./255.,  74./255.)
    tcols['purple'] = ROOT.TColor(icols['purple'], 152./255.,  78./255., 163./255.)
    tcols['orange'] = ROOT.TColor(icols['orange'], 255./255., 127./255.,   0./255.)

    kc = kobs
    c[kc] = ROOT.TCanvas("c%s"%kc,"c%s"%kc,wd,ht)

    pUp = ROOT.TPad("upperPad", "upperPad",.005, .305, .995, .995) # (,,Double_t xlow, Double_t ylow, Double_t xup, Double_t yup,...)
    pDn = ROOT.TPad("lowerPad", "lowerPad",.005, .005, .995, .305)
    pUp.Draw()
    pDn.Draw()
    pUp.SetMargin(16.e-02, 3.e-02, 2.e-02,  8.5e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pDn.SetMargin(16.e-02, 3.e-02, 38.e-02, 2.2e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)

    pUp.cd()

    k = kobs+'dummy'
    h[k] = h[kobs].Clone()
    h[k].Reset(k)
    h[k].SetName(k)
    #h[k] = set_hist(h[k], "m_{#Gamma,pred} [GeV]", "N_{#Gamma} / %d MeV"%dMa, "")
    #h[k] = set_hist(h[k], "m_{#Gamma} [GeV]", "Events / %d MeV"%dMa, "")
    h[k] = set_hist(h[k], "m_{#Gamma} [GeV]", "Events / %.2f GeV"%(dMa/1.e3), "")
    h[k].GetXaxis().SetTitle('')
    h[k].GetXaxis().SetLabelSize(0.)
    h[k].GetYaxis().SetTitleOffset(1.18) #0.9
    h[k].GetYaxis().SetLabelOffset(0.01)
    h[k].GetYaxis().SetTitleSize(0.073)
    h[k].GetYaxis().SetLabelSize(0.06)
    h[k].GetYaxis().SetMaxDigits(3)
    h[k].GetYaxis().SetTitleFont(txtFont)
    h[k].GetYaxis().SetLabelFont(txtFont)
    if yrange is not None:
        #h[k].GetYaxis().SetRangeUser(yrange[0], yrange[1])
        h[k].GetYaxis().SetRangeUser(yrange[0]+1.e-1, yrange[1])
    h[k].Draw("E")

    # Plot bkg hist line
    k = kbkg
    h[k].SetLineColor(icols['blue']) #9
    h[k].SetLineStyle(1)
    h[k].Draw("hist same")

    # Plot bkg err bands
    #hc[kbkg] = h[kbkg].Clone()
    #hc[kbkg].SetName(kbkg+'unc')
    #hc[kbkg].SetLineColor(3)
    #hc[kbkg].SetFillColor(3)
    #hc[kbkg].SetFillStyle(3002)
    #hc[kbkg].Draw("E2 same")
    hc[kbkg] = ROOT.TGraphErrors()
    hc[kbkg].SetName(kbkg+'unc')
    for i in range(1, h[kbkg].GetNbinsX()+1):
        hc[kbkg].SetPoint(i-1, h[k].GetBinCenter(i), h[kbkg].GetBinContent(i))
        hc[kbkg].SetPointError(i-1, h[k].GetBinWidth(i)/2., h[kbkg].GetBinError(i))
    hc[kbkg].SetLineColor(icols['green']) #3
    hc[kbkg].SetFillColor(icols['green']) #3
    #hc[kbkg].SetLineColor(3)
    #hc[kbkg].SetFillColor(3)
    hc[kbkg].SetFillStyle(3002)
    hc[kbkg].Draw("E2 same")

    # Plot obs data
    h[kobs].SetFillStyle(0)
    h[kobs].SetMarkerStyle(mrkstyle)
    h[kobs].SetMarkerSize(mrksize)
    #h[kobs].Draw("E same")
    #h[kobs].Draw("P same")
    h[kobs].Draw("EP same")

    fHepData = ROOT.TFile('hepdata/1D-mG_%d.root'%idx, "RECREATE")
    h[kbkg].Write()
    h[kobs].Write()

    # Plot sg
    #cols = [41, 14, 46]
    #cols = [41, 14, 2]
    #cols = [41, 2, 14]
    #cols = [icols['purple'], icols['red'], icols['orange']]
    cols = [icols['purple'], 14, icols['orange']]
    explimits = [0.00284129175647, 0.000880130779781, 0.00173156164283]
    for i,ksg in enumerate(ksgs):
        h[ksg].Scale(explimits[i]*1.e3)
        h[ksg].SetLineStyle(i+2)
        h[ksg].SetLineWidth(6)
        h[ksg].SetLineColor(cols[i])
        h[ksg].Draw("hist same")

        h[ksg].Write()
    fHepData.Close()

    # Draw 2dma region text
    blindTextOffset = 0.4
    #blindTextSize   = 0.65
    blindTextSize   = 0.75
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

    blindText = 'm_{H}-SR #cap m_{#it{A}}-SR' if 'offdiag' in blind else 'm_{#it{A}}-SB'
    if for_thesis:
        blindText = 'm_{H}-SR #cap m_{a}-SR' if 'offdiag' in blind else 'm_{a}-SB'
    #print(blind, blindText)
    ltx = ROOT.TLatex()
    ltx.SetNDC()
    ltx.SetTextFont(txtFont)#bold:62
    ltx.SetTextAlign(13)
    ltx.SetTextSize(blindTextSize*t_)
    #ltx.DrawLatex(0.44, 0.8, blindText)
    ltx.DrawLatex(0.44, 0.85, blindText)

    '''
    legend[k] = ROOT.TLegend(0.42, 0.7-0.28, 0.95, 0.7) #(x1, y1, x2, y2)
    legend[k].AddEntry(h[kobs].GetName(), "Obs.", "ep")
    legend[k].AddEntry(h[kbkg].GetName(), "Bkg.", "l")
    legend[k].AddEntry(hc[kbkg].GetName(), "Bkg. unc. (stat + syst)", "f")
    #legend[k].AddEntry(hc[kbkg].GetName(), "Bkg, stat", "f")
    legend[k].SetBorderSize(0)
    legend[k].SetTextFont(txtFont)
    legend[k].Draw("same")
    '''

    #legend[k] = ROOT.TLegend(0.42, 0.3, 0.93, 0.78) #(x1, y1, x2, y2)
    legend[k] = ROOT.TLegend(0.425, 0.31, 0.93, 0.78) #(x1, y1, x2, y2)
    #legend[k].AddEntry(h[kobs].GetName(), "Data", "ep")
    legend[k].AddEntry(h[kobs].GetName(), "Data", "p")
    legend[k].AddEntry(h[kbkg].GetName(), "Bkg.", "l")
    legend[k].AddEntry(hc[kbkg].GetName(), "Bkg. unc. (stat + syst)", "f")
    mas = [0.1, 0.4, 1.0]
    for i,ksg in enumerate(ksgs):
        if not for_thesis:
            legend[k].AddEntry(h[ksg].GetName(), "m_{#it{A}} = %.1f GeV"%mas[i], "l")
        else:
            legend[k].AddEntry(h[ksg].GetName(), "m_{a} = %.1f GeV"%mas[i], "l")
    legend[k].SetBorderSize(0)
    legend[k].SetTextFont(txtFont)
    legend[k].Draw("same")

    CMS_lumi.CMS_lumi(pUp, iPeriod, iPos)

    ##### Ratio plots on lower pad #####
    pDn.cd()
    pDn.SetTicky()
    #pDn.SetGridy()

    #fUnity = ROOT.TF1("fUnity","[0]",-0.4,1.2)
    fUnity = ROOT.TF1("fUnity","[0]",-0.,1.2)
    fUnity.SetParameter( 0,1. )

    #fUnity.GetXaxis().SetTitle("m_{#Gamma,pred} [GeV]")
    #pho_idx = ',%d'%idx if idx is not None else ''
    pho_idx = '%d'%idx if idx is not None else ''
    #fUnity.GetXaxis().SetTitle("m_{ #Gamma%s} [GeV]"%pho_idx)
    fUnity.GetXaxis().SetTitle("m_{ #Gamma_{%s}} [GeV]"%pho_idx)
    fUnity.GetXaxis().SetTickLength(0.1)
    fUnity.GetXaxis().SetTitleOffset(1.0)
    fUnity.GetXaxis().SetLabelOffset(0.01)
    #fUnity.GetXaxis().SetTitleSize(0.18)
    fUnity.GetXaxis().SetTitleSize(0.17)
    fUnity.GetXaxis().SetLabelSize(0.14)
    fUnity.GetXaxis().SetLabelFont(txtFont)
    fUnity.GetXaxis().SetTitleFont(txtFont)

    dY = 0.099
    dY = 0.075
    #dY = 0.199
    #dY = 0.399
    #fUnity.GetYaxis().SetTitle("SB/SR")
    fUnity.GetYaxis().SetTitle("Data / Bkg.")
    #fUnity.GetYaxis().SetRangeUser(1.-dY,1.+dY)
    fUnity.SetMaximum(1.+dY)
    fUnity.SetMinimum(1.-dY)
    fUnity.GetYaxis().SetNdivisions(305)
    fUnity.GetYaxis().SetTickLength(0.04)
    fUnity.GetYaxis().SetLabelFont(txtFont)
    fUnity.GetYaxis().SetTitleFont(txtFont)
    fUnity.GetYaxis().SetLabelOffset(0.01)
    fUnity.GetYaxis().SetTitleOffset(.5)
    fUnity.GetYaxis().SetLabelSize(0.14)
    fUnity.GetYaxis().SetTitleSize(0.165)

    fUnity.SetLineColor(9)
    fUnity.SetLineWidth(1)
    #fUnity.SetLineWidth(0)
    #fUnity.SetLineStyle(7)
    fUnity.SetLineStyle(1)
    fUnity.SetTitle("")
    fUnity.Draw()

    # Plot bkg err bands
    k = kbkg
    kr = k+'statsyst'
    #h[kr] = h[k].Clone()
    #h[kr].Reset()
    #h[kr].SetName(kr)
    #for i in range(1, h[k].GetNbinsX()+1):
    #    binc = h[kbkg].GetBinContent(i)
    #    binerr = h[kbkg].GetBinError(i)
    #    h[kr].SetBinContent(i, 1.)
    #    h[kr].SetBinError(i, binerr/binc if binc > 0. else 0.)
    #h[kr].SetFillColor(3)
    #h[kr].SetFillStyle(3002)
    #h[kr].Draw("E2 same")
    h[kr] = ROOT.TGraphErrors()
    h[kr].SetName(kr)
    for i in range(1, h[kbkg].GetNbinsX()+1):
        binc = h[kbkg].GetBinContent(i)
        binerr = h[kbkg].GetBinError(i)
        h[kr].SetPoint(i-1, (0.5+(i-1))*dMa/1.e3, 1.)
        h[kr].SetPointError(i-1, 0.5*dMa/1.e3, binerr/binc if binc > 0. else 0.)
    h[kr].SetLineColor(icols['green']) #3
    h[kr].SetFillColor(icols['green']) #3
    #h[kr].SetLineColor(3)
    #h[kr].SetFillColor(3)
    h[kr].SetFillStyle(3002)
    h[kr].Draw("E2 same")

    # Plot obs/bkg err bars
    k = kobs
    kr = k+'ratio'
    h[kr] = h[k].Clone()
    h[kr].Reset()
    h[kr].SetName(kr)
    for i in range(1, h[k].GetNbinsX()+1):
        binc_num = h[kobs].GetBinContent(i)
        binc_den = h[kbkg].GetBinContent(i)
        binerr_num = h[kobs].GetBinError(i)
        h[kr].SetBinContent(i, binc_num/binc_den if binc_den > 0. else 0.)
        h[kr].SetBinError(i, binerr_num/binc_num if binc_num > 0. else 0.)
    h[kr].SetMarkerStyle(mrkstyle)
    h[kr].SetMarkerSize(mrksize)
    h[kr].Draw("Ep same")

    c[kc].Draw()
    c[kc].Update()
    #c[kc].Print('Plots/Sys2D_%.pdf'%(kc))
    #c[kc].Print('Plots/Sys2D_%sfit_h4g%s_%s.pdf'%(fit, ma, kc))
    c[kc].Print('Plots/Sys2D_%sfit_%s.pdf'%(fit, kc))

def plot_datavmc_flat_postfit(kplots, nbins, yrange=None, colors=[3, 10], styles=[1001, 1001], titles=["im_{1} #times im_{2} + im_{2}", "Events"]):

    hc = {}
    legend = {}
    xtitle, ytitle = titles
    kbkg, kobs = kplots

    #sample = kobs.split('_')[1]
    #blind = kobs.split('_')[2]
    #sr = kobs[-3:]
    #sb = kbkg[-3:]
    #kc = '%s_%s_%s_%so%s_2dmaflat'%(sample, syst, blind, sr, sb)
    #print('>> Flat plot name: [sample, syst, blind, sr o sb]',kc, sample, syst, blind)
    #print('>> Flat plot kobs:',kobs)

    wd, ht = int(800*1), int(680*1)
    wd_wide = 1400
    mrkstyle = 20 #24 #20 #20
    mrksize = 0.6 #6
    err_style = 'E2'
    fill_style = 3002
    #txtFont = 62
    txtFont = 42

    kc = kobs
    c[kc] = ROOT.TCanvas('c'+kc, 'c'+kc, wd_wide, ht)

    #ROOT.TGaxis.fgMaxDigits = 3
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetErrorX(0)

    pUp = ROOT.TPad("upperPad", "upperPad",.005, .300, .995, .995) # (,, xlow, ylow, xup, yup)
    pDn = ROOT.TPad("lowerPad", "lowerPad",.005, .005, .995, .300)
    pUp.Draw()
    pDn.Draw()
    #pUp.SetMargin(14.e-02,3.e-02,5.e-03,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pUp.SetMargin(6.e-02,1.e-02,2.e-02,9.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pDn.SetMargin(6.e-02,1.e-02,36.e-02,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)

    pUp.cd()

    # Dummy plots (workaround)
    k = kbkg+'dummy'
    h[k] = h[kbkg].Clone()
    h[k].Reset(k)
    h[k].SetName(k)
    h[k].SetTitle("")
    h[k].GetXaxis().SetTitle(xtitle)
    #h[k].GetYaxis().SetTitle(ytitle+' / %d MeV'%dMa)
    h[k].GetYaxis().SetTitle(ytitle+' / %.2f GeV'%(dMa/1.e3))
    h[k].GetYaxis().SetTitleOffset(0.4)
    h[k].GetXaxis().SetTitleOffset(1.)
    h[k].GetXaxis().SetTitleSize(0.06)
    h[k].GetYaxis().SetTitleSize(0.075)
    h[k].GetXaxis().SetLabelFont(txtFont)
    h[k].GetXaxis().SetLabelSize(0)
    h[k].GetYaxis().SetLabelSize(0.055)
    h[k].GetXaxis().SetTitleFont(txtFont)
    h[k].GetYaxis().SetLabelFont(txtFont)
    h[k].GetYaxis().SetTitleFont(txtFont)
    h[k].GetYaxis().SetMaxDigits(3)
    if yrange is not None:
        #h[k].GetYaxis().SetRangeUser(yrange[0], yrange[1])
        h[k].GetYaxis().SetRangeUser(yrange[0]+1.e-1, yrange[1])
    h[k].SetLineColor(0)
    h[k].SetFillColor(0)
    h[k].Draw("LF2")

    # Plot bkg hist line
    k = kbkg
    h[k].SetLineColor(9)
    h[k].SetLineStyle(1)
    h[k].Draw("hist same")

    # Plot bkg err bands
    #hc[kbkg] = h[kbkg].Clone()
    #hc[kbkg].SetName(kbkg+'unc')
    #hc[kbkg].SetLineColor(3)
    #hc[kbkg].SetFillColor(3)
    #hc[kbkg].SetFillStyle(3002)
    ##hc[kbkg].Draw("E2 same")
    #hc[kbkg].Draw("E2 same")
    hc[kbkg] = ROOT.TGraphErrors()
    hc[kbkg].SetName(kbkg+'unc')
    for i in range(1, h[kbkg].GetNbinsX()+1):
        hc[kbkg].SetPoint(i-1, 0.5+(i-1), h[kbkg].GetBinContent(i))
        hc[kbkg].SetPointError(i-1, 0.5, h[kbkg].GetBinError(i))
    hc[kbkg].SetLineColor(3) #3
    hc[kbkg].SetFillColor(3) #3
    hc[kbkg].SetFillStyle(3002)
    hc[kbkg].Draw("E2 same")

    # Plot obs data
    h[kobs].SetFillStyle(0)
    h[kobs].SetMarkerStyle(mrkstyle)
    h[kobs].SetMarkerSize(mrksize)
    #h[kobs].Draw("E same")
    h[kobs].Draw("EP same")

    pUp.RedrawAxis()

    #blindTextSize     = 0.65
    blindTextSize     = 0.75
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
    #print(posY_)

    #blindText = 'm(a)-SR'
    #blindText = 'm_{a}-SR'
    #blindText = 'm_{H}-SR #cap m_{a}-SR'# if 'offdiag' in blind else 'm(a)-SB'
    blindText = 'm_{H}-SR #cap m_{#it{A}}-SR'# if 'offdiag' in blind else 'm(a)-SB'
    if for_thesis:
        blindText = 'm_{H}-SR #cap m_{a}-SR'# if 'offdiag' in blind else 'm(a)-SB'
    #blindText = 'h #rightarrow'
    ltx = ROOT.TLatex()
    ltx.SetNDC()
    #ltx.SetTextColor(ROOT.kBlack)
    ltx.SetTextFont(42)#bold:62
    ltx.SetTextAlign(13)
    ltx.SetTextSize(blindTextSize*t_)
    ltx.DrawLatex(posX_+0.05, posY_-0.08, blindText)

    k = kobs
    #legend[k] = ROOT.TLegend(0.75, posY_-0.35, 0.95, posY_-0.05) #(x1, y1, x2, y2)
    legend[k] = ROOT.TLegend(0.7, posY_-0.35, 0.95, posY_-0.05) #(x1, y1, x2, y2)
    legend[k].AddEntry(h[kobs].GetName(), "Data", "p")
    legend[k].AddEntry(h[kbkg].GetName(), "Bkg.", "l")
    legend[k].AddEntry(hc[kbkg].GetName(), "Bkg. unc. (stat+syst)", "f")
    #legend[k].AddEntry(hc[kbkg].GetName(), "Bkg, stat", "f")
    legend[k].SetBorderSize(0)
    legend[k].SetTextFont(txtFont)
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
    fUnity.GetXaxis().SetLabelFont(txtFont)
    fUnity.GetXaxis().SetTitleFont(txtFont)

    dY = 0.399
    dY = 0.199
    #dY = 0.75
    fUnity.GetYaxis().SetTitle("Data / Bkg.")
    #fUnity.GetYaxis().SetRangeUser(1.-dY,1.+dY)
    fUnity.SetMaximum(1.+dY)
    fUnity.SetMinimum(1.-dY)
    fUnity.GetYaxis().SetNdivisions(305)
    fUnity.GetYaxis().SetTickLength(0.04)
    fUnity.GetYaxis().SetLabelFont(txtFont)
    fUnity.GetYaxis().SetTitleFont(txtFont)
    fUnity.GetYaxis().SetTitleOffset(.172)
    fUnity.GetYaxis().SetTitleSize(0.165)
    fUnity.GetYaxis().SetLabelSize(0.12)

    fUnity.SetLineColor(9)
    #fUnity.SetLineColor(3)
    #fUnity.SetLineWidth(1)
    fUnity.SetLineWidth(0)
    fUnity.SetLineStyle(1)
    fUnity.SetTitle("")
    fUnity.Draw("L")

    # Plot bkg err bands
    k = kbkg
    kr = k+'statsyst'
    #h[kr] = h[k].Clone()
    #h[kr].Reset()
    #h[kr].SetName(kr)
    #for i in range(1, h[k].GetNbinsX()+1):
    #    binc = h[kbkg].GetBinContent(i)
    #    binerr = h[kbkg].GetBinError(i)
    #    h[kr].SetBinContent(i, 1.)
    #    h[kr].SetBinError(i, binerr/binc if binc > 0. else 0.)
    #h[kr].SetFillColor(3)
    #h[kr].SetFillStyle(3002)
    #h[kr].Draw("E2 same")
    h[kr] = ROOT.TGraphErrors()
    h[kr].SetName(kr)
    for i in range(1, h[kbkg].GetNbinsX()+1):
        binc = h[kbkg].GetBinContent(i)
        binerr = h[kbkg].GetBinError(i)
        #h[kr].SetPoint(i-1, 0.5+(i-1), 1.)
        #h[kr].SetPointError(i-1, 0.5, binerr/binc if binc > 0. else 0.)
        h[kr].SetPoint(i-1, h[kbkg].GetBinCenter(i), 1.)
        h[kr].SetPointError(i-1, h[k].GetBinWidth(i)/2., binerr/binc if binc > 0. else 0.)
    h[kr].SetLineColor(3) #3
    h[kr].SetFillColor(3) #3
    h[kr].SetFillStyle(3002)
    h[kr].Draw("E2 same")

    # Get obs pts from TGraphAsymm
    #xvals = h[kobs].GetX()
    #yvals = h[kobs].GetY()
    #eyhis = h[kobs].GetEYhigh()
    #eylos = h[kobs].GetEYlow()
    # Plot obs/bkg err bars
    k = kobs
    kr = k+'ratio'
    h[kr] = h[k].Clone()
    h[kr].Reset()
    h[kr].SetName(kr)
    for i in range(1, h[k].GetNbinsX()+1):
        binc_num = h[kobs].GetBinContent(i)
        binc_den = h[kbkg].GetBinContent(i)
        binerr_num = h[kobs].GetBinError(i)
        h[kr].SetBinContent(i, binc_num/binc_den if binc_den > 0. else 0.)
        h[kr].SetBinError(i, binerr_num/binc_num if binc_num > 0. else 0.)

    #h[kr] = ROOT.TGraphAsymmErrors()
    #h[kr].SetName(kr)
    #for i in range(h[k].GetN()):
    #    ib = i+1

    #    h[kr].SetPoint(i, xvals[i], binc_num/binc_den if binc_den > 0. else 0.)
    #    h[kr].SetPointError(
    #        i,
    #        0.,
    #        0.,
    #        1.- (yvals[i]-eylos[i])/yvals[i] if yvals[i] > 0. else 0.,
    #        (yvals[i]+eyhis[i])/yvals[i] - 1 if yvals[i] > 0. else 0.
    #        )
    h[kr].SetMarkerStyle(mrkstyle)
    h[kr].SetMarkerSize(mrksize)
    h[kr].Draw("Ep same")

    pDn.SetGridy()
    pDn.Update()
    #pDn.RedrawAxis()
    #fUnity.Draw("axis same")
    #'''
    c[kc].Draw()
    #c[kc].Update()
    #print(kc)
    #c[kc].Print('Plots/Sys2D_%sfit_h4g%s_%s.pdf'%(fit, ma, kc))
    c[kc].Print('Plots/Sys2D_%sfit_%s.pdf'%(fit, kc))

f, hf, = {}, {}
h = OrderedDict()
fLine = {}
hatch, hatch2 = {}, {}
ax, ay = {}, {}
c = {}

valid_blind = 'diag_lo_hi'
limit_blind = 'offdiag_lo_hi'
blinds = [valid_blind, limit_blind]
apply_blinding = True
apply_blinding = False
plot_syst = False
plot_syst = True

dMa = 25
dMa = 50
if dMa == 50:
    #nbins = {valid_blind:420, limit_blind:196} #dM50, blind_w=200MeV
    #nbins = {valid_blind:342, limit_blind:270} #dM50, blind_w=300MeV
    nbins = {valid_blind:342, limit_blind:234} #native dM50, blind_w=300MeV
elif dMa == 100:
    #nbins = {valid_blind:110, limit_blind:54} #dM100, blind_w = 200MeV
    nbins = {valid_blind:90, limit_blind:72} #dM100, blind_w = 300MeV
else:
    #nbins = {valid_blind:1640, limit_blind:664} #dM25, blind_w = 200MeV
    nbins = {valid_blind:1332, limit_blind:972} #dM25, blind_w = 300MeV

blind_w = 300.
if dMa == 100:
    # Run2
    ymax_1d = 54.e3
    ymax_flat = 18.e3
elif dMa == 50:
    # Run2
    ymax_1d = 35.e3
    ymax_flat = 6.e3
else:
    # Run2
    ymax_1d = 18.e3 # 16.e3
    ymax_flat = 1.6e3

##########
# Sg model
##########
r_sr = 'sr'
run = 'Run2'
k = 'ma0vma1'
indir = 'root://cmseos.fnal.gov//store/user/lpchaa4g/mandrews/%s'%run
sub_campaign = 'bdtgtm0p96_relChgIsolt0p07_etalt1p44' # bdt > -0.96, relChgIso < 0.07 !! optimal
dMa = 50
sel = 'nom'
#CMS_lumi.extraText = "Simulation"
ma_pts = ['0p1', '0p4', '1p0']
#ma_pts = ['0p4']
regions = [r_sr]
blinds = [limit_blind, valid_blind] # to get fully unblinded plots, run mk_sg_temp and combine_sg_temp with both blinding settings!
campaign = 'sg-Era22Jun2021v6/%s/nom-%s/Templates/systNom_nom'%(sub_campaign, sel) #  bin50MeV
do_blind = True
do_blind = False
for ma in ma_pts:

    sample = 'h4g-mA%sGeV'%ma if run == 'Run2' else 'h4g%s-mA%sGeV'%(run, ma)
    maxzs = []
    for r in regions:
        srk = '%s_%s_%s'%(sample, r, k)
        for b in blinds:

            inpath = "%s/%s/%s_%s_blind_%s_templates.root"%(indir, campaign, sample, r, b)
            print('>> Reading:', inpath)

            srkb = '%s-%s'%(srk, b)
            print('srkb:',srkb)

            hf[srkb] = ROOT.TFile.Open(inpath, "READ")

            h[srkb] = hf[srkb].Get(srkb)
            h[srkb].SetName(srkb)
            if b == limit_blind:
                h[srk] = h[srkb].Clone()
                h[srk].SetName(srk)
            else:
                # to make fully unblinded 2dma, add offdiag + diag blinded plots
                if not (do_blind and r == r_sr):
                    h[srk].Add(h[srkb])
        maxzs.append(h[srk].GetMaximum())
        print('h[%s], max: %f'%(srk, h[srk].GetMaximum()))

        ksg = srk
        ksg0 = ksg+'_ma0'
        h[ksg0] = h[ksg].ProjectionX(ksg0)
        h[ksg0].SetName(ksg0)
        #h[ksg0].Draw()
        ksg1 = ksg+'_ma1'
        h[ksg1] = h[ksg].ProjectionY(ksg1)
        h[ksg1].SetName(ksg1)
        #h[ksg1].Draw()
    #for r in regions:
    #    srk = '%s_%s_%s'%(sample, r, k)
    #    #draw_hist_2dma(srk, h, c, sample, limit_blind if do_blind and r == r_sr else None, ymax_=np.max(maxzs), do_trunc=True)

####
ksg0s = ['h4g-mA%sGeV_%s_%s_ma0'%(ma, r_sr, k) for ma in ma_pts]
ksg1s = ['h4g-mA%sGeV_%s_%s_ma1'%(ma, r_sr, k) for ma in ma_pts]
#print(ksg0s)

#########################
# S+B fits
#########################
regions = ['sr']
blind = limit_blind
sample_sg = 'h4g'

sub_campaign = 'bdtgtm0p96_relChgIsolt0p07_etalt1p44' # bdt > -0.96, relChgIso < 0.07 !! optimal
#campaign = 'sg-Era22Jun2021v3/%s/nom-nom/Templates'%sub_campaign # phoid+trg SFs. mgg95. no HLT applied.
campaign = 'sg-Era22Jun2021v6/%s/nom-nom/Templates'%sub_campaign # v5 but with 50MeV

#runs = ['Run2']
#runs = ['2018', '2017']
#runs = ['2016', '2017', '2018']

#ma_pts = ['0p1', '0p2', '0p4', '0p6', '0p8', '1p0', '1p2']
ma_pts = (np.arange(12)+1.)/10.
ma_pts = [str(m_).replace('.','p') for m_ in ma_pts]
ma_pts = ['0p1']
#ma_pts = ['0p1', '0p4', '1p0']

kbkg = 'bkg'
kobs_ = 'data'
#fit = 'pre'
#fit = 'post'

for ma in ma_pts:

    #file_in = ROOT.TFile.Open('Fits/fitDiagnostics.Test.root')
    file_in = ROOT.TFile.Open('Fits/fitDiagnostics.h4g%s.root'%ma)

    #for fit in ['pre', 'post']:
    for fit in ['post']:

        fit_str = 'prefit' if fit == 'pre' else 'fit_b'

        #file_in.cd('shapes_prefit/h4g0p1')
        h[kbkg] = file_in.Get('shapes_%s/h4g_%s/%s'%(fit_str, ma, kbkg))
        h[kobs_] = file_in.Get('shapes_%s/h4g_%s/%s'%(fit_str, ma, kobs_))
        #h[kbkg].Draw()
        #h[kobs].Draw('SAME')

        kobs = 'data-hist'
        # Get obs pts from TGraphAsymm
        xvals = h[kobs_].GetX()
        yvals = h[kobs_].GetY()
        eyhis = h[kobs_].GetEYhigh()
        eylos = h[kobs_].GetEYlow()
        # Make obs clone as hist
        h[kobs] = h[kbkg].Clone()
        h[kobs].Reset()
        h[kobs].SetName(kobs)
        for i in range(1, h[kobs].GetNbinsX()+1):
            ip = i-1
            binc = yvals[ip]
            binerr = eyhis[ip] if eyhis[ip] > eylos[ip] else eylos[ip]
            h[kobs].SetBinContent(i, binc)
            h[kobs].SetBinError(i, binerr)

        '''
        [DEPRECATED]
        for ma in ma_pts:

            for run in runs:

                sample = 'h4g-mA%sGeV'%ma if run == 'Run2' else 'h4g%s-mA%sGeV'%(run, ma)

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
        '''
        plot_datavmc_flat_postfit([kbkg, kobs], nbins[blind], yrange=[0., ymax_flat])

        #'''
        h2d = {}
        #h1d = {}
        h2d[kbkg] = ROOT.TH2F('2dma'+kbkg, '2dma'+kbkg, 1200/dMa, 0., 1.2, 1200//dMa, 0., 1.2)
        ib = 0
        for ix in range(1, h2d[kbkg].GetNbinsX()+1):
            for iy in range(1, h2d[kbkg].GetNbinsY()+1):
                if abs(ix - iy) >= int(blind_w/dMa): continue # if native binning
                #if abs(ix - iy) > int(blind_w/dMa): continue # if rebinned
                binc = h[kbkg].GetBinContent(ib+1)
                binerr = h[kbkg].GetBinError(ib+1)
                h2d[kbkg].SetBinContent(ix, iy, binc)
                h2d[kbkg].SetBinError(ix, iy, binerr)
                ib += 1
                #if ib < 10: print(binc)
        print(ib, nbins[blind], h[kbkg].GetNbinsX())
        assert ib == nbins[blind]
        assert ib == h[kbkg].GetNbinsX()
        #h2d[kbkg].Draw('COLZ')

        kbkg0 = kbkg+'_ma0'
        h[kbkg0] = h2d[kbkg].ProjectionX(kbkg0)
        h[kbkg0].SetName(kbkg0)
        kbkg1 = kbkg+'_ma1'
        h[kbkg1] = h2d[kbkg].ProjectionY(kbkg1)
        h[kbkg1].SetName(kbkg1)

        h2d[kobs] = ROOT.TH2F('2dma'+kobs, '2dma'+kobs, 1200/dMa, 0., 1.2, 1200//dMa, 0., 1.2)
        ib = 0
        for ix in range(1, h2d[kobs].GetNbinsX()+1):
            for iy in range(1, h2d[kobs].GetNbinsY()+1):
                if abs(ix - iy) >= int(blind_w/dMa): continue # if native binning
                #if abs(ix - iy) > int(blind_w/dMa): continue # if rebinned
                binc = h[kobs].GetBinContent(ib+1)
                binerr = h[kobs].GetBinError(ib+1)
                h2d[kobs].SetBinContent(ix, iy, binc)
                h2d[kobs].SetBinError(ix, iy, binerr)
                ib += 1
                #if ib < 10: print(binc)
        print(ib, nbins[blind], h[kobs].GetNbinsX())
        assert ib == nbins[blind]
        assert ib == h[kobs].GetNbinsX()
        #h2d[kobs].Draw('COLZ')

        #'''
        kobs0 = kobs+'_ma0'
        h[kobs0] = h2d[kobs].ProjectionX(kobs0)
        h[kobs0].SetName(kobs0)
        kobs1 = kobs+'_ma1'
        h[kobs1] = h2d[kobs].ProjectionY(kobs1)
        h[kobs1].SetName(kobs1)

        draw_hist_1dma_postfit_sg([kbkg0, kobs0], yrange=[0., ymax_1d], idx=1, ksgs=ksg0s)
        draw_hist_1dma_postfit_sg([kbkg1, kobs1], yrange=[0., ymax_1d], idx=2, ksgs=ksg1s)
