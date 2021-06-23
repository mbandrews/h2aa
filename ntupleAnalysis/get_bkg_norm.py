from __future__ import print_function
from multiprocessing import Pool
import numpy as np
import ROOT
import os, glob, re
from root_numpy import hist2array
from data_utils import *
from hist_utils import *

def bkg_process(sample, mh_region, ma_blind, ma_inputs, output_dir, do_combo_template=False, norm=1., do_ptomGG=True, do_pt_reweight=False, nevts=-1, do_mini2aod=False, write_pts=False, do_pu_rwgt=False, systPhoIdSF=None, systScale=None, systSmear=None):
    '''
    Convenience fn for running the background modeling event loop.
    Returns a string for the python command arguments to be executed.
    '''
    print('Running bkg model for sample %s, mh_region: %s, ma_blind: %s'%(sample, mh_region, ma_blind))
    pyargs = 'get_bkg_model.py -s %s -r %s -b %s -i %s -t %s -o %s -n %f -e %d'\
            %(sample, mh_region, ma_blind, ' '.join(ma_inputs), get_ma_tree_name(sample), output_dir, norm, nevts)
    if do_combo_template:
        pyargs += ' --do_combined_template'
    if do_ptomGG:
        pyargs += ' --do_ptomGG'
    if do_pt_reweight:
        pyargs += ' --do_pt_reweight'
    if do_mini2aod:
        pyargs += ' --do_mini2aod'
    if write_pts:
        pyargs += ' --write_pts'
    if do_pu_rwgt:
        pyargs += ' --do_pu_rwgt'
    if systPhoIdSF is not None:
        pyargs += ' --systPhoIdSF %s'%systPhoIdSF
    if systScale is not None:
        pyargs += ' --systScale %s'%systScale
    if systSmear is not None:
        pyargs += ' --systSmear %s'%systSmear
    print('cmd: %s'%pyargs)

    return pyargs

def run_ptweights(samples, regions, blind=None, workdir='Templates_tmp', output_dir='Weights', do_ptomGG=True, flo_=None, write_pts=False, distn='pt0vpt1'):
    '''
    Calculate 2d pt wgts to map data mH-SB 2d pt distn -> data mH-SR pt distn for a given f_SBlow `flo_`.
    '''

    if not os.path.isdir(workdir):
        os.makedirs(workdir)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # Run bkg model
    processes = []
    for sample in samples:
        ma_inputs = get_mantuples(sample)
        '''
        # Run sg injection
        ma = '100MeV'
        h24g_sample = 'h24gamma_1j_1M_%s'%ma
        h24g_inputs = glob.glob('MAntuples/%s_mantuple.root'%h24g_sample)
        print('len(h24g_inputs):',len(h24g_inputs))
        assert len(h24g_inputs) > 0
        ma_inputs = ma_inputs + h24g_inputs
        print('len(ma_inputs):',len(ma_inputs))
        '''
        s = sample.replace('[','').replace(']','')
        for r in regions[sample]:
            processes.append(bkg_process(s, r, blind, ma_inputs, workdir,\
                                        do_ptomGG=do_ptomGG if 'sb' in r else True,\
                                        write_pts=write_pts))

    # Run processes in parallel
    pool = Pool(processes=len(processes))
    pool.map(run_process, processes)
    pool.close()
    pool.join()

    h, hf = {}, {}
    for sample in samples:
        s = sample.replace('[','').replace(']','')
        load_hists(h, hf, [s], regions[sample], [distn], blind, workdir)
    #print(h.keys())

    k = distn
    norm_scale = 150.e3
    for sample in samples:
        s = sample.replace('[','').replace(']','')
        for tgt in ['sr']:

            # Get "natural flo if not user-specified
            if flo_ is None:
                flo_ = h['%s_sblo_%s'%(s, k)].Integral()/(h['%s_sblo_%s'%(s, k)].Integral()+h['%s_sbhi_%s'%(s, k)].Integral())
                print('Nsblo:%f, Nsbhi:%f, Nsr:%f'%(\
                        h['%s_sblo_%s'%(s, k)].Integral(),\
                        h['%s_sbhi_%s'%(s, k)].Integral(),\
                        h['%s_%s_%s'%(s, tgt, k)].Integral()))
            print('flo_:',flo_)

            # Normalize histograms to norm_scale
            h['%s_%s_%s'%(s, tgt, k)].Scale(norm_scale/h['%s_%s_%s'%(s, tgt, k)].Integral())
            h['%s_sblo_%s'%(s, k)].Scale(norm_scale/h['%s_sblo_%s'%(s, k)].Integral())
            h['%s_sbhi_%s'%(s, k)].Scale(norm_scale/h['%s_sbhi_%s'%(s, k)].Integral())

            # Add normalized SB-lo,hi hists in fracs: flo, 1.-flo
            kcombo = '%s_sbcombo_%s'%(s, k)
            h[kcombo] = h['%s_sblo_%s'%(s, k)].Clone()
            #print('sb-lo integral, pre-scale:',h[kcombo].Integral())
            h[kcombo].Scale(flo_)
            #print('sb-lo integral, post-scale:',h[kcombo].Integral())
            h[kcombo].Add(h['%s_sbhi_%s'%(s, k)], (1.-flo_))
            #print('sb-lo+hi integral, post-scale:',h[kcombo].Integral())

            # SB->SR weights given by ratio SR/SB
            h[tgt+'%s_ratio'%k] = h['%s_%s_%s'%(s, tgt, k)].Clone()
            h[tgt+'%s_ratio'%k].Divide(h[kcombo])

            # Save all histograms for reference
            # Actual weights to be used during event loop are written to separate file below
            hf[tgt+'ratios'] = ROOT.TFile("%s/%s_sb2%s_blind_%s_ptwgts.root"%(output_dir, s, tgt, blind), "RECREATE")
            h['%s_%s_%s'%(s, tgt, k)].SetName('%s_%s_%s'%(s, tgt, k))
            h['%s_%s_%s'%(s, tgt, k)].Write()
            h['%s_sblo_%s'%(s, k)].SetName('%s_sblo_%s'%(s, k))
            h['%s_sblo_%s'%(s, k)].Write()
            h['%s_sbhi_%s'%(s, k)].SetName('%s_sbhi_%s'%(s, k))
            h['%s_sbhi_%s'%(s, k)].Write()
            h[kcombo].SetName(kcombo)
            h[kcombo].Write()
            h[tgt+'%s_ratio'%k].SetName('%s_ratio'%k)
            h[tgt+'%s_ratio'%k].Write()
            hf[tgt+'ratios'].Close()

            # TH2 origin @ lower left + (ix, iy)
            # x:lead, y:sublead

            # hist2array().T origin @ lower left + (row, col) <=> (iy, ix)
            # NOTE: hist2array() drops uflow and ovflow bins => idx -> idx-1
            # row:sublead, col:lead
            ratio, pt_edges = hist2array(h[tgt+'%s_ratio'%k], return_edges=True)
            ratio, pt_edges_lead, pt_edges_sublead = ratio.T, pt_edges[0], pt_edges[1]
            #print(len(pt_edges_lead), len(pt_edges_sublead))

            # Remove unphysical values
            #ratio[ratio==0.] = 0.
            ratio[np.isnan(ratio)] = 1.
            ratio[ratio>10.] = 10.
            print('pt-ratio:')
            print(ratio.min(), ratio.max(), np.mean(ratio), np.std(ratio))

            # Write out weights to numpy file
            #np.savez("%s/%s_%s2%s_blind_%s_ptwgts.npz"%(output_dir, s, sb, tgt, blind), pt_edges=pt_edges, pt_wgts=ratio)
            np.savez("%s/%s_sb2%s_blind_%s_ptwgts.npz"\
                    %(output_dir, s, tgt, blind), pt_edges_lead=pt_edges_lead, pt_edges_sublead=pt_edges_sublead, pt_wgts=ratio)

    return flo_

def run_combined_sbfit(samples, regions, blind=None, output_dir='Templates_tmp', do_pt_reweight=False, do_ptomGG=True, flo_=None, distn='pt0vpt1', flo_nom=None):

    '''
    do_pt_reweight: boolean applied to SB regions only!
    do_ptomGG: boolean applied to SB regions only!

    [1] Run bkg analyzer with 2d-ma signal region `sg` blinded
    to derive 2d-ma templates for hgg in mH-SR, data mH-SB and the target data mH-SR

    [2] Use TFractionFitter to fit relative proportions of hgg, mH-low, mH-high SB templates
    in mH-SR, fgg, flo, fhi, respectively. TODO: Implement hgg

    '''
    if not do_ptomGG:
        assert do_pt_reweight

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # Run bkg model
    processes = []
    for sample in samples:
        ma_inputs = get_mantuples(sample)
        s = sample.replace('[','').replace(']','')
        for r in regions[sample]:
            processes.append(bkg_process(s, r, blind, ma_inputs, output_dir,\
                                        do_ptomGG=do_ptomGG if 'sb' in r else True,\
                                        do_pt_reweight=do_pt_reweight if 'sb' in r else False))

    # Run processes in parallel
    pool = Pool(processes=len(processes))
    pool.map(run_process, processes)
    pool.close()
    pool.join()

    # [2] Fit hgg and mH-SB template fractions into mH-SR:
    # Normalize templates to unit Integral() in the unblinded region.
    # NOTE: TFractionFiter seg faults at deconstruction in PyROOT...
    # need to put in fgg, flo, fhi by hand after, or [TODO] re-implement in C++.
    #fgg, flo, fhi = fit_templates_sb(blind, output_dir, derive_fit, flo_)
    fgg, flo, fhi = fit_templates_sb(samples, regions, blind, output_dir, flo_, distn, flo_nom)

    return fgg, flo, fhi
    #return 1., 0., 0.

def fit_templates_sb(samples, regions, blind=None, workdir='Templates_tmp', flo_=None, distn='pt0vpt1', flo_nom=None):
    '''
    Fit for fraction of hgg and data mH-low, mH-high SB templates in data mH-SR, fgg, flo, fhi, resp.
    Normalize each template to have unit Integral() first.
    '''
    assert flo_ is not None

    h, hf = {}, {}

    for sample in samples:
        s = sample.replace('[','').replace(']','')
        load_hists(h, hf, [s], regions[sample], [distn], blind, workdir)

    nSR = h['Run2017B-F_sr_%s'%distn].Integral()
    nSBlo = h['Run2017B-F_sblo_%s'%distn].Integral()
    nSBhi = h['Run2017B-F_sbhi_%s'%distn].Integral()
    nHgg = h['GluGluHToGG_sr_%s'%distn].Integral()
    print('Nsblo:%f, Nsbhi:%f, Nsr:%f'%(nSBlo, nSBhi, nSR))

    # To correctly calculate SB fractions when pt re-weighting src events so they yield same pt distn as for tgt events:
    # [1] Normalized pt distns must be scaled by their relative integrals just after re-weighting.
    #     In general, flo after pt re-weighting not the same as flo before, so must be calculated on post pt rewgt integrals.
    #     This is equivalent to not doing the normalization in the first place.
    #     (Needed because mass templates will be normalized).
    # [2] For any choice of flo != flo_nom = ratio of raw events Nsblo/(Nsblo+Nsbhi) used as input to pt rewgt,
    #     pt rewgting alone does not give right mix of SBs if pt weights applied to raw SB events evt-by-evt.
    #     Need to scale up/down SB events accordingly by relative ratio flo/flo_nom (pre pt rewgt values).
    #     ~ scaling src evts by flo_nom/flo
    flo_ptrwgt = 1.*nSBlo/(nSBlo+nSBhi) # flo post pt re-weighting -> to undo normalization of pt distn
    print('flo, pre-ptrwgt:%f, flo, post-ptrwgt:%f'%(flo_, flo_ptrwgt))
    print('flo_nom, pre-ptrwgt: %f'%(flo_nom))
    flo = flo_*flo_ptrwgt/flo_nom # [1]: flo_ptrwgt, [2]: flo_/flo_nom
    fhi = (1.-flo_)*(1.-flo_ptrwgt)/(1.-flo_nom)
    print(flo, fhi, flo+fhi)
    flohi = flo+fhi
    flo = flo/flohi
    fhi = fhi/flohi
    print(flo, fhi, flo+fhi)

    #hgguncert = -48.58*5.11e-3
    hgguncert = 0.
    hggscale = 2.27e-3*(48.58+hgguncert)*41.9e3*nHgg/214099989.445038
    hggscale /= nSR
    print('hgg lumi-wgt:',hggscale)

    fgg = hggscale
    #fgg = 0.
    fsb = 1.-fgg
    #if flo_ is None:
    #    flo = fsb*nSBlo/(nSBlo+nSBhi)
    #    fhi = fsb*nSBhi/(nSBlo+nSBhi)
    #else:
    #flo = fsb*flo_
    #fhi = fsb*(1.-flo_)
    flo = fsb*flo
    fhi = fsb*fhi

    print(fgg, flo, fhi, fgg+flo+fhi)
    assert abs(fgg+flo+fhi-1.) < 1.e-5

    return fgg, flo, fhi

def get_bkg_norm_sb(samples, regions, blind='diag_lo_hi', workdir='Templates_tmp', do_pt_reweight=False, do_ptomGG=True, distn='ma0vma1'):
    '''
    Calculate relative normalization between data mH-SB templates (srcs) and data mH-SR (tgt).
    '''

    if not do_ptomGG:
        pass
        assert do_pt_reweight

    if not os.path.isdir(workdir):
        os.makedirs(workdir)

    # Run bkg model
    processes = []
    for sample in samples:
        ma_inputs = get_mantuples(sample)
        s = sample.replace('[','').replace(']','')
        for r in regions[sample]:
            processes.append(bkg_process(s, r, blind, ma_inputs, workdir,\
                                        do_ptomGG=do_ptomGG if 'sb' in r else True,\
                                        do_pt_reweight=do_pt_reweight if 'sb' in r else False))

    # Run processes in parallel
    pool = Pool(processes=len(processes))
    pool.map(run_process, processes)
    pool.close()
    pool.join()

    h, hf = {}, {}
    entries = {}
    integral = {}
    norm = {}

    key = distn

    # Read in templates
    for sample in samples:
        s = sample.replace('[','').replace(']','')
        for r in regions[sample]:
            hf[s+r] = ROOT.TFile("%s/%s_%s_blind_%s_templates.root"%(workdir, s, r, blind), "READ")

    # Target distn is data mH-SR
    ktgt = [k for k in hf.keys() if 'Run2017' in k and 'sr' in k]
    assert len(ktgt) == 1
    ktgt = ktgt[0]

    # Src distns are data mH-SB and hgg mH-SR
    ksrcs = [k for k in hf.keys() if 'GluGluH' in k or 'sb' in k]

    # Calculate integrals (i.e. wgtd Nevts not in under/over-flow bins)
    for k in ksrcs+[ktgt]:
        h[k] = hf[k].Get(key)
        entries[k] = h[k].GetEntries()
        integral[k] = h[k].Integral()
        print(integral[k])

    # Calculate normalization ratio
    for ksrc in ksrcs:
        norm[ksrc] = integral[ktgt]/integral[ksrc]

    return norm['Run2017B-F'+'sblo'], norm['Run2017B-F'+'sbhi'], norm['GluGluHToGG'+'sr']

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

def get_pt_wgt(tree, pt_edges_lead, pt_edges_sublead, wgts):
    '''
    Convenience fn for returning 2d-pt wgt for an event loaded into `tree`
    '''
    assert tree.phoEt[0] > tree.phoEt[1]
    return get_weight_2d(tree.phoEt[0], tree.phoEt[1], pt_edges_lead, pt_edges_sublead, wgts)

def get_combined_template_wgt(tree, ma_edges, wgts):
    '''
    Convenience fn for returning 2d-ma wgt for an event loaded into `tree`
    '''
    return get_weight_2d(tree.ma0, tree.ma1, ma_edges, wgts)

def get_weight_2d(q_lead, q_sublead, q_edges_lead, q_edges_sublead, wgts):
    '''
    Returns wgt corresponding to (q_lead, q_sublead) in 2d-q plane
    '''
    # NOTE: assumes wgts corresponds to
    # row:sublead, col:lead
    iq_lead = get_weight_idx(q_lead, q_edges_lead)
    iq_sublead = get_weight_idx(q_sublead, q_edges_sublead)

    #print(iq_sublead, iq_lead)
    return wgts[iq_sublead, iq_lead]

def get_mini2aod_wgt(tree, ma_edges, pt_edges, wgts):
    wgt = 1.
    # ma0
    wgt = wgt*get_weight_2d(tree.ma0, tree.phoEt[0], ma_edges, pt_edges, wgts)
    # ma1
    wgt = wgt*get_weight_2d(tree.ma1, tree.phoEt[1], ma_edges, pt_edges, wgts)

    return wgt

def get_entries_cr(h, cr):
    '''
    Get number of raw histogram entries in a given control region of the 2d-ma plane
    '''
    #bin = 0;       underflow bin
    #bin = 1;       first bin with low-edge xlow INCLUDED
    #bin = nbins;   last bin with upper-edge xup EXCLUDED
    #bin = nbins+1; overflow bin
    # => range(1, nbins+1) to get physical bins
    # => gg at bin(1,1)

    if cr == 'gg':
        return h.GetBinContent(1,1)
    elif cr == 'gj':
        return sum(h.GetBinContent(1, iy) for iy in range(2,h.GetNbinsY()+1))
    elif cr == 'jg':
        return sum(h.GetBinContent(ix, 1) for ix in range(2,h.GetNbinsX()+1))
    elif cr == 'jj':
        njj = 0
        for ix in range(2,h.GetNbinsX()+1):
            for iy in range(2,h.GetNbinsY()+1):
                njj += h.GetBinContent(ix, iy)
        return njj
    else:
        return 0.

def floor_hist(h):

    for ix in range(0,h.GetNbinsX()+1):
        for iy in range(0,h.GetNbinsY()+1):
            if h.GetBinContent(ix, iy) < 0.:
                h.SetBinContent(ix, iy, 0.)
    return h

def get_sg_norm(sample, xsec=50., tgt_lumi=41.9e3): # xsec:pb, tgt_lumi:/pb

    #gg_cutflow = glob.glob('../ggSkims/%s_cut_hists.root'%sample)
    gg_cutflow = glob.glob('../ggSkims/3pho/%s_cut_hists.root'%sample)
    assert len(gg_cutflow) == 1

    cut = str(None)
    var = 'npho'
    key = cut+'_'+var
    hf = ROOT.TFile(gg_cutflow[0], "READ")
    h = hf.Get('%s/%s'%(cut, key))

    nevts_gen = h.GetEntries()
    # Sum of wgts
    if sample == 'DiPhotonJets':
        nevts_gen = 1118685275.488525
    elif sample == 'GluGluHToGG':
        nevts_gen = 214099989.445038
    print(nevts_gen)
    norm = xsec*tgt_lumi/nevts_gen
    #print(norm)
    return norm

def get_sg_norm_bycampaign(sample, campaign, tgt_lumi=41.9e3, xsec=50., eos_basedir='root://cmseos.fnal.gov//store/user/lpchaa4g/mandrews'): # xsec:pb, tgt_lumi:/pb

    # root://cmseos.fnal.gov//store/user/lpchaa4g/mandrews/2018/ggNtuples-Era04Dec2020v1_ggSkim-v1/ggSkims//h4g2018-mA1p2GeV_cut_hists.root
    year = re.findall('(201[6-8])', sample.split('-')[0])[0]
    inpath = '%s/%s/%s/ggNtuples-%s/ggSkims/%s_cut_hists.root'%(eos_basedir, year, campaign, sample)

    cut = str(None) # no cuts applied to get gen level event count
    var = 'npho' # any var that has 1 count per evt will do
    key = cut+'_'+var
    hf = ROOT.TFile.Open(inpath, "READ")
    h = hf.Get('%s/%s'%(cut, key))

    nevts_gen = h.GetEntries()
    # In general, one should use sum of wgtd evts to calculate `nevts_gen`
    # not just the raw event count. Only valid for samples with wgt = 1.
    # such as is the case for all h4g sg samples, but not for some bkg mc samples
    assert 'h4g' in sample
    ## Sum of wgts
    #if sample == 'DiPhotonJets':
    #    nevts_gen = 1118685275.488525
    #elif sample == 'GluGluHToGG':
    #    nevts_gen = 214099989.445038
    #print(nevts_gen)
    norm = xsec*tgt_lumi/nevts_gen
    #print(norm)
    print('>> For sample %s | norm(mc->data) from Ngen: %.f to data int. lumi: %.f /pb @ sg prodn xs: %.f pb: %.f'%(sample, nevts_gen, tgt_lumi, xsec, norm))
    return norm
