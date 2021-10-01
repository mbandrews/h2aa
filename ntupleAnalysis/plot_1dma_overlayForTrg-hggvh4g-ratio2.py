import ROOT
import numpy as np
from array import array
from hist_utils import *
from get_fracuncert import get_cplimits_sym
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

esf = 'systNom_nom'
enosf = 'systNom_nom_noTrgSF'
#expts = ['systNom_nom', 'systNom_nom_noTrgSF']
expts = [esf, enosf]

runs = ['h4g', 'hgg'] #
era = '2016'
mas = []
#mas.append('0p0')
mas.append('0p1')
#mas.append('0p4')
#mas.append('1p0')
k = 'maxy'

#mAvRun_hgg_1p0_systNom_nom_noTrgSF_maxyoh4g_1p0_systNom_nom_noTrgSF_maxy.txt
khgg, kh4g, infile, f, lines = {}, {}, {}, {}, {}
for m in mas:
    for e in expts:
        lines[m+e] = []
        khgg[m+e] = 'hgg_%s_%s_%s'%(m, e, k)
        kh4g[m+e] = 'h4g_%s_%s_%s'%(m, e, k)
        infile[m+e] = 'Plots/1dma_trgs/mAvRun_%so%s.txt'%(khgg[m+e], kh4g[m+e])
        f[m+e] = open(infile[m+e])
        for i,l in enumerate(f[m+e].readlines()):
            #print(l.replace('\n',''))
            if i == 0: continue # neg mass bin
            line = l.replace('\n','').split(' ')
            line = [float(v) for v in line]
            lines[m+e].append(line)
        f[m+e].close()
        #print(len(vals[m+e]))
        #break

ratios, uncerts = {}, {}
for m in mas:
    mesf = m+esf
    menosf = m+enosf
    assert len(lines[mesf]) == len(lines[menosf])
    ratios[m] = []
    uncerts[m] = []
    for i in range(len(lines[mesf])):
        #print(lines[mesf][i][1], lines[menosf][i][1])
        ratios[m].append(lines[mesf][i][1]/lines[menosf][i][1])

        err = get_cplimits_sym(lines[mesf][i][1], lines[menosf][i][1], lines[mesf][i][2], lines[menosf][i][2])#num, den, numerr, denerr
        uncerts[m].append(err)
        #if i > 3: break
    print(m, len(ratios[m]))

err_style = 'E2'
fill_style = 3002
#wd, ht = int(640*1), int(680*1)
wd, ht = int(640*1), int(200*1)
#ROOT.gStyle.SetErrorX(0)

#'''
dY = 0.099
h, c = {}, {}
for m in mas:

    c[m] = ROOT.TCanvas("c%s"%m,"c%s"%m,wd,ht)
    c[m].SetTicky()
    c[m].SetGridy()

    fUnity = ROOT.TF1("fUnity","[0]",0.,1.2)
    fUnity.SetParameter( 0,1. )

    fUnity.GetXaxis().SetTitle("m_{a,pred} [GeV]")
    fUnity.GetXaxis().SetTickLength(0.1)
    fUnity.GetXaxis().SetTitleOffset(1.05)
    fUnity.GetXaxis().SetTitleSize(0.16)
    fUnity.GetXaxis().SetLabelSize(0.14)

    fUnity.GetYaxis().SetTitle("SF/noSF(H#rightarrow#gamma#gamma/4#gamma)")
    fUnity.GetXaxis().SetRangeUser(0., 1.2)
    fUnity.SetMaximum(1.+dY)
    fUnity.SetMinimum(1.-dY)
    fUnity.GetYaxis().SetNdivisions(305)
    fUnity.GetYaxis().SetTickLength(0.04)
    fUnity.GetYaxis().SetLabelFont(62)
    fUnity.GetYaxis().SetTitleFont(62)
    fUnity.GetYaxis().SetTitleOffset(.4)
    fUnity.GetYaxis().SetTitleSize(0.16)
    fUnity.GetYaxis().SetLabelSize(0.12)

    fUnity.SetLineColor(9)
    fUnity.SetLineWidth(1)
    fUnity.SetLineStyle(7)
    fUnity.SetTitle("")
    fUnity.Draw()

    h[m] = ROOT.TH1F('h'+m, 'h'+m, len(ratios[m]), 0., 1.2)
    for ib in range(1, h[m].GetNbinsX()+1):
        h[m].SetBinContent(ib, ratios[m][ib-1])
        h[m].SetBinError(ib, uncerts[m][ib-1])
        #if ib < 3: print(ib, ratios[m][ib])
        print(ib, ratios[m][ib-1])
    h[m].SetStats(0)
    h[m].SetLineColor(2)
    h[m].Draw("hist e same")

    c[m].Draw()
    outfile = 'Plots/1dma_trgs/sfonosf_%s.pdf'%(m)
    #outfile = 'Plots/mAvEtaCut_%s_norm_%s.eps'%(k, normalize)
    #c[m].Print(outfile)
#'''
