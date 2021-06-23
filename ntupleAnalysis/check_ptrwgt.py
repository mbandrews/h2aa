import ROOT
from array import array
from hist_utils import *

def draw_hist_1dpt(ks, h, c, sample, blind, ymax_=None):

    ksr = ks[0]
    assert ksr in h.keys()
    ksb2sr = ks[1]
    assert ksb2sr in h.keys()

    hc = {}

    err_style = 'E2'
    fill_style = 3002
    wd, ht = int(640*1), int(680*1)

    k = ksr
    c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)

    # SR
    h[k] = set_hist(h[k], "p_{T,a} [GeV]", "N_{a}", "")
    h[k].SetFillStyle(0)
    h[k].SetMarkerStyle(20)
    h[k].SetMarkerSize(0.85)
    #h[k].GetXaxis().SetTitle('')
    #h[k].GetXaxis().SetLabelSize(0.)
    h[k].GetYaxis().SetTitleOffset(0.9)
    h[k].GetYaxis().SetTitleSize(0.07)
    h[k].GetYaxis().SetLabelSize(0.06)
    h[k].GetYaxis().SetMaxDigits(3)
    h[k].Draw("E")

    # SB2SR
    k = ksb2sr
    h[k].SetLineColor(2)#9
    h[k].Draw("hist E same")

    k = ksr
    #ymax = 1.2*max(h[ksr].GetMaximum(), h[ksb2sr].GetMaximum())
    ymax = 1.2*h[ksr].GetMaximum()
    h[ksr].GetYaxis().SetRangeUser(0.1, ymax)
    #h[ksr].GetXaxis().SetRangeUser(25., 100.)

    k = ksr
    c[k].Draw()
    c[k].Update()
    c[k].Print('Plots/%s_dataomc_blind_%s_%s.eps'%(sample, blind, k))

h = {}
c = {}

regions = ['sblo', 'sbhi', 'sr']
#regions = ['sr']
#keys = ['pt0vpt1']
keys = ['ptxy']
sample = 'Run2017B-F'
blind = None
indir = 'Templates_tmp'
#indir = 'Templates_tmp/no_ptrwgt'
#indir = 'Templates_tmp/floNone_ptrwgt'
#indir = 'Templates_tmp/flo0p504_ptrwgt'
#indir = 'Templates_tmp/flo0p791_ptrwgt'

flo_nom = 0.640902
flo_syst = 0.791 #504
flo_ratio = flo_syst/flo_nom
fhi_ratio = (1.-flo_syst)/(1.-flo_nom)
flo_ratio = (4415.026543110609/10000.5711528063)*flo_syst/flo_nom
fhi_ratio = (5585.544609695673/10000.5711528063)*(1.-flo_syst)/(1.-flo_nom)
print(flo_ratio, fhi_ratio)
ftot_ratio = flo_ratio+fhi_ratio
flo_ratio /= ftot_ratio
fhi_ratio /= ftot_ratio
#flo_ratio = 0.591249
flo_ratio = 0.610809671732
fhi_ratio = 0.389190328268
flo_ratio = 0.573252521388
fhi_ratio = 0.426747478612
#flo_ratio = 1.
#fhi_ratio = 0.
print(flo_ratio, fhi_ratio)

hf = {}
# Run2017B-F_sb2sr_blind_None_ptwgts.root
for k in ['pt0vpt1']:
    for r in regions:
        hf[r] = ROOT.TFile("%s/%s_%s_blind_%s_templates.root"%(indir, sample, r, blind),"READ")
        rk = '%s_%s'%(r, k)
        h[rk] = hf[r].Get(k)
        print(rk, h[rk].Integral())
print(h['sblo_%s'%k].Integral()/(h['sblo_%s'%k].Integral()+h['sbhi_%s'%k].Integral()))

for k in keys:
    for r in regions:
        hf[r] = ROOT.TFile("%s/%s_%s_blind_%s_templates.root"%(indir, sample, r, blind),"READ")
        rk = '%s_%s'%(r, k)
        h[rk] = hf[r].Get(k)
        if 'sb' in r:
            pass
            h[rk].Scale(1./h[rk].Integral())

    # Add templates
    ksblohi = 'sblohi_%s'%k
    h[ksblohi] = h['sblo_%s'%k].Clone()
    h[ksblohi].SetName(ksblohi)
    h[ksblohi].SetTitle(ksblohi)
    #h[ksblohi].Scale(flo_ratio*4415.026543110609/10000.5711528063)
    #h[ksblohi].Add(h['sbhi_%s'%k], fhi_ratio*5585.544609695673/10000.5711528063)
    h[ksblohi].Scale(flo_ratio)
    h[ksblohi].Add(h['sbhi_%s'%k], fhi_ratio)

    # Normalize templates
    ksb2sr = 'sb2sr_%s'%k
    h[ksb2sr] = h[ksblohi].Clone()
    h[ksb2sr].SetName(ksb2sr)
    h[ksb2sr].SetTitle(ksb2sr)
    h[ksb2sr].Scale(h['sr_%s'%k].Integral()/h[ksblohi].Integral())

    print('sb2sr integral:',h[ksb2sr].Integral())
    print('sr integral:',h['sr_%s'%k].Integral())

    draw_hist_1dpt(['sr_%s'%k, 'sb2sr_%s'%k], h, c, sample, blind, ymax_=None)
