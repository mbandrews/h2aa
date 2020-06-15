from __future__ import print_function
import ROOT
import numpy as np
np.random.seed(0)
from hist_utils_zee import fill_cut_hists
from multiprocessing import Pool
import os, glob
from root_numpy import hist2array
#from data_utils import *

def get_inv_mass(p4s):

    #diphoP4 = ROOT.TLorentzVector()
    diphoP4 = ROOT.Math.PtEtaPhiEVector()
    for idx in p4s.keys():
        diphoP4 += p4s[idx]

    return diphoP4.mass()

def reco_pho(i, tree):

    if tree.phoEt[i] < 10.: return False

    return True

def reco_ele(i, tree):

    if tree.eleCalibPt[i] < 10.: return False

    return True

def pho_presel(i, tree):

    if abs(tree.phoEt[i]) < 10.: return False
    if abs(tree.phoEta[i]) > 2.4: return False
    if abs(tree.phoEta[i]) > 1.442 and abs(tree.phoEta[i]) < 1.566: return False

    if tree.phoR9Full5x5[i] <= 0.5: return False
    if tree.phoHoverE[i] >= 0.08: return False
    #if tree.phohasPixelSeed[i] == True: return False

    if tree.phoR9Full5x5[i] <= 0.85:
        if tree.phoSigmaIEtaIEtaFull5x5[i] >= 0.015: return False
        if tree.phoPFPhoIso[i] >= 4.: return False
        if tree.phoPFChIso[i] >= 6.: return False

    return True

def EB_presel(i, tree):

    if abs(tree.phoEta[i]) >= 1.442: return False

    if tree.phoR9Full5x5[i] <= 0.5: return False
    if tree.phoHoverE[i] >= 0.08: return False
    if tree.phohasPixelSeed[i] == True: return False

    if tree.phoR9Full5x5[i] <= 0.85:
        if tree.phoSigmaIEtaIEtaFull5x5[i] >= 0.015: return False
        if tree.phoPFPhoIso[i] >= 4.: return False
        if tree.phoPFChIso[i] >= 6.: return False

    return True

def is_tight_ele(i, tree):

    if (tree.eleIDbit[i]>>3&1 == 0): return False # >>1:loose, 2:medium, 3:tight

    return True

def is_barrel_ele(i, tree):

    if abs(tree.eleEta[i]) >= 1.442: return False

    return True

def select_event(tree, cuts, hists, counts, outvars=None):

    cut = str(None)
    fill_cut_hists(hists, tree, cut, outvars)
    counts[cut] += 1

    # Trigger cut
    cut = 'trg'
    if cut in cuts:
        if (tree.HLTEleMuX>>4&1 == 0):
            # HLT_Ele27_WPTight_Gsf_v#HLT_DoubleEle24_22_eta2p1_WPLoose_Gsf_v
            return False
        fill_cut_hists(hists, tree, cut, outvars)
        counts[cut] += 1

    # nEle cut
    cut = 'nele'
    if cut in cuts:
        if tree.nEle < 2:
            return False
        nEle = sum([1 for i in range(tree.nEle) if tree.eleCalibPt[i] > 15.])
        if nEle < 2:
            return False
        fill_cut_hists(hists, tree, cut, outvars)
        counts[cut] += 1

    ## ^^SKIM^^ ##

    # presel cut
    cut = 'presel'
    if cut in cuts:
        phoRecoIdxs, eleRecoIdxs = [], []
        p4_pho, p4_ele = ROOT.TVector3(), ROOT.TVector3()
        for i in range(tree.nPho):
            if not pho_presel(i, tree): continue
            p4_pho.SetPtEtaPhi(tree.phoEt[i], tree.phoEta[i], tree.phoPhi[i])
            isMatched = False
            # Find matching object in electron collection
            for j in range(tree.nEle):
                #if (tree.eleIDbit[j]>>1&1 == 0): continue # >>1:loose, 2:medium, 3:tight
                p4_ele.SetPtEtaPhi(tree.eleCalibPt[j], tree.eleEta[j], tree.elePhi[j])
                dR = ROOT.Math.VectorUtil.DeltaR(p4_pho, p4_ele)
                if dR > 0.04: continue
                isMatched = True
                eleRecoIdxs.append(j)
                break
            if not isMatched: continue
            phoRecoIdxs.append(i)

        assert len(eleRecoIdxs) == len(phoRecoIdxs)
        #if len(eleRecoIdxs) < 2:
        if len(eleRecoIdxs) != 2:
            return False
        fill_cut_hists(hists, tree, cut, outvars)
        counts[cut] += 1

    '''
    # Tag electron present
    cut = 'tag'
    if cut in cuts:
        nTightEle = sum(1 if tree.eleIDbit[idx]>>3&1 == 1 else 0 for idx in eleRecoIdxs)
        if nTightEle < 1:
            return False
        fill_cut_hists(hists, tree, cut, outvars)
        counts[cut] += 1
    '''

    # mGG cut
    #cut = 'mee'
    cut = 'tnp'
    if cut in cuts:
        phoPreselIdxs, phoPreselEleIdxs = [], []
        inZwindow = False
        # Tag electron loop
        # tag electron should pass 'tight' ID requirements
        #for iele,ipho in zip(eleRecoIdxs, phoRecoIdxs):
        eleTagIdxs, eleProbeIdxs = [], []
        for iele in eleRecoIdxs:
            if not is_tight_ele(iele, tree): continue
            p4_i = ROOT.Math.PtEtaPhiEVector(tree.elePt[iele], tree.eleEta[iele], tree.elePhi[iele], tree.eleEn[iele])
            p4_i *= (tree.eleCalibPt[iele]/tree.elePt[iele])
            # Probe electron loop
            # probe electron just needs to have passed (photon) preselection
            inZwindow = False
            #for jele,jpho in zip(eleRecoIdxs, phoRecoIdxs):
            for jele in eleRecoIdxs:
                #if jele <= iele: continue # iele is always leading pt
                if jele == iele: continue
                #if (tree.eleIDbit[jele]>>1&1 == 0): continue # >>1:loose, 2:medium, 3:tight
                p4_j = ROOT.Math.PtEtaPhiEVector(tree.elePt[jele], tree.eleEta[jele], tree.elePhi[jele], tree.eleEn[jele])
                p4_j *= (tree.eleCalibPt[jele]/tree.elePt[jele])
                mee = (p4_i + p4_j).mass()
                # mee system should be withing Z-mass window
                if (mee < 60) or (mee > 120): continue
                inZwindow = True
                # tnp combination
                if is_tight_ele(jele, tree): # if both are tight: both are probe
                    eleProbeIdxs.append(iele)
                    eleProbeIdxs.append(jele)
                else:
                    eleTagIdxs.append(iele)
                    eleProbeIdxs.append(jele)# tag must always be tight in case of only 1 tight
                break
            if inZwindow: break
        if not inZwindow:
            return False
        assert len(eleTagIdxs) + len(eleProbeIdxs) == 2
        phoTagIdxs = [phoIdx for phoIdx, eleIdx in zip(phoRecoIdxs, eleRecoIdxs) if eleIdx in eleTagIdxs]
        phoProbeIdxs = [phoIdx for phoIdx, eleIdx in zip(phoRecoIdxs, eleRecoIdxs) if eleIdx in eleProbeIdxs]
        '''
        if len(phoTagIdxs) != len(eleTagIdxs):
            print('phoRecoIdxs',phoRecoIdxs)
            print('eleRecoIdxs',eleRecoIdxs)
            print('phoTagIdxs',phoTagIdxs)
            print('eleTagIdxs',eleTagIdxs)
            for i,j in zip(phoRecoIdxs, eleRecoIdxs):
                p4_pho.SetPtEtaPhi(tree.phoEt[i], tree.phoEta[i], tree.phoPhi[i])
                print('pho[%d]: (%f, %f, %f)'%(tree.phoEt[i], tree.phoEta[i], tree.phoPhi[i]))
                p4_ele.SetPtEtaPhi(tree.eleCalibPt[j], tree.eleEta[j], tree.elePhi[j])
                print('ele[%d]: (%f, %f, %f)'%(tree.elePt[j], tree.eleEta[j], tree.elePhi[j]))
                dR = ROOT.Math.VectorUtil.DeltaR(p4_pho, p4_ele)
                print('pho[%d], ele[%d]: dR = %.f'%(i, j, dR))
        if len(phoProbeIdxs) != len(eleProbeIdxs):
            print('phoRecoIdxs',phoRecoIdxs)
            print('eleRecoIdxs',eleRecoIdxs)
            print('phoProbeIdxs',phoProbeIdxs)
            print('eleProbeIdxs',eleProbeIdxs)
            for i,j in zip(phoRecoIdxs, eleRecoIdxs):
                p4_pho.SetPtEtaPhi(tree.phoEt[i], tree.phoEta[i], tree.phoPhi[i])
                print('pho[%d]: (%f, %f, %f)'%(i, tree.phoEt[i], tree.phoEta[i], tree.phoPhi[i]))
                p4_ele.SetPtEtaPhi(tree.eleCalibPt[j], tree.eleEta[j], tree.elePhi[j])
                print('ele[%d]: (%f, %f, %f)'%(j, tree.elePt[j], tree.eleEta[j], tree.elePhi[j]))
                dR = ROOT.Math.VectorUtil.DeltaR(p4_pho, p4_ele)
                print('pho[%d], ele[%d]: dR = %f'%(i, j, dR))
        '''
        assert len(phoTagIdxs) == len(eleTagIdxs), '%d vs %d'%(len(phoTagIdxs), len(eleTagIdxs))
        assert len(phoProbeIdxs) == len(eleProbeIdxs), '%d vs %d'%(len(phoProbeIdxs), len(eleProbeIdxs))
        #phoTagIdx = np.array(phoRecoIdxs)[np.array(eleRecoIdxs) == eleTagIdx][0]
        #phoProbeIdx = np.array(phoRecoIdxs)[np.array(eleRecoIdxs) == eleProbeIdx][0]
        outvars['mee'] = mee
        outvars['phoTagIdxs'] = phoTagIdxs
        outvars['phoProbeIdxs'] = phoProbeIdxs
        outvars['eleTagIdxs'] = eleTagIdxs
        outvars['eleProbeIdxs'] = eleProbeIdxs
        fill_cut_hists(hists, tree, cut, outvars)
        counts[cut] += 1

    cut = 'mee'
    if cut in cuts:
        if mee < 91.-10. or mee > 91.+10.: return False
        fill_cut_hists(hists, tree, cut, outvars)
        counts[cut] += 1

    # ptomee cut
    cut = 'ptomee'
    if cut in cuts:
        ptIdxs = np.sort(eleTagIdxs+eleProbeIdxs)
        leadPt, subLeadPt = tree.eleCalibPt[ptIdxs[0]], tree.eleCalibPt[ptIdxs[1]]
        '''
        if phoTagIdx < phoProbeIdx:
            #leadPt, subLeadPt = tree.phoEt[phoTagIdx], tree.phoEt[phoProbeIdx]
            leadPt, subLeadPt = tree.eleCalibPt[eleTagIdx], tree.eleCalibPt[eleProbeIdx]
        else:
            #leadPt, subLeadPt = tree.phoEt[phoProbeIdx], tree.phoEt[phoTagIdx]
            leadPt, subLeadPt = tree.eleCalibPt[eleProbeIdx], tree.eleCalibPt[eleTagIdx]
        '''
        if leadPt < mee/3.: return False
        if subLeadPt < mee/4.: return False
        fill_cut_hists(hists, tree, cut, outvars)
        counts[cut] += 1

    # chgIso cut
    cut = 'chgiso'
    if cut in cuts:
        if not chgiso_passed(tree, outvars['phoProbeIdxs']): return False
        fill_cut_hists(hists, tree, cut, outvars)
        counts[cut] += 1

    # bdt cut
    cut = 'bdt'
    if cut in cuts:
        if not bdt_passed(tree, outvars['phoProbeIdxs']): return False
        fill_cut_hists(hists, tree, cut, outvars)
        counts[cut] += 1

    return True

def analyze_event(tree, region, blind, do_ptomGG=True):

    # Check if event is in SB or SR region
    if not in_region(region, tree): return False

    # Check if event is part of blinded region
    if is_blinded(blind, tree): return False

    return True

def bdt_passed(tree, phoProbeIdxs):
    for idx in phoProbeIdxs:
        if tree.phoIDMVA[idx] < -0.98: return False
    return True

def chgiso_passed(tree, phoProbeIdxs):
    for idx in phoProbeIdxs:
        if (tree.phoPFChIso[idx]/tree.phoEt[idx]) > 0.05: return False
    return True

def ptomGG_passed(tree):

  #if tree.pho1_pt/tree.pho12_m < 1./3.: return False
  #if tree.pho2_pt/tree.pho12_m < 1./4.: return False
  assert tree.phoEt[tree.phoPreselIdxs[0]] > tree.phoEt[tree.phoPreselIdxs[1]]
  if tree.phoEt[tree.phoPreselIdxs[0]]/tree.mgg < 1./3.: return False
  if tree.phoEt[tree.phoPreselIdxs[1]]/tree.mgg < 1./4.: return False

  return True

def in_region(region, tree):

    #in_sblo = tree.pho12_m >= 100. and tree.pho12_m < 110.
    #in_sr   = tree.pho12_m >= 110. and tree.pho12_m < 140.
    #in_sbhi = tree.pho12_m >= 140. and tree.pho12_m < 180.
    in_sblo = tree.mgg >= 100. and tree.mgg < 110.
    in_sr   = tree.mgg >= 110. and tree.mgg < 140.
    in_sbhi = tree.mgg >= 140. and tree.mgg < 180.

    #if region == 'sb' or region == 'sb2sr':
    #if 'sb' in region:
    if 'all' in region:
        return True
    elif 'sblo' in region:
        if in_sblo: return True
    elif 'sbhi' in region:
        if in_sbhi: return True
    elif 'sb' in region:
        if in_sblo or in_sbhi: return True
    elif region == 'sr':
        if in_sr: return True
    return False

    # DEPRECATED:
    #if region == 'sb' or region == 'sb2sr':
    #    if tree.pho12_m < 100. or  tree.pho12_m > 180.: return False
    #    if tree.pho12_m > 110. and tree.pho12_m < 140.: return False
    ## mH
    #elif region == 'sr':
    #    if tree.pho12_m <= 110. or tree.pho12_m >= 140.: return False
    #return True


def is_blinded(blind, tree):

    ma_binw = 25. # MeV
    diag_w = 200. # MeV
    ma0_flr = ma_binw*(np.floor(1.e3*tree.ma0)//ma_binw) # MeV
    ma1_flr = ma_binw*(np.floor(1.e3*tree.ma1)//ma_binw) # MeV

    # All units in MeV
    is_diag = abs(ma0_flr - ma1_flr) < diag_w
    is_offdiag = not is_diag
    is_hi = not ((ma0_flr < 1.2e3) and (ma1_flr < 1.2e3))
    is_lo = not ((ma0_flr >= 0.) and (ma1_flr >= 0.))
    is_gjet = (ma0_flr < 0.) and (ma1_flr >= 0.)
    is_gg = (ma0_flr < 0.) and (ma1_flr < 0.)

    if 'sg' in blind:
        if (is_diag and not is_lo and not is_hi): return True

    # Diagonal blinding:
    if 'offdiag' in blind:
        if is_offdiag: return True
    elif 'diag' in blind:
        if is_diag: return True

    # GJet
    if 'notgjet' in blind:
        if not is_gjet: return True
    if 'notgg' in blind:
        if not is_gg: return True

    # Range blinding
    if 'lo' in blind:
        if is_lo: return True
    if 'hi' in blind:
        if is_hi: return True

    return False

def load_hists(h, hf, samples, keys, input_dir):

    # NOTE: Need to pass file objects `hf` as well for histograms `h`
    # to remain persistent, otherwise segfaults
    for s in samples:
        hf[s] = ROOT.TFile("%s/%s_templates.root"%(input_dir, s), "READ")
        for k in keys:
            h[s+k] = hf[s].Get(k)

def get_ptweights(sample_src='DYToEE', sample_tgt='Run2017', workdir='Templates'):

    h, hf = {}, {}
    sample_tgts = glob.glob('%s/%s?_templates.root'%(workdir, sample_tgt))
    sample_tgts = [s.split('/')[-1].split('_')[0] for s in sample_tgts]
    #print(sample_tgts)
    samples = [sample_src]+sample_tgts
    #print(samples)
    keys = ['pt1corr', 'elePt1corr']
    load_hists(h, hf, samples, keys, workdir)
    #print(h.keys())

    for k in keys:

        # Ratio is SR/SB
        kratio = k+'ratio'
        for i,s in enumerate(sample_tgts):
            if i == 0:
                h[kratio] = h[s+k].Clone()
            else:
                h[kratio].Add(h[s+k])

        h[kratio].Divide(h[sample_src+k])

        #'''
        # Save all histograms for reference
        # Actual weights to be used during event loop are written to separate file below
        output_dir = 'Weights'
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        hf[kratio] = ROOT.TFile("%s/%s2%s_%s_ptwgts.root"%(output_dir, sample_src, sample_tgt, k), "RECREATE")
        # Write ratio
        h[kratio].SetName(kratio)
        h[kratio].Write()
        # Also write numerator and denominator
        for s in samples:
            h[s+k].SetName(s+k)
            h[s+k].Write()
        hf[kratio].Close()

        # hist2array().T origin @ lower left + (row, col) <=> (iy, ix)
        # NOTE: hist2array() drops uflow and ovflow bins => idx -> idx-1
        # row:sublead, col:lead
        ratio, pt_edges = hist2array(h[kratio], return_edges=True)
        #ratio, pt_edges = ratio.T, pt_edges[0]
        ratio, pt_edges = ratio, pt_edges[0]
        #print(ratio)
        #print(pt_edges)

        # Remove unphysical values
        #ratio[ratio==0.] = 0.
        ratio[np.isnan(ratio)] = 1.
        #print('pt-ratio:')
        #print(ratio.min(), ratio.max(), np.mean(ratio), np.std(ratio))

        # Write out weights to numpy file
        np.savez("%s/%s2%s_%s_ptwgts.npz"%(output_dir, sample_src, sample_tgt, k), pt_edges=pt_edges, pt_wgts=ratio)

#def get_weight_idx(ma, ma_edges):
#    '''
#    Returns bin index `idx` in array `ma_edges` corresponding to
#    bin in which `ma` is bounded in `ma_edges`
#    '''
#    # If below lowest edge, return wgt at lowest bin
#    if ma < ma_edges[0]:
#        idx = 0
#    # If above highest edge, return wgt at highest bin
#    elif ma > ma_edges[-1]:
#        # n bins in ma_edges = len(ma_edges)-1
#        # then subtract another 1 to get max array index
#        idx = len(ma_edges)-2
#    # Otherwise, return wgt from bin containing `ma`
#    else:
#        # np.argmax(condition) returns first *edge* where `condition` is `True`
#        # Need to subtract by 1 to get *bin value* bounded by appropriate edges
#        # i.e. bin_i : [edge_i, edge_i+1) where edge_i <= value(bin_i) < edge_i+1
#        idx = np.argmax(ma <= ma_edges)-1
#    #if idx > 48: print(idx, ma, len(ma_edges))
#    return idx
#
#def get_pt_wgt(tree, pt_edges, wgts):
#    '''
#    Convenience fn for returning 2d-pt wgt for an event loaded into `tree`
#    '''
#    assert tree.phoEt[0] > tree.phoEt[1]
#    return get_weight_2d(tree.phoEt[0], tree.phoEt[1], pt_edges, wgts)
#
#def get_weight_1d(q, q_edges, wgts):
#    '''
#    Returns wgt corresponding to (q_lead, q_sublead) in 2d-q plane
#    '''
#    iq = get_weight_idx(q, q_edges)
#
#    return wgts[iq]
#
#def get_weight_2d(q_lead, q_sublead, q_edges, wgts):
#    '''
#    Returns wgt corresponding to (q_lead, q_sublead) in 2d-q plane
#    '''
#    # NOTE: assumes wgts corresponds to
#    # row:sublead, col:lead
#    iq_lead = get_weight_idx(q_lead, q_edges)
#    iq_sublead = get_weight_idx(q_sublead, q_edges)
#
#    #print(iq_sublead, iq_lead)
#    return wgts[iq_sublead, iq_lead]
