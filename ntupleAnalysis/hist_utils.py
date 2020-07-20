import ROOT
import numpy as np
from array import array

def create_hists(h):

    k = 'ma0'

    ma_bins = list(range(0,1200+25,25))
    ma_bins = [-400]+ma_bins
    #ma_bins = [-400, -200]+ma_bins
    ma_bins = [float(m)/1.e3 for m in ma_bins]
    #print(len(ma_bins))
    n_ma_bins = len(ma_bins)-1
    ma_bins = array('d', ma_bins)
    #print(ma_bins)

    #h[k] = ROOT.TH1F(k, k, 48, 0., 1.2)
    #h[k] = ROOT.TH1F(k, k, 56, -0.2, 1.2)
    h[k] = ROOT.TH1F(k, k, n_ma_bins, ma_bins)
    k = 'ma1'
    #h[k] = ROOT.TH1F(k, k, 48, 0., 1.2)
    #h[k] = ROOT.TH1F(k, k, 56, -0.2, 1.2)
    h[k] = ROOT.TH1F(k, k, n_ma_bins, ma_bins)
    k = 'ma0vma1'
    #h[k] = ROOT.TH2F(k, k, 48, 0., 1.2, 48, 0., 1.2)
    #h[k] = ROOT.TH2F(k, k, 56, -0.2, 1.2, 56, -0.2, 1.2)
    h[k] = ROOT.TH2F(k, k, n_ma_bins, ma_bins, n_ma_bins, ma_bins)
    k = 'maxy'
    #h[k] = ROOT.TH1F(k, k, 56, -0.2, 1.2)
    h[k] = ROOT.TH1F(k, k, n_ma_bins, ma_bins)

    #k = 'pt0'
    #h[k] = ROOT.TH1F(k, k, 50, 20., 170.)
    #k = 'pt1'
    #h[k] = ROOT.TH1F(k, k, 50, 20., 170.)
    #k = 'pt0vpt1'
    #h[k] = ROOT.TH2F(k, k, 50, 20., 170., 50, 20., 170.)

    pt_bins_ = {}
    '''
    dPt = 1
    #pt_bins_[0] = np.arange(26,100,dPt)
    pt_bins_[0] = np.arange(25,100,dPt)
    dPt = 5
    pt_bins_[1] = np.arange(100,120,dPt)
    dPt = 20
    pt_bins_[2] = np.arange(120,200,dPt)
    #dPt = 750-200
    #pt_bins_[3] = np.arange(200,750+dPt,dPt)
    '''
    dPt = 10
    pt_bins_[0] = np.arange(25,125+dPt,dPt)

    pt_bins = np.concatenate([pt_bin_ for pt_bin_ in pt_bins_.values()])
    n_pt_bins = len(pt_bins)-1
    pt_bins = array('d', list(pt_bins))

    k = 'pt0'
    h[k] = ROOT.TH1F(k, k, n_pt_bins, pt_bins)
    k = 'pt1'
    h[k] = ROOT.TH1F(k, k, n_pt_bins, pt_bins)
    k = 'ptxy'
    h[k] = ROOT.TH1F(k, k, n_pt_bins, pt_bins)

    k = 'ma0vpt0'
    h[k] = ROOT.TH2F(k, k, n_pt_bins, pt_bins, 49, ma_bins)
    k = 'ma1vpt1'
    h[k] = ROOT.TH2F(k, k, n_pt_bins, pt_bins, 49, ma_bins)

    pt_bins_x_ = {}
    dPt = 1
    pt_bins_x_[0] = np.arange(25,100,dPt)
    dPt = 5
    pt_bins_x_[1] = np.arange(100,120,dPt)
    dPt = 20
    pt_bins_x_[2] = np.arange(120,200,dPt)
    dPt = 750-200
    pt_bins_x_[3] = np.arange(200,750+dPt,dPt)
    pt_bins_x = np.concatenate([pt_bin_ for pt_bin_ in pt_bins_x_.values()])
    n_pt_bins_x = len(pt_bins_x)-1
    pt_bins_x = array('d', list(pt_bins_x))

    pt_bins_y_ = {}
    dPt = 1
    pt_bins_y_[0] = np.arange(25,60,dPt)
    dPt = 5
    pt_bins_y_[1] = np.arange(60,120,dPt)
    dPt = 20
    pt_bins_y_[2] = np.arange(120,200,dPt)
    dPt = 750-200
    pt_bins_y_[3] = np.arange(200,750+dPt,dPt)
    pt_bins_y = np.concatenate([pt_bin_ for pt_bin_ in pt_bins_y_.values()])
    n_pt_bins_y = len(pt_bins_y)-1
    pt_bins_y = array('d', list(pt_bins_y))

    k = 'pt0vpt1'
    h[k] = ROOT.TH2F(k, k, n_pt_bins_x, pt_bins_x, n_pt_bins_y, pt_bins_y)

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

    k = 'nEvtsWgtd'
    h[k] = ROOT.TH1F(k, k, 2, 0., 2.)

    for k in h.keys():
        h[k].Sumw2()

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
        h[cut+'relChgIso'] = ROOT.TH1F(cut+'relChgIso', cut+'relChgIso', 50, 0., 0.05)
        h[cut+'r9'] = ROOT.TH1F(cut+'r9', cut+'r9', 50, 0., 1.2)
        h[cut+'sieie'] = ROOT.TH1F(cut+'sieie', cut+'sieie', 50, 0., 0.1)
        h[cut+'hoe'] = ROOT.TH1F(cut+'hoe', cut+'hoe', 50, 0., 0.2)
        #h[cut+'HLTDipho_m90'] = ROOT.TH1F(cut+'HLTDipho_m90', cut+'HLTDipho_m90', 2, 0., 2.)
        h[cut+'HLTDiphoPV_m55'] = ROOT.TH1F(cut+'HLTDiphoPV_m55', cut+'HLTDiphoPV_m55', 2, 0., 2.)
        #h[cut+'wgt'] = ROOT.TH1F(cut+'wgt', cut+'wgt', 50, 0., 100.)

        #if 'mgg' in c:
        h[cut+'mgg'] = ROOT.TH1F(cut+'mgg', cut+'mgg', 50, 50., 200.)
        h[cut+'dR'] = ROOT.TH1F(cut+'dR', cut+'dR', 86, -0.0174, 85*0.0174)

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
        h[cut+'relChgIso'].Fill(tree.phoPFChIso[i]/tree.phoEt[i])
        h[cut+'r9'].Fill(tree.phoR9Full5x5[i])
        h[cut+'sieie'].Fill(tree.phoSigmaIEtaIEtaFull5x5[i])
        h[cut+'hoe'].Fill(tree.phoHoverE[i])
        #h[cut+'HLTDipho_m90'].Fill(tree.HLTPho>>14&1)
        #h[cut+'HLTDiphoPV_m55'].Fill(tree.HLTPho>>37&1)
        h[cut+'HLTDiphoPV_m55'].Fill((tree.HLTPho>>37&1) or (tree.HLTPho>>16&1))

    if outvars is not None:
        if 'mgg' in outvars.keys():
            h[cut+'mgg'].Fill(outvars['mgg'])
        if 'dR' in outvars.keys():
            h[cut+'dR'].Fill(outvars['dR'])


def fill_hists(h, tree, wgt):

    h['wgt'].Fill(wgt)
    h['nEvtsWgtd'].Fill(1., wgt)

    ma0_ = tree.ma0
    ma1_ = tree.ma1
    #scale = 1.+0.036 # +/- 0.001
    #offset = 0.-0.005
    # data -> mc
    #ma0_ = tree.ma0*scale + offset
    #ma1_ = tree.ma1*scale + offset
    # mc -> data
    #ma0_ = scale*tree.ma0 + offset
    #ma1_ = scale*tree.ma1 + offset

    h['ma0'].Fill(ma0_, wgt)
    h['ma1'].Fill(ma1_, wgt)
    h['ma0vma1'].Fill(ma0_, ma1_, wgt)
    h['maxy'].Fill(ma0_, wgt)
    h['maxy'].Fill(ma1_, wgt)

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

    h['ma0vpt0'].Fill(tree.phoEt[0], ma0_, wgt)
    h['ma1vpt1'].Fill(tree.phoEt[1], ma1_, wgt)

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
