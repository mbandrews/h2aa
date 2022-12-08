from __future__ import print_function
import ROOT
from array import array
from hist_utils import *

do_sg = False
do_sg = True
import tdrstyle
if do_sg:
    #import CMS_lumi_white as CMS_lumi # for PAS
    import CMS_lumi as CMS_lumi # for PRL
else:
    import CMS_lumi as CMS_lumi

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
if do_sg:
    iPos = 11 # CMS in frame
else:
    iPos = 0 # CMS above frame
iPos = 0 # for PRL
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
    blindTextSize   = 0.75

    k = k_
    c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
    h[k] = set_hist(h[k], "m_{ #Gamma,1} [GeV]", "m_{ #Gamma,2} [GeV]", "")
    ROOT.gPad.SetRightMargin(0.23)
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
    #units = '(%d MeV)^{2}'%dMa
    units = '(%.2f GeV)^{2}'%(dMa/1.e3)
    if label is None:
        h[k].GetZaxis().SetTitle("Events / %s"%units)
    else:
        h[k].GetZaxis().SetTitle("%s / %s"%(label, units))
    h[k].GetZaxis().SetTitleOffset(1.22)
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
    palette.SetX1NDC(0.779)
    palette.SetX2NDC(0.779+0.05)
    palette.SetY2NDC(0.916)
    palette.SetY1NDC(0.17)

    print(sample)
    mass = sample.split('GeV')[0].split('mA')[-1].replace('p','.')
    print(mass)
    blindText = 'm_{#bf{#it{A}}} = %s GeV'%mass
    t_ = ROOT.gPad.GetTopMargin()
    ltx = ROOT.TLatex()
    ltx.SetNDC()
    ltx.SetTextFont(txtFont)#bold:62
    ltx.SetTextAlign(13)
    ltx.SetTextSize(blindTextSize*t_)
    ltx.SetTextColor(17)
    if mass == '1.0':
        ltx.DrawLatex(0.22, 0.27, blindText)
    else:
        ltx.DrawLatex(0.22, 0.868, blindText)

    CMS_lumi.relPosY = 0.8

    CMS_lumi.CMS_lumi(c[k], iPeriod, iPos)

    c[k].Update()
    c[k].Print('Plots/2dma/%s_blind_%s_%s%s_sel-%s.pdf'%(sample, blind, k, '_ext' if not do_trunc else '', sel))

#def plot_2dma(sample, blind):

hf, h = {}, {}
c = {}


keys = ['ma0vma1']

''' old (2017) version
#regions = ['sblo', 'sbhi', 'sr']
#regions = ['sblo2sr', 'sbhi2sr', 'sb2sr', 'sr']
regions = ['sblo2sr', 'sbhi2sr', 'sb2sr']
sample = 'Run2017B-F'
#blind = 'diag_lo_hi'
#blind = 'offdiag_lo_hi'
blind = None
#indir = 'Templates_tmp'
indir = 'Templates/prod_normblind_diaglohi/nom-nom/flo_None'

for r in regions:
    #hf[r] = ROOT.TFile("%s/%s_%s_blind_%s_templates.root"%(indir, sample, r, blind),"READ")
    inpath = '%s/%s/%s_sb2sr+hgg.root'%(indir, campaign, sample)
    hf[r] = ROOT.TFile.Open("%s/%s_%s_blind_%s_templates.root"%(indir, sample, r, blind),"READ")
    for k in keys:
        rk = '%s_%s'%(r, k)
        h[rk] = hf[r].Get(k)
        #draw_hist_2dma(k, h, c, sample, blind, r, do_trunc=False)
        #draw_hist_2dma(k, h, c, sample, blind, r, do_trunc=True)
'''

#'''
run = 'Run2'
r_sb2sr, r_sr = 'sb2sr+hgg', 'sr'
valid_blind = 'diag_lo_hi'
limit_blind = 'offdiag_lo_hi'
indir = 'root://cmseos.fnal.gov//store/user/lpchaa4g/mandrews/%s'%run
sub_campaign = 'bdtgtm0p96_relChgIsolt0p07_etalt1p44' # bdt > -0.96, relChgIso < 0.07 !! optimal
k = keys[0]
dMa = 25
dMa = 50

#'''
if do_sg:
    # Sg model
    sel = 'nom'
    CMS_lumi.extraText = "Simulation" # for PRL
    #CMS_lumi.extraText = "Simulation Preliminary" # for PAS
    ma_pts = ['0p1', '0p4', '1p0']#, '0p5']
    #ma_pts = ['1p0']
    regions = [r_sr]
    blinds = [limit_blind, valid_blind] # to get fully unblinded plots, run mk_sg_temp and combine_sg_temp with both blinding settings!
    #blinds = [limit_blind] # to get fully unblinded plots, run mk_sg_temp and combine_sg_temp with both blinding settings!
    #campaign = 'sg-Era04Dec2020v6/%s/nom-%s/Templates/systNom_nom'%(sub_campaign, sel) # 2016-18 phoid, 2016-18 ss. ss implemented only for shifted syst (as in v4)
    #campaign = 'sg-Era22Jun2021v2/%s/nom-%s/Templates/systNom_nom'%(sub_campaign, sel) # 2016-18 phoid, 2016-18 ss. ss implemented only for shifted syst (as in v4)
    #campaign = 'sg-Era22Jun2021v3/%s/nom-%s/Templates/systNom_nom'%(sub_campaign, sel) # v2 + interpolated mass pts
    campaign = 'sg-Era22Jun2021v6/%s/nom-%s/Templates/systNom_nom'%(sub_campaign, sel) #  bin50MeV
    do_blind = True
    do_blind = False
    for ma in ma_pts:

        sample = 'h4g-mA%sGeV'%ma if run == 'Run2' else 'h4g%s-mA%sGeV'%(run, ma)
        maxzs = []
        for r in regions:
            srk = '%s_%s_%s'%(sample, r, k)
            for b in blinds:

                inpath = "%s/%s/%s_%s_blind_%s_templates.root"%(indir, campaign, sample, r, b)
                print('>> Reading:', inpath)

                srkb = '%s-%s'%(srk, b)
                print('srkb:',srkb)

                hf[srkb] = ROOT.TFile.Open(inpath, "READ")

                h[srkb] = hf[srkb].Get(srkb)
                h[srkb].SetName(srkb)
                if b == limit_blind:
                    h[srk] = h[srkb].Clone()
                    h[srk].SetName(srk)
                else:
                    # to make fully unblinded 2dma, add offdiag + diag blinded plots
                    if not (do_blind and r == r_sr):
                        h[srk].Add(h[srkb])
            maxzs.append(h[srk].GetMaximum())
            print('h[%s], max: %f'%(srk, h[srk].GetMaximum()))

        for r in regions:
            srk = '%s_%s_%s'%(sample, r, k)

            # overwrite empty bins
            for ix in range(0, h[srk].GetNbinsX()+2):
                for iy in range(0, h[srk].GetNbinsY()+2):

                    binc = h[srk].GetBinContent(ix, iy)
                    if binc == 0:
                        h[srk].SetBinContent(ix, iy, 1.)

            draw_hist_2dma(srk, h, c, sample, limit_blind if do_blind and r == r_sr else None, ymax_=np.max(maxzs), do_trunc=True)
    #'''

else:
    # Bkg model
    sample = 'data'
    sel = 'nom'
    sel = 'inv'
    #campaign = 'bkgPtWgts-Era04Dec2020v2/%s/nom-%s/Templates_bkg'%(sub_campaign, sel) # combined full Run2, 2016H+2018 failed lumis, run = 'Run2'
    #campaign = 'bkgPtWgts-Era22Jun2021v1/%s/nom-%s/Templates_bkg'%(sub_campaign, sel) # combined full Run2, 2016H+2018 failed lumis, run = 'Run2'
    #campaign = 'bkgPtWgts-Era22Jun2021v4/%s/nom-%s/Templates_bkg'%(sub_campaign, sel) # combined full Run2, mgg95, hgg template with SFs, fhgg from br(hgg)
    campaign = 'bkgPtWgts-Era22Jun2021v2/%s/nom-%s/Templates_bkg'%(sub_campaign, sel) # bin 50MeV
    regions = [r_sb2sr, r_sr]
    blinds = [valid_blind, limit_blind]
    #regions = [r_sb2sr]
    do_blind = True if sel == 'nom' else False
    if sel == 'inv':
        do_blind = False
    CMS_lumi.extraText = "Preliminary"
    #do_blind = False

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
            #if b == limit_blind: # for making illustrations only
            if b == valid_blind:
                h[srk] = h[srkb].Clone()
                h[srk].SetName(srk)
            else:
                if not (do_blind and r == r_sr):
                    h[srk].Add(h[srkb])
        maxzs.append(h[srk].GetMaximum())
        print('h[%s], max: %f'%(srk, h[srk].GetMaximum()))

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

    for r in regions:
        srk = '%s_%s_%s'%(sample, r, k)
        draw_hist_2dma(srk, h, c, sample, limit_blind if do_blind and r == r_sr else None, ymax_=np.max(maxzs)*(1. if sel=='nom' else 1.02), do_trunc=True, label=('Obs. events' if r==r_sr else None))

    # Make ratio plot
    kobs = '%s_%s_%s'%(sample, r_sr, k)
    kbkg = '%s_%s_%s'%(sample, r_sb2sr, k)
    kratio = '%so%s'%(r_sb2sr, r_sr)
    h[kratio] = h[kobs].Clone()
    h[kratio].SetName(kratio)
    h[kratio].Divide(h[kbkg])
    #print('h[%s], min,max: %f, %f'%(kratio, h[kratio].GetMinimum(), h[kratio].GetMaximum()))
    #draw_hist_2dma(kratio, h, c, sample, limit_blind if do_blind else None, ymax_=2., ymin_=0., do_trunc=True, label='(Obs/Bkg)')
    draw_hist_2dma(kratio, h, c, sample, limit_blind if do_blind else None, ymax_=1.5, ymin_=0.5, do_trunc=True, label='(Obs/Bkg)')

'''
# rebinned ratios
# need to calculate ratio AFTER rebinning input hists
# otherwise values will be wrong as below
dMa = 25
dMa = 50
#dMa = 100
ma_bins = list(range(0,1200+dMa,dMa))
ma_bins = [-400]+ma_bins
ma_bins = [float(m)/1.e3 for m in ma_bins]
nbins = len(ma_bins)-1
ma_bins = array('d', ma_bins)

kratio_rebin = kratio+'_rebin'
h[kratio_rebin] = ROOT.TH2F(kratio_rebin, kratio_rebin, nbins, ma_bins, nbins, ma_bins)
#rebin2d(kratio, kratio_rebin)#, ma_bins, h[kratio_rebin])

for ix in range(0, h[kratio].GetNbinsX()+2):
    ma_x = h[kratio].GetXaxis().GetBinCenter(ix)
    #ma_x = h[kratio].GetXaxis().GetBinLowEdge(ix)
    ix_rebin = h[kratio_rebin].GetXaxis().FindBin(ma_x)
    for iy in range(0, h[kratio].GetNbinsY()+2):
        ma_y = h[kratio].GetYaxis().GetBinCenter(iy)
        #ma_y = h[kratio].GetYaxis().GetBinLowEdge(iy)
        iy_rebin = h[kratio_rebin].GetYaxis().FindBin(ma_y)
        binc = h[kratio].GetBinContent(ix, iy)

        ixy_rebin = h[kratio_rebin].GetBin(ix_rebin, iy_rebin)
        h[kratio_rebin].AddBinContent(ixy_rebin, binc)

# workaround: for some reason need to re-set bin contents for plotting to work
for ix in range(1, h[kratio_rebin].GetNbinsX()+1):
    for iy in range(1, h[kratio_rebin].GetNbinsY()+1):
        binc = h[kratio_rebin].GetBinContent(ix, iy)
        binerr = h[kratio_rebin].GetBinError(ix, iy)
        h[kratio_rebin].SetBinContent(ix, iy, binc)
        h[kratio_rebin].SetBinError(ix, iy, binerr)

draw_hist_2dma(kratio_rebin, h, c, sample, limit_blind if do_blind else None, ymax_=2., ymin_=0., do_trunc=True, label='(Obs/Bkg)')
'''

'''
# Make pull plot
kpull = 'pull'#%(r_sb2sr, r_sr)
h[kpull] = h[kobs].Clone()
h[kpull].SetName(kpull)
for ix in range(1, h[kpull].GetNbinsX()+1):
    for iy in range(1, h[kpull].GetNbinsY()+1):

        obs = h[kobs].GetBinContent(ix, iy)
        if obs == 0: continue

        bkg = h[kbkg].GetBinContent(ix, iy)
        diff = obs - bkg
        sg_bkg = h[kbkg].GetBinError(ix, iy)
        sg_obs = h[kobs].GetBinError(ix, iy)
        #sg = np.sqrt(sg_bkg*sg_bkg + sg_obs*sg_obs)
        sg = sg_bkg
        pull = diff/sg
        pull = (obs-bkg)/np.sqrt(bkg)

        h[kpull].SetBinContent(ix, iy, pull)

#h[kpull].Divide(h['%s_%s_%s'%(sample, r_sb2sr, k)])
print('h[%s], min,max: %f, %f'%(kpull, h[kpull].GetMinimum(), h[kpull].GetMaximum()))
draw_hist_2dma(kpull, h, c, sample, limit_blind if do_blind else None, ymax_=8., ymin_=-8., do_trunc=True, label='pull')
#draw_hist_2dma(kpull, h, c, sample, limit_blind if do_blind else None, ymax_=1.+2., ymin_=0., do_trunc=True, label='pull')
'''
