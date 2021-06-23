import ROOT
import numpy as np
from array import array
from hist_utils import *
import CMS_lumi

ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
#change the CMS_lumi variables (see CMS_lumi.py)
CMS_lumi.lumi_7TeV = "4.8 fb^{-1}"
CMS_lumi.lumi_8TeV = "18.3 fb^{-1}"
CMS_lumi.writeExtraText = 1
CMS_lumi.extraText = "Simulation"
#CMS_lumi.lumi_sqrtS = "41.9 fb^{-1} (13 TeV)" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
iPos = 11
if( iPos==0 ): CMS_lumi.relPosX = 0.12
iPeriod = 0

def draw_hist_1dma_ratio(ks, h, c, sample, blind, ymax_=None, blind_diag=True):

    hc = {}

    err_style = 'E2'
    fill_style = 3002
    wd, ht = int(640*1), int(680*1)
    #ROOT.TGaxis.fgMaxDigits = 3
    ROOT.gStyle.SetErrorX(0)

    sr_k = ks[0]
    print('num:',sr_k)
    sb2sr_k = ks[1]
    print('den:',sb2sr_k)
    srosb2sr_k = '%so%s'%(ks[0], ks[1])

    k = sr_k
    c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)

    pUp = ROOT.TPad("upperPad", "upperPad",.005, .300, .995, .995) # (,,Double_t xlow, Double_t ylow, Double_t xup, Double_t yup,...)
    pDn = ROOT.TPad("lowerPad", "lowerPad",.005, .005, .995, .300)
    pUp.Draw()
    pDn.Draw()
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

    k = sr_k
    #ymax = 1.2*max(h[k].GetMaximum(), h[sb2sr_k].GetMaximum())
    if ymax_ == -1 and hc[k].GetBinContent(2) > 0.:
        ymax = 1.2*max(np.max([hc[k].GetBinContent(ib) for ib in range(2, hc[k].GetNbinsX()+1)]),
                       np.max([hc[sb2sr_k].GetBinContent(ib) for ib in range(2, hc[sb2sr_k].GetNbinsX()+1)]))
    if ymax_ is not None and ymax_ > 0.:
        ymax = ymax_
    hc[k].GetYaxis().SetRangeUser(0.1, ymax)
    #hc[k].GetXaxis().SetRangeUser(0., 1.2)

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

    fUnity = ROOT.TF1("fUnity","[0]",-0.4,1.2)
    #fUnity = ROOT.TF1("fUnity","[0]",-0.,1.2)
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
        h[k].SetBinError(ib, get_cplimits_sym(obs, bkg, obs_err, bkg_err))

    h[k].SetName(k)
    h[k].SetLineColor(9)
    h[k].Sumw2()
    h[k].SetStats(0)

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

    k = sr_k
    c[k].Draw()
    c[k].Update()
    c[k].Print('Plots/%s_blind_%s_%so%.eps'%(sample, blind, ks[0], ks[1]))
    #c[k].Print('Plots/%s_blind_%s_%so%s.eps'%(sample, blind, ks[0], ks[1]))

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

def draw_hist_1dma_overlay(k_, h, hc, c, l, hatch, legend, it, ymax_=None):

    #hc = {}
    print('key:%s, it:%d'%(k_, it))

    err_style = 'E2'
    fill_style = 3002
    #wd, ht = int(440*1), int(400*1)
    #wd, ht = int(640*1), int(580*1)
    wd, ht = int(640*1), int(680*1)
    #ROOT.gStyle.SetErrorX(0)

    #k = 'sb_%s'%k_
    #k = 'sblo_'+k_
    #k = region+'_'+k_
    k = k_
    if it == 0:
        #c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
        c.SetLeftMargin(0.16)
        c.SetRightMargin(0.04)
        c.SetBottomMargin(0.14)
        c.SetTopMargin(0.06)
        ROOT.gStyle.SetOptStat(0)
    else:
        c.cd()

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

    h[k] = set_hist(h[k], "m_{a,pred} [GeV]", "f_{a} / 25 MeV", "")
    #h[k].GetXaxis().SetTitleOffset(0.9)
    #h[k].GetXaxis().SetTitleSize(0.06)
    #h[k].SetLineColor(9)
    #h[k].SetFillColor(9)
    h[k].SetLineColor(it+1)
    h[k].SetFillColor(it+1)
    h[k].SetFillStyle(fill_style)
    #h[k].Draw("hist")
    if it == 0:
        h[k].Draw("%s"%err_style)
    else:
        h[k].Draw("%s same"%err_style)
    hc[k] = h[k].Clone()
    hc[k].SetName(k+'line')
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

    if ymax_ is None:
        ymax = 1.2*h[k].GetMaximum()
    elif ymax_ == -1:
        ima_low = h[k].GetXaxis().FindBin(0.)
        ymax = 1.2*np.max([h[k].GetBinContent(ib) for ib in range(ima_low, h[k].GetNbinsX()+2)])
    else:
        ymax = ymax_
    #print('>> ymax: %f -> %f'%(h[k].GetMaximum(), ymax))
    #ymax = 4.2e3
    #ymax = 3.4e3

    if it == 0:
        pass
        print('>> ymax[%d]: %f'%(it, ymax))
        #hc[k].GetYaxis().SetRangeUser(0.1, ymax)
        #hc[k].GetXaxis().SetRangeUser(0., 1.2)
        h[k].GetYaxis().SetRangeUser(1.e-5 if normalize else 0.1, ymax)
        h[k].GetXaxis().SetRangeUser(0., 1.2)
        #hc[k].GetYaxis().SetRangeUser(0.1, ymax)

    if it == nit - 1:
        mass = float(k.split('_')[1].replace('p','.'))
        print('>> mass: %f'%mass)
        print('>> ymax[%d]: %f'%(it, ymax))
        #l[k] = ROOT.TLine(0.135, 0., 0.135, ymax) # x0,y0, x1,y1
        #l[k].SetLineColor(14)
        #l[k].SetLineStyle(7)
        #l[k].Draw("same")

        #l[k+'550'] = ROOT.TLine(0.55, 0., 0.55, ymax) # x0,y0, x1,y1
        #l[k+'550'].SetLineColor(14)
        #l[k+'550'].SetLineStyle(7)
        #l[k+'550'].Draw("same")

        l[k] = ROOT.TLine(mass, 0., mass, ymax) # x0,y0, x1,y1
        l[k].SetLineColor(14)
        l[k].SetLineStyle(7)
        l[k].Draw("same")

        hatch[k] = ROOT.TGraph(2, array('d',[0.,0.]), array('d',[0.,ymax]));
        hatch[k].SetLineColor(14)
        hatch[k].SetLineWidth(5001)
        #hatch[k].SetLineWidth(5)
        hatch[k].SetFillStyle(3004)
        hatch[k].SetFillColor(14)
        hatch[k].Draw("same")

    if it == 0:
        c.Draw()
        CMS_lumi.CMS_lumi(c, iPeriod, iPos)
    c.Update()
    if it == nit-1:

        #print(h.keys())
        legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.88) #(x1, y1, x2, y2)
        for r in runs:
            rmek = '%s_%s'%(r, '_'.join(k_.split('_')[1:]))
            legend.AddEntry(rmek, r, "lef")
        legend.SetBorderSize(0)
        legend.Draw("same")

        outfile = 'Plots/mAvRun_%s.pdf'%(k)
        #outfile = 'Plots/mAvEtaCut_%s_norm_%s.eps'%(k, normalize)
        c.Print(outfile)
        #c.Print('Plots/mA_%.eps'%(k))

#def plot_1dma_overlay():

l, hatch = {}, {}
legend = {}

hf, h, hc = {}, {}, {}
c = {}

eos_redir = 'root://cmseos.fnal.gov'
eos_basedir = '/store/user/lpchaa4g/mandrews/'#$ root -l 2017/maNtuples-Era03Dec2020v1/h4g2017-mA0p4GeV_mantuple.root
#campaign = 'Templates/templates-Era04Dec2020v1'
campaign = 'sg-Era04Dec2020v6/bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-nom/Templates/systNom_nom'
#expts = ['', '-eta1p4', '-eta1p3', '-eta1p2'] # eta study
expts = ['']

runs = ['2016', '2017', '2018']
#runs = ['2017'] # eta study
mas = []
mas.append('0p1')
#mas.append('0p2')
mas.append('0p4')
#mas.append('0p6')
#mas.append('0p8')
mas.append('1p0')
#mas.append('1p2') # eta study
keys = ['ma0','ma1']
#keys = ['maxy']

nit = len(runs)*len(expts)
#normalize = False
normalize = True
if normalize:
    #ymaxs = {'0p1':0.07, '0p4':0.09, '1p0':0.08,  '1p2':0.08}
    ymax_norm = 0.1
    ymaxs = {m:ymax_norm for m in mas}
else:
    ymaxs = {'0p1':6.e3, '0p4':8.e3, '1p0':1.2e3, '1p2':1.2e3}

# /eos/uscms/store/user/lpchaa4g/mandrews/2017/sg-Era04Dec2020v6/bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-nom/Templates/systNom_nom/
for r in runs:
    for m in mas:
        for e in expts:
            #filepath = "%s/%s/%d/%s%s/systNomNom/h4g%d-mA%sGeV_mantuple.root"%(eos_redir, eos_basedir, r, campaign, e, m)
            #filepath = "%s%s/systNom_nom/h4g%s-mA%sGeV_sr_blind_None_templates.root"%(campaign, e, r, m)
            filepath = "%s/%s/%s/%s/h4g%s%s-mA%sGeV_sr_blind_None_templates.root"%(eos_redir, eos_basedir, r, campaign, r, e, m)
            print('>> Opening: %s'%filepath)
            hf[r+m+e] = ROOT.TFile.Open(filepath)
            for k in keys:
                rmek = '%s_%s_%s_%s'%(r, m, e, k)
                h[rmek] = hf[r+m+e].Get(k)
                if normalize:
                    h[rmek].Scale(1./h[rmek].GetEntries())
                    h[rmek].SetName(rmek)
                    h[rmek].SetTitle(rmek)
                print('>> %s: maximum: %f'%(rmek, h[rmek].GetMaximum()))
                print('>> %s: GetEntries: %f, Integral: %f'%(rmek, h[rmek].GetEntries(), h[rmek].Integral()))

it = {}
wd, ht = int(640*1), int(680*1)
for k in keys:
    for m in mas:
        it[k+m] = 0
        c[k+m] = ROOT.TCanvas("c%s"%(k+m), "c%s"%(k+m), wd, ht)
        ymax_ = ymaxs[m]
        #ymax_ = -1
        for r in runs:
            for e in expts:
                rmek = '%s_%s_%s_%s'%(r, m, e, k)
                for ix in range(0, h[rmek].GetNbinsX()+2):
                    pass
                    #print('%d: %f'%(ix, h[rmek].GetBinContent(ix)))
                draw_hist_1dma_overlay(rmek, h, hc, c[k+m], l, hatch, legend, it[k+m], ymax_)
                it[k+m] += 1
        #c[k+m].Print('Plots/mA_%.eps'%(k))

#plot_1dma_overlay()

def plot_1dma_ratio(sample, blind, regions=None, sample_types=None):

    hf, h = {}, {}
    c = {}

    if regions is None:
        #regions = ['sb2sr', 'sr']
        regions = ['sblo']
        #regions = ['all']
        #regions = ['sbcombo2sr', 'sr']
    #keys = ['maxy','ma0','ma1']
    keys = ['maxy']

    for typ in sample_types:
        for r in regions:
            hf[r+typ] = ROOT.TFile("Templates/%s_%s_blind_%s_%s_templates.root"%(sample, r, blind, typ), "READ")
            for k in keys:
                rkt = '%s_%s_%s'%(r, k, typ)
                h[rkt] = hf[r+typ].Get(k)
                print('%s, Nentries: %.2f'%(rkt, h[rkt].GetEntries()))
                print('%s, Integral: %.2f'%(rkt, h[rkt].Integral()))

    for r in regions:
        for k in keys:
            ks = ['%s_%s_%s'%(r, k, typ) for typ in sample_types]
            print(ks)
            h[ks[0]].Scale(h[ks[1]].Integral()/h[ks[0]].Integral())
            draw_hist_1dma_ratio(ks, h, c, sample, blind, -1)

#plot_1dma_ratio(sample='GluGluHToGG', blind='sg', regions=['sr'], sample_types=['aod', 'miniaod'])
