import numpy as np
import ROOT

import CMS_lumi#, tdrstyle
#tdrstyle.setTDRStyle()
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
#change the CMS_lumi variables (see CMS_lumi.py)
CMS_lumi.writeExtraText = 1
CMS_lumi.extraText = "Simulation"
iPeriod = 0
iPos = 0
if( iPos==0 ): CMS_lumi.relPosX = 0.17

histname = "dPhidEta_GG"
hist = "fevt/%s"%histname

xtalWindow = 4
xtalWidth = 0.0174

eosDir = '/eos/uscms/store/user/lpcml/mandrews/IMG/dPhidEta'
#eosDir = 'root://cmseos.fnal.gov//store/user/lpcml/mandrews/IMG/dPhidEta'

masses = [100, 400, 1000]
#masses = [100]

for mass in masses:

    sample = '%dMeV'%mass if mass < 1000 else '%dGeV'%(mass/1000.)
    print ' >> Sample:',sample

    decay = 'h24gamma_1j_1M_%s_PU2017_ext3'%sample

    t_in = ROOT.TFile('%s/%s_IMG_numEvent100000.root'%(eosDir, decay), 'READ')
    h_in = ROOT.gDirectory.Get(hist)
    # TODO: fix bug in SCRegressor::fillH2aaSel() where dPhi is *signed* difference
    # i.e. missing an abs(). Approx. half of samples have dPhi < 0
    # that fall in underflow. Normalize instead by Integral().
    print " >> N entries:",h_in.GetEntries()
    print " >> N integral:",h_in.Integral()
    # N entries in xtalWindow
    nROI = 0
    for ix in range(1,xtalWindow+1):
        for iy in range(1,xtalWindow+1):
            nROI += h_in.GetBinContent(ix, iy)
    print " >> N ROI:",nROI

    #nTot = 0
    #for ix in range(0,h_in.GetNbinsX()+2):
    #    #print(sum([h_in.GetBinContent(ix, iy_) for iy_ in range(h_in.GetNbinsY()+2)]))
    #    for iy in range(0,h_in.GetNbinsY()+2):
    #        print('ix:%d, iy:%d, %d'%(ix, iy, h_in.GetBinContent(ix, iy)))
    #        nTot += h_in.GetBinContent(ix, iy)
    #print " >> N total:",nTot

    # Define normalization:
    #h_in.Scale(1./h_in.GetEntries())
    h_in.Scale(1./h_in.Integral())
    #h_in.Scale(1./nROI)

    c = ROOT.TCanvas("c","c",680,600)
    c.SetBorderSize(0);
    c.SetFrameBorderMode(0)
    ROOT.gStyle.SetTitleBorderSize(0)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPalette(55)
    #ROOT.gStyle.SetPalette(104)
    #ROOT.gStyle.SetPalette(53)
    #ROOT.gPad.SetLogy()
    c.cd()

    ROOT.gPad.SetLeftMargin(0.15)
    ROOT.gPad.SetRightMargin(0.2)
    ROOT.gPad.SetBottomMargin(0.18)
    ROOT.gPad.SetTopMargin(0.08)

    ymax = 0.18
    h_in.SetTitle('')
    #h_in.SetTitle('#DeltaR(#gamma,#Gamma)')
    #h_in.SetTitle('f_{N_{#gamma} #geq 2}(m_{#pi},p_{T,#pi})_{reco}')
    #h_in.SetTitle('f_{N_{#gamma} #geq 2}(#Delta#phi,#Delta#eta)_{reco}')
    #h_in.SetTitle('A#rightarrow#gamma#gamma | f(#Delta#phi,#Delta#eta)')
    #h_in.SetTitle('p_{T,#gamma}/p_{T,#Gamma}(#Delta#phi,#Delta#eta)_{reco}')
    #h_in.SetLineColor(2)

    txtFont = 62 #bold
    txtFont = 42 #regular
    h_in.GetYaxis().SetLabelSize(0.05)
    h_in.GetYaxis().SetLabelFont(txtFont)
    #h_in.GetYaxis().SetTitle("#Deltai#eta(#gamma,#gamma)_{gen}")
    h_in.GetYaxis().SetTitle("#Delta#eta(#gamma_{1},#gamma_{2})^{gen}")
    h_in.GetYaxis().SetTitleOffset(0.9)
    h_in.GetYaxis().SetTitleSize(0.06)
    h_in.GetYaxis().SetTitleFont(txtFont)
    h_in.GetYaxis().SetRangeUser(0.,xtalWindow*xtalWidth)

    h_in.GetXaxis().SetLabelSize(0.05)
    h_in.GetXaxis().SetLabelFont(txtFont)
    #h_in.GetXaxis().SetTitle("#Deltai#varphi(#gamma,#gamma)_{gen}")
    h_in.GetXaxis().SetTitle("#Delta#phi(#gamma_{1},#gamma_{2})^{gen}")
    h_in.GetXaxis().SetTitleOffset(1.2)
    h_in.GetXaxis().SetTitleSize(0.06)
    h_in.GetXaxis().SetTitleFont(txtFont)
    h_in.GetXaxis().SetRangeUser(0.,xtalWindow*xtalWidth)

    #h_in.GetZaxis().SetTitle("f_{events}")
    h_in.GetZaxis().SetTitle("f_{a#rightarrow#gamma#gamma}")
    h_in.GetZaxis().SetTitleOffset(1.05)
    h_in.GetZaxis().SetTitleSize(0.06)
    h_in.GetZaxis().SetTitleFont(txtFont)
    h_in.GetZaxis().SetLabelSize(0.05)
    h_in.GetZaxis().SetLabelFont(txtFont)
    h_in.GetZaxis().SetNdivisions(5);

    h_in.SetMarkerColor(0)
    h_in.SetContour(100)
    #h_in.Draw("")
    #h_in.Draw("COL Z")
    h_in.Draw("COL Z TEXT")
    #h_in.SetMaximum(2)
    #h_in.SetMaximum(0.2)
    h_in.SetMaximum(1.)
    h_in.SetMarkerSize(2.4)
    #h_in.SetMaximum(500)
    ROOT.gStyle.SetPaintTextFormat('0.2f')

    # Draw xtal grid lines
    lines_phi = {}
    for i,iphi in enumerate(np.arange(xtalWindow+1)):
        #print(i)
        lines_phi[i] = ROOT.TLine(i*xtalWidth, 0., i*xtalWidth, xtalWindow*xtalWidth) # x0,y0, x1,y1
        #lines_phi[i].SetLineColor(14)
        lines_phi[i].SetLineColor(0)
        lines_phi[i].SetLineStyle(7)
        lines_phi[i].Draw("same")

    lines_eta = {}
    for i,ieta in enumerate(np.arange(xtalWindow+1)):
        #print(i)
        lines_eta[i] = ROOT.TLine(0., i*xtalWidth, xtalWindow*xtalWidth, i*xtalWidth) # x0,y0, x1,y1
        #lines_eta[i].SetLineColor(14)
        lines_eta[i].SetLineColor(0)
        lines_eta[i].SetLineStyle(7)
        lines_eta[i].Draw("same")

    ax = h_in.GetXaxis()
    ax.SetNdivisions(-004);
    ay = h_in.GetYaxis()
    ay.SetNdivisions(-004);
    # Express axis labels in crystal dR(iphi,ieta)
    # instead of physical dR(phi, eta)
    for i in range(xtalWindow+1):
        ax.ChangeLabel(i+1,-1,-1,-1,-1,-1,"%d"%(i))
        ay.ChangeLabel(i+1,-1,-1,-1,-1,-1,"%d"%(i))

    # Redraw axes
    ROOT.gPad.RedrawAxis()
    ROOT.gPad.Update()

    # CMS label
    CMS_lumi.lumi_sqrtS = "m(a) = %s"%sample.replace('GeV',' GeV').replace('MeV',' MeV') # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
    CMS_lumi.CMS_lumi(c, iPeriod, iPos)
    c.Draw()
    c.Update()

    #c.Print('Plots/%s_%s_xtal.png'%(decay, histname))
    #c.Print('Plots/%s_%s_xtal.eps'%(decay, histname))
    c.Print('Plots/%s_%s_xtal.pdf'%(decay, histname))
