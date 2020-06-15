from __future__ import print_function
import ROOT
import numpy as np
from array import array
from hist_utils import *
from get_bkg_norm import *

wd, ht = int(800*1), int(680*1)
wd_wide = 1400

#do_blind = True
do_blind = False

def var_params(params, varvec, side):

    if side == 'up':
        var_params = params + varvec
    elif side == 'dn':
        var_params = params - varvec
    else:
        raise Exception('Not a valid variation direction (up or dn): %s'%side)

    return var_params

'''
def get_cplimits_sym(num, den, num_err, den_err):

        # Clopper-Pearson errors
        # tail = (1 - cl) / 2
        # 2sigma (95% CL): tail = (1 - 0.95) / 2 = 0.025
        # 1sigma (68% CL): tail = (1 - 0.68) / 2 = 0.16
        tail = 0.16
        n_num = pow(num/num_err, 2.)
        n_den = pow(den/den_err, 2.)

        # nom
        n_rat = n_num / n_den

        # lower limit
        q_low = ROOT.Math.fdistribution_quantile_c(1 - tail, n_num * 2,
                (n_den + 1) * 2)
        r_low = q_low * n_num / (n_den + 1)

        # upper limit
        q_high = ROOT.Math.fdistribution_quantile_c(tail, (n_num + 1) * 2,
                n_den * 2)
        r_high = q_high * (n_num + 1) / n_den

        # lower, upper errors
        err_lo, err_hi = n_rat - r_low, r_high - n_rat

        #return err_lo, err_hi
        #err_ = np.sqrt(np.mean(np.array([err_lo, err_hi])**2))
        err_ = err_lo if num/den > 1. else err_hi
        return err_

'''
def isnot_sg(ix, iy):
    #if abs(ix - iy) > int(200/25): # 200MeV blinding / 25MeV bin widths -> 8 bins
    #if abs(ix - iy) > int(200/25) or (ix <= 1) or (iy <= 1): # 200MeV blinding / 25MeV bin widths -> 8 bins
    #if abs(ix - iy) >= int(200/50) or (ix <= 1) or (iy <= 1): # 200MeV blinding / 50MeV bin widths
    if abs(ix - iy) >= int(200/dMa) or (ix <= 1) or (iy <= 1): # 200MeV blinding / 50MeV bin widths
        return True
    else:
        return False

def plot_1dma(k, title='', yrange=[0., 600.], new_canvas=True, color=1, titles=["im_{x}#timesim_{y} + im_{y}", "N_{evts}"]):

    xtitle, ytitle = titles
    kc = k
    if new_canvas:
        #c[k] = ROOT.TCanvas("c%s"%k, "c%s"%k, wd_wide, ht)
        c[kc] = ROOT.TCanvas(kc, kc, wd_wide, ht)
        ROOT.gStyle.SetOptStat(0)
        ROOT.gPad.SetRightMargin(0.02)
        ROOT.gPad.SetLeftMargin(0.1)
        ROOT.gPad.SetTopMargin(0.05)
        ROOT.gPad.SetBottomMargin(0.14)
        h[k].SetTitle("")
        h[k].GetXaxis().SetTitle(xtitle)
        h[k].GetYaxis().SetTitle(ytitle)
        h[k].GetYaxis().SetTitleOffset(0.7)
        h[k].GetXaxis().SetTitleOffset(1.)
        h[k].GetXaxis().SetTitleSize(0.06)
        h[k].GetYaxis().SetTitleSize(0.06)
        h[k].GetXaxis().SetLabelFont(62)
        h[k].GetXaxis().SetTitleFont(62)
        h[k].GetYaxis().SetLabelFont(62)
        h[k].GetYaxis().SetTitleFont(62)

    h[k].SetLineColor(color)
    if yrange is not None:
        h[k].GetYaxis().SetRangeUser(yrange[0], yrange[1])

    c[kc].cd()
    if new_canvas:
        #h[k].SetMarkerStyle(20)
        #h[k].SetMarkerSize(0.85)
        #h[k].Draw("Ep same")
        h[k].Draw("hist E same")
        #h[k].Draw("hist")
        c[kc].Draw()
    else:
        h[k].Draw("hist same")
        c[kc].Update()
    c[kc].Print('Plots/Sys2D_%s.eps'%k)


def plot_2dma(k, title, xtitle, ytitle, ztitle, zrange=None, do_trunc=False, do_log=False):

    assert k in h.keys()
    print(h[k].GetMinimum(), h[k].GetMaximum(), h[k].Integral())

    c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
    if do_log: c[k].SetLogz()
    ROOT.gStyle.SetOptStat(0)
    ROOT.gPad.SetRightMargin(0.19)
    ROOT.gPad.SetLeftMargin(0.14)
    ROOT.gPad.SetTopMargin(0.05)
    ROOT.gPad.SetBottomMargin(0.14)
    ROOT.gStyle.SetPalette(55)#53
    h[k].SetTitle("")
    h[k].GetXaxis().SetTitle(xtitle)
    h[k].GetYaxis().SetTitle(ytitle)
    h[k].GetYaxis().SetTitleOffset(1.)
    h[k].GetZaxis().SetTitle(ztitle)
    h[k].GetZaxis().SetTitleOffset(1.3)
    h[k].GetZaxis().SetTitleSize(0.05)
    h[k].GetZaxis().SetTitleFont(62)
    h[k].GetZaxis().SetLabelSize(0.04)
    h[k].GetZaxis().SetLabelFont(62)
    h[k].GetXaxis().SetTitleOffset(1.)
    h[k].GetXaxis().SetTitleSize(0.06)
    h[k].GetYaxis().SetTitleSize(0.06)
    h[k].GetXaxis().SetLabelFont(62)
    h[k].GetXaxis().SetTitleFont(62)
    h[k].GetYaxis().SetLabelFont(62)
    h[k].GetYaxis().SetTitleFont(62)
    #h[k].SetContour(50)
    h[k].Draw("COLZ")
    if zrange is not None:
        h[k].SetMaximum(zrange[1])
        h[k].SetMinimum(zrange[0])
    else:
        h[k].SetMaximum(h[k].GetMaximum())
    c[k].Draw()

    if do_trunc:
        h[k].GetXaxis().SetRangeUser(0., 1.2)
        h[k].GetYaxis().SetRangeUser(0., 1.2)
    else:
        ax[k] = h[k].GetXaxis()
        ax[k].ChangeLabel(1,-1, 0,-1,-1,-1,"")
        ax[k].ChangeLabel(2,-1,-1,-1,-1,-1,"#font[22]{#gamma_{veto}}")
        ay[k] = h[k].GetYaxis()
        ay[k].ChangeLabel(1,-1, 0,-1,-1,-1,"")
        ay[k].ChangeLabel(2,-1,-1,-1,-1,-1,"#font[22]{#gamma_{veto}}")

        hatch[k] = ROOT.TGraph(2, array('d',[0.,0.]), array('d',[-0.4,1.2])) # n, x[n], y[2]
        hatch[k].SetLineColor(14)
        #hatch[k].SetLineWidth(5001)
        hatch[k].SetLineWidth(3401) # [+/-]ffll, where ff=fill width, ll=line width, +/-=which side of line hatching is drawn on
        #hatch[k].SetLineWidth(5)
        hatch[k].SetFillStyle(3004)
        hatch[k].SetFillColor(14)
        hatch[k].Draw("same")

        hatch2[k] = ROOT.TGraph(2, array('d',[-0.4,1.2]), array('d',[0.,0.])) # n, x[n], y[2]
        hatch2[k].SetLineColor(14)
        hatch2[k].SetLineWidth(-3401) # [+/-]ffll, where ff=fill width, ll=line width, +/-=which side of line hatching is drawn on
        #hatch2[k].SetLineWidth(5)
        hatch2[k].SetFillStyle(3004)
        hatch2[k].SetFillColor(14)
        hatch2[k].Draw("same")

    c[k].Draw()
    c[k].Update()

    c[k].Print('Plots/Sys2D_%s.eps'%(k))
    #c[k].Print('Plots/Sys2D_%s.png'%(k))

def plot_datavmc_flat(region, ks, nbins, yrange=None, colors=[3, 10], styles=[1001, 1001], titles=["im_{x}#timesim_{y} + im_{y}", "N_{evts}"]):

    xtitle, ytitle = titles
    kbkg_up, kbkg_dn, kbkg_nom, kobs_nom, _ = ks
    kshifts = [kbkg_up, kbkg_dn]

    kc = 'c%s_flat'%region
    c[kc] = ROOT.TCanvas(kc, kc, wd_wide, ht)

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetErrorX(0)

    pUp = ROOT.TPad("upperPad", "upperPad",.005, .300, .995, .995) # (,, xlow, ylow, xup, yup)
    pDn = ROOT.TPad("lowerPad", "lowerPad",.005, .005, .995, .300)
    pUp.Draw()
    pDn.Draw()
    #pUp.SetMargin(14.e-02,3.e-02,5.e-03,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pUp.SetMargin(8.e-02,1.e-02,2.e-02,9.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)
    pDn.SetMargin(8.e-02,1.e-02,36.e-02,2.e-02) # (Float_t left, Float_t right, Float_t bottom, Float_t top)

    pUp.cd()

    for i,k in enumerate(kshifts):
      #k = k_+'flat'
      print(k)
      h[k].SetTitle("")
      h[k].GetXaxis().SetTitle(xtitle)
      h[k].GetYaxis().SetTitle(ytitle)
      h[k].GetYaxis().SetTitleOffset(0.5)
      h[k].GetXaxis().SetTitleOffset(1.)
      h[k].GetXaxis().SetTitleSize(0.06)
      h[k].GetYaxis().SetTitleSize(0.075)
      h[k].GetXaxis().SetLabelFont(62)
      h[k].GetXaxis().SetLabelSize(0)
      h[k].GetYaxis().SetLabelSize(0.055)
      h[k].GetXaxis().SetTitleFont(62)
      h[k].GetYaxis().SetLabelFont(62)
      h[k].GetYaxis().SetTitleFont(62)
      if yrange is not None:
          h[k].GetYaxis().SetRangeUser(yrange[0], yrange[1])
      h[k].SetLineColor(colors[i])
      h[k].SetFillColor(colors[i])
      h[k].SetFillStyle(styles[i])
      if i == 0:
          h[k].Draw("LF2")
      else:
          h[k].Draw("LF2 same")
    h[kbkg_nom].SetLineColor(3)
    h[kbkg_nom].SetLineStyle(2)
    h[kbkg_nom].Draw("L same")
    #h[kobs_nom].SetFillStyle(0)
    h[kobs_nom].SetMarkerStyle(20)
    h[kobs_nom].SetMarkerSize(0.85)
    h[kobs_nom].Draw("E same")

    pUp.RedrawAxis()

    ##### Ratio plots on lower pad #####
    pDn.cd()

    #'''
    fUnity = ROOT.TF1('fUnity',"[0]",0.,float(nbins))
    fUnity.SetParameter( 0,1. )

    fUnity.GetXaxis().SetTitle(xtitle)
    fUnity.GetXaxis().SetTickLength(0.1)
    fUnity.GetXaxis().SetTitleOffset(1.05)
    fUnity.GetXaxis().SetTitleSize(0.16)
    fUnity.GetXaxis().SetLabelSize(0.14)

    dY = 0.399
    fUnity.GetYaxis().SetTitle("Obs/Fit")
    #fUnity.GetYaxis().SetRangeUser(1.-dY,1.+dY)
    fUnity.SetMaximum(1.+dY)
    fUnity.SetMinimum(1.-dY)
    fUnity.GetYaxis().SetNdivisions(305)
    fUnity.GetYaxis().SetTickLength(0.04)
    fUnity.GetYaxis().SetLabelFont(62)
    fUnity.GetYaxis().SetTitleFont(62)
    fUnity.GetYaxis().SetTitleOffset(.25)
    fUnity.GetYaxis().SetTitleSize(0.15)
    fUnity.GetYaxis().SetLabelSize(0.12)

    fUnity.SetLineColor(9)
    fUnity.SetLineWidth(1)
    fUnity.SetLineStyle(7)
    fUnity.SetTitle("")
    fUnity.Draw("L")

    colors_ = [3, 5]
    for i,k in enumerate(kshifts):
      kr = k+'ratio'
      print(kr)
      h[kr] = h[k].Clone()
      h[kr].Divide(h[kbkg_nom])
      #h[kr].SetLineColor(colors_[i])
      h[kr].SetLineColor(colors[i])
      h[kr].SetFillColor(colors[i])
      h[kr].SetFillStyle(styles[i])
      h[kr].Draw("LF2 same")
      #for ib in range(10):
      #    print(k, h[kr].GetBinContent(ib))

    #'''
    kr = kobs_nom+'ratio'
    h[kr] = h[kobs_nom].Clone()
    h[kr].Reset()
    ##h[kr].Divide(h[kbkg_nom])
    for i in range(1, h[kr].GetNbinsX()+1):
      #binc = h[kobs_nom].GetBinContent(i)
      #h[kr].SetBinError(i, 1./np.sqrt(binc) if binc != 0 else 0.)
      binc_num = h[kobs_nom].GetBinContent(i)
      binc_den = h[kbkg_nom].GetBinContent(i)
      binerr_num = h[kobs_nom].GetBinError(i)
      binerr_den = h[kbkg_nom].GetBinError(i)
      err_ = get_cplimits_sym(binc_num, binc_den, binerr_num, binerr_den)
      #print(i, binc_num, binc_den, binc_num/binc_den, binerr_num, binerr_den, err_)
      h[kr].SetBinContent(i, binc_num/binc_den)
      h[kr].SetBinError(i, err_)
      #if i<10: print(kr, binc_num/binc_den)

    #h[kr].SetFillStyle(0)
    h[kr].SetMarkerStyle(20)
    h[kr].SetMarkerSize(0.85)
    h[kr].Draw("Ep same")

    fUnityUp = ROOT.TF1('fUnityUp',"[0]",0., float(nbins))
    fUnityUp.SetParameter( 0, 1.2 )
    fUnityUp.SetLineWidth(1)
    fUnityUp.SetLineStyle(2)
    fUnityUp.Draw("L same")
    fUnityDn = ROOT.TF1('fUnityDn',"[0]",0., float(nbins))
    fUnityDn.SetParameter( 0, 0.8 )
    fUnityDn.SetLineWidth(1)
    fUnityDn.SetLineStyle(2)
    fUnityDn.Draw("L same")
    #'''

    pDn.SetGridy()
    pDn.Update()
    #pDn.RedrawAxis()
    fUnity.Draw("axis same")
    #'''
    c[kc].Draw()
    #c[kc].Update()
    c[kc].Print('Plots/Sys2D_flat_region%s_datavbkg.eps'%region)

def get_data_flat(region, ksrc, ktgt, nbins):

    k_flat = 'flat_'+ktgt
    h[k_flat] = ROOT.TH1F(k_flat, k_flat, nbins, 0., nbins)

    ibin = 1
    for ix in range(2, h[ksrc].GetNbinsX()+1):
        for iy in range(2, h[ksrc].GetNbinsY()+1):

            if h[ksrc].GetBinContent(ix, iy) == 0: continue

            binc = h[ksrc].GetBinContent(ix, iy)
            h[k_flat].SetBinContent(ibin, binc)
            ibin += 1

    print(ibin-1, nbins)
    assert ibin-1 == nbins

def get_datavmc_flat(region, ksrcs, kfits, ktgts, nbins):

    ksb2sr, ksr = ksrcs
    kint, kpol_nom, kpol_up, kpol_dn = None, None, None, None

    if len(kfits) == 2:
        # Use fit confidence interval for 1sg variation
        kpol_nom, kint = kfits
    elif len(kfits) == 3:
        # Use pol eigenvariation for 1sg variation
        kpol_nom, kpol_up, kpol_dn = kfits
    #else:
    #    raise Exception('Invalid number of pol fits (2 or 3): %d'%len(kfits))

    for k in ktgts:

        #k_flat = k+'flat'
        k_flat = 'flat_'+k
        h[k_flat] = ROOT.TH1F(k_flat, k_flat, nbins, 0., nbins)

        ibin = 1
        for ix in range(2, h[ksb2sr].GetNbinsX()+1):
            for iy in range(2, h[ksb2sr].GetNbinsY()+1):

                if h[ksb2sr].GetBinContent(ix, iy) == 0: continue

                bkgc = h[ksb2sr].GetBinContent(ix, iy)
                fit_conf = h[kint].GetBinError(ix, iy) if kint is not None else None

                if 'Up' in k:
                    binout = h[kpol_nom].GetBinContent(ix, iy)*bkgc + fit_conf if kint is not None\
                        else h[kpol_up].GetBinContent(ix, iy)*bkgc
                elif 'Down' in k:
                    binout = h[kpol_nom].GetBinContent(ix, iy)*bkgc - fit_conf if kint is not None\
                        else h[kpol_dn].GetBinContent(ix, iy)*bkgc
                elif 'Obs' in k:
                    if do_blind:
                        binout = bkgc if 'limit' in k else h[ksr].GetBinContent(ix, iy)
                    else:
                        binout = h[ksr].GetBinContent(ix, iy)
                elif 'Nom' in k:
                    binout = h[kpol_nom].GetBinContent(ix, iy)*bkgc
                elif 'Bkg' in k:
                    binout = bkgc
                else:
                    raise Exception("Unknown key: %s"%k)
                h[k_flat].SetBinContent(ibin, binout)
                #h[k_flat].SetBinError(ibin, binerr)
                ibin += 1

        print(ibin-1, nbins)
        assert ibin-1 == nbins

def get_pol_hist(params, ksb2sr, ktgt):

    #pol2_2d = '[0] + [1]*x + [2]*y'
    pol2_2d = '[0] + [1]*x + [2]*y +[3]*x*y'
    #pol2_2d = '[0] + [1]*x + [2]*y +[3]*x*y + [4]*x*x + [5]*y*y'
    #pol2_2d = '[0] + [1]*x + [2]*y +[3]*x*y + [4]*x*x + [5]*y*y + [6]*x*x*x + [7]*y*y*y + [8]*x*x*y + [9]*x*y*y'

    nparams = len(pol2_2d.split(']'))-1
    assert nparams == len(params)

    gpol = ROOT.TF2('pol2_2d'+ktgt, pol2_2d, -0.4, 1.2, -0.4, 1.2)
    for i,p in enumerate(params):
        gpol.SetParameter(i, p)

    h[ktgt] = h[ksb2sr].Clone()
    h[ktgt].Reset()
    for ix in range(h[ksb2sr].GetNbinsX()+2):
        for iy in range(h[ksb2sr].GetNbinsY()+2):
            ma_x, ma_y = h[ksb2sr].GetXaxis().GetBinCenter(ix), h[ksb2sr].GetYaxis().GetBinCenter(iy)
            pol_val = gpol.Eval(ma_x, ma_y)
            h[ktgt].SetBinContent(ix, iy, pol_val)

    print('pol_hist:%s, min:%f, max:%f'%(ktgt, h[ktgt].GetMinimum(), h[ktgt].GetMaximum()))

def rebin2d(h, ma_bins):

    nbins = len(ma_bins)-1
    print(h.GetName())
    name = h.GetName()+'_rebin'
    print(name)
    hrebin = ROOT.TH2F(name, name, nbins, ma_bins, nbins, ma_bins)
    #hrebin.Sumw2()

    for ix in range(0, h.GetNbinsX()+2):
        ma_x = h.GetXaxis().GetBinCenter(ix)
        #ma_x = h.GetXaxis().GetBinLowEdge(ix)
        ix_rebin = hrebin.GetXaxis().FindBin(ma_x)
        for iy in range(0, h.GetNbinsY()+2):
            ma_y = h.GetYaxis().GetBinCenter(iy)
            #ma_y = h.GetYaxis().GetBinLowEdge(iy)
            iy_rebin = hrebin.GetYaxis().FindBin(ma_y)
            binc = h.GetBinContent(ix, iy)

            ixy_rebin = hrebin.GetBin(ix_rebin, iy_rebin)
            hrebin.AddBinContent(ixy_rebin, binc)
            #if ix == 2: print(iy, ma_y, iy_rebin, binc)

    return hrebin.Clone()

f, hf, h = {}, {}, {}
fLine = {}
hatch, hatch2 = {}, {}
ax, ay = {}, {}
c = {}

sample = 'Run2017B-F'
regions = ['sb2sr', 'sr']
#key = 'ma0vma1'
key = 'ma1'
#valid_blind = 'diag_lo_hi'
valid_blind = 'sg'
#valid_blind = 'None'
limit_blind = 'offdiag_lo_hi'
#indir = 'Templates/sginjBySignificance/ma100MeV'
#blinds = ['sg']
blinds = [valid_blind, limit_blind]
#blinds = ['sg', 'None']
#indir = 'Templates/nominal/bdtgtm0p98_relchgisolt0p05'
#indir = 'Templates/nominal/nobdt_norelchgiso'
indir = 'Templates/chgiso_invertv2/lead_nom_sublead_inv'
#indir = 'Templates/chgiso_invertv2/lead_inv_sublead_inv'
#indir = 'Templates/chgiso_invertv2/lead_nom_sublead_nom'

for blind in blinds:
    for r in regions:
        #s_r = sample+r
        s_r = sample+r+blind
        hf[s_r] = ROOT.TFile("%s/%s_%s_blind_%s_templates.root"%(indir, sample, r, blind),"READ")
        h[s_r+key] = hf[s_r].Get(key)
        h[s_r+key].SetName(s_r+key)

dMa = 25
#dMa = 50
#dMa = 100
ma_bins = list(range(0,1200+dMa,dMa))
ma_bins = [-400]+ma_bins
ma_bins = [float(m)/1.e3 for m in ma_bins]
#print(len(ma_bins))
ma_bins = array('d', ma_bins)

print(h.keys())
##########################
sr_k = sample+'sr'+valid_blind+key
sb2sr_k = sample+'sb2sr'+valid_blind+key

k = 'pol_x_bkg'

def pol_x_bkg(x, par):

    imx = h[sb2sr_k].GetXaxis().FindBin(x[0])

    pol_val =  par[0] + par[1]*x[0]
    #pol_val =  par[0] + par[1]*x[0] + par[2]*x[1] + par[3]*x[0]*x[1]
    #pol_val =  par[0] + par[1]*x[0] + par[2]*x[1] + par[3]*x[0]*x[1] + par[4]*x[0]*x[0] + par[5]*x[1]*x[1]
    #pol_val =  par[0] + par[1]*x[0] + par[2]*x[1] + par[3]*x[0]*x[1] + par[4]*x[0]*x[0] + par[5]*x[1]*x[1]\
    #            + par[6]*x[0]*x[0]*x[0] + par[7]*x[1]*x[1]*x[1] + par[8]*x[0]*x[0]*x[1] + par[9]*x[0]*x[1]*x[1]
    hist_val = h[sb2sr_k].GetBinContent(imx)

    return pol_val*hist_val

nparams = 2
h[k] = ROOT.TF1(k, pol_x_bkg, -0.4, 1.2, nparams)

#fitResult = h[sr_k].Fit(h[k], "LLIEMNS")
fitResult = h[sr_k].Fit(h[k], "LLS")
chi2 = h[k].GetChisquare()
ndof = h[k].GetNDF()
pval = h[k].GetProb()
print('chi2 / ndf: %f / %f = %f'%(chi2, ndof, chi2/ndof))
#print('chi2 / (ndf-nDiag): %f / %f = %f'%(chi2, ndof-nDiag, chi2/(ndof-nDiag)))
print('p-val:',pval)
cor = fitResult.GetCorrelationMatrix()
cov = fitResult.GetCovarianceMatrix()
cor.Print()
cov.Print()

# Get 68% confidence interval of total fit from ROOT
kfit = 'bkgfit'
h[kfit] = h[sb2sr_k].Clone()
h[kfit].Reset()
h[kfit].SetName(k)
(ROOT.TVirtualFitter.GetFitter()).GetConfidenceIntervals(h[kfit], 0.683) # 1sg: 0.683, 2sg: 0.95

kobs = sb2sr_k
k = 'pull'
ROOT.gStyle.SetOptFit(1)
c[k] = ROOT.TCanvas(k, k, wd, ht)
h[k] = ROOT.TH1F(k, k, 50, -10., 10.)
for ib in range(1, h[kobs].GetNbinsX()+1):
    diff = h[kobs].GetBinContent(ib) - h[kfit].GetBinContent(ib)
    sg = h[kfit].GetBinError(ib)
    pull = diff/sg
    h[k].Fill(pull)
    #if ib < 10:
    #    print(diff, sg, diff/sg)

#ROOT.gStyle.SetOptStat(1)
gfit = ROOT.TF1("gfit","gaus",-10.,10.)
fit_xmax = 4.
h[k].Fit('gfit','L', '', -fit_xmax, fit_xmax)
h[k].SetMarkerStyle(20)
h[k].SetMarkerSize(0.85)
h[k].Draw('Ep')
gfit.SetLineColor(2)
gfit.Draw('same')
c[k].Draw()
c[k].Update()
#c[k].Print('Plots/Sys2D_flat_%s_pull.eps'%region)
chi2 = gfit.GetChisquare()
ndof = gfit.GetNDF()
print('chi2 / ndf: %f / %f = %f'%(chi2, ndof, chi2/ndof))


'''
nbins = {'valid':420, 'limit':196}
hvalid, hlimit = {}, {}

xtitle, ytitle, ztitle = "m_{a_{1},pred} [GeV]", "m_{a_{2},pred} [GeV]", "N_{evts} / %d MeV"%(dMa)
zrange = None
zrange = [1., 4100.]

for blind in blinds:
    for r in regions:

        kreg = sample+r+blind+key

        if ma_bins is not None:
            h[kreg+'rebin'] = rebin2d(h[kreg], ma_bins)

        k = kreg+'rebin'
        for ix in range(1, h[k].GetNbinsX()+1):
            for iy in range(1, h[k].GetNbinsY()+1):
                binc = h[k].GetBinContent(ix, iy)
                h[k].SetBinContent(ix, iy, binc)

        xtitle, ytitle, ztitle = "m_{a_{1},pred} [GeV]", "m_{a_{2},pred} [GeV]", "N_{evts} / %d MeV"%(dMa)
        zrange = None
        zrange = [1., 4100.]
        plot_2dma(k, "", xtitle, ytitle, ztitle, zrange, do_log=True)

##########################
xtitle, ytitle, ztitle = "m_{a_{1},pred} [GeV]", "m_{a_{2},pred} [GeV]", "(Data/Bkg) / %d MeV"%(dMa)
zrange = [0., 2.]

sr_k = sample+'sr'+valid_blind+key
sb2sr_k = sample+'sb2sr'+valid_blind+key

k = 'ratio'
h[k] = h[sr_k+'rebin'].Clone()
err_default = 1.e6

h[k].Reset()
nDiag = 0
nNonZero = 0
for ix in range(1, h[k].GetNbinsX()+1):
    for iy in range(1, h[k].GetNbinsY()+1):
        binc_sr = h[sr_k+'rebin'].GetBinContent(ix, iy)
        binc_sb2sr = h[sb2sr_k+'rebin'].GetBinContent(ix, iy)
        binerr_sr = h[sr_k+'rebin'].GetBinError(ix, iy)
        binerr_sb2sr = h[sb2sr_k+'rebin'].GetBinError(ix, iy)
        if binc_sb2sr != 0:
            binc = binc_sr/binc_sb2sr
            h[k].SetBinContent(ix, iy, binc)
            err_ = get_cplimits_sym(binc_sr, binc_sb2sr, binerr_sr, binerr_sb2sr)
            h[k].SetBinError(ix, iy, err_)
            #if nNonZero < 10:
            #    print(ix, iy, err_lo, err_hi, err_)
            #    nNonZero += 1
        else:
            h[k].SetBinContent(ix, iy, 1.)
            h[k].SetBinError(ix, iy, err_default)
            nDiag += 1

plot_2dma(k, "", xtitle, ytitle, ztitle, zrange)

#binc_sr = h[sr_k+'rebin'].GetBinContent(ix, iy)
#binc_sb2sr = h[sb2sr_k+'rebin'].GetBinContent(ix, iy)
##########################
k = 'pol2_2d_x_bkg'

def pol2_2d_x_bkg(x, par):

    imx = h[sb2sr_k+'rebin'].GetXaxis().FindBin(x[0])
    imy = h[sb2sr_k+'rebin'].GetYaxis().FindBin(x[1])

    #pol_val =  par[0] + par[1]*x[0] + par[2]*x[1]
    pol_val =  par[0] + par[1]*x[0] + par[2]*x[1] + par[3]*x[0]*x[1]
    #pol_val =  par[0] + par[1]*x[0] + par[2]*x[1] + par[3]*x[0]*x[1] + par[4]*x[0]*x[0] + par[5]*x[1]*x[1]
    #pol_val =  par[0] + par[1]*x[0] + par[2]*x[1] + par[3]*x[0]*x[1] + par[4]*x[0]*x[0] + par[5]*x[1]*x[1]\
    #            + par[6]*x[0]*x[0]*x[0] + par[7]*x[1]*x[1]*x[1] + par[8]*x[0]*x[0]*x[1] + par[9]*x[0]*x[1]*x[1]
    hist_val = h[sb2sr_k+'rebin'].GetBinContent(imx, imy)

    return pol_val*hist_val

#nparams = 3
nparams = 4
#nparams = 6
#nparams = 10
h[k] = ROOT.TF2(k, pol2_2d_x_bkg, -0.4, 1.2, -0.4, 1.2, nparams)
#h[k] = ROOT.TF2(k, pol2_2d_x_bkg, 0., 1.2, 0., 1.2, nparams)

fitResult = h[sr_k+'rebin'].Fit(h[k], "LLIEMNS")
chi2 = h[k].GetChisquare()
ndof = h[k].GetNDF()
pval = h[k].GetProb()
print('chi2 / ndf: %f / %f = %f'%(chi2, ndof, chi2/ndof))
#print('chi2 / (ndf-nDiag): %f / %f = %f'%(chi2, ndof-nDiag, chi2/(ndof-nDiag)))
print('p-val:',pval)
cor = fitResult.GetCorrelationMatrix()
cov = fitResult.GetCovarianceMatrix()
cor.Print()
cov.Print()

# Get 68% confidence interval of total fit from ROOT
k = 'hint'
h[k] = h[sb2sr_k+'rebin'].Clone()
h[k].Reset()
h[k].SetName(k)
(ROOT.TVirtualFitter.GetFitter()).GetConfidenceIntervals(h[k], 0.683) # 1sg: 0.683, 2sg: 0.95
plot_2dma(k, "", xtitle, ytitle, ztitle, zrange=None)
########################
# Get just the 2d pol fit fn at nominal fit values
k = 'pol_nom'
params = {}
params['nom'] = [h['pol2_2d_x_bkg'].GetParameter(i) for i in range(nparams)]
get_pol_hist(params['nom'], ksb2sr=sb2sr_k+'rebin', ktgt=k)
plot_2dma(k, "", xtitle, ytitle, 'pol2d', zrange)

# Eigenvariations from solving covariance matrix
# Must be hardcoded here
inflate = 1.
#inflate = 1.e4
varvec = np.array([
    # a0 nom, a1 inv
    np.sqrt(6.510147e-06) * np.array([ 0.835471776477,0.0888621119847,0.542301056392 ]),
    np.sqrt(8.085227e-05) * np.array([ 0.471999314239,-0.621426092018,-0.625336916803 ]),
    np.sqrt(6.392758e-05) * np.array([ -0.281431267042,-0.778417071506,0.561126816966 ]),
    ## a0 inv, a1 inv
    #np.sqrt(2.924295e-04) * np.array([ 0.605757640747,-0.54562723984,-0.579092907763 ]),
    #np.sqrt(1.621729e-05) * np.array([ -0.794901949312,-0.383479565268,-0.470185403859 ]),
    #np.sqrt(1.245532e-04) * np.array([ -0.0344756676018,-0.745140482169,0.666015833277 ]),
    ## a0 nom, a1 nom
    #np.sqrt(7.057870e-06) * np.array([ -0.959113801422,-0.11351884742,-0.259256990653 ]),
    #np.sqrt(4.515042e-05) * np.array([ -0.220044343874,-0.276999154061,0.935335210167 ]),
    #np.sqrt(5.654171e-05) * np.array([ 0.177992142105,-0.95414094343,-0.240694531345 ]),
    ])
varvec *= inflate
for v in varvec:
    print(v)


# Get pol variations based on parameter eigenvariations, e_i
# Create a 2d histogram with bin contents corresponding to
# polynomial fit but with params p_i shifted: p_i +/ e_i
#print('n', 'nm', params['nom'])
for i in range(nparams):
    for shift in ['up', 'dn']:
        v = 'e%d_1sg%s'%(i, shift)
        params[v] = var_params(params['nom'], varvec[i], shift)
        #print(i, shift, params[v])
        kpol = 'pol_'+v
        get_pol_hist(params[v], ksb2sr=sb2sr_k+'rebin', ktgt=kpol)
        #plot_2dma(kpol, "", xtitle, ytitle, ztitle, zrange)

#########################
yrange_flat = [0., 650.] # a0nom, a1inv
#yrange_flat = [0., 200.] # a0inv, a1inv
#yrange_flat = [0., 1100.] # a0nom, a1nom
for blind in blinds:

    region = 'valid' if 'sg' in blind else 'limit'
    nbin = nbins[region]

    sr_k = sample+'sr'+blind+key
    sb2sr_k = sample+'sb2sr'+blind+key

    # Get bkg variation corresponding to shifted pol fits for each param p_i
    # For flattened 2d -> 1d: unroll bkg then multiply by pol fits
    # at nominal p_i value and at shifted p_i +/- e_i, separately for each p_i
    for i in range(nparams):
        ksrcs = [sb2sr_k+'rebin', sr_k+'rebin']
        kfits = ['pol_nom', 'pol_e%d_1sgup'%i, 'pol_e%d_1sgdn'%i]
        ktgts = ['Up', 'Down', 'Nom', 'Obs', 'Bkg']
        ktgts = ['%sfit_e%d%s'%(region, i, k) for k in ktgts]
        get_datavmc_flat(region, ksrcs, kfits, ktgts, nbin)
        #kplots = [k+'flat' for k in ktgts]
        kplots = ['flat_'+k for k in ktgts]
        #if i != 0: continue
        plot_datavmc_flat(region+str(i), kplots, nbin, yrange=yrange_flat)

    kobs = 'flat_%sfit_e0Obs'%(region)
    kfit = 'flat_%sfit_e0Nom'%(region)
    k = 'pull_%sfit'%(region)
    ROOT.gStyle.SetOptFit(1)
    c[k] = ROOT.TCanvas(k, k, wd, ht)
    h[k] = ROOT.TH1F(k, k, 50, -10., 10.)
    for ib in range(1, h[kobs].GetNbinsX()+1):
        diff = h[kobs].GetBinContent(ib) - h[kfit].GetBinContent(ib)
        sg = h[kfit].GetBinError(ib)
        pull = diff/sg
        h[k].Fill(pull)
        #if ib < 10:
        #    print(diff, sg, diff/sg)

    #ROOT.gStyle.SetOptStat(1)
    gfit = ROOT.TF1("gfit","gaus",-10.,10.)
    fit_xmax = 4. if region =='valid' else 3.
    h[k].Fit('gfit','L', '', -fit_xmax, fit_xmax)
    h[k].SetMarkerStyle(20)
    h[k].SetMarkerSize(0.85)
    h[k].Draw('Ep')
    gfit.SetLineColor(2)
    gfit.Draw('same')
    c[k].Draw()
    c[k].Update()
    c[k].Print('Plots/Sys2D_flat_%s_pull.eps'%region)
    chi2 = gfit.GetChisquare()
    ndof = gfit.GetNDF()
    print('chi2 / ndf: %f / %f = %f'%(chi2, ndof, chi2/ndof))

    file_out = ROOT.TFile('Fits/Bkgfits_flat_region%s.root'%region, "RECREATE")
    for i in range(nparams):
        for shift in ['Up', 'Down']:
            kbkg = 'flat_%sfit_e%d%s'%(region, i, shift)
            print(kbkg)
            assert kbkg in h.keys()
            h[kbkg].Write()
        for nom in ['Nom', 'Bkg', 'Obs']:
            knom = 'flat_%sfit_e%d%s'%(region, i, nom)
            print(knom)
            assert knom in h.keys()
            #h[knom].Write()

    hout = hvalid if region == 'valid' else hlimit
    k_ = 'flat_%sfit'%region
    hout[k_] = h['flat_%sfit_e0Nom'%region].Clone()
    hout[k_].SetName(k_)
    #for shift in ['Up', 'Down']:
    #    k_shift = k_+'_stat'+shift
    #    hout[k_shift] = hout[k_].Clone()
    #    hout[k_shift].Reset()
    #    hout[k_shift].SetName(k_shift)
    #    for ib in range(1, hout[k_shift].GetNbinsX()+1):
    #        binc = hout[k_].GetBinContent(ib)
    #        binerr = hout[k_].GetBinError(ib)
    #        binout = binc + binerr if shift == 'Up' else binc - binerr
    #        hout[k_shift].SetBinContent(ib, binout)
    #k_ = 'flat_%sraw'%region
    #hout[k_] = h['flat_%sfit_e0Bkg'%region].Clone()
    #hout[k_].SetName(k_)
    #hout[k_].Write()
    k_ = 'data_obs'
    hout[k_] = h['flat_%sfit_e0Obs'%region].Clone()
    hout[k_].SetName(k_)
    #hvalid[k_].Write()

    file_out.Write()
    file_out.Close()

#########################
sample = 'h24gamma_1j_1M_100MeV'
regions = ['sr']
blinds = [limit_blind]

for blind in blinds:
    for r in regions:
        #s_r = sample+r
        s_r = sample+r+blind
        hf[s_r] = ROOT.TFile("%s/%s_%s_blind_%s_templates.root"%(indir, sample, r, blind),"READ")
        h[s_r+key] = hf[s_r].Get(key)
        h[s_r+key].SetName(s_r+key)
        norm = get_sg_norm(sample, xsec=50.*1.e0)
        print('%s mc2data norm: %.4f'%(sample, norm))
        h[s_r+key].Scale(norm)

xtitle, ytitle, ztitle = "m_{a_{1},pred} [GeV]", "m_{a_{2},pred} [GeV]", "N_{evts} / %d MeV"%(dMa)
zrange = None
zrange = [1., 4100.]
for blind in blinds:
    for r in regions:

        kbkg = 'Run2017B-F'+'sb2sr'+blind+key+'rebin'
        kreg = sample+r+blind+key
        k = kreg+'rebin'

        if ma_bins is not None:
            h[k] = rebin2d(h[kreg], ma_bins)

        for ix in range(1, h[k].GetNbinsX()+1):
            for iy in range(1, h[k].GetNbinsY()+1):
                binc = h[k].GetBinContent(ix, iy)
                h[k].SetBinContent(ix, iy, binc)

        plot_2dma(k, "", xtitle, ytitle, ztitle, zrange, do_log=True)

        region = 'limit'

        ksrcs = [kbkg, k]
        ktgts = [sample+'_Obs']
        get_datavmc_flat(region, ksrcs, [None], ktgts, nbins[region])
        #yrange = [0., 600.]
        plot_1dma('flat_'+ktgts[0], color=4, yrange=yrange_flat)

        file_out = ROOT.TFile('Fits/Bkgfits_flat_region%s.root'%region, "UPDATE")
        #file_out = ROOT.TFile('Fits/Bkgfits_flat_region%s.root'%region, "RECREATE")
        hout = hvalid if region == 'valid' else hlimit
        #k_ = 'flat_%sh4g100MeV'%region
        k_ = 'flat_%sh4g'%region
        hout[k_] = h['flat_'+ktgts[0]].Clone()
        hout[k_].SetName(k_)
        #for shift in ['Up', 'Down']:
        #    k_shift = k_+'_stat'+shift
        #    hout[k_shift] = hout[k_].Clone()
        #    hout[k_shift].Reset()
        #    hout[k_shift].SetName(k_shift)
        #    for ib in range(1, hout[k_shift].GetNbinsX()+1):
        #        binc = hout[k_].GetBinContent(ib)
        #        binerr = hout[k_].GetBinError(ib)
        #        binout = binc + binerr if shift == 'Up' else binc - binerr
        #        hout[k_shift].SetBinContent(ib, binout)
        file_out.Write()
        file_out.Close()
'''
