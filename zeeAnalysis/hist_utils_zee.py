import ROOT
import numpy as np
from array import array

def create_hists(h):

    ma_bins = list(range(0,1200+25,25))
    ma_bins = [-400]+ma_bins
    ma_bins = [float(m)/1.e3 for m in ma_bins]
    #print(len(ma_bins))
    ma_bins = array('d', ma_bins)
    #print(ma_bins)
    n_ma_bins = len(ma_bins)-1

    for s in ['', 'phoEcorr', 'eleEcorr']:
        for n in ['0', '1', 'xy']:
            k = 'ma'+n+s
            #h[k] = ROOT.TH1F(k, k, 48, 0., 1.2)
            #h[k] = ROOT.TH1F(k, k, 56, -0.2, 1.2)
            h[k] = ROOT.TH1F(k, k, n_ma_bins, ma_bins)
    #k = 'ma0vma1'
    #h[k] = ROOT.TH2F(k, k, 48, 0., 1.2, 48, 0., 1.2)
    #h[k] = ROOT.TH2F(k, k, 56, -0.2, 1.2, 56, -0.2, 1.2)
    #h[k] = ROOT.TH2F(k, k, 49, ma_bins, 49, ma_bins)

    #k = 'pt0'
    #h[k] = ROOT.TH1F(k, k, 50, 20., 170.)
    #k = 'pt1'
    #h[k] = ROOT.TH1F(k, k, 50, 20., 170.)
    #k = 'pt0vpt1'
    #h[k] = ROOT.TH2F(k, k, 50, 20., 170., 50, 20., 170.)

    pt_bins_ = {}
    #dPt = 1
    #pt_bins_[0] = np.arange(25,100,dPt)
    #dPt = 5
    #pt_bins_[1] = np.arange(100,120,dPt)
    #dPt = 20
    #pt_bins_[2] = np.arange(120,200,dPt)
    #dPt = 750-200
    #pt_bins_[3] = np.arange(200,750+dPt,dPt)
    #dPt = 1
    #pt_bins_[0] = np.arange(18,70,dPt)
    #dPt = 5
    #pt_bins_[1] = np.arange(70,90,dPt)
    #dPt = 20
    #pt_bins_[2] = np.arange(90,140,dPt)
    #dPt = 750-140
    #pt_bins_[3] = np.arange(140,750+dPt,dPt)
    dPt = 1
    pt_bins_[0] = np.arange(20,90,dPt)
    dPt = 5
    pt_bins_[1] = np.arange(90,135,dPt)
    dPt = 20
    pt_bins_[2] = np.arange(135,175,dPt)
    dPt = 500-175
    pt_bins_[3] = np.arange(175,500+dPt,dPt)
    #dPt = 1
    #pt_bins_[0] = np.arange(20,120,dPt)

    pt_bins = np.concatenate([pt_bin_ for pt_bin_ in pt_bins_.values()])
    n_pt_bins = len(pt_bins)-1
    pt_bins = array('d', list(pt_bins))

    for s in ['', 'corr']:
        for n in ['0', '1', 'xy']:
            # pho
            k = 'pt'+n+s
            h[k] = ROOT.TH1F(k, k, n_pt_bins, pt_bins)
            # ele
            k = 'elePt'+n+s
            h[k] = ROOT.TH1F(k, k, n_pt_bins, pt_bins)
    #k = 'pt0vpt1'
    #h[k] = ROOT.TH2F(k, k, n_pt_bins, pt_bins, n_pt_bins, pt_bins)
    k = 'ma1vpt1corr'
    h[k] = ROOT.TH2F(k, k, n_pt_bins, pt_bins, n_ma_bins, ma_bins)
    k = 'ma1phoEcorrvpt1corr'
    h[k] = ROOT.TH2F(k, k, n_pt_bins, pt_bins, n_ma_bins, ma_bins)
    k = 'ma1velePt1corr'
    h[k] = ROOT.TH2F(k, k, n_pt_bins, pt_bins, n_ma_bins, ma_bins)
    k = 'ma1eleEcorrvelePt1corr'
    h[k] = ROOT.TH2F(k, k, n_pt_bins, pt_bins, n_ma_bins, ma_bins)

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

    k = 'mee'
    h[k] = ROOT.TH1F(k, k, 60, 60., 120.)

    k = 'wgt'
    #h[k] = ROOT.TH1F(k, k, 50, 0., 50.)
    h[k] = ROOT.TH1F(k, k, 300, -600., 600.)

    k = 'tagIdx'
    h[k] = ROOT.TH1F(k, k, 10, 0., 10.)
    k = 'probeIdx'
    h[k] = ROOT.TH1F(k, k, 10, 0., 10.)
    k = 'eleEcorr'
    h[k] = ROOT.TH1F(k, k, 50, 1.-0.05, 1.+0.05)
    k = 'phoEcorr'
    h[k] = ROOT.TH1F(k, k, 50, 1.-0.05, 1.+0.05)

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
        h[cut+'mee'] = ROOT.TH1F(cut+'mee', cut+'mee', 60, 60., 120.)
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
        #h[cut+'HLTDiphoPV_m55'].Fill((tree.HLTPho>>37&1) or (tree.HLTPho>>16&1))
        h[cut+'HLTDiphoPV_m55'].Fill(tree.HLTEleMuX>>4&1 == 1)

    if outvars is not None:
        if 'mee' in outvars.keys():
            h[cut+'mee'].Fill(outvars['mee'])
        if 'dR' in outvars.keys():
            h[cut+'dR'].Fill(outvars['dR'])


#def fill_hists(h, tree, wgt, outvars=None):
def fill_hists(h, tree, wgt, outvars=None, pt_wgts=None, pt_edges=None):

    h['wgt'].Fill(wgt)

    '''
    #h['ma0'].Fill(tree.ma0, wgt)
    #h['ma1'].Fill(tree.ma1, wgt)
    #h['ma0vma1'].Fill(tree.ma0, tree.ma1, wgt)
    #h['maxy'].Fill(tree.ma0, wgt)
    #h['maxy'].Fill(tree.ma1, wgt)

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

    #h['mee'].Fill(tree.mgg, wgt)
    '''
    if outvars is not None:
        if 'mee' in outvars.keys():
            h['mee'].Fill(outvars['mee'], wgt)

        # tag gets idx = 0
        if 'phoTagIdxs' in outvars.keys():
            for i,idx in enumerate(outvars['phoTagIdxs']):
                h['tagIdx'].Fill(idx, wgt)
                h['ma0'].Fill(tree.ma[idx], wgt)
                h['maxy'].Fill(tree.ma[idx], wgt)
                h['pt0'].Fill(tree.phoEt[idx], wgt)
                h['ptxy'].Fill(tree.phoEt[idx], wgt)
                h['pt0corr'].Fill(tree.phoCalibEt[idx], wgt)
                h['ptxycorr'].Fill(tree.phoCalibEt[idx], wgt)
                h['energy0'].Fill(tree.phoE[idx], wgt)
                h['bdt0'].Fill(tree.phoIDMVA[idx], wgt)
                h['bdtxy'].Fill(tree.phoIDMVA[idx], wgt)
                phoEcorr_ = tree.phoCalibEt[idx]/tree.phoEt[idx]
                h['phoEcorr'].Fill(phoEcorr_, wgt)
                h['ma0phoEcorr'].Fill(tree.ma[idx]*phoEcorr_, wgt)
                h['maxyphoEcorr'].Fill(tree.ma[idx]*phoEcorr_, wgt)
                if 'eleTagIdxs' in outvars.keys():
                    eleIdx_ = outvars['eleTagIdxs'][i]
                    eleEcorr_ = tree.eleCalibPt[eleIdx_]/tree.elePt[eleIdx_]
                    h['ma0eleEcorr'].Fill(tree.ma[idx]*eleEcorr_, wgt)
                    h['maxyeleEcorr'].Fill(tree.ma[idx]*eleEcorr_, wgt)
        # probe gets idx = 1
        if 'phoProbeIdxs' in outvars.keys():
            for i,idx in enumerate(outvars['phoProbeIdxs']):
                tot_wgt = wgt*get_weight_1d(tree.phoCalibEt[idx], pt_edges['pt1corr'], pt_wgts['pt1corr']) if pt_wgts is not None else wgt
                h['tagIdx'].Fill(idx, tot_wgt)
                h['ma1'].Fill(tree.ma[idx], tot_wgt)
                h['maxy'].Fill(tree.ma[idx], tot_wgt)
                h['pt1'].Fill(tree.phoEt[idx], tot_wgt)
                h['ptxy'].Fill(tree.phoEt[idx], tot_wgt)
                h['pt1corr'].Fill(tree.phoCalibEt[idx], tot_wgt)
                h['ptxycorr'].Fill(tree.phoCalibEt[idx], tot_wgt)
                h['energy1'].Fill(tree.phoE[idx], tot_wgt)
                h['bdt1'].Fill(tree.phoIDMVA[idx], tot_wgt)
                h['bdtxy'].Fill(tree.phoIDMVA[idx], tot_wgt)
                phoEcorr_ = tree.phoCalibEt[idx]/tree.phoEt[idx]
                h['phoEcorr'].Fill(phoEcorr_, tot_wgt)
                h['ma1phoEcorr'].Fill(tree.ma[idx]*phoEcorr_, tot_wgt)
                h['maxyphoEcorr'].Fill(tree.ma[idx]*phoEcorr_, tot_wgt)
                h['pt1corr'].Fill(tree.phoCalibEt[idx], tot_wgt)
                h['ma1vpt1corr'].Fill(tree.phoCalibEt[idx], tree.ma[idx], tot_wgt)
                h['ma1phoEcorrvpt1corr'].Fill(tree.phoCalibEt[idx], tree.ma[idx]*phoEcorr_, tot_wgt)
                if 'eleProbeIdxs' in outvars.keys():
                    eleIdx_ = outvars['eleProbeIdxs'][i]
                    eleEcorr_ = tree.eleCalibPt[eleIdx_]/tree.elePt[eleIdx_]
                    tot_wgt = wgt*get_weight_1d(tree.eleCalibPt[eleIdx_], pt_edges['elePt1corr'], pt_wgts['elePt1corr']) if pt_wgts is not None else wgt
                    h['ma1eleEcorr'].Fill(tree.ma[idx]*eleEcorr_, tot_wgt)
                    h['maxyeleEcorr'].Fill(tree.ma[idx]*eleEcorr_, tot_wgt)
                    h['ma1velePt1corr'].Fill(tree.eleCalibPt[eleIdx_], tree.ma[idx], tot_wgt)
                    h['ma1eleEcorrvelePt1corr'].Fill(tree.eleCalibPt[eleIdx_], tree.ma[idx]*eleEcorr_, tot_wgt)
        # electrons
        # tag gets idx = 0
        if 'eleTagIdxs' in outvars.keys():
            for idx in outvars['eleTagIdxs']:
                h['elePt0'].Fill(tree.elePt[idx], wgt)
                h['elePtxy'].Fill(tree.elePt[idx], wgt)
                h['elePt0corr'].Fill(tree.eleCalibPt[idx], wgt)
                h['elePtxycorr'].Fill(tree.eleCalibPt[idx], wgt)
                h['eleEcorr'].Fill(tree.eleCalibPt[idx]/tree.elePt[idx], wgt)
        # probe gets idx = 1
        if 'eleProbeIdxs' in outvars.keys():
            for idx in outvars['eleProbeIdxs']:
                tot_wgt = wgt*get_weight_1d(tree.eleCalibPt[idx], pt_edges['elePt1corr'], pt_wgts['elePt1corr']) if pt_wgts is not None else wgt
                h['elePt1'].Fill(tree.elePt[idx], tot_wgt)
                h['elePtxy'].Fill(tree.elePt[idx], tot_wgt)
                h['elePt1corr'].Fill(tree.eleCalibPt[idx], tot_wgt)
                h['elePtxycorr'].Fill(tree.eleCalibPt[idx], tot_wgt)
                h['eleEcorr'].Fill(tree.eleCalibPt[idx]/tree.elePt[idx], tot_wgt)
        '''
        # tag gets idx = 0
        if 'phoTagIdx' in outvars.keys():
            h['tagIdx'].Fill(outvars['phoTagIdx'], wgt)
            h['ma0'].Fill(tree.ma[outvars['phoTagIdx']], wgt)
            h['maxy'].Fill(tree.ma[outvars['phoTagIdx']], wgt)
            #h['pt0'].Fill(tree.phoEt[outvars['phoTagIdx']], wgt)
            #h['ptxy'].Fill(tree.phoEt[outvars['phoTagIdx']], wgt)
            h['energy0'].Fill(tree.phoE[outvars['phoTagIdx']], wgt)
            h['bdt0'].Fill(tree.phoIDMVA[outvars['phoTagIdx']], wgt)
            h['bdtxy'].Fill(tree.phoIDMVA[outvars['phoTagIdx']], wgt)
        # probe gets idx = 1
        if 'phoProbeIdx' in outvars.keys():
            h['probeIdx'].Fill(outvars['phoProbeIdx'], wgt)
            h['ma1'].Fill(tree.ma[outvars['phoProbeIdx']], wgt)
            h['maxy'].Fill(tree.ma[outvars['phoProbeIdx']], wgt)
            #h['pt1'].Fill(tree.phoEt[outvars['phoProbeIdx']], wgt)
            #h['ptxy'].Fill(tree.phoEt[outvars['phoProbeIdx']], wgt)
            h['energy1'].Fill(tree.phoE[outvars['phoProbeIdx']], wgt)
            h['bdt1'].Fill(tree.phoIDMVA[outvars['phoProbeIdx']], wgt)
            h['bdtxy'].Fill(tree.phoIDMVA[outvars['phoProbeIdx']], wgt)
        if 'phoTagIdx' in outvars.keys() and 'phoProbeIdx' in outvars.keys():
            h['pt0vpt1'].Fill(tree.phoEt[outvars['phoTagIdx']], tree.phoEt[outvars['phoProbeIdx']], wgt)
            h['ma0vma1'].Fill(tree.ma[outvars['phoTagIdx']], tree.ma[outvars['phoProbeIdx']], wgt)

        # electrons
        # tag gets idx = 0
        if 'eleTagIdx' in outvars.keys():
            h['pt0'].Fill(tree.eleCalibPt[outvars['eleTagIdx']], wgt)
            h['ptxy'].Fill(tree.eleCalibPt[outvars['eleTagIdx']], wgt)
        # probe gets idx = 1
        if 'eleProbeIdx' in outvars.keys():
            h['pt1'].Fill(tree.eleCalibPt[outvars['eleProbeIdx']], wgt)
            h['ptxy'].Fill(tree.eleCalibPt[outvars['eleProbeIdx']], wgt)
        '''

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

def get_weight_idx(ma, ma_edges):
    '''
    Returns bin index `idx` in array `ma_edges` corresponding to
    bin in which `ma` is bounded in `ma_edges`
    '''
    # If below lowest edge, return wgt at lowest bin
    if ma < ma_edges[0]:
        idx = 0
    # If above highest edge, return wgt at highest bin
    elif ma > ma_edges[-1]:
        # n bins in ma_edges = len(ma_edges)-1
        # then subtract another 1 to get max array index
        idx = len(ma_edges)-2
    # Otherwise, return wgt from bin containing `ma`
    else:
        # np.argmax(condition) returns first *edge* where `condition` is `True`
        # Need to subtract by 1 to get *bin value* bounded by appropriate edges
        # i.e. bin_i : [edge_i, edge_i+1) where edge_i <= value(bin_i) < edge_i+1
        idx = np.argmax(ma <= ma_edges)-1
    #if idx > 48: print(idx, ma, len(ma_edges))
    return idx

def get_pt_wgt(tree, pt_edges, wgts):
    '''
    Convenience fn for returning 2d-pt wgt for an event loaded into `tree`
    '''
    assert tree.phoEt[0] > tree.phoEt[1]
    return get_weight_2d(tree.phoEt[0], tree.phoEt[1], pt_edges, wgts)

def get_weight_1d(q, q_edges, wgts):
    '''
    Returns wgt corresponding to (q_lead, q_sublead) in 2d-q plane
    '''
    iq = get_weight_idx(q, q_edges)

    return wgts[iq]

def get_weight_2d(q_lead, q_sublead, q_edges, wgts):
    '''
    Returns wgt corresponding to (q_lead, q_sublead) in 2d-q plane
    '''
    # NOTE: assumes wgts corresponds to
    # row:sublead, col:lead
    iq_lead = get_weight_idx(q_lead, q_edges)
    iq_sublead = get_weight_idx(q_sublead, q_edges)

    #print(iq_sublead, iq_lead)
    return wgts[iq_sublead, iq_lead]
