from __future__ import print_function
import ROOT
from array import array
from hist_utils import *

import CMS_lumi, tdrstyle

#tdrstyle.setTDRStyle()
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
#change the CMS_lumi variables (see CMS_lumi.py)
CMS_lumi.lumi_7TeV = "4.8 fb^{-1}"
CMS_lumi.lumi_8TeV = "18.3 fb^{-1}"
CMS_lumi.writeExtraText = 1
CMS_lumi.cmsTextOffset = 0.
#CMS_lumi.extraText = "Preliminary"
#CMS_lumi.lumi_sqrtS = "41.5 fb^{-1} (13 TeV)" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
CMS_lumi.lumi_sqrtS = "136 fb^{-1} (13 TeV)" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
#iPos = 11 # CMS in frame
iPos = 0 # CMS above frame
if( iPos==0 ): CMS_lumi.relPosX = 0.19
iPeriod = 0

def rebin2d(kratio, kratio_rebin):

    for ix in range(0, h[kratio].GetNbinsX()+2):
        ma_x = h[kratio].GetXaxis().GetBinCenter(ix)
        #ma_x = h[kratio].GetXaxis().GetBinLowEdge(ix)
        ix_rebin = h[kratio].GetXaxis().FindBin(ma_x)
        for iy in range(0, h[kratio].GetNbinsY()+2):
            ma_y = h[kratio].GetYaxis().GetBinCenter(iy)
            #ma_y = h[kratio].GetYaxis().GetBinLowEdge(iy)
            iy_rebin = h[kratio].GetYaxis().FindBin(ma_y)
            binc = h[kratio].GetBinContent(ix, iy)

            ixy_rebin = h[kratio].GetBin(ix_rebin, iy_rebin)
            h[kratio].AddBinContent(ixy_rebin, binc)
            #if ix == 2: print(iy, ma_y, iy_rebin, binc)

    #return hrebin.Clone()
    #return hrebin

def draw_hist_2dma(k_, h, c, sample, blind, ymax_=None, ymin_=None, do_trunc=True, label=None):

    hc = {}
    wd, ht = int(800*1), int(680*1)
    txtFont = 42

    k = k_
    c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
    h[k] = set_hist(h[k], "m_{#Gamma,1} [GeV]", "m_{#Gamma,2} [GeV]", "")
    ROOT.gPad.SetRightMargin(0.22)
    ROOT.gPad.SetLeftMargin(0.17)
    #ROOT.gPad.SetTopMargin(0.05) # no cms
    ROOT.gPad.SetTopMargin(0.085) # with cms
    ROOT.gPad.SetBottomMargin(0.17)
    ROOT.gStyle.SetPalette(55)#53
    #ROOT.TGaxis.fgMaxDigits = 1

    h[k].GetXaxis().SetTitleOffset(1.1)
    h[k].GetXaxis().SetLabelOffset(0.01)
    h[k].GetXaxis().SetTitleSize(0.07)
    h[k].GetXaxis().SetLabelSize(0.06)
    h[k].GetXaxis().SetLabelFont(txtFont)
    h[k].GetXaxis().SetTitleFont(txtFont)

    h[k].GetYaxis().SetTitleSize(0.07)
    h[k].GetYaxis().SetLabelSize(0.06)
    h[k].GetYaxis().SetTitleOffset(1.1)
    h[k].GetYaxis().SetLabelOffset(0.01)
    h[k].GetYaxis().SetLabelFont(txtFont)
    h[k].GetYaxis().SetTitleFont(txtFont)

    #h[k].GetZaxis().SetTitle("Events")
    #h[k].GetZaxis().SetTitle("Events / 25 MeV")
    if label is None:
        h[k].GetZaxis().SetTitle("Events / (%d MeV)^{2}"%dMa)
    else:
        h[k].GetZaxis().SetTitle("%s / (%d MeV)^{2}"%(label, dMa))
    h[k].GetZaxis().SetTitleOffset(1.1)
    h[k].GetZaxis().SetLabelOffset(0.01)
    h[k].GetZaxis().SetTitleSize(0.07)
    h[k].GetZaxis().SetTitleFont(txtFont)
    h[k].GetZaxis().SetLabelSize(0.06)
    h[k].GetZaxis().SetLabelFont(txtFont)
    h[k].GetZaxis().SetNdivisions(506)
    h[k].GetZaxis().SetMaxDigits(3) #doesnt seem to work on zaxis -> use newer version of ROOT (lcgdev4.sh)

    h[k].SetContour(100)

    if do_trunc:
        h[k].GetXaxis().SetRangeUser(0., 1.2)
        h[k].GetYaxis().SetRangeUser(0., 1.2)
    h[k].Draw("COL Z")
    #h[k].Draw("COL")

    #ymax_ = ...
    if ymax_ is not None:
        h[k].SetMaximum(ymax_)
    if ymin_ is not None:
        h[k].SetMinimum(ymin_)
    else:
        h[k].SetMinimum(0.)
    c[k].Draw()
    palette = h[k].GetListOfFunctions().FindObject("palette")
    palette.SetX1NDC(0.785)
    palette.SetX2NDC(0.785+0.05)
    palette.SetY2NDC(0.916)
    palette.SetY1NDC(0.17)

    CMS_lumi.CMS_lumi(c[k], iPeriod, iPos)

    c[k].Update()
    c[k].Print('Plots/2dma/%s_blind_%s_%s%s_sel-%s.pdf'%(sample, blind, k, '_ext' if not do_trunc else '', sel))

#def plot_2dma(sample, blind):

hf, h = {}, {}
c = {}


keys = ['ma0vma1']

run = 'Run2'
r_sb2sr, r_sr = 'sb2sr+hgg', 'sr'
valid_blind = 'diag_lo_hi'
limit_blind = 'offdiag_lo_hi'
indir = 'root://cmseos.fnal.gov//store/user/lpchaa4g/mandrews/%s'%run
sub_campaign = 'bdtgtm0p96_relChgIsolt0p07_etalt1p44' # bdt > -0.96, relChgIso < 0.07 !! optimal
k = keys[0]
dMa = 25
dMa = 50

# Bkg model
sample = 'data'
sel = 'nom'
#sel = 'inv'
#campaign = 'bkgPtWgts-Era04Dec2020v2/%s/nom-%s/Templates_bkg'%(sub_campaign, sel) # combined full Run2, 2016H+2018 failed lumis, run = 'Run2'
#campaign = 'bkgPtWgts-Era22Jun2021v1/%s/nom-%s/Templates_bkg'%(sub_campaign, sel) # combined full Run2, 2016H+2018 failed lumis, run = 'Run2'
#campaign = 'bkgPtWgts-Era22Jun2021v4/%s/nom-%s/Templates_bkg'%(sub_campaign, sel) # combined full Run2, mgg95, hgg template with SFs, fhgg from br(hgg)
campaign = 'bkgPtWgts-Era22Jun2021v2/%s/nom-%s/Templates_bkg'%(sub_campaign, sel) # bin 50MeV
#regions = [r_sb2sr, r_sr]
regions = [r_sr]
#blinds = [valid_blind, limit_blind]
blinds = [limit_blind]
blinds = [limit_blind, valid_blind]
#regions = [r_sb2sr]
do_blind = True if sel == 'nom' else False
if sel == 'inv':
    do_blind = False
do_blind = False
CMS_lumi.extraText = "Preliminary"

inpath = '%s/%s/%s_sb2sr+hgg.root'%(indir, campaign, sample)
print('>> Reading file:', inpath)
hf['nom'] = ROOT.TFile.Open(inpath, "READ")
maxzs = []
for r in regions:
    srk = '%s_%s_%s'%(sample, r, k)
    for b in blinds:
        srkb = '%s-%s'%(srk, b)
        print('srkb:',srkb)
        h[srkb] = hf['nom'].Get(srkb)
        h[srkb].SetName(srkb)
        if b == limit_blind:
            h[srk] = h[srkb].Clone()
            h[srk].SetName(srk)
        else:
            if not do_blind:
                h[srk].Add(h[srkb])
    maxzs.append(h[srk].GetMaximum())
    print('h[%s], max: %f'%(srk, h[srk].GetMaximum()))

'''
# Overwrite bkg plot with pol-optimized one from running `get_2dsyst+pol*.py`
hf['bkgxpol'] = ROOT.TFile.Open('Fits/bkgxpol.root', "READ")
# data_sb2sr_diag_lo_hi_ma0vma1_rebin
kbkg = '%s_%s_%s'%(sample, r_sb2sr, k)
srkb = 'data_sb2sr_%s_%s_rebin'%(valid_blind, k)
h[kbkg].Reset()
h[kbkg] = hf['bkgxpol'].Get(srkb)
#if not do_blind:
srkb = 'data_sb2sr_%s_%s_rebin'%(limit_blind, k)
h[kbkg].Add(hf['bkgxpol'].Get(srkb))
h[kbkg].SetName('data_sb2sr_%s'%k)
'''

for r in regions:
    srk = '%s_%s_%s'%(sample, r, k)
    draw_hist_2dma(srk, h, c, sample, limit_blind if do_blind and r == r_sr else None, ymax_=np.max(maxzs), do_trunc=True)
