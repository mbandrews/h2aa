import ROOT
import numpy as np
from array import array

def create_hists(h):

    k = 'ma0'

    ma_bins = list(range(0,1200+25,25))
    ma_bins = [-400]+ma_bins
    ma_bins = [float(m)/1.e3 for m in ma_bins]
    #print(len(ma_bins))
    ma_bins = array('d', ma_bins)
    #print(ma_bins)

    #h[k] = ROOT.TH1F(k, k, 48, 0., 1.2)
    #h[k] = ROOT.TH1F(k, k, 56, -0.2, 1.2)
    h[k] = ROOT.TH1F(k, k, 49, ma_bins)
    k = 'ma1'
    #h[k] = ROOT.TH1F(k, k, 48, 0., 1.2)
    #h[k] = ROOT.TH1F(k, k, 56, -0.2, 1.2)
    h[k] = ROOT.TH1F(k, k, 49, ma_bins)
    k = 'ma0vma1'
    #h[k] = ROOT.TH2F(k, k, 48, 0., 1.2, 48, 0., 1.2)
    #h[k] = ROOT.TH2F(k, k, 56, -0.2, 1.2, 56, -0.2, 1.2)
    h[k] = ROOT.TH2F(k, k, 49, ma_bins, 49, ma_bins)
    k = 'maxy'
    #h[k] = ROOT.TH1F(k, k, 56, -0.2, 1.2)
    h[k] = ROOT.TH1F(k, k, 49, ma_bins)

    #k = 'pt0'
    #h[k] = ROOT.TH1F(k, k, 50, 20., 170.)
    #k = 'pt1'
    #h[k] = ROOT.TH1F(k, k, 50, 20., 170.)
    #k = 'pt0vpt1'
    #h[k] = ROOT.TH2F(k, k, 50, 20., 170., 50, 20., 170.)

    pt_bins_ = {}
    dPt = 1
    #pt_bins_[0] = np.arange(26,100,dPt)
    pt_bins_[0] = np.arange(25,100,dPt)
    dPt = 5
    pt_bins_[1] = np.arange(100,120,dPt)
    dPt = 20
    pt_bins_[2] = np.arange(120,200,dPt)
    dPt = 750-200
    pt_bins_[3] = np.arange(200,750+dPt,dPt)

    pt_bins = np.concatenate([pt_bin_ for pt_bin_ in pt_bins_.values()])
    n_pt_bins = len(pt_bins)-1
    pt_bins = array('d', list(pt_bins))

    k = 'pt0'
    h[k] = ROOT.TH1F(k, k, n_pt_bins, pt_bins)
    k = 'pt1'
    h[k] = ROOT.TH1F(k, k, n_pt_bins, pt_bins)
    k = 'pt0vpt1'
    h[k] = ROOT.TH2F(k, k, n_pt_bins, pt_bins, n_pt_bins, pt_bins)
    k = 'ptxy'
    h[k] = ROOT.TH1F(k, k, n_pt_bins, pt_bins)

    k = 'energy0'
    h[k] = ROOT.TH1F(k, k, 50, 20., 170.)
    k = 'energy1'
    h[k] = ROOT.TH1F(k, k, 50, 20., 170.)

    k = 'bdt0'
    h[k] = ROOT.TH1F(k, k, 50, -1., 1.)
    k = 'bdt1'
    h[k] = ROOT.TH1F(k, k, 50, -1., 1.)
    k = 'bdtxy'
    h[k] = ROOT.TH1F(k, k, 50, -1., 1.)

    k = 'mGG'
    h[k] = ROOT.TH1F(k, k, 50, 90., 190.)

    k = 'wgt'
    #h[k] = ROOT.TH1F(k, k, 50, 0., 50.)
    h[k] = ROOT.TH1F(k, k, 300, -600., 600.)

def create_cut_hists(h, cuts):

    for c in cuts:

        cut = c+'_'
        h[cut+'npho'] = ROOT.TH1F(cut+'npho', cut+'npho', 10, 0., 10.)
        h[cut+'pt'] = ROOT.TH1F(cut+'pt', cut+'pt', 50, 0., 150.)
        h[cut+'eta'] = ROOT.TH1F(cut+'eta', cut+'eta', 50, -3., 3.)
        h[cut+'phi'] = ROOT.TH1F(cut+'phi', cut+'phi', 50, -3.14, 3.14)
        h[cut+'bdt'] = ROOT.TH1F(cut+'bdt', cut+'bdt', 50, -1., 1.)
        h[cut+'phoIso'] = ROOT.TH1F(cut+'phoIso', cut+'phoIso', 50, 0., 10.)
        h[cut+'chgIso'] = ROOT.TH1F(cut+'chgIso', cut+'chgIso', 50, 0., 10.)
        h[cut+'r9'] = ROOT.TH1F(cut+'r9', cut+'r9', 50, 0., 1.2)
        h[cut+'sieie'] = ROOT.TH1F(cut+'sieie', cut+'sieie', 50, 0., 0.1)
        h[cut+'hoe'] = ROOT.TH1F(cut+'hoe', cut+'hoe', 50, 0., 0.2)
        #h[cut+'HLTDipho_m90'] = ROOT.TH1F(cut+'HLTDipho_m90', cut+'HLTDipho_m90', 2, 0., 2.)
        h[cut+'HLTDiphoPV_m55'] = ROOT.TH1F(cut+'HLTDiphoPV_m55', cut+'HLTDiphoPV_m55', 2, 0., 2.)
        #h[cut+'wgt'] = ROOT.TH1F(cut+'wgt', cut+'wgt', 50, 0., 100.)

        #if 'mgg' in c:
        h[cut+'mgg'] = ROOT.TH1F(cut+'mgg', cut+'mgg', 50, 50., 200.)

def fill_cut_hists(h, tree, cut_, outvars=None):

    cut = cut_+'_'

    h[cut+'npho'].Fill(tree.nPho)

    for i in range(tree.nPho):
        h[cut+'pt'].Fill(tree.phoEt[i])
        h[cut+'eta'].Fill(tree.phoEta[i])
        h[cut+'phi'].Fill(tree.phoPhi[i])
        h[cut+'bdt'].Fill(tree.phoIDMVA[i])
        h[cut+'phoIso'].Fill(tree.phoPFPhoIso[i])
        h[cut+'chgIso'].Fill(tree.phoPFChIso[i])
        h[cut+'r9'].Fill(tree.phoR9Full5x5[i])
        h[cut+'sieie'].Fill(tree.phoSigmaIEtaIEtaFull5x5[i])
        h[cut+'hoe'].Fill(tree.phoHoverE[i])
        #h[cut+'HLTDipho_m90'].Fill(tree.HLTPho>>14&1)
        #h[cut+'HLTDiphoPV_m55'].Fill(tree.HLTPho>>37&1)
        h[cut+'HLTDiphoPV_m55'].Fill((tree.HLTPho>>37&1) or (tree.HLTPho>>16&1))

    if outvars is not None:
        if 'mgg' in outvars.keys():
            h[cut+'mgg'].Fill(outvars['mgg'])


def fill_hists(h, tree, wgt):

    h['wgt'].Fill(wgt)

    h['ma0'].Fill(tree.ma0, wgt)
    h['ma1'].Fill(tree.ma1, wgt)
    h['ma0vma1'].Fill(tree.ma0, tree.ma1, wgt)
    h['maxy'].Fill(tree.ma0, wgt)
    h['maxy'].Fill(tree.ma1, wgt)

    #h['pt0'].Fill(tree.pho1_pt)
    #h['pt1'].Fill(tree.pho2_pt)
    #h['pt0vpt1'].Fill(tree.pho1_pt, tree.pho2_pt)

    #h['energy0'].Fill(tree.pho1_energy)
    #h['energy1'].Fill(tree.pho2_energy)

    #h['bdt0'].Fill(tree.pho1_EGMVA)
    #h['bdt1'].Fill(tree.pho2_EGMVA)

    #h['mGG'].Fill(tree.pho12_m)

    assert tree.phoEt[0] > tree.phoEt[1]
    h['pt0'].Fill(tree.phoEt[0], wgt)
    h['pt1'].Fill(tree.phoEt[1], wgt)
    h['pt0vpt1'].Fill(tree.phoEt[0], tree.phoEt[1], wgt)
    h['ptxy'].Fill(tree.phoEt[0], wgt)
    h['ptxy'].Fill(tree.phoEt[1], wgt)

    h['energy0'].Fill(tree.phoE[0], wgt)
    h['energy1'].Fill(tree.phoE[1], wgt)

    h['bdt0'].Fill(tree.phoIDMVA[0], wgt)
    h['bdt1'].Fill(tree.phoIDMVA[1], wgt)
    h['bdtxy'].Fill(tree.phoIDMVA[0], wgt)
    h['bdtxy'].Fill(tree.phoIDMVA[1], wgt)

    h['mGG'].Fill(tree.mgg, wgt)

def norm_hists(h, norm):

    for k in h.keys():
        h[k].Scale(norm)

def get_unique(keys):
    '''
    Get list of unique entries, preserving their order in `keys`
    '''
    cuts = []
    for k in keys:
        if k not in cuts:
            cuts.append(k)

    return cuts

def write_cut_hists(h, out_filename):

    file_out = ROOT.TFile(out_filename, "RECREATE")
    #file_out.cd("h4gCandidateDumper")
    cuts = np.array([k.split('_')[0] for k in h.keys()])
    cuts = get_unique(cuts)

    for cut in cuts:
        file_out.cd()
        file_out.mkdir(cut)
        file_out.cd(cut)
        cut_keys = [k for k in h.keys() if cut+'_' in k]
        for k in cut_keys:
            h[k].Write()

    file_out.Write()
    file_out.Close()

def write_hists(h, out_filename):

    file_out = ROOT.TFile(out_filename, "RECREATE")
    #file_out.cd("h4gCandidateDumper")
    for k in h.keys():
        h[k].Write()
    file_out.Write()
    file_out.Close()

#def set_hist(h, c, xtitle, ytitle, htitle):
def set_hist(h, xtitle, ytitle, htitle):
    #c.SetLeftMargin(0.16)
    #c.SetRightMargin(0.15)
    #c.SetBottomMargin(0.13)
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

    #return h, c
    return h

def print_stats(counts, file_out):

    writer = open(file_out, "w")

    nTotal = counts['None']
    nLast = nTotal
    print('>> Cut flow summary:')
    for k in counts.keys():
        #print('>> %s: | Npassed: %d | f_prev: %.2f | f_total: %.2f'%(k, counts[k], 1.*counts[k]/nLast, 1.*counts[k]/nTotal))
        line = '.. {:>10} | Npassed: {:>7d} | f_prev: {:>.3f} | f_total: {:>.3f}'\
                .format(k, counts[k], 1.*counts[k]/nLast if nLast > 0 else 0., 1.*counts[k]/nTotal)
        print(line)
        writer.write(line+'\n')
        nLast = counts[k]

    writer.close()
