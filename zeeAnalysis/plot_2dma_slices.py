import ROOT
import numpy as np
from array import array
from hist_utils_zee import *
#from plot_2dma import draw_hist_2dma

def draw_hist_1dma(h, c, ymax_=-1):

    print(h.keys())
    #kdata = 'data'+region+k_
    kdata = kslicehi
    assert kdata in h.keys()
    #kmc = 'mc'+region+k_
    kmc = kslicelo
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
    c[k].Print('Plots/Zee_ptlohi_%s.eps'%(k))

def draw_hist_2dma(k, h, c, sample, ymax_=None, ztitle='N_{e}'):

    hc = {}
    wd, ht = int(800*1), int(680*1)

    c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
    #h[k], c[k] = set_hist(h[k], c[k], "m_{a-lead,pred} [GeV]", "m_{a-sublead,pred} [GeV]", "m_{a_{1},pred} vs. m_{a_{0},pred}")
    h[k] = set_hist(h[k], "p_{T,e} [GeV]", "m_{a,pred} [GeV]", "")
    ROOT.gPad.SetRightMargin(0.19)
    ROOT.gPad.SetLeftMargin(0.14)
    ROOT.gPad.SetTopMargin(0.05)
    ROOT.gPad.SetBottomMargin(0.14)
    ROOT.gStyle.SetPalette(55)#53
    ROOT.gStyle.SetNumberContours(100)
    h[k].GetYaxis().SetTitleOffset(1.)
    #h[k].GetZaxis().SetTitle("Events")
    h[k].GetZaxis().SetTitle(ztitle)
    h[k].GetZaxis().SetTitleOffset(1.3)
    h[k].GetZaxis().SetTitleSize(0.05)
    h[k].GetZaxis().SetTitleFont(62)
    h[k].GetZaxis().SetLabelSize(0.04)
    h[k].GetZaxis().SetLabelFont(62)
    h[k].GetXaxis().SetTitleOffset(1.)
    h[k].GetXaxis().SetTitleSize(0.06)
    h[k].GetYaxis().SetTitleSize(0.06)
    h[k].GetYaxis().SetRangeUser(0., 1.2)
    #h[k].GetYaxis().ChangeLabel(1,-1, 0,-1,-1,-1,"")
    #h[k].GetYaxis().ChangeLabel(2,-1,-1,-1,-1,-1,"#font[22]{#gamma_{veto}}")
    h[k].GetZaxis().SetMaxDigits(3)
    ROOT.gPad.SetLogz()

    #h[k].GetXaxis().SetRangeUser(0., 1.2)
    #h[k].GetYaxis().SetRangeUser(0., 1.2)
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
    c[k].Print('Plots/Zee_%s_%s.eps'%(k, sample))
    #c[k].Print('Plots/%s_2dma_blind_%s_%s%s.eps'%(sample, blind, k, '_ext' if not do_trunc else ''))

samples = ['Run2017B-F']
sample_types = [s.split('_')[0] for s in samples]
eras = ['B', 'C', 'D', 'E', 'F']
samples = ['Run2017']

hf, h = {}, {}
c = {}

#keys = ['pt1corr', 'elePt1corr', 'ma1', 'ma1phoEcorr', 'ma1eleEcorr' ,'mee', 'bdt1']
#keys = ['ma1vpt1corr']
keys = ['ma1velePt1corr']

pt_bins_ = {}
dPt = 1
pt_bins_[0] = np.arange(20,90,dPt)
dPt = 5
pt_bins_[1] = np.arange(90,135,dPt)
dPt = 20
pt_bins_[2] = np.arange(135,175,dPt)
dPt = 500-175
pt_bins_[3] = np.arange(175,500+dPt,dPt)

pt_bins = np.concatenate([pt_bin_ for pt_bin_ in pt_bins_.values()])
n_pt_bins = len(pt_bins)-1

print(np.argwhere(pt_bins == 100.))
print(n_pt_bins)

offset = 5
#print(pt_bins[
for s in samples:

    for k in keys:

        for i,e in enumerate(eras):
            hf[e] = ROOT.TFile("Templates/%s%s_templates.root"%(s, e),"READ")
            h[k+e] = hf[e].Get(k)
            if i == 0:
                h[s+k] = h[k+e].Clone()
            else:
                h[s+k].Add(h[k+e])

        print(s+k,h[s+k].GetEntries(),h[s+k].Integral())

        draw_hist_2dma(s+k, h, c, sample='raw', ztitle='N_{e}')
        start_iy = 1
        for ix in range(1, h[s+k].GetNbinsX()+1):
            sumx = sum([h[s+k].GetBinContent(ix, iy) for iy in range(start_iy, h[s+k].GetNbinsY()+2)])
            if ix < 10: print(sumx)
            for iy in range(start_iy, h[s+k].GetNbinsY()+2):
                binc = h[s+k].GetBinContent(ix, iy)
                h[s+k].SetBinContent(ix, iy, binc/sumx)
        draw_hist_2dma(s+k, h, c, sample='normed', ztitle='N_{e}/N_{e}(p_{T})')

        pt = 100.
        ipt = h[s+k].GetXaxis().FindBin(pt)
        print(ipt)
        print(pt_bins[ipt-offset], pt_bins[ipt+offset+1])
        #kslice = s+k+'slice'+str(ipt)
        kslicelo = s+k+'slicelo'
        h[kslicelo] = h[s+k].ProjectionY(kslicelo, ipt-offset, ipt-1)
        #h[kslicelo] = h[s+k].ProjectionY(kslicelo, ipt-10, ipt-1)
        #h[kslicelo] = h[s+k].ProjectionY(kslicelo, 1, ipt-1)
        h[kslicelo].SetName(kslicelo)
        #draw_hist_1dma(kslicelo, c)
        print(h[kslicelo].GetEntries())

        kslicehi = s+k+'slicehi'
        #h[kslicehi] = h[s+k].ProjectionY(kslicehi, ipt, -1)
        h[kslicehi] = h[s+k].ProjectionY(kslicehi, ipt, ipt+offset+1)
        h[kslicehi].SetName(kslicehi)
        #draw_hist_1dma(kslicehi, c)
        #draw_hist_1dma([kslicelo, kslicehi], c)
        print(h[kslicehi].GetEntries())
        #draw_hist_1dma(h, c)

