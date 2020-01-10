import os, glob
import ROOT
from ROOT import TFile, TTree, TCanvas, TGraph, TMultiGraph, TGraphErrors, TLegend
from multiprocessing import Pool
from collections import OrderedDict
import argparse

parser = argparse.ArgumentParser(description='Run h2aa limit setting.')
parser.add_argument('--no_fit', action='store_true', help='Switch to skip limit fitting.')
args = parser.parse_args()

def run_combine(process):
    os.system('combine %s'%process)

samples = [
    '0p1'
    ,'0p4'
    ,'1'
    ] # GeV

fitalgo = 'AsymptoticLimits'
processes = ['-M %s Datacards/h4g_MA_.txt --keyword-value MA=%sGeV'%(fitalgo, s) for s in samples]

do_fit = not args.no_fit
if do_fit:
    print('Doing limit fitting.')
    pool = Pool(processes=len(processes))
    pool.map(run_combine, processes)
    pool.close()
    pool.join()

def get_limitfile_mass(f):
    mass = f.split('.')[-2].replace('MA','').replace('GeV','')
    return mass

# NOTE: an extra `scale` needed to be applied when running `run_sg_yield.py` for limit setting here to converge.
# => Need to undo this `scale` when making the actual plots!!!
def get_limits(f, scale=1.e-3):

    tree = ROOT.TChain("limit")
    tree.Add(f)
    n_limit_pts = tree.GetEntries()
    print(n_limit_pts)
    assert n_limit_pts == 6

    pts = ['dn2', 'dn1', 'nom', 'up1', 'up2', 'obs']

    limit_pts = {}
    for i,pt in enumerate(pts):
        tree.GetEntry(i)
        limit_pts[pt] = scale*tree.limit
        if i == 2:
            print(limit_pts[pt])

    return limit_pts

sample_limits = OrderedDict()
for s in samples:
    fs = glob.glob('higgsCombineTest.%s.mH120.MA%sGeV.root'%(fitalgo, s))
    assert len(fs) == 1
    sample_limits[s] = get_limits(fs[0])

# Plot limits
def plotUpperLimits(sample_limits):
    # adapted from: https://wiki.physik.uzh.ch/cms/limits:brazilianplotexample
    # see CMS plot guidelines: https://ghm.web.cern.ch/ghm/plots/
    labels = list(sample_limits.keys())
    print(labels)
    values = [float(label.replace('p','.')) for label in labels]

    N = len(labels)
    yellow = TGraph(2*N)    # yellow band
    green = TGraph(2*N)     # green band
    median = TGraph(N)      # median line

    up2s = [ ]
    for i in range(N):
        #file_name = "higgsCombine"+labels[i]+"Asymptotic.mH125.root"
        #limit = getLimits(file_name)
        limit = sample_limits[labels[i]]
        up2s.append(limit['up2'])
        yellow.SetPoint(    i,    values[i], limit['up2'] ) # + 2 sigma
        green.SetPoint(     i,    values[i], limit['up1'] ) # + 1 sigma
        median.SetPoint(    i,    values[i], limit['nom'] ) # median
        green.SetPoint(  2*N-1-i, values[i], limit['dn1'] ) # - 1 sigma
        yellow.SetPoint( 2*N-1-i, values[i], limit['dn2'] ) # - 2 sigma

    W = 800
    H  = 600
    T = 0.08*H
    B = 0.12*H
    L = 0.12*W
    R = 0.04*W
    c = TCanvas("c","c",100,100,W,H)
    c.SetFillColor(0)
    c.SetBorderMode(0)
    c.SetFrameFillStyle(0)
    c.SetFrameBorderMode(0)
    c.SetLeftMargin( L/W )
    c.SetRightMargin( R/W )
    c.SetTopMargin( T/H )
    c.SetBottomMargin( B/H )
    c.SetTickx(0)
    c.SetTicky(0)
    c.SetGrid()
    c.cd()
    frame = c.DrawFrame(1.4,0.001, 4.1, 10)
    frame.GetYaxis().CenterTitle()
    frame.GetYaxis().SetTitleSize(0.05)
    frame.GetXaxis().SetTitleSize(0.05)
    frame.GetXaxis().SetLabelSize(0.04)
    frame.GetYaxis().SetLabelSize(0.04)
    frame.GetYaxis().SetTitleOffset(1.1)
    frame.GetYaxis().SetMaxDigits(3)
    #frame.GetXaxis().SetNdivisions(508)
    frame.GetYaxis().CenterTitle(True)
    #frame.GetYaxis().SetTitle("95% upper limit on #sigma / #sigma_{SM}")
    #frame.GetYaxis().SetTitle("95% upper limit on #sigma #times BR / (#sigma #times BR)_{SM}")
    frame.GetYaxis().SetTitle("95% upper limit on #sigma_{h} #times BR / #sigma_{h}")
    #frame.GetXaxis().SetTitle("background systematic uncertainty [%]")
    frame.GetXaxis().SetTitle("m_{a} [GeV]")
    frame.SetMinimum(0)
    #frame.SetMaximum(max(up2s)*1.05)
    frame.SetMaximum(max(up2s)*1.4)
    #frame.SetMinimum(1.e-4)
    #frame.SetMaximum(1.e-2)
    #ROOT.gPad.SetLogy()
    #frame.GetXaxis().SetLimits(min(values),max(values))
    frame.GetXaxis().SetLimits(0., 1.2) # GeV

    yellow.SetFillColor(ROOT.kOrange)
    yellow.SetLineColor(ROOT.kOrange)
    yellow.SetFillStyle(1001)
    yellow.Draw('F')

    green.SetFillColor(ROOT.kGreen+1)
    green.SetLineColor(ROOT.kGreen+1)
    green.SetFillStyle(1001)
    green.Draw('Fsame')

    median.SetLineColor(1)
    median.SetLineWidth(2)
    median.SetLineStyle(2)
    median.Draw('Lsame')

    #CMS_lumi.CMS_lumi(c,14,11)
    #ROOT.gPad.SetTicks(1,1)
    #frame.Draw('sameaxis')

    x1 = 0.15
    x2 = x1 + 0.24
    y2 = 0.86
    y1 = 0.70
    legend = TLegend(x1,y1,x2,y2)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.041)
    legend.SetTextFont(42)
    legend.AddEntry(median, "Asymptotic CL_{s} expected",'L')
    legend.AddEntry(green, "#pm 1 std. deviation",'f')
    #legend.AddEntry(green, "Asymptotic CL_{s} #pm 1 std. deviation",'f')
    legend.AddEntry(yellow,"#pm 2 std. deviation",'f')
    #legend.AddEntry(green, "Asymptotic CL_{s} #pm 2 std. deviation",'f')
    legend.Draw()

    print " "
    c.Draw()
    c.Update()
    c.Print("Plots/UpperLimits%s.eps"%(''))
    #c.Close()

plotUpperLimits(sample_limits)
