from __future__ import print_function
from multiprocessing import Pool
import os, glob
import numpy as np
import subprocess
from get_bkg_norm import *
from plot_srvsb import plot_srvsb
from collections import OrderedDict

samples = [
    '100MeV'
    ,'400MeV'
    ,'1GeV'
    ]
samples = ['h24gamma_1j_1M_%s'%s for s in samples]
#samples = ['Run2017[B-F]']
samples.append('Run2017[B-F]')

output_dir = 'Datacards'
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

hf_in = {}
h_in = {}
h_out = OrderedDict()

def shiftNomUpDn(h_, hname):

    h = h_.Clone()

    print(hname)
    if 'Up' in hname:
        for ib in range(h.GetNbinsX()+2):
            binc = h.GetBinContent(ib)
            h.SetBinContent(ib, binc + np.sqrt(binc))
    elif 'Down' in hname:
        for ib in range(h.GetNbinsX()+2):
            binc = h.GetBinContent(ib)
            h.SetBinContent(ib, binc - np.sqrt(binc))
    #elif 'Nom' in hname:
    else:
        pass
        #binsum = 0
        #for ib in range(h.GetNbinsX()+2):
        #    print(h.GetBinContent(ib))
        #    binsum += h.GetBinContent(ib)
        #print(binsum)
        print(h.GetEntries())
        print(h.Integral())
    #else:
    #    print(hname)
    #    raise Exception('Unknown shift: %s'%hname)

    h.SetName(hname)
    return h

def flatten_th2(h):

    binc_flat = []
    binerr_flat = []
    #for ix in range(h.GetNbinsX()+2):
    #    for iy in range(h.GetNbinsY()+2):
    for ix in range(2, h.GetNbinsX()+1):
        for iy in range(2, h.GetNbinsY()+1):
            if abs(ix - iy) > int(200/25): continue # 200MeV blinding / 25MeV bin widths -> 8 bins
            #if ix != iy: continue
            #print(h.GetBin(ix, iy))
            binc_flat.append(h.GetBinContent(ix, iy))
            binerr_flat.append(h.GetBinError(ix, iy))
            if h.GetBinContent(ix, iy) > 0:
                pass
                #print(ix, iy, h.GetBinContent(ix, iy), h.GetBinError(ix, iy), h.GetBinError(ix, iy)/h.GetBinContent(ix, iy))

    return len(binc_flat), binc_flat, binerr_flat

def getBkgUncert2d_flat(h_in, sample):

    h_test, c = {}, {}
    k = s+'sb2sr'+'diag_lo_hi'
    #c[k] = ROOT.TCanvas('c'+k, 'c'+k, 500, 500)
    h_test[k] = h_in[k].Clone()

    j = s+'sr'+'diag_lo_hi'
    #c[j] = ROOT.TCanvas('c'+j, 'c'+j, 500, 500)
    h_test[j] = h_in[j].Clone()

    frac_diff_flat = []
    #for ix in range(h_test[k].GetNbinsX()+2):
    for ix in range(2, h_test[k].GetNbinsX()+1):
        sumY   = sum(h_test[k].GetBinContent(ix, iy_) for iy_ in range(h_test[k].GetNbinsY()+2))
        sumYsr = sum(h_test[j].GetBinContent(ix, iy_) for iy_ in range(h_test[j].GetNbinsY()+2))
        #print(ix, sumY)
        #for iy in range(h_test[k].GetNbinsY()+2):
        for iy in range(2, h_test[k].GetNbinsY()+1):
            pass
            if abs(ix - iy) > int(200/25): continue # 200MeV blinding / 25MeV bin widths -> 8 bins
            #if ix != iy: continue
            #print(h.GetBin(ix, iy))
            #h_test[k].GetBinContent(ix, iy)
            #binc = h_test[k].GetBinContent(ix, iy)
            #binc = 1e3
            #h_test[k].SetBinContent(ix, iy, binc)
            sumX   = sum(h_test[k].GetBinContent(ix_, iy) for ix_ in range(h_test[k].GetNbinsX()+2))
            sumXsr = sum(h_test[j].GetBinContent(ix_, iy) for ix_ in range(h_test[j].GetNbinsX()+2))
            #print(iy, sumX)
            #print(ix, iy, sumY, sumX)
            #print('ix:%d, iy:%d | (%.f, %.f) (%.f, %.f) -> (%.2f, %.2f)'%(ix, iy, sumY, sumX, sumYsr, sumXsr, sumY/sumYsr, sumX/sumXsr))
            #meanXY   = np.sqrt(sumY*sumY     + sumX*sumX)
            #meanXYsr = np.sqrt(sumYsr*sumYsr + sumXsr*sumXsr)
            #frac_diff = np.abs((meanXY/meanXYsr) - 1.)
            #frac_diff = np.abs((meanXYsr/meanXY) - 1.)
            #print('ix:%d, iy:%d | (%.f) (%.f) -> (%.2f)'%(ix, iy, meanXY, meanXYsr, meanXY/meanXYsr))
            #print('ix:%d, iy:%d | (%.f) (%.f) -> (%.2f) -> (%.2f)'%(ix, iy, meanXY, meanXYsr, meanXY/meanXYsr, frac_diff))
            #frac_diffX = np.abs((sumX/sumXsr)-1.)
            #frac_diffY = np.abs((sumY/sumYsr)-1.)
            frac_diffX = np.abs((sumXsr/sumX)-1.)
            frac_diffY = np.abs((sumYsr/sumY)-1.)
            frac_diffmean = np.sqrt(frac_diffX*frac_diffX + frac_diffY*frac_diffY)
            #print('ix:%d, iy:%d | (%.2f) (%.2f) -> (%.2f) vs. (%.2f)'%(ix, iy, frac_diffX, frac_diffY, frac_diffmean, frac_diff))
            #print('ix:%d, iy:%d | (%.2f) (%.2f) -> (%.2f)'%(ix, iy, frac_diffX, frac_diffY, frac_diffmean))
            frac_diff_flat.append(frac_diffmean)
        #break

    '''
    h_test[k].Draw('COL Z')
    c[k].Draw()
    c[k].Print('Plots/Datacard_2dtest_%s.eps'%k)
    kx = k+'x'
    c[kx] = ROOT.TCanvas('c'+kx, 'c'+kx, 500, 500)
    h_test[kx] = h_test[k].ProjectionX(kx)
    h_test[kx].Draw()
    c[kx].Draw()
    c[kx].Print('Plots/Datacard_2dtest_%s.eps'%kx)
    ky = k+'y'
    c[ky] = ROOT.TCanvas('c'+ky, 'c'+ky, 500, 500)
    h_test[ky] = h_test[k].ProjectionY(ky)
    h_test[ky].Draw()
    c[ky].Draw()
    c[ky].Print('Plots/Datacard_2dtest_%s.eps'%ky)
    '''
    return frac_diff_flat

def shiftNomUpDn_2d(h, hname, frac_diff=None):

    nbins, binc_flat, binerr_flat = flatten_th2(h.Clone())
    if frac_diff is not None:
        assert len(binc_flat) == len(frac_diff)

    h_flat = ROOT.TH1F(hname+'flat', hname+'flat', nbins+2, 0., nbins+2) # add 2 for under/over flow

    print(hname, h_flat.GetNbinsX())
    for i in range(len(binc_flat)):
        ib = i + 1
        #print(ib)
        if 'Up' in hname:
            #h_flat.SetBinContent(ib, binc_flat[i] + np.sqrt(binc_flat[i]))
            #diff = np.sqrt(binc_flat[i]) if frac_diff is None else binc_flat[i]*frac_diff[i]
            diff = binerr_flat[i] if frac_diff is None else binc_flat[i]*frac_diff[i]
            #print(frac_diff[i], binc_flat[i], diff)
            h_flat.SetBinContent(ib, np.maximum(0., binc_flat[i] + diff))
        elif 'Down' in hname:
            #h_flat.SetBinContent(ib, binc_flat[i] - np.sqrt(binc_flat[i]))
            #diff = np.sqrt(binc_flat[i]) if frac_diff is None else binc_flat[i]*frac_diff[i]
            diff = binerr_flat[i] if frac_diff is None else binc_flat[i]*frac_diff[i]
            h_flat.SetBinContent(ib, np.maximum(0., binc_flat[i] - diff))
        else:
            #h_flat.SetBinContent(ib, binc_flat[i])
            h_flat.SetBinContent(ib, np.maximum(0., binc_flat[i]))
        #else:
        #    print(hname)
        #    raise Exception('Unknown shift: %s'%hname)

    #print(h_flat.GetEntries())
    #print(h_flat.Integral())
    h_flat.SetName(hname)
    return h_flat

def get_hname(s, r):

    if 'h24gamma' in s:
        if 'MeV' in s:
            hname = '0p%sGeV'%s.split('_')[-1][0]
        else:
            hname = s.split('_')[-1]
        hname = 'h4g_%s'%hname
    elif 'Run2017' in s:
        if 'sb2sr' in r:
            hname = 'bkg'
        elif 'sr' in r:
            hname = 'data_obs'
        else:
            hname = None
    else:
        hname = None

    return hname

for s in samples:

    #key = 'ma1'
    #key = 'ma0'
    key = 'ma0vma1'
    #key = 'maxy'
    #r = 'sr'
    r = 'sb2sr' if 'Run2017' in s else 'sr'
    #blind = 'sg'
    #blind = None
    blind = 'offdiag_lo_hi'
    s = s.replace('[','').replace(']','')
    indir = 'Templates/_prod_varptbinsxy/a0noma1inv/nom'

    hf_in[s] = ROOT.TFile('%s/%s_%s_blind_%s_templates.root'%(indir, s, r, blind), "READ")
    h_in[s] = hf_in[s].Get(key)
    if 'h24' in s:
        #print(h_in[s].Integral())
        #scale = 1.e-3
        scale = 1.
        norm = get_sg_norm(s)*scale
        h_in[s].Scale(norm)

    hname = get_hname(s, r)
    h_out[hname] = h_in[s].Clone()
    h_out[hname].SetName(hname)

    for shift in ['Nom', 'Up', 'Down']:
        #hname_shift = '%s_alpha%s'%(hname, shift) if shift != 'Nom' else hname
        hname_shift = '%s_stat%s'%(hname, shift) if shift != 'Nom' else hname
        #print('shift: %s, hname: %s, hname_shift: %s'%(shift, hname, hname_shift))
        #h_out[hname_shift] = shiftNomUpDn(h_out[hname], hname_shift)
        #if 'h4g_1GeV' not in hname_shift: continue
        #if 'Down' not in hname_shift: continue
        h_out[hname_shift] = shiftNomUpDn_2d(h_in[s].Clone(), hname_shift) if key == 'ma0vma1' else shiftNomUpDn(h_in[s].Clone(), hname_shift)
        #print('storing in: %s'%hname_shift)

    if 'Run2017' in s:
        h_out['data_obs'] = h_out['bkg'].Clone()
        h_out['data_obs'].SetName('data_obs')

        # Bkg modeling
        for region in ['sb2sr', 'sr']:
            for b in ['diag_lo_hi', 'offdiag_lo_hi']:
                hf_in[s+region+b] = ROOT.TFile('%s/%s_%s_blind_%s_templates.root'%(indir, s, region, b), "READ")
                h_in[s+region+b] = hf_in[s+region+b].Get(key)

        #bkg_uncert_flat = getBkgUncert2d_flat(h_in, s)
        #for shift in ['Up', 'Down']:
        #    hname_shift = 'bkg_shape'+shift
        #    h_out[hname_shift] = shiftNomUpDn_2d(h_in[s].Clone(), hname_shift, bkg_uncert_flat)

#hf_out = ROOT.TFile('Datacards/%s_hists.root'%hname.split('_')[0], "RECREATE")
hf_out = ROOT.TFile('Datacards/%s_hists.root'%'shape', "RECREATE")
print(h_out.keys())
for hname in h_out.keys():
    #h_out[hname].SetName(hname)
    h_out[hname].Write()
hf_out.Close()

# combine -M AsymptoticLimits realistic-counting-experiment.txt
