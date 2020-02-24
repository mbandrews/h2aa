import ROOT
import numpy as np
from array import array
from hist_utils import *

def draw_hist_1dma(region, k_, h, c, sample, blind, ymax_=None):

    hc = {}

    err_style = 'E2'
    fill_style = 3002
    #wd, ht = int(440*1), int(400*1)
    #wd, ht = int(640*1), int(580*1)
    wd, ht = int(640*1), int(680*1)
    #ROOT.gStyle.SetErrorX(0)

    #k = 'sb_%s'%k_
    #k = 'sblo_'+k_
    k = region+'_'+k_
    c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)

    c[k].SetLeftMargin(0.16)
    c[k].SetRightMargin(0.04)
    c[k].SetBottomMargin(0.14)
    c[k].SetTopMargin(0.06)
    ROOT.gStyle.SetOptStat(0)

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

    h[k] = set_hist(h[k], "m_{a,pred} [GeV]", "N_{a} / 25 MeV", "")
    #h[k].GetXaxis().SetTitleOffset(0.9)
    #h[k].GetXaxis().SetTitleSize(0.06)
    h[k].SetLineColor(9)
    #h[k].Draw("hist")
    h[k].SetFillColor(9)
    h[k].SetFillStyle(fill_style)
    h[k].Draw("%s"%err_style)
    hc[k] = h[k].Clone()
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

    ymax = 1.2*h[k].GetMaximum()
    if ymax_ == -1 and h[k].GetBinContent(2) > 0.:
        ymax = 1.2*np.max([h[k].GetBinContent(ib) for ib in range(2, h[k].GetNbinsX()+2)])
    ymax = 4.2e3
    #ymax = 3.4e3

    #hc[k].GetYaxis().SetRangeUser(0.1, ymax)
    #hc[k].GetXaxis().SetRangeUser(0., 1.2)
    h[k].GetYaxis().SetRangeUser(0.1, ymax)
    h[k].GetXaxis().SetRangeUser(0., 1.2)

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

    c[k].Draw()
    c[k].Update()
    #c[k].Print('Plots/%s_sb2srvsr_blind_%s.eps'%(sample, blind))
    #c[k].Print('Plots/%s_sb2srvsr_blind_%.eps'%(sample, blind))
    c[k].Print('Plots/%s_sb_blind_%s_%s.eps'%(sample, blind, k))
    if 'ma1' in k_:
        pass
        #c[k].Print('Plots/%s_sb2srvsr_blind_%.eps'%(sample, blind))

def plot_1dma(sample, blind, regions=None):

    hf, h = {}, {}
    c = {}

    if regions is None:
        #regions = ['sb2sr', 'sr']
        regions = ['sblo']
        #regions = ['all']
        #regions = ['sbcombo2sr', 'sr']
    #keys = ['ma0vma1', 'maxy']
    #keys = ['maxy']
    keys = ['maxy','ma0','ma1']

    for r in regions:
        hf[r] = ROOT.TFile("Templates/%s_%s_blind_%s_templates.root"%(sample, r, blind),"READ")
        for k in keys:
            rk = '%s_%s'%(r, k)
            #if rk == 'sr_maxy': c[rk] = ROOT.TCanvas("c%s"%rk,"c%s"%rk, wd, ht)
            h[rk] = hf[r].Get(k)
            #h[rk].Draw("")

    for k in keys:
        pass
        #h['sb_%s'%k] = h['sblo2sr_%s'%k].Clone()
        #h['sb2sr_%s'%k].Add(h['sbhi2sr_%s'%k])

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
    for region in regions:
        for k in keys:
            if k == 'maxy':
                draw_hist_1dma(region, k, h, c, sample, blind, -1)
                #draw_hist_1dma(region, k, h, c, sample, blind, 4.e3)
                #draw_hist_1dma(region, k, h, c, sample, blind)
            else:
                #draw_hist_1dma(reion, k, h, c, sample, blind)
                draw_hist_1dma(region, k, h, c, sample, blind, -1)

#plot_1dma('Run2017B-F', 'notgjet')
