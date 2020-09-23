import ROOT
from array import array
from hist_utils import *

import CMS_lumi, tdrstyle

#tdrstyle.setTDRStyle()
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
#change the CMS_lumi variables (see CMS_lumi.py)
CMS_lumi.writeExtraText = 1
CMS_lumi.extraText = "Simulation"
CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
iPos = 11
if( iPos==0 ): CMS_lumi.relPosX = 0.12
iPeriod = 0


def draw_hist_mGG(k_, h, c, sample, blind, r, ymax_=None, do_trunc=True, zmax=None):

    hc = {}
    #wd, ht = int(800*1), int(680*1)
    wd, ht = int(680*1.1), int(680*1)

    print(h.keys())

    overlay = False
    if type(sample) is str:
        k = '%s_%s'%(sample, k_)
    else:
        k = '%s_%s'%(sample[0], k_)
        overlay = True
    c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
    #h[k], c[k] = set_hist(h[k], c[k], "m_{a-lead,pred} [GeV]", "m_{a-sublead,pred} [GeV]", "m_{a_{1},pred} vs. m_{a_{0},pred}")
    h[k] = set_hist(h[k], "m_{#Gamma#Gamma} [GeV]", "a.u. / 250 MeV", "")
    ROOT.gPad.SetRightMargin(0.05)
    ROOT.gPad.SetLeftMargin(0.14)
    ROOT.gPad.SetTopMargin(0.05)
    ROOT.gPad.SetBottomMargin(0.13)
    ROOT.gStyle.SetPalette(55)#53
    h[k].GetYaxis().SetTitleOffset(1.1)
    h[k].GetXaxis().SetTitleOffset(0.95)
    h[k].GetXaxis().SetTitleSize(0.06)
    h[k].GetYaxis().SetTitleSize(0.06)

    h[k].GetXaxis().SetRangeUser(100., 150.)
    #h[k].GetYaxis().SetRangeUser(0., 1.2*h[k].GetMaximum())
    h[k].GetYaxis().SetRangeUser(0., 800.)

    #h[k].Draw("hist")
    h[k].SetLineColor(1)
    h[k].Draw("hist")
    hc[k] = h[k].Clone()
    hc[k].SetName(k+'_err')
    hc[k].SetFillColor(1)
    hc[k].SetFillStyle(3002)
    hc[k].Draw("E2 same")

    cols = [4, 2]
    if overlay:
        for i,ko_ in enumerate(sample[1:]):
            ko = '%s_%s'%(ko_, k_)
            h[ko].SetLineColor(cols[i])
            h[ko].Draw("hist same")
            hc[ko] = h[ko].Clone()
            hc[ko].SetName(ko+'_err')
            hc[ko].SetFillColor(cols[i])
            hc[ko].SetFillStyle(3002)
            hc[ko].Draw("E2 same")
    #if zmax is not None:
    #    h[k].SetMaximum(zmax)

    names = ['m(a) = 100 MeV', 'm(a) = 400 MeV', 'm(a) = 1 GeV']
    posY_ = 0.85
    posX_ = 0.90
    legend = ROOT.TLegend(posX_-0.30, posY_-0.16 , posX_, posY_) #(x1, y1, x2, y2)
    legend.AddEntry(hc[k].GetName(), names[0], "fl")
    for i,ko_ in enumerate(sample[1:]):
        ko = '%s_%s'%(ko_, k_)
        legend.AddEntry(hc[ko].GetName(), names[i+1], "fl")
    legend.SetBorderSize(0)
    legend.Draw("same")

    c[k].Draw()

    CMS_lumi.CMS_lumi(c[k], iPeriod, iPos)

    c[k].Update()
    c[k].Print('Plots/%s_mGG_blind_%s.eps'%('_'.join(sample), blind))

hf = {}
h = {}
c = {}

regions = ['all']
keys = ['mGG']
#sample = 'Run2017B-F'
samples = ['h24gamma_1j_1M_100MeV', 'h24gamma_1j_1M_400MeV', 'h24gamma_1j_1M_1GeV']
blind = None
indir = 'Templates'
r = regions[0]

norm = 1.e4

for s in samples:
    hf[s] = ROOT.TFile("%s/%s_all_blind_%s_templates.root"%(indir, s, blind),"READ")
    for k in keys:
        sk = '%s_%s'%(s, k)
        h[sk] = hf[s].Get(k)
        h[sk].Scale(norm/h[sk].Integral())
        #draw_hist_mGG(k, h, c, s, blind, r, do_trunc=True)

draw_hist_mGG(keys[0], h, c, samples, blind, r, do_trunc=True)
