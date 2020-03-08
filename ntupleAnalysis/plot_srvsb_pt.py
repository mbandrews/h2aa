import ROOT
from array import array
from hist_utils import *

def draw_hist_1dma(k_, h, c, sample, blind, ymax_=None, sb='sb2sr'):

    hc = {}

    err_style = 'E2'
    fill_style = 3002
    #wd, ht = int(440*1), int(400*1)
    #wd, ht = int(640*1), int(580*1)
    wd, ht = int(640*1), int(680*1)
    #ROOT.TGaxis.fgMaxDigits = 3
    ROOT.gStyle.SetErrorX(0)

    k = 'sr_%s'%k_
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
    #h[k].GetXaxis().SetTitleOffset(0.9)
    #h[k].GetXaxis().SetTitleSize(0.06)
    #h[k].SetLineColor(9)
    #h[k].Draw("hist")
    #h[k].SetFillColor(9)
    #h[k].SetFillStyle(fill_style)
    #h[k].Draw("%s"%err_style)
    hc[k] = h[k].Clone()
    #hc[k].SetLineColor(9)
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
    k = sb+'_%s'%k_
    h[k].SetLineColor(9)
    #h[k].Draw("hist SAME")
    h[k].SetFillColor(9)
    h[k].SetFillStyle(fill_style)
    h[k].Draw("%s same"%err_style)
    hc[k] = h[k].Clone()
    hc[k].SetLineColor(9)
    hc[k].SetFillStyle(0)
    hc[k].Draw("hist same")

    k = 'sr_%s'%k_
    ymax = 1.2*max(h[k].GetMaximum(), h[sb+'_%s'%k_].GetMaximum())
    if ymax_ == -1 and hc[k].GetBinContent(2) > 0.:
        ymax = 1.2*hc[k].GetBinContent(2)
    if ymax_ is not None and ymax_ > 0.:
        ymax = ymax_
    hc[k].GetYaxis().SetRangeUser(0.1, ymax)
    hc[k].GetXaxis().SetRangeUser(0., 100.)

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
    #legend[k].AddEntry(hc[sb+'_maxy'].GetName(),"Exp","l")
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
    fUnity.GetYaxis().SetTitle("SB/SR")
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

    k = sb+'osr_%s'%k_
    h[k] = h[sb+'_%s'%k_].Clone()
    h[k].SetLineColor(9)
    h[k].Sumw2()
    h[k].SetStats(0)
    h[k].Divide(h['sr_%s'%k_])
    h[k].SetMarkerStyle(20)
    h[k].SetMarkerSize(0.85)
    h[k].SetMarkerColor(9)
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

    k = 'sr_%s'%k_
    c[k].Draw()
    c[k].Update()
    #c[k].Print('Plots/%s_sb2srvsr_blind_%s.eps'%(sample, blind))
    #c[k].Print('Plots/%s_sb2srvsr_blind_%.eps'%(sample, blind))
    if 'pt1' in k_:
        pass
        c[k].Print('Plots/%s_sb2srvsr_blind_%.eps'%(sample, blind))
    #c[k].Print('Plots/%s_sb2srvsr_blind_%s_%s.eps'%(sample, blind, k))

def plot_srvsb_pt(sample, blind, sb='sb2sr'):

    hf, h = {}, {}
    c = {}

    regions = [sb, 'sr']
    #regions = ['sbcombo2sr', 'sr']
    regions = ['sblo2sr', 'sbhi2sr', 'sr']
    #keys = ['ma0vma1', 'maxy']
    #keys = ['maxy']
    keys = ['pt0','pt1']

    for r in regions:
        hf[r] = ROOT.TFile("Templates/%s_%s_blind_%s_templates.root"%(sample, r, blind),"READ")
        for k in keys:
            rk = '%s_%s'%(r, k)
            #if rk == 'sr_maxy': c[rk] = ROOT.TCanvas("c%s"%rk,"c%s"%rk, wd, ht)
            h[rk] = hf[r].Get(k)
            #h[rk].Draw("")

    #regions = ['sb2sr', 'sr']

    for k in keys:
        h['sb2sr_%s'%k] = h['sblo2sr_%s'%k].Clone()
        h['sb2sr_%s'%k].Add(h['sbhi2sr_%s'%k])

    '''
    r = 'sb2sr'
    for k in keys:
        if k != 'maxy': continue
        rk = '%s_%s'%(r, k)
        h['sr_%s'%k].SetLineColor(9)
        h['sr_%s'%k].Draw("hist")
        h[rk].SetLineColor(2)
        h[rk].Draw("hist same")
    '''
    # plot ratio
    # derive 1sigma uncert vs ma

    #k = 'maxy'
    for k in keys:
        if k == 'maxy':
            draw_hist_1dma(k, h, c, sample, blind, -1, sb=sb)
            #draw_hist_1dma(k, h, c, sample, blind, 4.e3)
            #draw_hist_1dma(k, h, c, sample, blind)
        else:
            draw_hist_1dma(k, h, c, sample, blind, sb=sb)

