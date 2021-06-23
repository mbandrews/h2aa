import ROOT
import numpy as np
from array import array
from hist_utils import *
#from plot_2dma import draw_hist_2dma

def draw_hist_1dma(k, c, ymax=None):

    hc = {}

    err_style = 'E2'
    fill_style = 3002
    wd, ht = int(640*1), int(680*1)

    c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
    #pUp.SetMargin(13.e-02,3.e-02,2.e-02,9.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)

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

    if ymax is None:
        ymax = 1.2*h[k].GetMaximum()
        print(ymax)
        if hc[k].GetBinContent(2) > 0.:
            ymax = 1.2*np.max([hc[k].GetBinContent(ib) for ib in range(2, hc[k].GetNbinsX()+2)])
            print(ymax)
    hc[k].GetYaxis().SetRangeUser(0.1, ymax)
    hc[k].GetXaxis().SetRangeUser(0., 1.2)

    c[k].Draw()
    c[k].Update()
    #c[k].Print('Plots/%k_curvefit.eps'%(k))
    return hc[k]

def plot_color(key):
    if 'QCD' in key:
        return 2 #red
    elif 'GJet' in key:
        return 4 #blue
    #elif 'DiPhoton' in key:
    elif 'DiPhoton' in key or 'DYToEE' in key:
        return 3 #green
    else:
        return 5 # yellow

def get_dataomc_norm(k_, region, h):

    kdata = 'data'+region+k_
    assert kdata in h.keys()
    kmc = 'mc'+region+k_
    assert kmc in h.keys()

    norm = h[kdata].Integral()/h[kmc].Integral()
    return norm

samples = ['Run2017B-F']
sample_types = [s.split('_')[0] for s in samples]

hf, h = {}, {}
c = {}

#keys = ['pt1corr', 'elePt1corr', 'ma1', 'ma1phoEcorr', 'ma1eleEcorr' ,'mee', 'bdt1']
keys = ['ma1']

for s in samples:
    hf[s] = ROOT.TFile("Templates/_%s_templates.root"%(s),"READ")
    for k in keys:
        h[s+k] = hf[s].Get(k)
        print(s+k,h[s+k].GetEntries(),h[s+k].Integral())
        #h[s+k].Scale(norm[s])
        #print(s+k,h[s+k].GetEntries(),h[s+k].Integral())

        draw_hist_1dma(s+k, c)

'''
k = 'pol2_2d'
pol2_2d = '[0] + [1]*x + [2]*y +[3]*x*y'
#pol2_2d = '[0] + [1]*x + [2]*y'
h[k] = ROOT.TF2(k, pol2_2d, -0.4, 1.2, -0.4, 1.2)

#h['ratio'].Fit(h[k], "IEMN")
#h['ratio'].Fit(h[k], "LIEMN")
fitResult = h['ratio'].Fit(h[k], "LIEMNS")
chi2 = h[k].GetChisquare()
ndof = h[k].GetNDF() - nDiag
print('chi2 / ndf: %f / %f = %f'%(chi2, ndof, chi2/ndof))
#cor = fitResult.GetCorrelationMatrix()
cov = fitResult.GetCovarianceMatrix()
#cor.Print()
cov.Print()
hint = h['ratio'].Clone()
hint.Reset()
hint.SetName('hint')
(ROOT.TVirtualFitter.GetFitter()).GetConfidenceIntervals(hint, 0.683)
'''
