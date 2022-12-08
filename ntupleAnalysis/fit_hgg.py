import ROOT
import numpy as np
import os, glob, re

sel = 'nom'
sel = 'inv'
indir = '/eos/uscms/store/user/lpchaa4g/mandrews/2018/bkgPtWgts-Era22Jun2021v1/bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-%s/Run2/Templates_bkg'%sel
#hggonly/
#sbonly/
fname = 'data2018_sb2sr+hgg.root'
bkgname = 'data2018_sb2sr+hgg_ma0vma1-diag_lo_hi'
obsname = 'data2018_sr_ma0vma1-diag_lo_hi'

draw_plots = False
remove_negs = False

f, h = {}, {}
c = {}

expt = 'hgg'
f[expt] = ROOT.TFile.Open('%s/%sonly/%s'%(indir, expt, fname))
h[expt+'bkg'] = f[expt].Get(bkgname)
#h[expt+'obs'] = f[expt].Get(obsname)
print('%s: %f'%(expt+'bkg:', h[expt+'bkg'].Integral()))
#print('%s: %f'%(expt+'obs:', h[expt+'obs'].Integral()))
if remove_negs:
    # set negative bins to zero
    for ix in range(h[expt+'bkg'].GetNbinsX()+2):
        for iy in range(h[expt+'bkg'].GetNbinsX()+2):
            binc = h[expt+'bkg'].GetBinContent(ix, iy)
            if binc < 0:
                h[expt+'bkg'].SetBinContent(ix, iy, 0.)
if draw_plots:
    c[expt] = ROOT.TCanvas(expt, expt, 400, 400)
    h[expt+'bkg'].Draw('COLZ')
    c[expt].Draw()

expt = 'sb'
f[expt] = ROOT.TFile.Open('%s/%sonly/%s'%(indir, expt, fname))
h[expt+'bkg'] = f[expt].Get(bkgname)
h[expt+'obs'] = f[expt].Get(obsname)
print('%s: %f'%(expt+'bkg:', h[expt+'bkg'].Integral()))
print('%s: %f'%(expt+'obs:', h[expt+'obs'].Integral()))
if draw_plots:
    c[expt] = ROOT.TCanvas(expt, expt, 400, 400)
    h[expt+'bkg'].Draw('COLZ')
    c[expt].Draw()

#'''
mc = ROOT.TObjArray()
mc.Add(h['hggbkg'])
mc.Add(h['sbbkg'])
fit = ROOT.TFractionFitter(h['sbobs'], mc)
fit.Constrain(0, 0., 1.)
fit.Constrain(1, 0., 1.)
status = fit.Fit() # seg faults at deconstruction (not supported in PyROOT)
print('fit status:', int(status))
print('X^2 / ndf = %f / %d = %f'%(fit.GetChisquare(), fit.GetNDF(), fit.GetChisquare()/fit.GetNDF()))
cov = fit.GetCovarianceMatrix()
cov.Print()
#'''
