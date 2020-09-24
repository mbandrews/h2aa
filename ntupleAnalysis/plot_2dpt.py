import ROOT
from array import array
from hist_utils import *

def draw_hist_2dpt(k_, h, c, sample, blind, r, ymax_=None, do_trunc=True, zmax=None):

    hc = {}
    wd, ht = int(800*1), int(680*1)

    k = '%s_%s'%(r, k_) if r is not None else k_
    c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
    #h[k], c[k] = set_hist(h[k], c[k], "m_{a-lead,pred} [GeV]", "m_{a-sublead,pred} [GeV]", "m_{a_{1},pred} vs. m_{a_{0},pred}")
    h[k] = set_hist(h[k], "p_{T,a_{1},pred} [GeV]", "p_{T,a_{2},pred} [GeV]", "")
    ROOT.gPad.SetRightMargin(0.19)
    ROOT.gPad.SetLeftMargin(0.14)
    ROOT.gPad.SetTopMargin(0.05)
    ROOT.gPad.SetBottomMargin(0.14)
    ROOT.gStyle.SetPalette(55)#53
    h[k].GetYaxis().SetTitleOffset(1.)
    #h[k].GetZaxis().SetTitle("Events")
    #h[k].GetZaxis().SetTitle("Events / 25 MeV")
    h[k].GetZaxis().SetTitleOffset(1.5)
    h[k].GetZaxis().SetTitleSize(0.05)
    h[k].GetZaxis().SetTitleFont(62)
    h[k].GetZaxis().SetLabelSize(0.04)
    h[k].GetZaxis().SetLabelFont(62)
    h[k].GetXaxis().SetTitleOffset(1.)
    h[k].GetXaxis().SetTitleSize(0.06)
    h[k].GetYaxis().SetTitleSize(0.06)

    if do_trunc:
        h[k].GetXaxis().SetRangeUser(33., 160.)
        h[k].GetYaxis().SetRangeUser(25., 160.)
    #h[k].Draw("COL Z")
    h[k].Draw("COL")
    if zmax is not None:
        h[k].SetMaximum(zmax)
    #h[k].SetMaximum(680.)
    #h[k].SetMaximum(175.)
    #h[k].SetMaximum(340.)
    c[k].Draw()
    palette = h[k].GetListOfFunctions().FindObject("palette")
    #palette.SetX1NDC(0.84)
    #palette.SetX2NDC(0.89)
    #palette.SetY1NDC(0.13)

    c[k].Update()
    #c[k].Print('Plots/%s_2dpt_blind_%s_%s%s.eps'%(sample, blind, k, '_ext' if not do_trunc else ''))
    c[k].Print('Plots/%s_2dpt_blind_%s_%s%s.png'%(sample, blind, k, '_ext' if not do_trunc else ''))

#def plot_2dpt(sample, blind):

h = {}
c = {}

regions = ['sblo', 'sbhi', 'sr', 'sbcombo']
#regions = ['sblo2sr', 'sbhi2sr', 'sb2sr']
keys = ['pt0vpt1']
sample = 'Run2017B-F'
blind = None
indir = 'Weights'

# Run2017B-F_sb2sr_blind_None_ptwgts.root
hf = ROOT.TFile("%s/%s_sb2sr_blind_%s_ptwgts.root"%(indir, sample, blind),"READ")
for k in keys:
    for r in regions:
        rk = '%s_%s'%(r, k)
        h[rk] = hf.Get(sample+'_'+rk)
        draw_hist_2dpt(k, h, c, sample, blind, r, do_trunc=True)

    k_ = k+'_ratio'
    h[k_] = hf.Get(k_)
    draw_hist_2dpt(k_, h, c, sample, blind, r=None, do_trunc=True, zmax=10.)
