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
iPos = 0
if( iPos==0 ): CMS_lumi.relPosX = 0.16
iPeriod = 0

#def draw_hist_1dma_overlay_ratio(ks, h, c, sample, blind, ymax_=None, blind_diag=True):
def draw_hist_1dma_overlay_ratio(k_, h, hc, c, l, hatch, legend, it, ymax_=None):

    print('key:%s, it:%d'%(k_, it))

    err_style = 'E2'
    fill_style = 3002
    wd, ht = int(640*1), int(680*1)
    #ROOT.gStyle.SetErrorX(0)

    k = k_
    if it == 0:
        #c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
        #c.SetLeftMargin(0.16)
        #c.SetRightMargin(0.04)
        #c.SetBottomMargin(0.14)
        #c.SetTopMargin(0.06)
        #pUp = ROOT.TPad("upperPad", "upperPad",.005, .300, .995, .995) # (,,Double_t xlow, Double_t ylow, Double_t xup, Double_t yup,...)
        #pDn = ROOT.TPad("lowerPad", "lowerPad",.005, .005, .995, .300)
        pUp.Draw()
        pDn.Draw()
        pUp.SetMargin(13.e-02,3.e-02,2.e-02,9.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
        pDn.SetMargin(13.e-02,3.e-02,36.e-02,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
        ROOT.gStyle.SetOptStat(0)
    else:
        c.cd()

    print('it:',it)
    pUp.cd()

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
    #h[k].SetLineColor(it+1)
    h[k].SetLineColor(3 if k == ksf else 1)
    #h[k].SetFillColor(it+1)
    #h[k].SetFillStyle(fill_style)
    #h[k].GetYaxis().SetTitleSize(0.06)
    #h[k].GetYaxis().SetLabelSize(0.04)
    #h[k].GetYaxis().SetMaxDigits(3)
    #h[k].GetXaxis().SetTitleSize(0.06)
    #h[k].GetXaxis().SetLabelSize(0.04)
    #h[k].GetXaxis().SetTitleOffset(1.)

    h[k].GetXaxis().SetTitle('')
    h[k].GetXaxis().SetLabelSize(0.)
    h[k].GetYaxis().SetTitleOffset(0.9)
    h[k].GetYaxis().SetTitleSize(0.07)
    #h[k].GetYaxis().SetLabelSize(0.06)
    h[k].GetYaxis().SetLabelSize(0.05)
    h[k].GetYaxis().SetMaxDigits(3)

    if it == 0:
        #h[k].SetFillColor(it+1)
        #h[k].SetFillStyle(fill_style)
        #h[k].Draw("%s"%err_style)
        h[k].Draw("hist e")
    else:
        h[k].Draw("hist e same")
    #hc[k] = h[k].Clone()
    #hc[k].SetName(k+'line')
    ##hc[k].SetLineColor(9)
    #hc[k].SetFillStyle(0)
    #hc[k].SetMarkerStyle(20)
    #hc[k].SetMarkerSize(0.85)
    #hc[k].Draw("hist same")

    if ymax_ is None:
        ymax = 1.2*h[k].GetMaximum()
    elif ymax_ == -1:
        ima_low = h[k].GetXaxis().FindBin(0.)
        ymax = 1.2*np.max([h[k].GetBinContent(ib) for ib in range(ima_low, h[k].GetNbinsX()+2)])
    else:
        ymax = ymax_

    if it == 0:
        pass
        print('>> ymax[%d]: %f'%(it, ymax))
        h[k].GetYaxis().SetRangeUser(1.e-5 if normalize else 0.1, ymax)
        h[k].GetXaxis().SetRangeUser(0., 1.2)

    if it == nit - 1:
        mass = float(k.split('_')[1].replace('p','.'))
        print('>> mass: %f'%mass)
        print('>> ymax[%d]: %f'%(it, ymax))

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

        legend = ROOT.TLegend(0.65, 0.75, 0.9, 0.88) #(x1, y1, x2, y2)
        legend.AddEntry(ksf, 'SF #pm syst', "le")
        legend.AddEntry(knosf, 'noSF #pm stat', "le")
        legend.SetBorderSize(0)
        legend.Draw("same")

    ##### Ratio plots on lower pad #####
    pDn.cd()
    pDn.SetTicky()
    pDn.SetGridy()
    dY = 0.099

    #if it == nit-1:
    if it == 0:

        #fUnity = ROOT.TF1("fUnity","[0]",-0.4,1.2)
        #fUnity = ROOT.TF1("fUnity","[0]",-0.,1.2)
        fUnity.SetParameter( 0,1. )

        fUnity.GetXaxis().SetTitle("m_{a,pred} [GeV]")
        fUnity.GetXaxis().SetTickLength(0.1)
        fUnity.GetXaxis().SetTitleOffset(1.05)
        fUnity.GetXaxis().SetTitleSize(0.16)
        fUnity.GetXaxis().SetLabelSize(0.14)

        #fUnity.GetYaxis().SetTitle("SB/SR")
        fUnity.GetYaxis().SetTitle("SF/noSF")
        #fUnity.GetYaxis().SetRangeUser(1.-dY,1.+dY)
        fUnity.GetXaxis().SetRangeUser(0., 1.2)
        fUnity.SetMaximum(1.+dY)
        fUnity.SetMinimum(1.-dY)
        fUnity.GetYaxis().SetNdivisions(305)
        fUnity.GetYaxis().SetTickLength(0.04)
        fUnity.GetYaxis().SetLabelFont(62)
        fUnity.GetYaxis().SetTitleFont(62)
        fUnity.GetYaxis().SetTitleOffset(.4)
        fUnity.GetYaxis().SetTitleSize(0.16)
        #fUnity.GetYaxis().SetLabelSize(0.14)
        fUnity.GetYaxis().SetLabelSize(0.12)

        fUnity.SetLineColor(9)
        fUnity.SetLineWidth(1)
        fUnity.SetLineStyle(7)
        fUnity.SetTitle("")
        fUnity.Draw()

    if it == nit-1:
        #pass
        #'''
        # noSF stat errors
        kr = 'nosf'+'staterrs'
        h[kr] = h[ksf].Clone()
        h[kr].Reset()
        h[kr].SetName(kr)
        for ib in range(1, h[kr].GetNbinsX()+1):
            bkg = h[knosf].GetBinContent(ib)
            if bkg == 0.: continue
            bkg_err = h[knosf].GetBinError(ib)
            h[kr].SetBinContent(ib, 1.)
            h[kr].SetBinError(ib, bkg_err/bkg)
            #if ib < 3: print(ib, bkg_err/bkg)
        h[kr].SetStats(0)
        h[kr].SetFillColor(1)
        h[kr].SetFillStyle(3002)
        h[kr].Draw("E2 same")

        # SF errors
        kr = 'sfonosf'+'errs'
        h[kr] = h[ksf].Clone()
        h[kr].Reset()
        h[kr].SetName(kr)
        for ib in range(1, h[kr].GetNbinsX()+1):
            obs = h[ksf].GetBinContent(ib)
            obs_err = h[ksf].GetBinError(ib)
            bkg = h[knosf].GetBinContent(ib)
            if bkg == 0.: continue
            bkg_err = h[knosf].GetBinError(ib)
            h[kr].SetBinContent(ib, obs/bkg)
            h[kr].SetBinError(ib, obs_err/obs)
            #if ib < 3: print(ib, obs/bkg)

        h[kr].SetStats(0)
        h[kr].SetLineColor(3)
        #h[kr].SetMarkerStyle(20)
        #h[kr].SetMarkerSize(0.85)
        #h[kr].SetMarkerColor(2)
        h[kr].Draw("hist e same")

        l[kr] = ROOT.TLine(mass, 1.-dY, mass, 1.+dY) # x0,y0, x1,y1
        l[kr].SetLineColor(14)
        l[kr].SetLineStyle(7)
        l[kr].Draw("same")
        #'''

    if it == 0:
        c.Draw()
        CMS_lumi.CMS_lumi(pUp, iPeriod, iPos)

    c.Update()

    if it == nit-1:
        outfile = 'Plots/1dma_trgs/mAvRun_%s.pdf'%(k)
        #outfile = 'Plots/mAvEtaCut_%s_norm_%s.eps'%(k, normalize)
        c.Print(outfile)

def draw_hist_1dma_overlay(k_, h, hc, c, l, hatch, legend, it, ymax_=None):

    print('key:%s, it:%d'%(k_, it))

    err_style = 'E2'
    fill_style = 3002
    wd, ht = int(640*1), int(680*1)
    #ROOT.gStyle.SetErrorX(0)

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
    h[k].SetLineColor(it+1)
    #h[k].SetFillColor(it+1)
    #h[k].SetFillStyle(fill_style)
    h[k].GetYaxis().SetTitleSize(0.06)
    h[k].GetYaxis().SetLabelSize(0.04)
    h[k].GetYaxis().SetMaxDigits(3)
    h[k].GetXaxis().SetTitleSize(0.06)
    h[k].GetXaxis().SetLabelSize(0.04)
    h[k].GetXaxis().SetTitleOffset(1.)
    if it == 0:
        #h[k].SetFillColor(it+1)
        #h[k].SetFillStyle(fill_style)
        #h[k].Draw("%s"%err_style)
        h[k].Draw("hist e")
    else:
        h[k].Draw("hist e same")
    #hc[k] = h[k].Clone()
    #hc[k].SetName(k+'line')
    ##hc[k].SetLineColor(9)
    #hc[k].SetFillStyle(0)
    #hc[k].SetMarkerStyle(20)
    #hc[k].SetMarkerSize(0.85)
    #hc[k].Draw("hist same")

    if ymax_ is None:
        ymax = 1.2*h[k].GetMaximum()
    elif ymax_ == -1:
        ima_low = h[k].GetXaxis().FindBin(0.)
        ymax = 1.2*np.max([h[k].GetBinContent(ib) for ib in range(ima_low, h[k].GetNbinsX()+2)])
    else:
        ymax = ymax_
    if it == 0:
        pass
        print('>> ymax[%d]: %f'%(it, ymax))
        h[k].GetYaxis().SetRangeUser(1.e-5 if normalize else 0.1, ymax)
        h[k].GetXaxis().SetRangeUser(0., 1.2)

    if it == nit - 1:
        mass = float(k.split('_')[1].replace('p','.'))
        print('>> mass: %f'%mass)
        print('>> ymax[%d]: %f'%(it, ymax))

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
        legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.88) #(x1, y1, x2, y2)
        for r in runs:
            rmek = '%s_%s'%(r, '_'.join(k_.split('_')[1:]))
            legend.AddEntry(rmek, r, "lef")
        legend.SetBorderSize(0)
        legend.Draw("same")

        outfile = 'Plots/mAvRun_%s.pdf'%(k)
        #outfile = 'Plots/mAvEtaCut_%s_norm_%s.eps'%(k, normalize)
        #c.Print(outfile)

l, hatch = {}, {}
legend = {}

hf, h, hc = {}, {}, {}
c = {}

eos_redir = 'root://cmseos.fnal.gov'
eos_basedir = '/store/user/lpchaa4g/mandrews/'#$ root -l 2017/maNtuples-Era03Dec2020v1/h4g2017-mA0p4GeV_mantuple.root
#campaign = 'Templates/templates-Era04Dec2020v1'
campaign = 'sg-Era04Dec2020v6/bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-nom/Templates/systNom_nom'
#expts = ['', '-eta1p4', '-eta1p3', '-eta1p2'] # eta study
expts = ['systNom_nom', 'systTrgSF_dn', 'systTrgSF_up', 'systNom_nom_noTrgSF']
#expts = ['systNom_nom', 'systNom_nom_noTrgSF']
#expts = ['systTrgSF_dn', 'systTrgSF_up']
#expts = ['systNom_nom_noTrgSF', 'systSmear_dn', 'systSmear_up']

runs = ['2016'] #
mas = []
#mas.append('0p0')
#mas.append('0p1')
#mas.append('0p2')
mas.append('0p4')
#mas.append('0p6')
#mas.append('0p8')
#mas.append('1p0')
#mas.append('1p2') # eta study
#keys = ['ma0','ma1']
keys = ['maxy']

nit = len(runs)*2
normalize = False
#normalize = True
if normalize:
    #ymaxs = {'0p1':0.07, '0p4':0.09, '1p0':0.08,  '1p2':0.08}
    ymax_norm = 0.1
    ymaxs = {m:ymax_norm for m in mas}
else:
    ymaxs = {'0p0':6.e3, '0p1':6.e3, '0p4':8.e3, '1p0':1.2e3, '1p2':1.2e3}

# /eos/uscms/store/user/lpchaa4g/mandrews/2017/sg-Era04Dec2020v6/bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-nom/Templates/systNom_nom/
for r in runs:
    for m in mas:
        for e in expts:
            #filepath = "%s/%s/%s/%s/h4g%s%s-mA%sGeV_sr_blind_None_templates.root"%(eos_redir, eos_basedir, r, campaign, r, e, m)
            if m == '0p0':
                filepath = "Templates/%s/bg%s-hgg_sr_blind_None_templates.root"%(e, r)
            else:
                filepath = "Templates/%s/h4g%s-mA%sGeV_sr_blind_None_templates.root"%(e, r, m)
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

print h.keys()

#'''
for k in keys:
    for m in mas:
        for r in runs:
            for e in expts:
                rmek = '%s_%s_%s_%s'%(r, m, e, k)
                #if e == expts[0]: print(h[rmek].GetName())
                if e != expts[0]: continue
                #print(h[rmek].GetName())
                for ix in range(0, h[rmek].GetNbinsX()+2):
                    kup = rmek.replace(e, expts[2])
                    #print(kup)
                    kdn = rmek.replace(e, expts[1])
                    #print(kdn)
                    binc_up = h[kup].GetBinContent(ix)
                    binc_dn = h[kdn].GetBinContent(ix)
                    binc = h[rmek].GetBinContent(ix)
                    binerr = h[rmek].GetBinError(ix)
                    #print(binc_dn, binc, binc_up, binc-binerr, binc+binerr, binc-binc_dn, binc_up-binc)
                    new_err = np.maximum([abs(binc-binc_dn)], [abs(binc_up-binc)])
                    h[rmek].SetBinError(ix, new_err)
                    #binerr = h[rmek].GetBinError(ix)
                    #print(binc_dn, binc, binc_up, binc-binerr, binc+binerr, binc-binc_dn, binc_up-binc)
                    #if ix > 3:
                    #    break
#'''

it = {}
wd, ht = int(640*1), int(680*1)
for k in keys:
    for m in mas:
        it[k+m] = 0
        c[k+m] = ROOT.TCanvas("c%s"%(k+m), "c%s"%(k+m), wd, ht)
        pUp = ROOT.TPad("upperPad", "upperPad",.005, .300, .995, .995) # (,,Double_t xlow, Double_t ylow, Double_t xup, Double_t yup,...)
        pDn = ROOT.TPad("lowerPad", "lowerPad",.005, .005, .995, .300)
        fUnity = ROOT.TF1("fUnity","[0]",-0.4,1.2)
        #pUp.Draw()
        #pDn.Draw()
        #pUp.SetMargin(13.e-02,3.e-02,2.e-02,9.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
        #pDn.SetMargin(13.e-02,3.e-02,36.e-02,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
        ymax_ = ymaxs[m]
        ymax_ = None
        if m == '0p0' or m == '0p1':
            ymax_ = -1
        for r in runs:
            for e in expts:
                if e == expts[1] or e == expts[2]: continue
                rmek = '%s_%s_%s_%s'%(r, m, e, k)
                print(rmek)
                if e == expts[0]:
                    ksf = rmek
                elif e == expts[-1]:
                    knosf = rmek
                #for ix in range(0, h[rmek].GetNbinsX()+2):
                #    pass
                #    #print('%d: %f'%(ix, h[rmek].GetBinContent(ix)))
                #draw_hist_1dma_overlay(rmek, h, hc, c[k+m], l, hatch, legend, it[k+m], ymax_)
                draw_hist_1dma_overlay_ratio(rmek, h, hc, c[k+m], l, hatch, legend, it[k+m], ymax_)
                it[k+m] += 1
        #c[k+m].Print('Plots/mA_%.eps'%(k))

#plot_1dma_overlay()
