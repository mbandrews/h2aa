import ROOT
import numpy as np
from array import array
from hist_utils import *
from template_utils import *
import CMS_lumi

ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
#change the CMS_lumi variables (see CMS_lumi.py)
CMS_lumi.lumi_7TeV = "4.8 fb^{-1}"
CMS_lumi.lumi_8TeV = "18.3 fb^{-1}"
CMS_lumi.writeExtraText = 1
CMS_lumi.extraText = "Simulation"
CMS_lumi.lumi_sqrtS = "136 fb^{-1} (13 TeV)" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
#CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
CMS_lumi.cmsTextOffset = 0.
iPos = 11 # CMS in frame
#iPos = 0 # CMS above frame
if iPos==0:
    #CMS_lumi.cmsTextOffset = 0.
    CMS_lumi.relPosX = 0.12
iPeriod = 0

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

    #h[k] = set_hist(h[k], "m_{#Gamma,pred} [GeV]", "N_{#Gamma} / 25 MeV", "")
    h[k] = set_hist(h[k], "m_{#Gamma} [GeV]", "Events / %d MeV"%dMa, "")
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
        h[k].GetYaxis().SetRangeUser(0.1, ymax)
        h[k].GetXaxis().SetRangeUser(0., 1.2)
        #hc[k].GetYaxis().SetRangeUser(0.1, ymax)

    if it == nit - 1:
        mass = float(k.split('_')[0].replace('p','.'))
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

    if it == nit - 1:

        if mass != 1.: # GeV
            legend = ROOT.TLegend(0.55, 0.78, 0.85, 0.88) #(x1, y1, x2, y2)
        else:
            legend = ROOT.TLegend(0.4, 0.78, 0.7, 0.88) #(x1, y1, x2, y2)

        for k in keys:
            mk = '%s_%s'%(k_.split('_')[0], k)
            legend.AddEntry(mk, '%s p_{T}'%('leading' if k == 'ma0' else 'sub-leading'), "lf")
        legend.SetBorderSize(0)
        legend.Draw("same")

        c.Update()

        #outfile = 'Plots/mAvRun_%s.pdf'%(k)
        outfile = 'Plots/1dma/mAvLeadSubleadPt_mA%sGeV.pdf'%(k_.split('_')[0])
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
#campaign = 'sg-Era04Dec2020v6/bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-nom/Templates/systNom_nom'
#campaign = 'sg-Era22Jun2021v2/bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-nom/Templates/systNom_nom'
campaign = 'sg-Era22Jun2021v6/bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-nom/Templates/systNom_nom' #bin50MeV

dMa = 50

# For mc->data normalization
#ggntuple_campaign = 'Era04Dec2020v1_ggSkim-v1' # fixed h4g mc triggers
#ggntuple_campaign = 'Era20May2021v1_ggSkim-v'+campaign.split('/')[0][-1]
ggntuple_campaign = 'Era20May2021v1_ggSkim-v2'
xs_sg = 1. #pb
# Official lumis: https://twiki.cern.ch/twiki/bin/view/CMS/TWikiLUM
#tgt_lumis = {'2016': 36.33e3, #35.92e3,
#             '2017': 41.53e3,
#             '2018': 59.74e3} # /pb.
# Estimated lumis modulo missing lumis: https://docs.google.com/spreadsheets/d/1wmDcb88uJfgJakIE9BfKfHXU_sb1ldy6NArZZzr0fRk/edit#gid=0
# Calculated using:
#   [1] cmslpc:~mba2012/nobackup/h2aa/CMSSW_10_5_0/src/h2aa/crab/run_getLumis.py
#   [2] lxplus:~mandrews/work/h2aa/brilcalc_work/getLumis_byEra.sh
tgt_lumis = {'2016': 36.25e3,
             '2017': 41.53e3,
             '2018': 58.75e3} # /pb. Run2: 136.53/pb

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

nit = len(keys)
#ymaxs = {'0p1':2.e3, '0p4':2.5e3, '1p0':500.}
#ymaxs = {'0p1':2.4e3, '0p4':2.8e3, '1p0':800.}
ymaxs = {'0p1':2.*2.4e3, '0p4':5.4e3, '1p0':1.5e3}

# /eos/uscms/store/user/lpchaa4g/mandrews/2017/sg-Era04Dec2020v6/bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-nom/Templates/systNom_nom/
for r in runs:
    for m in mas:
        #filepath = "%s/%s/%d/%s%s/systNomNom/h4g%d-mA%sGeV_mantuple.root"%(eos_redir, eos_basedir, r, campaign, e, m)
        #filepath = "%s%s/systNom_nom/h4g%s-mA%sGeV_sr_blind_None_templates.root"%(campaign, e, r, m)
        filepath = "%s/%s/%s/%s/h4g%s-mA%sGeV_sr_blind_None_templates.root"%(eos_redir, eos_basedir, r, campaign, r, m)
        print('>> Opening: %s'%filepath)
        hf[r+m] = ROOT.TFile.Open(filepath)
        for k in keys:
            rmk = '%s_%s_%s'%(r, m, k)
            h[rmk] = hf[r+m].Get(k)
            mcnorm = get_mc2data_norm('h4g%s-mA%sGeV'%(r, m), ggntuple_campaign, tgt_lumis[r], xsec=xs_sg)
            h[rmk].Scale(mcnorm)
            h[rmk].SetName(rmk)
            h[rmk].SetTitle(rmk)
            print('>> %s: maximum: %f'%(rmk, h[rmk].GetMaximum()))
            print('>> %s: GetEntries: %f, Integral: %f'%(rmk, h[rmk].GetEntries(), h[rmk].Integral()))

it = {}
wd, ht = int(640*1), int(680*1)
for m in mas:
    c[m] = ROOT.TCanvas("c%s"%(m), "c%s"%(m), wd, ht)
    ymax_ = ymaxs[m]
    #ymax_ = -1
    it[m] = 0
    for k in keys:
        mk = '%s_%s'%(m, k)

        # add years
        for ir,r in enumerate(runs):
            rmk = '%s_%s'%(r, mk)
            if ir == 0:
                h[mk] = h[rmk].Clone()
                h[mk].SetName(mk)
            else:
                h[mk].Add(h[rmk])

        #for ix in range(0, h[rmek].GetNbinsX()+2):
        #    pass
        #    #print('%d: %f'%(ix, h[rmek].GetBinContent(ix)))
        draw_hist_1dma_overlay(mk, h, hc, c[m], l, hatch, legend, it[m], ymax_)
        it[m] += 1
    #c[k+m].Print('Plots/mA_%.eps'%(k))
