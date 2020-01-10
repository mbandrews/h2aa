import ROOT
import numpy as np
np.random.seed(0)
from hist_utils import fill_cut_hists

def get_inv_mass(p4s):

    #diphoP4 = ROOT.TLorentzVector()
    diphoP4 = ROOT.Math.PtEtaPhiEVector()
    for idx in p4s.keys():
        diphoP4 += p4s[idx]

    return diphoP4.mass()

def reco_pho(i, tree):

    if tree.phoEt[i] < 10.: return False

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

def select_event(tree, cuts, hists, counts, outvars):

    cut = str(None)
    fill_cut_hists(hists, tree, cut, outvars)
    counts[cut] += 1

    #print(type(tree.HLTPho))
    # Trigger cut
    cut = 'trg'
    if cut in cuts:
        #if tree.HLTPho>>14&1 == 0 and tree.HLTPho>>17&1 == 0: # HLT_Diphoton30_18_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90, HLT_Diphoton30EB_18EB_R9Id_OR_IsoCaloId_AND_HE_R9Id_DoublePixelVeto_Mass55_v
        if tree.HLTPho>>37&1 == 0: #HLT_Diphoton30PV_18PV_R9Id_AND_IsoCaloId_AND_HE_R9Id_PixelVeto_Mass55_v
            return False
        fill_cut_hists(hists, tree, cut, outvars)
        counts[cut] += 1

    # nPhoton cut
    cut = 'npho'
    if cut in cuts:
        phoRecoIdxs = []
        for i in range(tree.nPho):
            if not reco_pho(i, tree): continue
            phoRecoIdxs.append(i)
        if len(phoRecoIdxs) != 2:
            return False
        fill_cut_hists(hists, tree, cut, outvars)
        counts[cut] += 1

    # Photon pre-selection
    cut = 'presel'
    if cut in cuts:
        phoPreselIdxs = []
        for idx in phoRecoIdxs:
            if not EB_presel(idx, tree): continue
            #print(idx, tree.phoEt[idx], tree.phoEta[idx], tree.phoPhi[idx])
            phoPreselIdxs.append(idx)
        if len(phoPreselIdxs) != 2:
            return False
        outvars['phoPreselIdxs'] = phoPreselIdxs
        fill_cut_hists(hists, tree, cut, outvars)
        counts[cut] += 1

    # mGG cut
    cut = 'mgg'
    if cut in cuts:
        phoP4 = {}
        for idx in phoPreselIdxs:
            #p4 = ROOT.TLorentzVector()
            #p4 = ROOT.Math.PtEtaPhiEVector()
            p4 = ROOT.Math.PtEtaPhiEVector(tree.phoEt[idx], tree.phoEta[idx], tree.phoPhi[idx], tree.phoE[idx])
            #p4.SetPtEtaPhiE(tree.phoEt[idx], tree.phoEta[idx], tree.phoPhi[idx], tree.phoE[idx])
            phoP4[idx] = p4
        outvars['mgg'] = get_inv_mass(phoP4)
        if outvars['mgg'] <= 90:
            return False
        fill_cut_hists(hists, tree, cut, outvars)
        counts[cut] += 1

    return True

def analyze_event(tree, region, blind, do_ptomGG=True):

    # Check if event is in SB or SR region
    if not in_region(region, tree): return False

    # Check if event is part of blinded region
    if is_blinded(blind, tree): return False

    # Check if passes pt/mGG cuts
    if 'sb' not in region and not ptomGG_passed(tree): return False
    #else:
    #    if do_ptomGG and not ptomGG_passed(tree): return False

    if not bdt_passed(tree): return False

    return True

def bdt_passed(tree):
    #if tree.phoIDMVA[0] < -0.96: return False
    #if tree.phoIDMVA[1] < -0.96: return False
    if tree.phoIDMVA[0] < -0.90: return False
    if tree.phoIDMVA[1] < -0.90: return False
    return True

def ptomGG_passed(tree):

  #if tree.pho1_pt/tree.pho12_m < 1./3.: return False
  #if tree.pho2_pt/tree.pho12_m < 1./4.: return False
  assert tree.phoEt[0] > tree.phoEt[1]
  if tree.phoEt[0]/tree.mgg < 1./3.: return False
  if tree.phoEt[1]/tree.mgg < 1./4.: return False

  return True

def in_region(region, tree):

    #in_sblo = tree.pho12_m >= 100. and tree.pho12_m < 110.
    #in_sr   = tree.pho12_m >= 110. and tree.pho12_m < 140.
    #in_sbhi = tree.pho12_m >= 140. and tree.pho12_m < 180.
    in_sblo = tree.mgg >= 100. and tree.mgg < 110.
    in_sr   = tree.mgg >= 110. and tree.mgg < 140.
    in_sbhi = tree.mgg >= 140. and tree.mgg < 180.

    #if region == 'sb' or region == 'sb2sr':
    if 'sb' in region:
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

#def evt_wgt(is_data, tree, do_ptwgt=False):
#
#    wgt = 1. if is_data else tree.weight
#
#    if do_ptwgt:
#        pass
#        #wgt = wgt*ptweight(tree.pho1_pt, tree.pho2_pt)
#    if do_hggwgt:
#        wgt = wgt*get_combined_template_wgt
#
#    return wgt
