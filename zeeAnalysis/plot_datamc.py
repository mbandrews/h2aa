from __future__ import print_function
import ROOT
import re
import numpy as np
from array import array
from hist_utils import *
#from plot_2dma import draw_hist_2dma

def draw_hist_1dma(k_, region, h, c, samples, blind, ymax_=None):

    print(h.keys())
    kdata = 'data'+region+k_
    assert kdata in h.keys()
    kmc = 'mc'+region+k_
    assert kmc in h.keys()

    hc = {}

    err_style = 'E2'
    fill_style = 3002
    #wd, ht = int(440*1), int(400*1)
    #wd, ht = int(640*1), int(580*1)
    wd, ht = int(640*1), int(680*1)
    #ROOT.TGaxis.fgMaxDigits = 3
    #ROOT.gStyle.SetErrorX(0)

    #k = 'sr_%s'%k_
    k = kdata
    c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)

    pUp = ROOT.TPad("upperPad", "upperPad",.005, .300, .995, .995) # (,,Double_t xlow, Double_t ylow, Double_t xup, Double_t yup,...)
    pDn = ROOT.TPad("lowerPad", "lowerPad",.005, .005, .995, .300)
    pUp.Draw()
    pDn.Draw()
    #pUp.SetMargin(14.e-02,3.e-02,5.e-03,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pUp.SetMargin(13.e-02,3.e-02,2.e-02,9.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pDn.SetMargin(13.e-02,3.e-02,36.e-02,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)

    pUp.cd()
    #h[k], c[k] = set_hist(h[k], c[k], "m_{a,pred} [GeV]", "N_{a}", "")
    h[k] = set_hist(h[k], "m_{a,pred} [GeV]", "N_{a}", "")
    hc[k] = h[k].Clone()
    hc[k].SetFillStyle(0)
    hc[k].SetMarkerStyle(20)
    hc[k].SetMarkerSize(0.85)
    hc[k].GetXaxis().SetTitle('')
    hc[k].GetXaxis().SetLabelSize(0.)
    hc[k].GetYaxis().SetTitleOffset(0.9)
    hc[k].GetYaxis().SetTitleSize(0.07)
    hc[k].GetYaxis().SetLabelSize(0.06)
    hc[k].GetYaxis().SetMaxDigits(3)
    #hc[k].Draw("hist same")
    hc[k].Draw("E")

    # SB
    #k = 'sb2sr_%s'%k_
    k = kmc
    h[k].Scale(h[kdata].Integral()/h[kmc].Integral())
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

    #k = 'sr_%s'%k_
    k = kdata
    ymax = 1.2*max(h[kdata].GetMaximum(), h[kmc].GetMaximum())
    #ymax = 1.2*h[k].GetMaximum()
    if ymax_ == -1 and hc[k].GetBinContent(2) > 0.:
        #ymax = 1.2*hc[k].GetBinContent(2)
        ymax = 1.2*max(np.max([hc[kdata].GetBinContent(ib) for ib in range(2, hc[kdata].GetNbinsX()+2)]),
                       np.max([hc[kmc].GetBinContent(ib) for ib in range(2, hc[kmc].GetNbinsX()+2)]))
        #ymax = 1.2*np.max([hc[k].GetBinContent(ib) for ib in range(2, hc[k].GetNbinsX()+2)])
        #print(np.max([hc[k].GetBinContent(ib) for ib in range(2, hc[k].GetNbinsX()+2)]))
    #if ymax_ is not None and ymax_ > 0.:
    #    ymax = ymax_
    hc[kdata].GetYaxis().SetRangeUser(0.1, ymax)
    #hc[kdata].GetXaxis().SetRangeUser(0., 100.)

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
    #legend[k].AddEntry(hc[kdata].GetName(),"Obs","l")
    #legend[k].AddEntry(hc[kmc].GetName(),"Exp","l")
    #legend[k].SetBorderSize(0)
    #legend[k].Draw("same")

    ##### Ratio plots on lower pad #####
    pDn.cd()
    pDn.SetTicky()
    pDn.SetGridy()

    fUnity = ROOT.TF1("fUnity","[0]",-0.4,1.2)
    fUnity.SetParameter( 0,1. )

    fUnity.GetXaxis().SetTitle("m_{a,pred} [GeV]")
    fUnity.GetXaxis().SetTickLength(0.1)
    fUnity.GetXaxis().SetTitleOffset(1.05)
    fUnity.GetXaxis().SetTitleSize(0.16)
    fUnity.GetXaxis().SetLabelSize(0.14)

    dY = 0.199
    dY = 0.399
    #fUnity.GetYaxis().SetTitle("SB/SR")
    fUnity.GetYaxis().SetTitle("Data/MC")
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

    #k = 'sb2srosr_%s'%k_
    kr = kdata+'ratio'
    h[kr] = h[k].Clone()
    h[kr].SetLineColor(9)
    h[kr].Sumw2()
    h[kr].SetStats(0)
    h[kr].Divide(h[kmc])
    h[kr].SetMarkerStyle(20)
    h[kr].SetMarkerSize(0.85)
    h[kr].SetMarkerColor(9)
    h[kr].Draw("ep same")

    k = kr
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

    #k = 'sr_%s'%k_
    k = kdata
    c[k].Draw()
    c[k].Update()
    #c[k].Print('Plots/%s_sb2srvsr_blind_%s.eps'%(samples, blind))
    #c[k].Print('Plots/%s_sb2srvsr_blind_%.eps'%(samples, blind))
    samples_str = '_'.join(samples)
    c[k].Print('Plots/%s_dataomc_blind_%s_%s.eps'%(samples_str, blind, k))
    if 'ma1' in k_ or 'pt1' in k_:
        pass
    #c[k].Print('Plots/%s_sb2srvsr_blind_%.eps'%(samples[0], blind))

def draw_hist_1dpt(k_, region, h, c, samples, blind, ymax_=None):

    print(h.keys())
    kdata = 'data'+region+k_
    assert kdata in h.keys()
    kmc = 'mc'+region+k_
    assert kmc in h.keys()

    hc = {}

    err_style = 'E2'
    fill_style = 3002
    #wd, ht = int(440*1), int(400*1)
    #wd, ht = int(640*1), int(580*1)
    wd, ht = int(640*1), int(680*1)
    #ROOT.TGaxis.fgMaxDigits = 3
    #ROOT.gStyle.SetErrorX(0)

    k = kdata
    c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)

    pUp = ROOT.TPad("upperPad", "upperPad",.005, .300, .995, .995) # (,,Double_t xlow, Double_t ylow, Double_t xup, Double_t yup,...)
    pDn = ROOT.TPad("lowerPad", "lowerPad",.005, .005, .995, .300)
    pUp.Draw()
    pDn.Draw()
    #pUp.SetMargin(14.e-02,3.e-02,5.e-03,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pUp.SetMargin(13.e-02,3.e-02,2.e-02,9.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pDn.SetMargin(13.e-02,3.e-02,36.e-02,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)

    pUp.cd()
    #h[k], c[k] = set_hist(h[k], c[k], "m_{a,pred} [GeV]", "N_{a}", "")
    h[k] = set_hist(h[k], "p_{T,a} [GeV]", "N_{a}", "")
    hc[k] = h[k].Clone()
    hc[k].SetFillStyle(0)
    hc[k].SetMarkerStyle(20)
    hc[k].SetMarkerSize(0.85)
    hc[k].GetXaxis().SetTitle('')
    hc[k].GetXaxis().SetLabelSize(0.)
    hc[k].GetYaxis().SetTitleOffset(0.9)
    hc[k].GetYaxis().SetTitleSize(0.07)
    hc[k].GetYaxis().SetLabelSize(0.06)
    hc[k].GetYaxis().SetMaxDigits(3)
    #hc[k].Draw("hist same")
    hc[k].Draw("E")

    # SB
    #k = 'sb2sr_%s'%k_
    k = kmc
    h[k].Scale(h[kdata].Integral()/h[kmc].Integral())
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

    #k = 'sr_%s'%k_
    k = kdata
    ymax = 1.2*max(h[kdata].GetMaximum(), h[kmc].GetMaximum())
    #ymax = 1.2*h[k].GetMaximum()
    #if ymax_ == -1 and hc[k].GetBinContent(2) > 0.:
    #    #ymax = 1.2*hc[k].GetBinContent(2)
    #    ymax = 1.2*max(np.max([hc[k].GetBinContent(ib) for ib in range(2, hc[k].GetNbinsX()+2)]),
    #                   np.max([hc['sb2sr_%s'%k_].GetBinContent(ib) for ib in range(2, hc['sb2sr_%s'%k_].GetNbinsX()+2)]))
    #    #ymax = 1.2*np.max([hc[k].GetBinContent(ib) for ib in range(2, hc[k].GetNbinsX()+2)])
    #    #print(np.max([hc[k].GetBinContent(ib) for ib in range(2, hc[k].GetNbinsX()+2)]))
    #if ymax_ is not None and ymax_ > 0.:
    #    ymax = ymax_
    hc[kdata].GetYaxis().SetRangeUser(0.1, ymax)
    hc[kdata].GetXaxis().SetRangeUser(25., 100.)

    #l, l2, hatch = {}, {}, {}
    #legend = {}

    #pUp.cd()
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
    fUnity = ROOT.TF1("fUnity","[0]",25.,100.)
    fUnity.SetParameter( 0,1. )

    fUnity.GetXaxis().SetTitle("p_{T,a} [GeV]")
    fUnity.GetXaxis().SetTickLength(0.1)
    fUnity.GetXaxis().SetTitleOffset(1.05)
    fUnity.GetXaxis().SetTitleSize(0.16)
    fUnity.GetXaxis().SetLabelSize(0.14)

    dY = 0.199
    dY = 0.399
    #fUnity.GetYaxis().SetTitle("SB/SR")
    fUnity.GetYaxis().SetTitle("Data/MC")
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

    #k = 'sb2srosr_%s'%k_
    kr = kdata+'ratio'
    h[kr] = h[k].Clone()
    h[kr].SetLineColor(9)
    h[kr].Sumw2()
    h[kr].SetStats(0)
    h[kr].Divide(h[kmc])
    #for ib in range(h[kr].GetNbinsX()):
    #    print(h[kr].GetBinContent(ib))
    h[kr].SetMarkerStyle(20)
    h[kr].SetMarkerSize(0.85)
    h[kr].SetMarkerColor(9)
    h[kr].Draw("ep same")

    #k = 'sr_%s'%k_
    k = kdata
    c[k].Draw()
    c[k].Update()
    #c[k].Print('Plots/%s_sb2srvsr_blind_%s.eps'%(samples, blind))
    #c[k].Print('Plots/%s_sb2srvsr_blind_%.eps'%(samples, blind))
    samples_str = '_'.join(samples)
    c[k].Print('Plots/%s_dataomc_blind_%s_%s.eps'%(samples_str, blind, k))
    if 'ma1' in k_ or 'pt1' in k_:
        pass
    #c[k].Print('Plots/%s_sb2srvsr_blind_%.eps'%(samples[0], blind))

def draw_hist_1dmee(k_, region, h, c, samples, blind, ymax_=None):

    print(h.keys())
    kdata = 'data'+region+k_
    assert kdata in h.keys()
    kmc = 'mc'+region+k_
    assert kmc in h.keys()
    print('kdata:',kdata, 'kmc:',kmc)

    hc = {}

    err_style = 'E2'
    fill_style = 3002
    #wd, ht = int(440*1), int(400*1)
    #wd, ht = int(640*1), int(580*1)
    wd, ht = int(640*1), int(680*1)
    #ROOT.TGaxis.fgMaxDigits = 3
    #ROOT.gStyle.SetErrorX(0)

    k = kdata
    c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)

    pUp = ROOT.TPad("upperPad", "upperPad",.005, .300, .995, .995) # (,,Double_t xlow, Double_t ylow, Double_t xup, Double_t yup,...)
    pDn = ROOT.TPad("lowerPad", "lowerPad",.005, .005, .995, .300)
    pUp.Draw()
    pDn.Draw()
    #pUp.SetMargin(14.e-02,3.e-02,5.e-03,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pUp.SetMargin(13.e-02,3.e-02,2.e-02,9.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pDn.SetMargin(13.e-02,3.e-02,36.e-02,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)

    pUp.cd()
    #h[k], c[k] = set_hist(h[k], c[k], "m_{a,pred} [GeV]", "N_{a}", "")
    h[k] = set_hist(h[k], "m_{#gamma,#gamma} [GeV]", "N_{a}", "")
    hc[k] = h[k].Clone()
    hc[k].SetFillStyle(0)
    hc[k].SetMarkerStyle(20)
    hc[k].SetMarkerSize(0.85)
    hc[k].GetXaxis().SetTitle('')
    hc[k].GetXaxis().SetLabelSize(0.)
    hc[k].GetYaxis().SetTitleOffset(0.9)
    hc[k].GetYaxis().SetTitleSize(0.07)
    hc[k].GetYaxis().SetLabelSize(0.06)
    hc[k].GetYaxis().SetMaxDigits(3)
    #hc[k].Draw("hist same")
    hc[k].Draw("E")

    # SB
    #k = 'sb2sr_%s'%k_
    k = kmc
    norm = h[kdata].Integral()/h[kmc].Integral()
    print('data/mc norm:',norm, h[kdata].Integral(), h[kmc].Integral())
    h[k].Scale(h[kdata].Integral()/h[kmc].Integral())
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

    #k = 'sr_%s'%k_
    k = kdata
    ymax = 1.2*max(h[kdata].GetMaximum(), h[kmc].GetMaximum())
    #ymax = 1.2*h[k].GetMaximum()
    #if ymax_ == -1 and hc[k].GetBinContent(2) > 0.:
    #    #ymax = 1.2*hc[k].GetBinContent(2)
    #    ymax = 1.2*max(np.max([hc[k].GetBinContent(ib) for ib in range(2, hc[k].GetNbinsX()+2)]),
    #                   np.max([hc['sb2sr_%s'%k_].GetBinContent(ib) for ib in range(2, hc['sb2sr_%s'%k_].GetNbinsX()+2)]))
    #    #ymax = 1.2*np.max([hc[k].GetBinContent(ib) for ib in range(2, hc[k].GetNbinsX()+2)])
    #    #print(np.max([hc[k].GetBinContent(ib) for ib in range(2, hc[k].GetNbinsX()+2)]))
    #if ymax_ is not None and ymax_ > 0.:
    #    ymax = ymax_
    hc[kdata].GetYaxis().SetRangeUser(0.1, ymax)
    #hc[kdata].GetXaxis().SetRangeUser(100., 180.)
    hc[kdata].GetXaxis().SetRangeUser(60., 120.)

    #l, l2, hatch = {}, {}, {}
    #legend = {}

    #pUp.cd()
    #legend[k] = ROOT.TLegend(0.5,0.68,0.8,0.86) #(x1, y1, x2, y2)
    #legend[k].AddEntry(hc[k].GetName(),"Obs","l")
    #legend[k].AddEntry(hc['sb2sr_maxy'].GetName(),"Exp","l")
    #legend[k].SetBorderSize(0)
    #legend[k].Draw("same")

    ##### Ratio plots on lower pad #####
    pDn.cd()
    pDn.SetTicky()
    pDn.SetGridy()

    #fUnity = ROOT.TF1("fUnity","[0]",100.,180.)
    fUnity = ROOT.TF1("fUnity","[0]",60.,120.)
    fUnity.SetParameter( 0,1. )

    fUnity.GetXaxis().SetTitle("m_{#gamma,#gamma} [GeV]")
    fUnity.GetXaxis().SetTickLength(0.1)
    fUnity.GetXaxis().SetTitleOffset(1.05)
    fUnity.GetXaxis().SetTitleSize(0.16)
    fUnity.GetXaxis().SetLabelSize(0.14)

    dY = 0.199
    dY = 0.399
    #fUnity.GetYaxis().SetTitle("SB/SR")
    fUnity.GetYaxis().SetTitle("Data/MC")
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

    #k = 'sb2srosr_%s'%k_
    kr = kdata+'ratio'
    h[kr] = h[k].Clone()
    h[kr].SetLineColor(9)
    h[kr].Sumw2()
    h[kr].SetStats(0)
    h[kr].Divide(h[kmc])
    #for ib in range(h[kr].GetNbinsX()):
    #    print(h[kr].GetBinContent(ib))
    h[kr].SetMarkerStyle(20)
    h[kr].SetMarkerSize(0.85)
    h[kr].SetMarkerColor(9)
    h[kr].Draw("ep same")

    #k = 'sr_%s'%k_
    k = kdata
    c[k].Draw()
    c[k].Update()
    #c[k].Print('Plots/%s_sb2srvsr_blind_%s.eps'%(samples, blind))
    #c[k].Print('Plots/%s_sb2srvsr_blind_%.eps'%(samples, blind))
    samples_str = '_'.join(samples)
    c[k].Print('Plots/%s_dataomc_blind_%s_%s.eps'%(samples_str, blind, k))
    if 'ma1' in k_ or 'pt1' in k_:
        pass
    #c[k].Print('Plots/%s_sb2srvsr_blind_%.eps'%(samples[0], blind))

def draw_hist_1dstacked(k_, region, hist_list, c, samples, blind, ymax_=None, mcnorm=1., range_minmax=[0., 100.], title=''):

    h, hsample = hist_list

    print(h.keys())
    kdata = 'data'+region+k_
    assert kdata in h.keys()
    kmc = 'mc'+region+k_
    assert kmc in h.keys()
    kmcsample = 'mcsample'+region+k_
    print('kdata:',kdata, 'kmc:',kmc)
    print(h[kmc].Integral())

    hc = {}

    err_style = 'E2'
    fill_style = 3002
    wd, ht = int(640*1), int(680*1)
    #ROOT.TGaxis.fgMaxDigits = 3
    #ROOT.gStyle.SetErrorX(0)

    k = kdata
    c[k+'stack'] = ROOT.TCanvas("c%s_stacked"%k,"c%s_stacked"%k,wd,ht)

    pUp = ROOT.TPad("upperPad", "upperPad",.005, .300, .995, .995) # (,,Double_t xlow, Double_t ylow, Double_t xup, Double_t yup,...)
    pDn = ROOT.TPad("lowerPad", "lowerPad",.005, .005, .995, .300)
    pUp.Draw()
    pDn.Draw()
    #pUp.SetMargin(14.e-02,3.e-02,5.e-03,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pUp.SetMargin(13.e-02,3.e-02,2.e-02,9.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pDn.SetMargin(13.e-02,3.e-02,36.e-02,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)

    pUp.cd()
    #h[k], c[k] = set_hist(h[k], c[k], "m_{a,pred} [GeV]", "N_{a}", "")
    h[k] = set_hist(h[k], title, "N_{a}", "")
    hc[k] = h[k].Clone()
    hc[k].SetFillStyle(0)
    hc[k].SetMarkerStyle(20)
    hc[k].SetMarkerSize(0.85)
    hc[k].GetXaxis().SetTitle('')
    hc[k].GetXaxis().SetLabelSize(0.)
    hc[k].GetYaxis().SetTitleOffset(0.9)
    hc[k].GetYaxis().SetTitleSize(0.07)
    hc[k].GetYaxis().SetLabelSize(0.06)
    hc[k].GetYaxis().SetMaxDigits(3)
    #hc[k].Draw("hist same")
    hc[k].Draw("E")

    # SB
    #k = 'sb2sr_%s'%k_
    k = kmc
    #norm = h[kdata].Integral()/h[kmc].Integral()
    #norm = 0.011002413288983316
    #print('data/mc norm:',norm, h[kdata].Integral(), h[kmc].Integral())
    h[k].Scale(mcnorm)
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

    hstack = ROOT.THStack("hs","hs")
    print(hsample.keys())
    for i,key in enumerate(hsample.keys()):
        if 'Run' in key: continue
        if k_ not in key: continue
        hsample[key].SetLineColor(plot_color(key))
        #print(key, hsample[key].Integral(), norm)
        hsample[key].Scale(mcnorm)
        print(key, hsample[key].Integral())
        #hsample[key].GetXaxis().SetRangeUser(25., 100.)
        hstack.Add(hsample[key])
    hstack.Draw("hist same")

    #k = 'sr_%s'%k_
    k = kdata
    ymax = 1.2*max(h[kdata].GetMaximum(), h[kmc].GetMaximum())
    if ymax_ == -1 and hc[k].GetBinContent(2) > 0.:
        #ymax = 1.2*hc[k].GetBinContent(2)
        ymax = 1.2*max(np.max([hc[kdata].GetBinContent(ib) for ib in range(2, hc[kdata].GetNbinsX()+2)]),
                       np.max([hc[kmc].GetBinContent(ib) for ib in range(2, hc[kmc].GetNbinsX()+2)]))
    hc[kdata].GetYaxis().SetRangeUser(0.1, ymax)
    hc[kdata].GetXaxis().SetRangeUser(range_minmax[0], range_minmax[1])

    #l, l2, hatch = {}, {}, {}
    #legend = {}

    #pUp.cd()
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
    fUnity = ROOT.TF1("fUnity","[0]",range_minmax[0], range_minmax[1])
    fUnity.SetParameter( 0,1. )

    fUnity.GetXaxis().SetTitle(title)
    fUnity.GetXaxis().SetTickLength(0.1)
    fUnity.GetXaxis().SetTitleOffset(1.05)
    fUnity.GetXaxis().SetTitleSize(0.16)
    fUnity.GetXaxis().SetLabelSize(0.14)

    dY = 0.199
    dY = 0.399
    #fUnity.GetYaxis().SetTitle("SB/SR")
    fUnity.GetYaxis().SetTitle("Data/MC")
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

    #k = 'sb2srosr_%s'%k_
    kr = kdata+'ratio'
    h[kr] = h[k].Clone()
    h[kr].SetLineColor(9)
    h[kr].Sumw2()
    h[kr].SetStats(0)
    h[kr].Divide(h[kmc])
    #for ib in range(h[kr].GetNbinsX()):
    #    print(h[kr].GetBinContent(ib))
    h[kr].SetMarkerStyle(20)
    h[kr].SetMarkerSize(0.85)
    h[kr].SetMarkerColor(9)
    h[kr].Draw("ep same")

    #k = 'sr_%s'%k_
    k = kdata+'stack'
    c[k].Draw()
    c[k].Update()
    #c[k].Print('Plots/%s_sb2srvsr_blind_%s.eps'%(samples, blind))
    #c[k].Print('Plots/%s_sb2srvsr_blind_%.eps'%(samples, blind))
    samples_str = '_'.join(samples)
    c[k].Print('Plots/%s_dataomc_blind_%s_%s.eps'%(samples_str, blind, k))
    if 'ma1' in k_ or 'pt1' in k_:
        pass
    #c[k].Print('Plots/%s_sb2srvsr_blind_%.eps'%(samples[0], blind))

def draw_hist_1dptstacked(k_, region, hist_list, c, samples, blind, ymax_=None, mcnorm=1., range_minmax=[0., 100.], title=''):

    h, hsample = hist_list

    print(h.keys())
    kdata = 'data'+region+k_
    assert kdata in h.keys()
    kmc = 'mc'+region+k_
    assert kmc in h.keys()

    hc = {}

    err_style = 'E2'
    fill_style = 3002
    #wd, ht = int(440*1), int(400*1)
    #wd, ht = int(640*1), int(580*1)
    wd, ht = int(640*1), int(680*1)
    #ROOT.TGaxis.fgMaxDigits = 3
    #ROOT.gStyle.SetErrorX(0)

    #k = 'sr_%s'%k_
    k = kdata
    #c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
    c[k+'stack'] = ROOT.TCanvas("c%s_stacked"%k,"c%s_stacked"%k,wd,ht)

    pUp = ROOT.TPad("upperPad", "upperPad",.005, .300, .995, .995) # (,,Double_t xlow, Double_t ylow, Double_t xup, Double_t yup,...)
    pDn = ROOT.TPad("lowerPad", "lowerPad",.005, .005, .995, .300)
    pUp.Draw()
    pDn.Draw()
    #pUp.SetMargin(14.e-02,3.e-02,5.e-03,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pUp.SetMargin(13.e-02,3.e-02,2.e-02,9.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pDn.SetMargin(13.e-02,3.e-02,36.e-02,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)

    pUp.cd()

    hdummy = h[k].Clone()
    hdummy.Reset()
    hdummy = set_hist(hdummy, title, "N_{a}", "")
    hdummy.GetXaxis().SetTitle('')
    hdummy.GetXaxis().SetLabelSize(0.)
    hdummy.GetYaxis().SetTitleOffset(0.9)
    hdummy.GetYaxis().SetTitleSize(0.07)
    hdummy.GetYaxis().SetLabelSize(0.06)
    hdummy.GetYaxis().SetMaxDigits(3)
    #hdummy.SetLineColor(0)
    hdummy.Draw("hist")

    hstack = ROOT.THStack("hs","hs")
    print(hsample.keys())
    for i,key in enumerate(hsample.keys()):
        if 'Run' in key: continue
        if k_ not in key: continue
        hsample[key].SetFillStyle(3002)
        hsample[key].SetFillColor(plot_color(key))
        hsample[key].SetLineColor(plot_color(key))
        #print(key, hsample[key].Integral(), norm)
        hsample[key].Scale(mcnorm)
        print(key, hsample[key].Integral())
        hstack.Add(hsample[key])
    hstack.Draw("hist same")

    #h[k], c[k] = set_hist(h[k], c[k], "m_{a,pred} [GeV]", "N_{a}", "")
    h[k] = set_hist(h[k], title, "N_{a}", "")
    hc[k] = h[k].Clone()
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

    # SB
    #k = 'sb2sr_%s'%k_
    k = kmc
    h[k].Scale(h[kdata].Integral()/h[kmc].Integral())
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

    #k = 'sr_%s'%k_
    k = kdata
    ymax = 1.2*max(h[kdata].GetMaximum(), h[kmc].GetMaximum())
    #ymax = 1.2*h[k].GetMaximum()
    if ymax_ == -1 and hc[k].GetBinContent(2) > 0.:
        #ymax = 1.2*hc[k].GetBinContent(2)
        ymax = 1.2*max(np.max([hc[kdata].GetBinContent(ib) for ib in range(2, hc[kdata].GetNbinsX()+2)]),
                       np.max([hc[kmc].GetBinContent(ib) for ib in range(2, hc[kmc].GetNbinsX()+2)]))
        #ymax = 1.2*np.max([hc[k].GetBinContent(ib) for ib in range(2, hc[k].GetNbinsX()+2)])
        #print(np.max([hc[k].GetBinContent(ib) for ib in range(2, hc[k].GetNbinsX()+2)]))
    #if ymax_ is not None and ymax_ > 0.:
    #    ymax = ymax_
    #hc[kdata].GetYaxis().SetRangeUser(0.1, ymax)
    #hc[kdata].GetXaxis().SetRangeUser(0., 100.)
    hdummy.GetYaxis().SetRangeUser(0.1, ymax)
    hdummy.GetXaxis().SetRangeUser(range_minmax[0], range_minmax[1])
    ROOT.gPad.RedrawAxis()

    #l, l2, hatch = {}, {}, {}
    #legend = {}

    #l[k] = ROOT.TLine(0.135, 0., 0.135, ymax) # x0,y0, x1,y1
    #l[k].SetLineColor(14)
    #l[k].SetLineStyle(7)
    #l[k].Draw("same")

    #l2[k] = ROOT.TLine(0.55, 0., 0.55, ymax) # x0,y0, x1,y1
    #l2[k].SetLineColor(14)
    #l2[k].SetLineStyle(7)
    #l2[k].Draw("same")

    #hatch[k] = ROOT.TGraph(2, array('d',[0.,0.]), array('d',[0.,ymax]));
    #hatch[k].SetLineColor(14)
    #hatch[k].SetLineWidth(5001)
    ##hatch[k].SetLineWidth(5)
    #hatch[k].SetFillStyle(3004)
    ##hatch[k].SetFillColor(14)
    #hatch[k].SetFillColor(12)
    ##ROOT.gStyle.SetHatchesLineWidth(2)
    #hatch[k].Draw("same")

    #legend[k] = ROOT.TLegend(0.5,0.68,0.8,0.86) #(x1, y1, x2, y2)
    #legend[k].AddEntry(hc[kdata].GetName(),"Obs","l")
    #legend[k].AddEntry(hc[kmc].GetName(),"Exp","l")
    #legend[k].SetBorderSize(0)
    #legend[k].Draw("same")

    ##### Ratio plots on lower pad #####
    pDn.cd()
    pDn.SetTicky()
    pDn.SetGridy()

    fUnity = ROOT.TF1("fUnity","[0]",range_minmax[0], range_minmax[1])
    fUnity.SetParameter( 0,1. )

    fUnity.GetXaxis().SetTitle(title)
    fUnity.GetXaxis().SetTickLength(0.1)
    fUnity.GetXaxis().SetTitleOffset(1.05)
    fUnity.GetXaxis().SetTitleSize(0.16)
    fUnity.GetXaxis().SetLabelSize(0.14)

    dY = 0.199
    dY = 0.399
    #fUnity.GetYaxis().SetTitle("SB/SR")
    fUnity.GetYaxis().SetTitle("Data/MC")
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

    #k = 'sb2srosr_%s'%k_
    kr = kdata+'ratio'
    h[kr] = h[k].Clone()
    h[kr].SetLineColor(9)
    h[kr].Sumw2()
    h[kr].SetStats(0)
    h[kr].Divide(h[kmc])
    h[kr].SetMarkerStyle(20)
    h[kr].SetMarkerSize(0.85)
    h[kr].SetMarkerColor(9)
    h[kr].Draw("ep same")

    #k = kr
    #l[k] = ROOT.TLine(0.135, 1.-dY, 0.135, 1.+dY) # x0,y0, x1,y1
    #l[k].SetLineColor(14)
    #l[k].SetLineStyle(7)
    #l[k].Draw("same")

    #l2[k] = ROOT.TLine(0.55, 1.-dY, 0.55, 1.+dY) # x0,y0, x1,y1
    #l2[k].SetLineColor(14)
    #l2[k].SetLineStyle(7)
    #l2[k].Draw("same")

    #hatch[k] = ROOT.TGraph(2, array('d',[0.,0.]), array('d',[1.-dY,1.+dY]));
    #hatch[k].SetLineColor(14)
    #hatch[k].SetLineWidth(5001)
    ##hatch[k].SetLineWidth(5)
    #hatch[k].SetFillStyle(3004)
    #hatch[k].SetFillColor(14)
    #hatch[k].Draw("same")
    ##h[k].SetLineColor(2)
    ##h[k].SetLineWidth(1)
    ##h[k].SetLineStyle(4)
    ##h[k].SetTitle("")

    #k = 'sr_%s'%k_
    #k = kdata
    k = kdata+'stack'
    c[k].Draw()
    c[k].Update()
    #c[k].Print('Plots/%s_sb2srvsr_blind_%s.eps'%(samples, blind))
    #c[k].Print('Plots/%s_sb2srvsr_blind_%.eps'%(samples, blind))
    samples_str = '_'.join(samples)
    c[k].Print('Plots/%s_dataomc_blind_%s_%s.eps'%(samples_str, blind, k))
    if 'ma1' in k_ or 'pt1' in k_:
        pass
    #c[k].Print('Plots/%s_sb2srvsr_blind_%.eps'%(samples[0], blind))

def draw_hist_1dmastacked(k_, region, hist_list, c, samples, blind, ymax_=None, mcnorm=1., range_minmax=[0., 100.], title=''):

    h, hsample = hist_list

    print(h.keys())
    kdata = 'data'+region+k_
    assert kdata in h.keys()
    kmc = 'mc'+region+k_
    assert kmc in h.keys()

    hc = {}

    err_style = 'E2'
    fill_style = 3002
    #wd, ht = int(440*1), int(400*1)
    #wd, ht = int(640*1), int(580*1)
    wd, ht = int(640*1), int(680*1)
    #ROOT.TGaxis.fgMaxDigits = 3
    #ROOT.gStyle.SetErrorX(0)

    #k = 'sr_%s'%k_
    k = kdata
    #c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
    c[k+'stack'] = ROOT.TCanvas("c%s_stacked"%k,"c%s_stacked"%k,wd,ht)

    pUp = ROOT.TPad("upperPad", "upperPad",.005, .300, .995, .995) # (,,Double_t xlow, Double_t ylow, Double_t xup, Double_t yup,...)
    pDn = ROOT.TPad("lowerPad", "lowerPad",.005, .005, .995, .300)
    pUp.Draw()
    pDn.Draw()
    #pUp.SetMargin(14.e-02,3.e-02,5.e-03,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pUp.SetMargin(13.e-02,3.e-02,2.e-02,9.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pDn.SetMargin(13.e-02,3.e-02,36.e-02,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)

    pUp.cd()

    hdummy = h[k].Clone()
    hdummy.Reset()
    hdummy = set_hist(hdummy, "m_{a,pred} [GeV]", "N_{a}", "")
    hdummy.GetXaxis().SetTitle('')
    hdummy.GetXaxis().SetLabelSize(0.)
    hdummy.GetYaxis().SetTitleOffset(0.9)
    hdummy.GetYaxis().SetTitleSize(0.07)
    hdummy.GetYaxis().SetLabelSize(0.06)
    hdummy.GetYaxis().SetMaxDigits(3)
    #hdummy.SetLineColor(0)
    hdummy.Draw("hist")

    hstack = ROOT.THStack("hs","hs")
    print(hsample.keys())
    for i,key in enumerate(hsample.keys()):
        if 'Run' in key: continue
        if k_ not in key: continue
        hsample[key].SetFillStyle(3002)
        hsample[key].SetFillColor(plot_color(key))
        hsample[key].SetLineColor(plot_color(key))
        #print(key, hsample[key].Integral(), norm)
        hsample[key].Scale(mcnorm)
        print(key, hsample[key].Integral())
        hstack.Add(hsample[key])
    hstack.Draw("hist same")

    #h[k], c[k] = set_hist(h[k], c[k], "m_{a,pred} [GeV]", "N_{a}", "")
    h[k] = set_hist(h[k], "m_{a,pred} [GeV]", "N_{a}", "")
    hc[k] = h[k].Clone()
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

    # SB
    #k = 'sb2sr_%s'%k_
    k = kmc
    h[k].Scale(h[kdata].Integral()/h[kmc].Integral())
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

    #k = 'sr_%s'%k_
    k = kdata
    #ymax = 1.2*max(h[kdata].GetMaximum(), h[kmc].GetMaximum())
    if ymax_ == -1 and hc[k].GetBinContent(2) > 0.:
        ymax = 1.2*max(np.max([hc[kdata].GetBinContent(ib) for ib in range(2, hc[kdata].GetNbinsX()+2)]),
                       np.max([hc[kmc].GetBinContent(ib) for ib in range(2, hc[kmc].GetNbinsX()+2)]))
    #hc[kdata].GetYaxis().SetRangeUser(0.1, ymax)
    #hc[kdata].GetXaxis().SetRangeUser(0., 100.)
    hdummy.GetYaxis().SetRangeUser(0.1, ymax)
    ROOT.gPad.RedrawAxis()

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
    #hatch[k].SetFillColor(14)
    hatch[k].SetFillColor(12)
    #ROOT.gStyle.SetHatchesLineWidth(2)
    hatch[k].Draw("same")

    #legend[k] = ROOT.TLegend(0.5,0.68,0.8,0.86) #(x1, y1, x2, y2)
    #legend[k].AddEntry(hc[kdata].GetName(),"Obs","l")
    #legend[k].AddEntry(hc[kmc].GetName(),"Exp","l")
    #legend[k].SetBorderSize(0)
    #legend[k].Draw("same")

    ##### Ratio plots on lower pad #####
    pDn.cd()
    pDn.SetTicky()
    pDn.SetGridy()

    fUnity = ROOT.TF1("fUnity","[0]",-0.4,1.2)
    fUnity.SetParameter( 0,1. )

    fUnity.GetXaxis().SetTitle("m_{a,pred} [GeV]")
    fUnity.GetXaxis().SetTickLength(0.1)
    fUnity.GetXaxis().SetTitleOffset(1.05)
    fUnity.GetXaxis().SetTitleSize(0.16)
    fUnity.GetXaxis().SetLabelSize(0.14)
    fUnity.GetXaxis().ChangeLabel(1,-1, 0,-1,-1,-1,"")
    fUnity.GetXaxis().ChangeLabel(2,-1,-1,-1,-1,-1,"#font[22]{#gamma_{veto}}")

    dY = 0.199
    dY = 0.399
    #fUnity.GetYaxis().SetTitle("SB/SR")
    fUnity.GetYaxis().SetTitle("Data/MC")
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

    #k = 'sb2srosr_%s'%k_
    kr = kdata+'ratio'
    h[kr] = h[k].Clone()
    h[kr].SetLineColor(9)
    h[kr].Sumw2()
    h[kr].SetStats(0)
    h[kr].Divide(h[kmc])
    h[kr].SetMarkerStyle(20)
    h[kr].SetMarkerSize(0.85)
    h[kr].SetMarkerColor(9)
    h[kr].Draw("ep same")

    k = kr
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

    #k = 'sr_%s'%k_
    #k = kdata
    k = kdata+'stack'
    c[k].Draw()
    c[k].Update()
    #c[k].Print('Plots/%s_sb2srvsr_blind_%s.eps'%(samples, blind))
    #c[k].Print('Plots/%s_sb2srvsr_blind_%.eps'%(samples, blind))
    samples_str = '_'.join(samples)
    c[k].Print('Plots/%s_dataomc_blind_%s_%s.eps'%(samples_str, blind, k))
    c[k].Print('Plots/%s_dataomc_blind_%s_%s.png'%(samples_str, blind, k))
    if 'ma1' in k_ or 'pt1' in k_:
        pass
    #c[k].Print('Plots/%s_sb2srvsr_blind_%.eps'%(samples[0], blind))

def draw_hist_2dma(k_, h, c, samples, blind, r, ymax_=None, do_trunc=True):

    hc = {}
    wd, ht = int(800*1), int(680*1)
    print(h.keys())

    k = 'mc'+'%s%s'%(r, k_)
    c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
    #h[k], c[k] = set_hist(h[k], c[k], "m_{a-lead,pred} [GeV]", "m_{a-sublead,pred} [GeV]", "m_{a_{1},pred} vs. m_{a_{0},pred}")
    h[k] = set_hist(h[k], "m_{a_{1},pred} [GeV]", "m_{a_{2},pred} [GeV]", "")
    ROOT.gPad.SetRightMargin(0.19)
    ROOT.gPad.SetLeftMargin(0.14)
    ROOT.gPad.SetTopMargin(0.05)
    ROOT.gPad.SetBottomMargin(0.14)
    ROOT.gStyle.SetPalette(55)#53
    h[k].GetYaxis().SetTitleOffset(1.)
    #h[k].GetZaxis().SetTitle("Events")
    h[k].GetZaxis().SetTitle("Events / 25 MeV")
    h[k].GetZaxis().SetTitleOffset(1.5)
    h[k].GetZaxis().SetTitleSize(0.05)
    h[k].GetZaxis().SetTitleFont(62)
    h[k].GetZaxis().SetLabelSize(0.04)
    h[k].GetZaxis().SetLabelFont(62)
    h[k].GetXaxis().SetTitleOffset(1.)
    h[k].GetXaxis().SetTitleSize(0.06)
    h[k].GetYaxis().SetTitleSize(0.06)

    if do_trunc:
        h[k].GetXaxis().SetRangeUser(0., 1.2)
        h[k].GetYaxis().SetRangeUser(0., 1.2)
    h[k].Draw("COL Z")
    #h[k].SetMaximum(350.)
    #h[k].SetMaximum(680.)
    #h[k].SetMaximum(175.)
    #h[k].SetMaximum(340.)
    c[k].Draw()
    palette = h[k].GetListOfFunctions().FindObject("palette")
    #palette.SetX1NDC(0.84)
    #palette.SetX2NDC(0.89)
    #palette.SetY1NDC(0.13)

    c[k].Update()
    samples_str = '_'.join(samples)
    c[k].Print('Plots/%s_2dma_blind_%s_%s%s.eps'%(samples_str, blind, k, '_ext' if not do_trunc else ''))

def plot_color(key):
    if 'QCD' in key:
        return 2 #red
    elif 'GJet' in key:
        return 4 #blue
    #elif 'DiPhoton' in key:
    elif 'DiPhoton' in key or 'DYToEE' in key:
        return 3 #green
    else:
        return 5 # yellow

def get_dataomc_norm(k_, region, h):

    kdata = 'data'+region+k_
    assert kdata in h.keys()
    kmc = 'mc'+region+k_
    assert kmc in h.keys()

    norm = h[kdata].Integral()/h[kmc].Integral()
    return norm

def get_sample_type(s):
    s = s.split('_')[0]
    if 'Run' in s:
        sample = re.search('(Run201[0-9])', s).group(1)
    else:
        sample = s
    #print(sample)
    return sample

def plot_datamc(samples, blind, norm, regions):

    assert len(samples) > 0
    samples = [s.replace('[','').replace(']','') for s in samples]

    sample_types = list(set([get_sample_type(s) for s in samples]))

    hf, h = {}, {}
    c = {}

    #keys = ['ptxy', 'maxy','mee','bdtxy']
    #keys = ['pt1', 'ma1','mee','bdt1']
    keys = ['pt1corr', 'elePt1corr', 'ma1', 'ma1phoEcorr', 'ma1eleEcorr' ,'mee', 'bdt1']
    #keys = ['ma1']

    for s in samples:
        for r in regions:
            print('sample: %s, region: %s'%(s, r))
            #hf[s+r] = ROOT.TFile("Templates/%s_templates.root"%(s),"READ")
            hf[s+r] = ROOT.TFile("Templates/%s_rewgt_templates.root"%(s),"READ")
            for k in keys:
                h[s+r+k] = hf[s+r].Get(k)
                h[s+r+k].Scale(norm[s])
                print('key: %s: GetEntries: %.f, Integral: %.f @ scale: %.2f'\
                    %(k, h[s+r+k].GetEntries(), h[s+r+k].Integral(), norm[s]))

    hsum = {}
    hsample = {}
    for k in keys:
        for r in regions:
            print('key: %s, region: %s'%(k, r))
            # Initialize
            for d in ['data', 'mc']:
                # Clone struct of histogram without copying its contents
                hsum[d+r+k] = h[samples[0]+r+k].Clone()
                hsum[d+r+k].Reset()
                print('Initializing hsum: %s'%(d+r+k))

            # Add up
            for s in samples:
                d = 'data' if 'Run' in s else 'mc'
                hsum[d+r+k].Add(h[s+r+k])
                print('For hsum[%s], adding %s -> Integral: %.f'%(d+r+k, s+r+k, hsum[d+r+k].Integral()))

    for k in keys:
        for r in regions:
            print('key: %s, region: %s'%(k, r))
            # Initialize
            for t in sample_types:
                hsample[t+r+k] = h[samples[0]+r+k].Clone()
                hsample[t+r+k].Reset()
                print('Initializing hsample: %s'%(t+r+k))
            for s in samples:
                t = get_sample_type(s)
                hsample[t+r+k].Add(h[s+r+k])
                print('For hsample[%s], adding %s -> Integral: %.f'%(t+r+k, s+r+k, hsample[t+r+k].Integral()))

            mcnorm = get_dataomc_norm(k, r, hsum)
            print('key %s: MC to Data norm: %.4f'%(k+r, mcnorm))

            #'''
            if 'pt' in k or 'Pt' in k:
                print('pt')
                #draw_hist_1dpt(k, r, hsum, c, samples, blind, -1)
                draw_hist_1dptstacked(k, r, [hsum, hsample], c, sample_types, blind, -1, mcnorm, [20., 100.], "p_{T,a} [GeV]")
            if 'ma' in k and 'v' not in k:
                print('max')
                #draw_hist_1dma(k, r, hsum, c, samples, blind, -1)
                draw_hist_1dmastacked(k, r, [hsum, hsample], c, sample_types, blind, -1, mcnorm, [-0.4, 1.2], "m_{a,pred} [GeV]")
            if 'mee' in k:
                print('mee')
                #draw_hist_1dmee(k, r, hsum, c, samples, blind, -1)
                draw_hist_1dptstacked(k, r, [hsum, hsample], c, sample_types, blind, -1, mcnorm, [60., 120.], "m_{#gamma,#gamma} [GeV]")
            if 'bdt' in k:
                print('bdt')
                draw_hist_1dptstacked(k, r, [hsum, hsample], c, sample_types, blind, None, mcnorm, [-1., 1.], "Photon ID")
            #if 'ma0vma1' in k:
            #    print('ma0vma1')
            #    draw_hist_2dma(k, hsum, c, samples, blind, r, do_trunc=True)
            #'''
