import ROOT
import numpy as np
from array import array
from hist_utils import *
from get_bkg_norm import load_hists

def draw_hist_1dma(k_, h, c, sample, blind, ymax_=None):

    hc = {}

    err_style = 'E2'
    fill_style = 3002
    #wd, ht = int(440*1), int(400*1)
    #wd, ht = int(640*1), int(580*1)
    wd, ht = int(640*1), int(680*1)
    #ROOT.TGaxis.fgMaxDigits = 3
    ROOT.gStyle.SetErrorX(0)

    #k = 'sr_%s'%k_
    sr_k = sample+'sr'+k_
    sb2sr_k = sample+'sb2sr'+k_
    sb2srosr_k = sample+'sb2srosr'+k_

    k = sr_k
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
    #h[k] = set_hist(h[k], "m_{a,pred} [GeV]", "N_{a}", "")
    h[k] = set_hist(h[k], "m_{a,pred} [GeV]", "N_{a} / 25 MeV", "")
    #h[k].GetXaxis().SetTitleOffset(0.9)
    #h[k].GetXaxis().SetTitleSize(0.06)
    #h[k].SetLineColor(9)
    #h[k].Draw("hist")
    #h[k].SetFillColor(9)
    #h[k].SetFillStyle(fill_style)
    #h[k].Draw("%s"%err_style)
    hc[k] = h[k].Clone()

    # if blinding in SR, leave uncommented
    if blind == 'offdiag_lo_hi':
        hc[k].Reset()

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
    #k = 'sb2sr_%s'%k_
    k = sb2sr_k
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
    k = sr_k
    ymax = 1.2*max(h[k].GetMaximum(), h[sb2sr_k].GetMaximum())
    if ymax_ == -1 and hc[k].GetBinContent(2) > 0.:
        #ymax = 1.2*hc[k].GetBinContent(2)
        ymax = 1.2*max(np.max([hc[k].GetBinContent(ib) for ib in range(2, hc[k].GetNbinsX()+2)]),
                       np.max([hc[sb2sr_k].GetBinContent(ib) for ib in range(2, hc[sb2sr_k].GetNbinsX()+2)]))
        #ymax = 1.2*np.max([hc[k].GetBinContent(ib) for ib in range(2, hc[k].GetNbinsX()+2)])
        #print(np.max([hc[k].GetBinContent(ib) for ib in range(2, hc[k].GetNbinsX()+2)]))
    if ymax_ is not None and ymax_ > 0.:
        ymax = ymax_
    hc[k].GetYaxis().SetRangeUser(0.1, ymax)
    hc[k].GetXaxis().SetRangeUser(0., 1.2)

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

    #k = 'sb2srosr_%s'%k_
    k = sb2srosr_k
    h[k] = h[sb2sr_k].Clone()
    h[k].SetLineColor(9)
    h[k].Sumw2()
    h[k].SetStats(0)

    if blind == 'offdiag_lo_hi':
        # if blinding in SR, leave uncommented
        h[k].Divide(h[k])
    else:
        # if blinding in SR, leave commented
        h[k].Divide(h[sr_k])

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

    #k = 'sr_%s'%k_
    k = sr_k
    c[k].Draw()
    c[k].Update()
    #c[k].Print('Plots/%s_sb2srvsr_blind_%s.eps'%(sample, blind))
    #c[k].Print('Plots/%s_sb2srvsr_blind_%.eps'%(sample, blind))
    c[k].Print('Plots/%s_sb2srvsr_blind_%s_%s.eps'%(sample, blind, k))
    if 'ma1' in k_:
        pass
        #c[k].Print('Plots/%s_sb2srvsr_blind_%.eps'%(sample, blind))

def draw_hist_2dma(k_, h, c, sample, blind, r, ymax_=None, do_trunc=True):

    hc = {}
    wd, ht = int(800*1), int(680*1)

    sr_k = sample+'sr'+k_
    sb2sr_k = sample+'sb2sr'+k_

    #k = '%s_%s'%(r, k_)
    #k = 'sb2sr'+'_%s'%(k_)
    k = sb2sr_k
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
    c[k].Print('Plots/%s_sb2srvsr_blind_%s_%s.eps'%(sample, blind, k))

def draw_hist_2dma_ratio(k_, h, c, sample, blind, r, ymax_=None, do_trunc=True):

    hc = {}
    wd, ht = int(800*1), int(680*1)

    sr_k = sample+'sr'+k_
    sb2sr_k = sample+'sb2sr'+k_

    #k = '%s_%s'%(r, k_)
    #k = 'sb2sr'+'_%s'%(k_)
    k = sb2sr_k
    c[k] = ROOT.TCanvas("c%s_ratio"%k,"c%s_ratio"%k,wd,ht)
    #h[k], c[k] = set_hist(h[k], c[k], "m_{a-lead,pred} [GeV]", "m_{a-sublead,pred} [GeV]", "m_{a_{1},pred} vs. m_{a_{0},pred}")
    h[k] = set_hist(h[k], "m_{a_{1},pred} [GeV]", "m_{a_{2},pred} [GeV]", "")
    #h[k].Divide(h['sr_'+k_])
    h[k].Divide(h[sr_k])
    ROOT.gPad.SetRightMargin(0.19)
    ROOT.gPad.SetLeftMargin(0.14)
    ROOT.gPad.SetTopMargin(0.05)
    ROOT.gPad.SetBottomMargin(0.14)
    ROOT.gStyle.SetPalette(55)#53
    h[k].GetYaxis().SetTitleOffset(1.)
    #h[k].GetZaxis().SetTitle("Events")
    #h[k].GetZaxis().SetTitle("Events / 25 MeV")
    h[k].GetZaxis().SetTitle("(Bkg/Data) / 25 MeV")
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
    h[k].SetMaximum(2.)
    h[k].SetMinimum(0.)
    c[k].Draw()
    palette = h[k].GetListOfFunctions().FindObject("palette")
    #palette.SetX1NDC(0.84)
    #palette.SetX2NDC(0.89)
    #palette.SetY1NDC(0.13)

    c[k].Update()
    c[k].Print('Plots/%s_sb2srvsr_blind_%s_%s_ratio.eps'%(sample, blind, k))

def plot_srvsb_sb(sample, blind):

    hf, h = {}, {}
    c = {}

    #regions = ['sb2sr', 'sr']
    regions = ['sblo2sr', 'sbhi2sr', 'sr']
    #regions = ['sbcombo2sr', 'sr']
    #keys = ['ma0vma1', 'maxy']
    #keys = ['maxy']
    #keys = ['maxy','ma0','ma1']
    keys = ['maxy','ma0','ma1','ma0vma1']

    for r in regions:
        s_r = sample+r
        hf[s_r] = ROOT.TFile("Templates/%s_%s_blind_%s_templates.root"%(sample, r, blind),"READ")

    s_hgg = 'GluGluHToGG'
    r_hgg = 'sr'
    hf[s_hgg+r_hgg] = ROOT.TFile("Templates/%s_%s_blind_%s_templates.root"%(s_hgg, r_hgg, blind),"READ")
    for s_r in hf.keys():
        for k in keys:
            s_r_k = s_r+k
            h[s_r_k] = hf[s_r].Get(k)

    # h[data sr].Add(scale*sg)
    tgt_region = 'sb2sr'
    houtf = ROOT.TFile("Templates/%s_%s_blind_%s_templates.root"%(sample, tgt_region, blind), "RECREATE")
    for k in keys:
        s_r_k_tgt = sample+tgt_region+k
        #r_k_tgt = tgt_region+'_'+k
        #s_r_k_tgt = r_k_tgt
        h[s_r_k_tgt] = h[sample+'sblo2sr'+k].Clone()
        h[s_r_k_tgt].Add(h[sample+'sbhi2sr'+k])
        h[s_r_k_tgt].Add(h[s_hgg+r_hgg+k])
        h[s_r_k_tgt].Write()
    houtf.Write()
    #houtf.Close()

    #ma = '100MeV'
    #sgbr = 1.
    #k = keys[0]
    #load_hists(h, hf, ['h24gamma_1j_1M_%s'%ma], ['sr'], keys, blind, 'Templates')
    #print(h.keys())
    #for k in keys:
    #    s_sr_k = sample+'sr'+k
    #    print(h[s_sr_k].Integral())
    #    print(h['h24gamma_1j_1M_%s_sr_%s'%(ma, k)].Integral())
    #    h['h24gamma_1j_1M_%s_sr_%s'%(ma, k)].Scale(41.9e3*50.*sgbr/592275.)
    #    print(h['h24gamma_1j_1M_%s_sr_%s'%(ma, k)].Integral())
    #    h[s_sr_k].Add(h['h24gamma_1j_1M_%s_sr_%s'%(ma, k)])
    #    print(h[s_sr_k].Integral())

    #    s_r_k_tgt = sample+tgt_region+k
    #    h[s_r_k_tgt].Add(h['h24gamma_1j_1M_%s_sr_%s'%(ma, k)])

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
            draw_hist_1dma(k, h, c, sample, blind, -1)
            #draw_hist_1dma(k, h, c, sample, blind, 4.e3)
            #draw_hist_1dma(k, h, c, sample, blind)
        if k == 'ma0vma1':
            draw_hist_2dma(k, h, c, sample, blind, r, do_trunc=True)
            draw_hist_2dma_ratio(k, h, c, sample, blind, r, do_trunc=True)
        else:
            #draw_hist_1dma(k, h, c, sample, blind)
            draw_hist_1dma(k, h, c, sample, blind, -1)

