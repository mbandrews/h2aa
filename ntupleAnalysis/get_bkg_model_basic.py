import numpy as np
np.random.seed(0)
import os, glob
import time
import argparse
from array import array

import ROOT

# Register command line options
parser = argparse.ArgumentParser(description='Run STEALTH selection.')
parser.add_argument('-s', '--sample', default='test', type=str, help='Sample name.')
parser.add_argument('-i', '--inputs', default=['MAntuples/Run2017F_mantuple.root'], nargs='+', type=str, help='Input MA ntuple.')
parser.add_argument('-t', '--treename', default='Data', type=str, help='H4G TTree name prefix.')
parser.add_argument('-o', '--outdir', default='MAntuples', type=str, help='Output directory.')
args = parser.parse_args()

# Load H4G ntuples as TTree friend
print('Setting H4G as TTree friend')
print('N H4G files:',len(args.inputs))
print('H4G file[0]:',args.inputs[0])
treef = ROOT.TChain("h4gCandidateDumper/trees/%s_13TeV_2photons"%args.treename)
#for fh in args.inputs:
for i,fh in enumerate(args.inputs):
    treef.Add(fh)
    #if i > 10: break
nEvtsf = treef.GetEntries()
print('N evts in MA ntuple:',nEvtsf)

'''
# Initialize output ntuple
# Merges H4G variables + regressed m_a
if not os.path.isdir(args.outdir):
    os.makedirs(args.outdir)
file_out = ROOT.TFile("%s/%s_mantuple.root"%(args.outdir, args.sample), "RECREATE")
file_out.mkdir("h4gCandidateDumper/trees")
file_out.cd("h4gCandidateDumper/trees")
# Clone TTree structure of H4G ntuple
tree_out = treef.CloneTree(0)
#print(list(tree_out.GetListOfBranches()))

'''
c, h = {}, {}
wd, ht = int(440*1), int(400*1)

k = 'ma0'
c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
h[k] = ROOT.TH1F(k, k, 56, -0.2, 1.2)
#h[k] = ROOT.TH1F(k, k, 48, 0., 1.2)
k = 'ma1'
h[k] = ROOT.TH1F(k, k, 56, -0.2, 1.2)
#h[k] = ROOT.TH1F(k, k, 48, 0., 1.2)
k = 'maxy'
c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
h[k] = ROOT.TH1F(k, k, 56, -0.2, 1.2)

k = 'pt0'
c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
h[k] = ROOT.TH1F(k, k, 50, 20., 170.)
k = 'pt1'
h[k] = ROOT.TH1F(k, k, 50, 20., 170.)

k = 'energy0'
c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
h[k] = ROOT.TH1F(k, k, 50, 20., 170.)
k = 'energy1'
h[k] = ROOT.TH1F(k, k, 50, 20., 170.)

k = 'bdt0'
c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
h[k] = ROOT.TH1F(k, k, 50, -1., 1.)
k = 'bdt1'
h[k] = ROOT.TH1F(k, k, 50, -1., 1.)

k = 'mGG'
c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
h[k] = ROOT.TH1F(k, k, 50, 90., 190.)

k = 'ma0vma1'
c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
#h[k] = ROOT.TH2F(k, k, 48, 0., 1.2, 48, 0., 1.2)
h[k] = ROOT.TH2F(k, k, 56, -0.2, 1.2, 56, -0.2, 1.2)

k = 'pt0vpt1'
c[k] = ROOT.TCanvas("c%s"%k,"c%s"%k,wd,ht)
h[k] = ROOT.TH2F(k, k, 50, 20., 170., 50, 20., 170.)
#'''

# Event range to process
iEvtStart = 0
iEvtEnd   = nEvtsf
#iEvtEnd   = 100

print(">> Getting pt weights: [",iEvtStart,"->",iEvtEnd,")")
for iEvt in range(iEvtStart,iEvtEnd):

    # Initialize event
    if iEvt%10e3==0: print(iEvt,'/',nEvtsf)
    evt_statusf = treef.GetEntry(iEvt)
    if evt_statusf <= 0: continue

    if treef.pho12_m < 100. or  treef.pho12_m > 180.: continue
    if treef.pho12_m > 110. and treef.pho12_m < 140.: continue

    #h['pt0'].Fill(treef.pho1_pt)
    #h['pt1'].Fill(treef.pho2_pt)
    h['pt0vpt1'].Fill(treef.pho1_pt, treef.pho2_pt)

ma_binw = 25. # MeV
diag_w = 200. # MeV

print(">> Processing entries: [",iEvtStart,"->",iEvtEnd,")")
nWrite = 0
sw = ROOT.TStopwatch()
sw.Start()
for iEvt in range(iEvtStart,iEvtEnd):

    # Initialize event
    if iEvt%10e3==0: print(iEvt,'/',nEvtsf)
    evt_statusf = treef.GetEntry(iEvt)
    if evt_statusf <= 0: continue

    # SBlo
    #if treef.pho12_m < 100. or treef.pho12_m > 110.: continue
    # SBlo + SBhi
    if treef.pho12_m < 100. or  treef.pho12_m > 180.: continue
    if treef.pho12_m > 110. and treef.pho12_m < 140.: continue
    # mH
    #if treef.pho12_m <= 110. or treef.pho12_m >= 140.: continue
    #if treef.pho12_m <= 110.: continue
    #if treef.pho1_energy < 100.: continue

    wgt = treef.weight

    h['ma0'].Fill(treef.ma0)
    h['ma1'].Fill(treef.ma1)
    h['pt0'].Fill(treef.pho1_pt)
    h['pt1'].Fill(treef.pho2_pt)
    h['energy0'].Fill(treef.pho1_energy)
    h['energy1'].Fill(treef.pho2_energy)
    h['bdt0'].Fill(treef.pho1_EGMVA)
    h['bdt1'].Fill(treef.pho2_EGMVA)
    h['mGG'].Fill(treef.pho12_m)

    '''
    # Apply blinding:
    # Since pdfs are binned by 25 MeV, blinding of the data should emulate this
    # Binning includes lower edge but not upper edge so must take floor of mass to nearest 25 MeV
    m_pdf_0_floor_25MeV = 25.*(np.floor(1.e3*m_pdf_0_)//25)
    m_pdf_1_floor_25MeV = 25.*(np.floor(1.e3*m_pdf_1_)//25)

    diag_mask = (abs(m_pdf_0_floor_25MeV-m_pdf_1_floor_25MeV) < 200.) #& (m_pdf_0_ >= 0.) & (m_pdf_1_ >= 0.)
    if blind is None:
        mask_blind_pdf = np.full(m_pdf_0_.shape, True)
    elif blind == 'diag':
        mask_blind_pdf = ~diag_mask & (m_pdf_0_ > 0) & (m_pdf_1_ > 0)
    elif blind == 'off':
        mask_blind_pdf = diag_mask #& (m_pdf_0_ > 0) & (m_pdf_1_ > 0)
    elif blind == '!upper':
        mask_blind_pdf = ~diag_mask & (m_pdf_0_floor_25MeV < m_pdf_1_floor_25MeV)
    elif blind == '!lower':
        mask_blind_pdf = ~diag_mask & (m_pdf_0_floor_25MeV > m_pdf_1_floor_25MeV)
    else:
        raise ValueError('Allowed values for blind are: None, diag, off')

    f_unblinded = 1.*len(mask_blind_pdf[mask_blind_pdf == True])/len(mask_blind_pdf)
    print('%f of values unblinded'%f_unblinded)

    m_pdf_0_, m_pdf_1_ = m_pdf_0_[mask_blind_pdf], m_pdf_1_[mask_blind_pdf]
    '''
    ma0_flr = ma_binw*(np.floor(1.e3*treef.ma0)//ma_binw) # MeV
    ma1_flr = ma_binw*(np.floor(1.e3*treef.ma1)//ma_binw) # MeV
    is_diag = abs(ma0_flr - ma1_flr) < diag_w # MeV
    is_pos  = (ma0_flr > 0.) and (ma1_flr > 0.)

    if not is_diag: continue
    if not is_pos: continue

    h['ma0vma1'].Fill(treef.ma0, treef.ma1)
    h['maxy'].Fill(treef.ma0, wgt)
    h['maxy'].Fill(treef.ma1, wgt)

    nWrite += 1

sw.Stop()
print(">> N events written: %d / %d"%(nWrite, nEvtsf))
print(">> Real time:",sw.RealTime()/60.,"minutes")
print(">> CPU time: ",sw.CpuTime() /60.,"minutes")

'''
file_out.cd("h4gCandidateDumper")
for k in h.keys():
    h[k].Write()

file_out.Write()
file_out.Close()
'''

sample = 'Data'
#makeplots = True
makeplots = False

def set_hist(h, c, xtitle, ytitle, htitle):
    c.SetLeftMargin(0.16)
    c.SetRightMargin(0.15)
    c.SetBottomMargin(0.13)
    ROOT.gStyle.SetOptStat(0)

    h.GetXaxis().SetLabelSize(0.04)
    h.GetXaxis().SetLabelFont(62)
    h.GetXaxis().SetTitle(xtitle)
    h.GetXaxis().SetTitleOffset(0.09)
    h.GetXaxis().SetTitleSize(0.06)
    h.GetXaxis().SetTitleFont(62)

    h.GetYaxis().SetLabelSize(0.04)
    h.GetYaxis().SetLabelFont(62)
    h.GetYaxis().SetTitleOffset(1.2)
    h.GetYaxis().SetTitleSize(0.06)
    h.GetYaxis().SetTitleFont(62)
    h.GetYaxis().SetTitle(ytitle)

    h.SetTitleSize(0.04)
    h.SetTitleFont(62)
    h.SetTitle(htitle)
    h.SetTitleOffset(1.2)

    return h, c

mass_line = 0.135

hc, legend, l, l2, hatch = {}, {}, {}, {}, {}
err_style = 'E2'
fill_style = 3002

k = 'ma0'
c[k].cd()
h[k], c[k] = set_hist(h[k], c[k], "m_{a,pred} [GeV]", "N_{a}", "")
h[k].GetXaxis().SetTitleOffset(0.9)
h[k].GetXaxis().SetTitleSize(0.06)
h[k].SetLineColor(9)
#h[k].Draw("hist")
h[k].SetFillColor(9)
h[k].SetFillStyle(fill_style)
h[k].Draw("%s"%err_style)
hc[k] = h[k].Clone()
hc[k].SetLineColor(9)
hc[k].SetFillStyle(0)
hc[k].Draw("hist same")
k = 'ma1'
h[k].SetLineColor(2)
#h[k].Draw("hist SAME")
h[k].SetFillColor(2)
h[k].SetFillStyle(fill_style)
h[k].Draw("%s same"%err_style)
hc[k] = h[k].Clone()
hc[k].SetLineColor(2)
hc[k].SetFillStyle(0)
hc[k].Draw("hist same")

ymax = 1.2*max(h['ma0'].GetMaximum(), h['ma1'].GetMaximum())
#ymax = 6800.
#ymax = 9000.
#ymax = 2500.
#ymax = 7000.

h['ma0'].GetYaxis().SetRangeUser(0., ymax)

l[k] = ROOT.TLine(mass_line, 0., mass_line, ymax) # x0,y0, x1,y1
l[k].SetLineColor(14)
l[k].SetLineStyle(7)
l[k].Draw("same")

#'''
l2[k] = ROOT.TLine(0.55, 0., 0.55, ymax) # x0,y0, x1,y1
l2[k].SetLineColor(14)
l2[k].SetLineStyle(7)
l2[k].Draw("same")
#'''

hatch[k] = ROOT.TGraph(2, array('d',[0.,0.]), array('d',[0.,ymax]));
hatch[k].SetLineColor(14)
hatch[k].SetLineWidth(2001)
hatch[k].SetFillStyle(3004)
hatch[k].SetFillColor(14)
hatch[k].Draw("same")

k = 'ma0'
legend[k] = ROOT.TLegend(0.5,0.68,0.8,0.86) #(x1, y1, x2, y2)
legend[k].AddEntry(h[k].GetName(),"lead p_{T}","l")
legend[k].AddEntry('ma1',"sub-lead p_{T}","l")
legend[k].SetBorderSize(0)
legend[k].Draw("same")
#c[k].SetGrid()
c[k].Draw()
c[k].Update()
if makeplots:
    c[k].Print('plots/%s_%s_e2e.eps'%(k, sample))
##############################
k = 'ma0vma1'
c[k].cd()
#h[k], c[k] = set_hist(h[k], c[k], "m_{a-lead,pred} [GeV]", "m_{a-sublead,pred} [GeV]", "m_{a_{1},pred} vs. m_{a_{0},pred}")
h[k], c[k] = set_hist(h[k], c[k], "m_{a_{1},pred} [GeV]", "m_{a_{2},pred} [GeV]", "")
ROOT.gPad.SetRightMargin(0.17)
ROOT.gStyle.SetPalette(55)#53
h[k].GetZaxis().SetTitle("Events")
h[k].GetZaxis().SetTitleOffset(1.1)
h[k].GetZaxis().SetTitleSize(0.05)
h[k].GetZaxis().SetTitleFont(62)
h[k].GetZaxis().SetLabelSize(0.04)
h[k].GetZaxis().SetLabelFont(62)
h[k].GetXaxis().SetTitleOffset(0.9)
h[k].GetYaxis().SetTitleOffset(1.1)
h[k].GetXaxis().SetTitleSize(0.06)
h[k].GetYaxis().SetTitleSize(0.06)
h[k].Draw("COL Z")
#h[k].SetMaximum(350.)
#h[k].SetMaximum(680.)
#h[k].SetMaximum(175.)
#h[k].SetMaximum(340.)
c[k].Draw()
c[k].Update()
palette = h[k].GetListOfFunctions().FindObject("palette")
palette.SetX1NDC(0.84)
palette.SetX2NDC(0.89)
palette.SetY1NDC(0.13)
if makeplots:
    pass
    c[k].Print('plots/%s_%s_e2e.eps'%(k, sample))
##############################
k = 'mGG'
c[k].cd()
h[k], c[k] = set_hist(h[k], c[k], "m_{#Gamma,#Gamma} [GeV]", "N_{a}", "")
#h[k].GetYaxis().SetRangeUser(0., 18000.)
h[k].GetXaxis().SetTitleOffset(0.9)
h[k].GetXaxis().SetTitleSize(0.06)
h[k].SetLineColor(9)
h[k].SetFillColor(9)
h[k].SetFillStyle(fill_style)
h[k].Draw("%s"%err_style)
hc[k] = h[k].Clone()
hc[k].SetLineColor(9)
hc[k].SetFillStyle(0)
hc[k].Draw("hist same")
c[k].Draw()
c[k].Update()
##############################
k = 'pt0'
c[k].cd()
h[k], c[k] = set_hist(h[k], c[k], "p_{T,a} [GeV]", "N_{a}", "")
h[k].GetXaxis().SetTitleOffset(0.9)
h[k].GetXaxis().SetTitleSize(0.06)
h[k].SetLineColor(9)
#h[k].Draw("hist")
h[k].SetFillColor(9)
h[k].SetFillStyle(fill_style)
h[k].Draw("%s"%err_style)
hc[k] = h[k].Clone()
hc[k].SetLineColor(9)
hc[k].SetFillStyle(0)
hc[k].Draw("hist same")
k = 'pt1'
h[k].SetLineColor(2)
#h[k].Draw("hist SAME")
h[k].SetFillColor(2)
h[k].SetFillStyle(fill_style)
h[k].Draw("%s same"%err_style)
hc[k] = h[k].Clone()
hc[k].SetLineColor(2)
hc[k].SetFillStyle(0)
hc[k].Draw("hist same")

ymax = 1.2*max(h['pt0'].GetMaximum(), h['pt1'].GetMaximum())
h['pt0'].GetYaxis().SetRangeUser(0., ymax)

k = 'pt0'
legend[k] = ROOT.TLegend(0.5,0.68,0.8,0.86) #(x1, y1, x2, y2)
legend[k].AddEntry(h[k].GetName(),"lead p_{T}","l")
legend[k].AddEntry('pt1',"sub-lead p_{T}","l")
legend[k].SetBorderSize(0)
legend[k].Draw("same")
#c[k].SetGrid()
c[k].Draw()
c[k].Update()
if makeplots:
    c[k].Print('plots/%s_%s_e2e.eps'%(k, sample))
##############################
k = 'energy0'
c[k].cd()
h[k], c[k] = set_hist(h[k], c[k], "E_{a} [GeV]", "N_{a}", "")
h[k].GetXaxis().SetTitleOffset(0.9)
h[k].GetXaxis().SetTitleSize(0.06)
h[k].SetLineColor(9)
#h[k].Draw("hist")
h[k].SetFillColor(9)
h[k].SetFillStyle(fill_style)
h[k].Draw("%s"%err_style)
hc[k] = h[k].Clone()
hc[k].SetLineColor(9)
hc[k].SetFillStyle(0)
hc[k].Draw("hist same")
k = 'energy1'
h[k].SetLineColor(2)
#h[k].Draw("hist SAME")
h[k].SetFillColor(2)
h[k].SetFillStyle(fill_style)
h[k].Draw("%s same"%err_style)
hc[k] = h[k].Clone()
hc[k].SetLineColor(2)
hc[k].SetFillStyle(0)
hc[k].Draw("hist same")

ymax = 1.2*max(h['energy0'].GetMaximum(), h['energy1'].GetMaximum())
h['energy0'].GetYaxis().SetRangeUser(0., ymax)

k = 'energy0'
legend[k] = ROOT.TLegend(0.5,0.68,0.8,0.86) #(x1, y1, x2, y2)
legend[k].AddEntry(h[k].GetName(),"lead p_{T}","l")
legend[k].AddEntry('energy1',"sub-lead p_{T}","l")
legend[k].SetBorderSize(0)
legend[k].Draw("same")
#c[k].SetGrid()
c[k].Draw()
c[k].Update()
if makeplots:
    c[k].Print('plots/%s_%s_e2e.eps'%(k, sample))
##############################
k = 'bdt0'
c[k].cd()
h[k], c[k] = set_hist(h[k], c[k], "MVA_{#Gamma}", "N_{a}", "")
h[k].GetXaxis().SetTitleOffset(0.9)
h[k].GetXaxis().SetTitleSize(0.06)
h[k].SetLineColor(9)
#h[k].Draw("hist")
h[k].SetFillColor(9)
h[k].SetFillStyle(fill_style)
h[k].Draw("%s"%err_style)
hc[k] = h[k].Clone()
hc[k].SetLineColor(9)
hc[k].SetFillStyle(0)
hc[k].Draw("hist same")
k = 'bdt1'
h[k].SetLineColor(2)
#h[k].Draw("hist SAME")
h[k].SetFillColor(2)
h[k].SetFillStyle(fill_style)
h[k].Draw("%s same"%err_style)
hc[k] = h[k].Clone()
hc[k].SetLineColor(2)
hc[k].SetFillStyle(0)
hc[k].Draw("hist same")

ymax = 1.2*max(h['bdt0'].GetMaximum(), h['bdt1'].GetMaximum())
h['bdt0'].GetYaxis().SetRangeUser(0., ymax)

k = 'bdt0'
legend[k] = ROOT.TLegend(0.5,0.68,0.8,0.86) #(x1, y1, x2, y2)
legend[k].AddEntry(h[k].GetName(),"lead p_{T}","l")
legend[k].AddEntry('bdt1',"sub-lead p_{T}","l")
legend[k].SetBorderSize(0)
legend[k].Draw("same")
#c[k].SetGrid()
c[k].Draw()
c[k].Update()
if makeplots:
    c[k].Print('plots/%s_%s_e2e.eps'%(k, sample))
##############################
k = 'pt0vpt1'
c[k].cd()
h[k], c[k] = set_hist(h[k], c[k], "p_{T,a_{1},pred} [GeV]", "p_{T,a_{2},pred} [GeV]", "")
ROOT.gPad.SetRightMargin(0.17)
ROOT.gStyle.SetPalette(55)#53
h[k].GetZaxis().SetTitle("Events")
h[k].GetZaxis().SetTitleOffset(1.1)
h[k].GetZaxis().SetTitleSize(0.05)
h[k].GetZaxis().SetTitleFont(62)
h[k].GetZaxis().SetLabelSize(0.04)
h[k].GetZaxis().SetLabelFont(62)
h[k].GetXaxis().SetTitleOffset(0.9)
h[k].GetYaxis().SetTitleOffset(1.1)
h[k].GetXaxis().SetTitleSize(0.06)
h[k].GetYaxis().SetTitleSize(0.06)
h[k].Draw("COL Z")
#h[k].SetMaximum(350.)
#h[k].SetMaximum(680.)
#h[k].SetMaximum(175.)
#h[k].SetMaximum(340.)
c[k].Draw()
c[k].Update()
palette = h[k].GetListOfFunctions().FindObject("palette")
palette.SetX1NDC(0.84)
palette.SetX2NDC(0.89)
palette.SetY1NDC(0.13)
if makeplots:
    pass
    c[k].Print('plots/%s_%s_e2e.eps'%(k, sample))
##############################
k = 'maxy'
c[k].cd()
h[k], c[k] = set_hist(h[k], c[k], "m_{a,pred} [GeV]", "N_{a}", "")
h[k].GetXaxis().SetTitleOffset(0.9)
h[k].GetXaxis().SetTitleSize(0.06)
h[k].SetLineColor(9)
#h[k].Draw("hist")
h[k].SetFillColor(9)
h[k].SetFillStyle(fill_style)
h[k].Draw("%s"%err_style)
hc[k] = h[k].Clone()
hc[k].SetLineColor(9)
hc[k].SetFillStyle(0)
hc[k].Draw("hist same")

ymax = 1.2*h[k].GetMaximum()
h[k].GetYaxis().SetRangeUser(0., ymax)

l[k] = ROOT.TLine(mass_line, 0., mass_line, ymax) # x0,y0, x1,y1
l[k].SetLineColor(14)
l[k].SetLineStyle(7)
l[k].Draw("same")

#'''
l2[k] = ROOT.TLine(0.55, 0., 0.55, ymax) # x0,y0, x1,y1
l2[k].SetLineColor(14)
l2[k].SetLineStyle(7)
l2[k].Draw("same")
#'''

hatch[k] = ROOT.TGraph(2, array('d',[0.,0.]), array('d',[0.,ymax]));
hatch[k].SetLineColor(14)
hatch[k].SetLineWidth(2001)
hatch[k].SetFillStyle(3004)
hatch[k].SetFillColor(14)
hatch[k].Draw("same")

'''
legend[k] = ROOT.TLegend(0.5,0.68,0.8,0.86) #(x1, y1, x2, y2)
legend[k].AddEntry(h[k].GetName(),"lead p_{T}","l")
legend[k].AddEntry('ma1',"sub-lead p_{T}","l")
legend[k].SetBorderSize(0)
legend[k].Draw("same")
'''
#c[k].SetGrid()
c[k].Draw()
c[k].Update()
if makeplots:
    c[k].Print('plots/%s_%s_e2e.eps'%(k, sample))
##############################
#blue: leading
#red: sub-leading

