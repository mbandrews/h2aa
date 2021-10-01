import ROOT
import numpy as np
np.random.seed(0)
from hist_utils import fill_cut_hists
from trigger_systs import *

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
    #if tree.phoHoverE[i] >= 0.08: return False
    if tree.phoHoverE[i] >= 0.04596: return False
    if tree.phohasPixelSeed[i] == True: return False

    if tree.phoR9Full5x5[i] <= 0.85:
        if tree.phoSigmaIEtaIEtaFull5x5[i] >= 0.015: return False
        if tree.phoPFPhoIso[i] >= 4.: return False
        if tree.phoPFChIso[i] >= 6.: return False

    return True

def select_event(tree, cuts, hists, counts, outvars=None, year=None):

    cut = str(None)
    #fill_cut_hists(hists, tree, cut, outvars)
    fill_cut_hists(hists, tree, cut, outvars, year)
    counts[cut] += 1

    #print(type(tree.HLTPho))
    # Trigger cut
    cut = 'trg'
    if cut in cuts:
        #assert year is not None
        if year == '2016':
            '''
            NO LONGER USED: low-mass hgg trgs
            if (tree.HLTPho>>16&1 == 0) and (tree.HLTPho>>17&1 == 0):
                #HLT_Diphoton30PV_18PV_R9Id_AND_IsoCaloId_AND_HE_R9Id_DoublePixelVeto_Mass55_v
                #HLT_Diphoton30EB_18EB_R9Id_OR_IsoCaloId_AND_HE_R9Id_DoublePixelVeto_Mass55_v
                return False
            '''
            if tree.HLTPho>>14&1 == 0:
                # 14:HLT_Diphoton30_18_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90:2016 only
                return False
        #elif year == '2018':
        else:
            # same for 2017/18
            #if (tree.HLTPho>>14&1 == 0) and (tree.HLTPho>>39&1 == 0): # OR
            if tree.HLTPho>>14&1 == 0:
                # 14:HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90_v
                # 39:HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass95_v, Linda: 39 subset of 14
                return False
            '''
            NO LONGER USED: low-mass hgg trgs
            if (tree.HLTPho>>38&1 == 0):
                #HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId_NoPixelVeto_v
            '''
        '''
        NO LONGER USED: low-mass hgg trgs
        else:
            #if tree.HLTPho>>14&1 == 0 and tree.HLTPho>>17&1 == 0: # HLT_Diphoton30_18_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90, HLT_Diphoton30EB_18EB_R9Id_OR_IsoCaloId_AND_HE_R9Id_DoublePixelVeto_Mass55_v
            if (tree.HLTPho>>37&1 == 0) and (tree.HLTPho>>16&1 == 0):
                #HLT_Diphoton30PV_18PV_R9Id_AND_IsoCaloId_AND_HE_R9Id_PixelVeto_Mass55_v
                #HLT_Diphoton30PV_18PV_R9Id_AND_IsoCaloId_AND_HE_R9Id_DoublePixelVeto_Mass55_v
                return False
        '''
        #fill_cut_hists(hists, tree, cut, outvars)
        fill_cut_hists(hists, tree, cut, outvars, year)
        counts[cut] += 1

    # nPhoton cut
    cut = 'npho'
    if cut in cuts:
        phoRecoIdxs = []
        for i in range(tree.nPho):
            if not reco_pho(i, tree): continue
            phoRecoIdxs.append(i)
        #if len(phoRecoIdxs) != 2:
        if len(phoRecoIdxs) != 2 and len(phoRecoIdxs) != 3:
            return False
        '''
        if len(phoRecoIdxs) == 3:

            # Find reco idx not preselected
            nonPreselIdx = [idx for idx in range(tree.nPho) if idx not in tree.phoPreselIdxs]
            assert len(nonPreselIdx) == 1
            nonPreselIdx = nonPreselIdx[0]
            #print(list(tree.phoPreselIdxs))
            #print(nonPreselIdx)

            p4_nonPresel = ROOT.TVector3()
            p4_nonPresel.SetPtEtaPhi(tree.phoEt[nonPreselIdx], tree.phoEta[nonPreselIdx], tree.phoPhi[nonPreselIdx])
            #print('%d nonpresel: %f, %f, %f'%(nonPreselIdx, tree.phoEt[nonPreselIdx], tree.phoEta[nonPreselIdx], tree.phoPhi[nonPreselIdx]))

            minDR = 10.
            p4_presel = ROOT.TVector3()
            for preselIdx in tree.phoPreselIdxs:

                # presel photon vector
                p4_presel.SetPtEtaPhi(tree.phoEt[preselIdx], tree.phoEta[preselIdx], tree.phoPhi[preselIdx])
                #print('%d presel: %f, %f, %f'%(preselIdx, tree.phoEt[preselIdx], tree.phoEta[preselIdx], tree.phoPhi[preselIdx]))

                # Ensure photons are alike
                dR = abs(ROOT.Math.VectorUtil.DeltaR(p4_presel, p4_nonPresel))
                #print('dR: %f'%dR)

                if dR < minDR:
                    minDR = dR

            outvars['dR'] = minDR

        else:

            outvars['dR'] = -1.*0.0174

            #print('pass')
        '''
        #fill_cut_hists(hists, tree, cut, outvars)
        fill_cut_hists(hists, tree, cut, outvars, year)
        counts[cut] += 1

    '''
    # dR(presel photon, reco photon)
    cut = 'dR'
    if cut in cuts:

        assert 'dR' in outvars.keys()

        if outvars['dR'] > 0.3:
            return False

        #fill_cut_hists(hists, tree, cut, outvars)
        fill_cut_hists(hists, tree, cut, outvars, year)
        counts[cut] += 1
    '''

    # Photon pre-selection
    cut = 'presel'
    if cut in cuts:
        phoPreselIdxs = []
        for idx in phoRecoIdxs:
            if not EB_presel(idx, tree): continue
            #print(idx, tree.phoEt[idx], tree.phoEta[idx], tree.phoPhi[idx])
            phoPreselIdxs.append(idx)
        #if len(phoPreselIdxs) < 2: # >= 2 EB_presel
        if len(phoPreselIdxs) != 2: # == 2 EB_presel
            return False
        outvars['phoPreselIdxs'] = phoPreselIdxs
        #fill_cut_hists(hists, tree, cut, outvars)
        fill_cut_hists(hists, tree, cut, outvars, year)
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
        #if outvars['mgg'] < 90.:
        #if outvars['mgg'] < 100.:
        if outvars['mgg'] < 100. or outvars['mgg'] > 180.:
            return False
        #fill_cut_hists(hists, tree, cut, outvars)
        fill_cut_hists(hists, tree, cut, outvars, year)
        counts[cut] += 1

    # pt/mGG cuts
    cut = 'ptomGG'
    if cut in cuts:
        if not ptomGG_passed(tree,
                outvars['phoPreselIdxs'] if 'phoPreselIdxs' in outvars else tree.phoPreselIdxs,
                outvars['mgg'] if 'mgg' in outvars else tree.mgg
                ): return False
        #fill_cut_hists(hists, tree, cut, outvars)
        fill_cut_hists(hists, tree, cut, outvars, year)
        counts[cut] += 1

    # bdt cut
    cut = 'bdt'
    if cut in cuts:
        #if not bdt_passed(tree): return False
        #if not bdt_passed(tree, outvars['phoPreselIdxs'] if 'phoPreselIdxs' in outvars else tree.phoPreselIdxs, cut=-0.99): return False # skim
        #if not bdt_passed(tree, outvars['phoPreselIdxs'] if 'phoPreselIdxs' in outvars else tree.phoPreselIdxs, cut=-0.98): return False # full selection
        #if not bdt_passed(tree, outvars['phoPreselIdxs'] if 'phoPreselIdxs' in outvars else tree.phoPreselIdxs, cut=-0.97): return False # full selection
        if not bdt_passed(tree, outvars['phoPreselIdxs'] if 'phoPreselIdxs' in outvars else tree.phoPreselIdxs, cut=-0.96): return False # optimal !!
        #if not bdt_passed(tree, outvars['phoPreselIdxs'] if 'phoPreselIdxs' in outvars else tree.phoPreselIdxs, cut=-0.90): return False # hgg
        #fill_cut_hists(hists, tree, cut, outvars)
        fill_cut_hists(hists, tree, cut, outvars, year)
        counts[cut] += 1

    # chgIso cut
    cut = 'chgiso'
    if cut in cuts:
        if not chgiso_passed(tree, outvars['phoPreselIdxs'] if 'phoPreselIdxs' in outvars else tree.phoPreselIdxs): return False
        #fill_cut_hists(hists, tree, cut, outvars)
        fill_cut_hists(hists, tree, cut, outvars, year)
        counts[cut] += 1

    # eta cut
    cut = 'phoEta'
    if cut in cuts:
        if not eta_passed(tree, outvars['phoPreselIdxs'] if 'phoPreselIdxs' in outvars else tree.phoPreselIdxs): return False
        #fill_cut_hists(hists, tree, cut, outvars)
        fill_cut_hists(hists, tree, cut, outvars, year)
        counts[cut] += 1

    return True

def analyze_event(tree, region, blind, do_ptomGG=True):

    # Check if event is in SB or SR region
    #if not in_region(region, tree): return False
    if not in_region(region, tree.mgg): return False

    # DEPRECATED: 2d-ma blinding performed post-selections
    ## Check if event is part of blinded region
    #if is_blinded(blind, tree): return False
    assert blind is None or blind == 'None', '2D-ma blinding is deprecated. Only `None` allowed but got:'%blind

    return True

# for backward compatibility with legacy code
def in_mh_region(mhregion, mgg):

    if not in_region(mhregion, mgg): return False

    return True

#def eta_passed(tree, phoIdxs, cut=1.2):
def eta_passed(tree, phoIdxs, cut=1.479):
    if abs(tree.phoEta[phoIdxs[0]]) > cut: return False
    if abs(tree.phoEta[phoIdxs[1]]) > cut: return False
    return True

#def bdt_passed(tree, phoIdxs, cut=-0.98):
def bdt_passed(tree, phoIdxs, cut=-0.96):
    if tree.phoIDMVA[phoIdxs[0]] <= cut: return False
    if tree.phoIDMVA[phoIdxs[1]] <= cut: return False
    '''
    # h4g
    passedH4g = True
    if tree.phoIDMVA[phoIdxs[0]] <= cut:
        passedH4g = False
    if tree.phoIDMVA[phoIdxs[1]] <= cut:
        passedH4g = False
    # hgg
    passedHgg = True
    #if tree.phoIDMVA[phoIdxs[0]] <= -0.9: return False
    #if tree.phoIDMVA[phoIdxs[1]] <= -0.9: return False
    if tree.phoIDMVA[phoIdxs[0]] <= -0.9:
        passedHgg = False
    if tree.phoIDMVA[phoIdxs[1]] <= -0.9:
        passedHgg = False
    #if not passedHgg: return False
    #if not passedH4g: return False
    if not (passedHgg and passedH4g): return False #common
    #if not (passedH4g and (not passedHgg)): return False # addtl
    #if tree.phoIDMVA[phoIdxs[0]] <= 0.: return False
    ##if tree.ma0 > 0.: return False
    #if tree.phoIDMVA[phoIdxs[1]] <= cut: return False
    '''
    return True

#def chgiso_passed(tree, phoIdxs, cut=0.03):
#def chgiso_passed(tree, phoIdxs, cut=0.05):
#def chgiso_passed(tree, phoIdxs, cut=0.06):
#def chgiso_passed(tree, phoIdxs, cut=0.08):
#def chgiso_passed(tree, phoIdxs, cut=0.09):
def chgiso_passed(tree, phoIdxs, cut=0.07):
    # Nominal
    if (tree.phoPFChIso[phoIdxs[0]]/tree.phoEt[phoIdxs[0]]) > cut: return False
    if (tree.phoPFChIso[phoIdxs[1]]/tree.phoEt[phoIdxs[1]]) > cut: return False
    # a1, Inverted
    #if (tree.phoPFChIso[phoIdxs[0]]/tree.phoEt[phoIdxs[0]]) >  cut: return False
    #if (tree.phoPFChIso[phoIdxs[1]]/tree.phoEt[phoIdxs[1]]) <= cut: return False
    # Inverted, any 1
    #nIso = 0
    #if (tree.phoPFChIso[phoIdxs[0]]/tree.phoEt[phoIdxs[0]]) < cut: nIso += 1
    #if (tree.phoPFChIso[phoIdxs[1]]/tree.phoEt[phoIdxs[1]]) < cut: nIso += 1
    #if nIso != 1: return False
    '''
    # h4g
    passedH4g = True
    if (tree.phoPFChIso[phoIdxs[0]]/tree.phoEt[phoIdxs[0]]) > cut:
        passedH4g = False
    if (tree.phoPFChIso[phoIdxs[1]]/tree.phoEt[phoIdxs[1]]) > cut:
        passedH4g = False
    # hgg
    passedHgg = True
    #if not ( ((tree.phoR9Full5x5[phoIdxs[0]] > 0.8) and (tree.phoPFChIso[phoIdxs[0]] < 20.)) or (tree.phoPFChIso[phoIdxs[0]]/tree.phoEt[phoIdxs[0]] < 0.3) ): return False
    #if not ( ((tree.phoR9Full5x5[phoIdxs[1]] > 0.8) and (tree.phoPFChIso[phoIdxs[1]] < 20.)) or (tree.phoPFChIso[phoIdxs[1]]/tree.phoEt[phoIdxs[1]] < 0.3) ): return False
    if not ( ((tree.phoR9Full5x5[phoIdxs[0]] > 0.8) and (tree.phoPFChIso[phoIdxs[0]] < 20.)) or (tree.phoPFChIso[phoIdxs[0]]/tree.phoEt[phoIdxs[0]] < 0.3) ):
        passedHgg = False
    if not ( ((tree.phoR9Full5x5[phoIdxs[1]] > 0.8) and (tree.phoPFChIso[phoIdxs[1]] < 20.)) or (tree.phoPFChIso[phoIdxs[1]]/tree.phoEt[phoIdxs[1]] < 0.3) ):
        passedHgg = False
    #if not passedHgg: return False
    #if not passedH4g: return False # addtl
    if not (passedHgg and passedH4g): return False # common
    '''
    return True

def ptomGG_passed(tree, phoIdxs, mgg):

  #assert tree.phoEt[tree.phoPreselIdxs[0]] > tree.phoEt[tree.phoPreselIdxs[1]]
  #if tree.phoEt[tree.phoPreselIdxs[0]]/tree.mgg < 1./3.: return False
  #if tree.phoEt[tree.phoPreselIdxs[1]]/tree.mgg < 1./4.: return False
  assert tree.phoEt[phoIdxs[0]] > tree.phoEt[phoIdxs[1]]
  if tree.phoEt[phoIdxs[0]]/mgg < 1./3.: return False
  if tree.phoEt[phoIdxs[1]]/mgg < 1./4.: return False

  return True

#def in_region(region, tree):
def in_region(region, mgg_):

    #in_sblo = tree.pho12_m >= 100. and tree.pho12_m < 110.
    #in_sr   = tree.pho12_m >= 110. and tree.pho12_m < 140.
    #in_sbhi = tree.pho12_m >= 140. and tree.pho12_m < 180.
    #in_sblo = tree.mgg >= 100. and tree.mgg < 110.
    #in_sr   = tree.mgg >= 110. and tree.mgg < 140.
    #in_sbhi = tree.mgg >= 140. and tree.mgg < 180.
    in_sblo = mgg_ >= 100. and mgg_ < 110.
    in_sr   = mgg_ >= 110. and mgg_ < 140.
    in_sbhi = mgg_ >= 140. and mgg_ < 180.

    #if region == 'sb' or region == 'sb2sr':
    #if 'sb' in region:
    #if 'None' in region:
    if 'all' in region:
        return True
    elif 'sblo' in region:
        if in_sblo: return True
    elif 'sbhi' in region:
        if in_sbhi: return True
    elif 'sb' in region:
        if in_sblo or in_sbhi: return True
    #elif region == 'sr':
    elif 'sr' in region:
        if in_sr: return True
    else:
        raise Exception('Regions %s not recognized'%region)
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

    # DEPRECATED:
    # 2d-ma blinding performed post-selections

    if blind is None:
        return False

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
    #is_diag_neg = (ma0_flr < 0. and ma1_flr < diag_w) or (ma1_flr < 0. and ma0_flr < diag_w)
    is_diag_neg = (ma0_flr < diag_w and ma0_flr >= -diag_w) and\
                  (ma1_flr < diag_w and ma1_flr >= -diag_w)

    if 'sg' in blind:
        if (is_diag and not is_lo and not is_hi): return True
        #if (is_diag or is_diag_neg and not is_hi): return True

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

def get_sf(tree, preselIdx, h, shift='nom'):

    pt = tree.phoEt[preselIdx]
    sceta = tree.phoSCEta[preselIdx]

    ieta = h.GetXaxis().FindBin(sceta)
    ipt = h.GetYaxis().FindBin(pt)
    sf = h.GetBinContent(ieta, ipt)
    sf = sf if (sf > 0.) and (sf < 10.) else 1.

    if shift == 'nom':
        pass
        #sf = sf
    elif shift == 'up':
       sf += h.GetBinError(ieta, ipt)
    elif shift == 'dn':
       sf -= h.GetBinError(ieta, ipt)
    else:
       raise Exception('Unknown pho ID SF shift: %s'%shift)

    #print(preselIdx, pt, sceta, sf)
    return sf

def get_sftot(tree, h, shift='nom'):

    sftot = 1.
    if shift is None: return sftot

    for idx in tree.phoPreselIdxs:
        sftot *= get_sf(tree, idx, h, shift)
    return sftot

def get_pumc(tree):

    bx = np.array(tree.puBX)
    pu = np.array(tree.puTrue)
    ibx0 = np.argwhere(bx == 0)
    return pu[ibx0]

def get_puwgt(tree, h):

    ib = h.GetXaxis().FindBin(get_pumc(tree))
    wgt = h.GetBinContent(ib)
    wgt = wgt if (wgt > 0.) and (wgt < 10.) else 1.

    return wgt

def get_ptwgt(tree, h, ceil=10.):

    assert tree.phoEt[0] > tree.phoEt[1]

    ipt0 = h.GetXaxis().FindBin(tree.phoEt[0])
    ipt1 = h.GetYaxis().FindBin(tree.phoEt[1])
    wgt = h.GetBinContent(ipt0, ipt1)
    if wgt > ceil:
        wgt = ceil

    return wgt

def get_trgSFtot(tree, year, shift=None):

    sftot = 1.
    if shift is None: return sftot

    for i,idx in enumerate(tree.phoPreselIdxs):

        r9 = tree.phoR9[idx]
        abs_sceta = abs(tree.phoSCEta[idx])
        pt = tree.phoEt[idx]

        #sftot *= getTrgSF2016(r9, abs_sceta, pt, i, year, shift)
        sftot *= getTrgSF(r9, abs_sceta, pt, i, year, shift)

    return sftot
