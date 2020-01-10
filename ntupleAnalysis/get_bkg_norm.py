from __future__ import print_function
from multiprocessing import Pool
import numpy as np
import ROOT
import os, glob
from root_numpy import hist2array
from data_utils import *

def bkg_process(s, r, blind, ma_inputs, output_dir, do_combo_template=False, norm=1., do_ptomGG=True, do_pt_reweight=False):
    '''
    Convenience fn for running the background modeling event loop.
    Returns a string for the python command arguments to be executed.
    '''
    print('Running bkg model for sample %s, region: %s, blind: %s'%(s, r, blind))
    pyargs = 'get_bkg_model.py -s %s -r %s -b %s -i %s -t %s -o %s -n %f'\
            %(s, r, blind, ' '.join(ma_inputs), get_ma_tree_name(s), output_dir, norm)
    if do_combo_template:
        pyargs += ' --do_combined_template'
    if do_ptomGG:
        pyargs += ' --do_ptomGG'
    if do_pt_reweight:
        pyargs += ' --do_pt_reweight'
    print('cmd: %s'%pyargs)

    return pyargs

def run_combined_template(fgg=None, fjj=None, norm=1., derive_fit=False, do_pt_reweight=False, do_ptomGG=False):

    '''
    do_pt_reweight: boolean applied to SB regions only!
    do_ptomGG: boolean applied to SB regions only!

    [1] Run bkg analyzer with 2d-ma signal region `sg` blinded
    to derive 2d-ma templates for hgg in mH-SR, data mH-SB and the target data mH-SR

    [2] Use TFractionFitter to fit relative proportions of hgg, mH-SB templates
    in mH-SR, fgg and fjj, respectively

    [3] Re-run bkg analyzer with full 2d-ma unblinded on hgg and data mH-SB and
    calculate wgts for mapping data mH-SB -> combined hgg + data mH-SB by taking ratio

    ( fgg*template_hgg + fjj*template_mH-SB ) / template_mH-SB

    Since we use 1d-ma1,2 for setting limits, we cannot simply use the
    combined template as is but must use it to derive a set of event weights
    binned by the 2d-ma distn. These will then be responsible for "enhancing" the
    basic mH-SB shape to account for the hgg contribution when running the evt loop.
    '''
    if not do_ptomGG:
        assert do_pt_reweight

    output_dir = 'Templates'
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # [1] First run hgg, data mH-SB, data mH-SR with 2d-ma-SR blinded
    # These will output TH2F histograms into root files which will be picked up in [2]
    blind = 'sg'

    # Data mH-SB and mH-SR
    s = 'Run2017[B-F]'
    ma_inputs = glob.glob('MAntuples/%s_mantuple.root'%s)
    print('len(ma_inputs):',len(ma_inputs))
    assert len(ma_inputs) > 0

    s = s.replace('[','').replace(']','')
    regions = ['sb', 'sr']
    processes = [bkg_process(s, r, blind, ma_inputs, output_dir,\
            do_ptomGG=do_ptomGG if 'sb' in r else True,\
            do_pt_reweight=do_pt_reweight if 'sb' in r else False)\
            for r in regions]

    # hgg, mH-SR
    s = 'GluGluHToGG'
    ma_inputs = glob.glob('MAntuples/%s_mantuple.root'%s)
    print('len(ma_inputs):',len(ma_inputs))
    assert len(ma_inputs) > 0

    r = 'sr'
    processes.append(bkg_process(s, r, blind, ma_inputs, output_dir))
    #processes.append(bkg_process(s, r, blind, ma_inputs, output_dir, do_pt_reweight=do_pt_reweight))

    # Run processes in parallel
    pool = Pool(processes=len(processes))
    pool.map(run_process, processes)
    pool.close()
    pool.join()

    # [2] Fit hgg and mH-SB template fractions into mH-SR:
    # Normalize templates to have same normalization as SR in gg bin for hgg template
    # and off-diag 0 <= m_a < 1.2 bins for SB template. This is also needed for fit convergence.
    # NOTE: TFractionFiter seg faults at deconstruction in PyROOT...
    # need to put in fgg and fjj by hand after, or [TODO] re-implement in C++.
    #if derive_fit:
    fgg, fjj, norm = fit_templates(blind, output_dir, derive_fit)

    # [3] Re-run the hgg and mH-SB processes only on the full 2d-ma plane.
    # to derive the evt wgts over the full 2d-ma plane:
    # Construct fgg*template_hgg + fjj*template_mH-SB then
    # then divide by template_mH-SB. The ratio then gives evt wgts
    # to be applied per region of 2d-ma. They will be slightly enhanced
    # in the gg area and tend to 1 in the jj region.
    blind = None

    # Data mH-SB
    s = 'Run2017[B-F]'
    ma_inputs = glob.glob('MAntuples/%s_mantuple.root'%s)
    print('len(ma_inputs):',len(ma_inputs))
    assert len(ma_inputs) > 0

    s = s.replace('[','').replace(']','')
    regions = ['sb']
    processes = [bkg_process(s, r, blind, ma_inputs, output_dir,\
            do_ptomGG=do_ptomGG if 'sb' in r else True,\
            do_pt_reweight=do_pt_reweight if 'sb' in r else False)\
            for r in regions]

    # hgg, mH-SR
    s = 'GluGluHToGG'
    ma_inputs = glob.glob('MAntuples/%s_mantuple.root'%s)
    print('len(ma_inputs):',len(ma_inputs))
    assert len(ma_inputs) > 0

    r = 'sr'
    processes.append(bkg_process(s, r, blind, ma_inputs, output_dir))

    # Run processes in parallel
    pool = Pool(processes=len(processes))
    pool.map(run_process, processes)
    pool.close()
    pool.join()

    # Calculate ratio from output templates
    get_template_ratio(fgg, fjj, norm, blind, output_dir)

def load_hists(h, hf, samples, regions, keys, blind, input_dir):

    # NOTE: Need to pass file objects `hf` as well for histograms `h`
    # to remain persistent, otherwise segfaults
    for s in samples :
        for r in regions:
            if s == 'GluGluHToGG' and r == 'sb': continue
            if 'Run2017' in s and r == 'sr' and blind == None and 'pt0vpt1' not in keys: continue
            sr = '%s_%s'%(s, r)
            hf[sr] = ROOT.TFile("%s/%s_%s_blind_%s_templates.root"%(input_dir, s, r, blind),"READ")
            for k in keys:
                srk = '%s_%s_%s'%(s, r, k)
                h[srk] = hf[sr].Get(k)

def run_ptweights(blind=None, sb='sb', sample='Run2017[B-F]', workdir='Templates', do_ptomGG=False):
    '''
    Calculate normalization for the mapping of 2d-ma data mH-SB template(s) to data mH-SR.
    '''

    # Run both SB and SR to bkg processes
    ma_inputs = glob.glob('MAntuples/%s_mantuple.root'%sample)
    print('len(ma_inputs):',len(ma_inputs))
    assert len(ma_inputs) > 0
    sample = sample.replace('[','').replace(']','')
    regions = [sb, 'sr']
    processes = [bkg_process(sample, r, blind, ma_inputs, workdir, do_ptomGG=do_ptomGG if r == sb else True) for r in regions]

    # Run processes in parallel
    pool = Pool(processes=len(processes))
    pool.map(run_process, processes)
    pool.close()
    pool.join()

    h, hf = {}, {}
    sample = sample.replace('[','').replace(']','')
    samples = [sample]
    #regions = ['sb', 'sr']
    keys = ['pt0vpt1']
    load_hists(h, hf, samples, regions, keys, blind, workdir)
    print(h.keys())

    k = keys[0]
    h['%s_ratio'%k] = h['%s_sr_%s'%(sample, k)].Clone()
    h['%s_ratio'%k].Divide(h['%s_%s_%s'%(sample, sb, k)])

    # Save all histograms for reference
    # Actual weights to be used during event loop are written to separate file below
    output_dir = 'Weights'
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    hf['ratios'] = ROOT.TFile("%s/%s_%s_blind_%s_ptwgts.root"%(output_dir, sample, r, blind), "RECREATE")
    h['%s_sr_%s'%(sample, k)].SetName('%s_sr_%s'%(sample, k))
    h['%s_sr_%s'%(sample, k)].Write()
    h['%s_%s_%s'%(sample, sb, k)].SetName('%s_%s_%s'%(sample, sb, k))
    h['%s_%s_%s'%(sample, sb, k)].Write()
    h['%s_ratio'%k].SetName('%s_ratio'%k)
    h['%s_ratio'%k].Write()
    hf['ratios'].Close()

    # TH2 origin @ lower left + (ix, iy)
    # x:lead, y:sublead

    # hist2array().T origin @ lower left + (row, col) <=> (iy, ix)
    # NOTE: hist2array() drops uflow and ovflow bins => idx -> idx-1
    # row:sublead, col:lead
    ratio, pt_edges = hist2array(h['%s_ratio'%k], return_edges=True)
    ratio, pt_edges = ratio.T, pt_edges[0]

    # Remove unphysical values
    #ratio[ratio==0.] = 0.
    ratio[np.isnan(ratio)] = 1.
    print('pt-ratio:')
    print(ratio.min(), ratio.max(), np.mean(ratio), np.std(ratio))

    # Write out weights to numpy file
    np.savez("%s/%s_%s2sr_blind_%s_ptwgts.npz"%(output_dir, sample, sb, blind), pt_edges=pt_edges, pt_wgts=ratio)

def get_bkg_norm(blind='sg', sb='sb', sample='Run2017[B-F]', workdir='Templates', do_pt_reweight=False, do_ptomGG=False):
    '''
    Calculate normalization for the mapping of 2d-ma data mH-SB template(s) to data mH-SR.
    '''
    if not do_ptomGG:
        assert do_pt_reweight

    # Run both SB and SR to bkg processes
    ma_inputs = glob.glob('MAntuples/%s_mantuple.root'%sample)
    print('len(ma_inputs):',len(ma_inputs))
    assert len(ma_inputs) > 0
    sample = sample.replace('[','').replace(']','')
    regions = [sb, 'sr']
    processes = [bkg_process(sample, r, blind, ma_inputs, workdir,\
            do_combo_template=True if r == 'sbcombo' else False,\
            do_ptomGG=do_ptomGG if r == sb else True,\
            do_pt_reweight=do_pt_reweight if r == sb else False)\
            for r in regions]

    # Run processes in parallel
    pool = Pool(processes=len(processes))
    pool.map(run_process, processes)
    pool.close()
    pool.join()

    h, hf = {}, {}
    entries = {}
    integral = {}

    regions = [sb, 'sr']
    keys = ['maxy']

    print("%s/%s_%s_blind_%s_templates.root"%(workdir, sample, r, blind))

    for r in regions:
        hf[r] = ROOT.TFile("%s/%s_%s_blind_%s_templates.root"%(workdir, sample, r, blind),"READ")
        for k in keys:
            rk = '%s_%s'%(r, k)
            #if rk == 'sr_maxy': c[rk] = ROOT.TCanvas("c%s"%rk,"c%s"%rk, wd, ht)
            h[rk] = hf[r].Get(k)
            #h[rk].Draw("")
            entries[rk] = h[rk].GetEntries()
            integral[rk] = h[rk].Integral()

    r = '%s2sr'%sb
    for k in keys:
        if k != 'maxy': continue
        rk = '%s_%s'%(r, k)
        h[rk] = h['%s_%s'%(sb, k)].Clone()
        #norm = entries['sr_%s'%k]/entries['sb_%s'%k]
        norm = integral['sr_%s'%k]/integral['%s_%s'%(sb, k)]
        print('%s2sr norm: %f'%(sb, norm))
        #h[rk].Scale(norm)
        #h['sr_%s'%k].SetLineColor(9)
        #h['sr_%s'%k].Draw("hist")
        #h[rk].SetLineColor(2)
        #h[rk].Draw("hist same")

    return norm
    # derive 1sigma uncert vs ma

def fit_templates(blind='sg', workdir='Templates', derive_fit=False):
    '''
    Fit for fraction of hgg and data mH-SB templates in data mH-SR, fgg and fjj, resp.
    Need to also return the normalizations used for the input templates.
    '''
    h, hf = {}, {}
    samples = ['Run2017B-F', 'GluGluHToGG']
    regions = ['sb', 'sr']
    keys = ['ma0vma1']
    load_hists(h, hf, samples, regions, keys, blind, workdir)

    '''
    for s in samples :
        for r in regions:
            if s == 'GluGluHToGG' and r == 'sb': continue
            for k in keys:
                srk = '%s_%s_%s'%(s, r, k)
                print(srk)
                print(h[srk].GetNbinsX(), h[srk].GetNbinsY())
                print(h[srk].Integral())
                print(h[srk].GetBinContent(1,1))
                ngg = 0
                for i,ix in enumerate(range(1,h[srk].GetNbinsX()+1)):
                    for j,iy in enumerate(range(1,h[srk].GetNbinsY()+1)):
                        ngg += h[srk].GetBinContent(ix, iy)
                print(ngg)
                print('gg:',get_entries_cr(h[srk], 'gg'))
                print('gj:',get_entries_cr(h[srk], 'gj'))
                print('jg:',get_entries_cr(h[srk], 'jg'))
                print('jj:',get_entries_cr(h[srk], 'jj'))
                print('integral-all:',h[srk].Integral()-(\
                        get_entries_cr(h[srk], 'gg')\
                        +get_entries_cr(h[srk], 'gj')\
                        +get_entries_cr(h[srk], 'jg')\
                        +get_entries_cr(h[srk], 'jj')))
    '''

    # sb2sr = fgg*gg_normed + fsb*sb_normed
    # 0th ordero: fgg, fsb chosen s.t.
    # to check sb2sr(gg) ~ sr(gg) AND sb2sr(jj) ~ sr(jj)
    # need not be fsb = 1-fgg since normalizations are not completely orthogonal
    # 1st order: do TFractionFitter template fit -> converges but segfaults on exit
    # => need to put in values by hand after fit
    norm = {}

    h['gg'] = h['GluGluHToGG_sr_ma0vma1'].Clone()
    norm['gg'] = get_entries_cr(h['Run2017B-F_sr_ma0vma1'],'gg')/get_entries_cr(h['gg'], 'gg')
    h['gg'].Scale(norm['gg'])
    #print('gg:',get_entries_cr(h['Run2017B-F_sr_ma0vma1'],'gg'), get_entries_cr(h['gg'], 'gg'))
    print('higgs-only, gg:%f, jj:%f'%(get_entries_cr(h['gg'], 'gg'), get_entries_cr(h['gg'], 'jj')))

    h['jj'] = h['Run2017B-F_sb_ma0vma1'].Clone()
    norm['jj'] = get_entries_cr(h['Run2017B-F_sr_ma0vma1'],'jj')/get_entries_cr(h['jj'], 'jj')
    h['jj'].Scale(norm['jj'])
    #print('jj:',get_entries_cr(h['Run2017B-F_sr_ma0vma1'],'jj'), get_entries_cr(h['jj'], 'jj'))
    print('sb-only, gg:%f, jj:%f'%(get_entries_cr(h['jj'], 'gg'), get_entries_cr(h['jj'], 'jj')))
    print('sr-obs, gg:%f, jj:%f'%(get_entries_cr(h['Run2017B-F_sr_ma0vma1'], 'gg'), get_entries_cr(h['Run2017B-F_sr_ma0vma1'], 'jj')))

    #fgg, fjj = 1., 0.
    #fgg, fjj = 0., 1.
    #fgg, fjj = 0.01, 1.
    #v1
    #fgg = 1.01192e-02
    #fjj = 9.89872e-01
    #v2
    #fgg = 9.95548e-03
    #fjj = 9.90042e-01
    # ggntuple+ptreweight, n=10k
    #fgg = 1.02883e-02
    #fjj = 9.89702e-01
    # ggntuple+ptreweight+bdt>-0.98, n=all
    fgg = 7.63500e-04
    fjj = 9.99414e-01
    # ggntuple+ptreweight+bdt>-0.90, n=all
    fgg = 0.
    fjj = 1.
    #fgg = 0.05
    #fjj = 0.95

    if derive_fit:
        mc = ROOT.TObjArray()
        mc.Add(h['gg'])
        mc.Add(h['jj'])
        fit = ROOT.TFractionFitter(h['Run2017B-F_sr_ma0vma1'], mc)
        fit.Constrain(0, 0., 0.1)
        fit.Constrain(1, 0.9, 1.)
        status = fit.Fit() # seg faults at deconstruction (not supported in PyROOT)
        print('fit status:',status)

    k = 'Run2017B-F_sb2sr_ma0vma1'
    h[k] = h['gg'].Clone()
    h[k].Scale(fgg)
    #print(get_entries_cr(h[k],'gg'))
    h[k].Add(h['jj'], fjj)

    print('sb2sr, gg:%f, jj:%f'%(get_entries_cr(h[k], 'gg'), get_entries_cr(h[k], 'jj')))
    #h[k].Scale(1.01)
    #h[k].Scale(21160.999930/20963.916237)
    norm['sb2sr'] = get_entries_cr(h['Run2017B-F_sr_ma0vma1'], 'jj')/get_entries_cr(h[k], 'jj')
    h[k].Scale(norm['sb2sr'])
    print('sb2sr, gg:%f, jj:%f'%(get_entries_cr(h[k], 'gg'), get_entries_cr(h[k], 'jj')))
    print('gg ratio discrepancy:',get_entries_cr(h['Run2017B-F_sr_ma0vma1'], 'gg')/get_entries_cr(h[k], 'gg'))

    return fgg, fjj, norm

def get_template_ratio(fgg, fjj, norm, blind=None, workdir='Templates'):
    '''
    Calculate ratio ( fgg*template_hgg + fjj*template_mH-SB ) / template_mH-SB
    for hgg and data mH-SB templates found in `workdir` to derive evt wgts binned in 2d-ma.
    Outputs reference histograms and a numpy file containing actual 2d-ma wgts.
    NOTE: need to use same template normalizations `norm` as were used to derive the fits `fgg`, `fjj`.
    '''
    h, hf = {}, {}
    samples = ['Run2017B-F', 'GluGluHToGG']
    regions = ['sb', 'sr']
    keys = ['ma0vma1']
    load_hists(h, hf, samples, regions, keys, blind, workdir)

    # Get hgg template and normalize
    h['gg'] = h['GluGluHToGG_sr_ma0vma1'].Clone()
    h['gg'].Scale(norm['gg'])
    #print('gg:',get_entries_cr(h['Run2017B-F_sr_ma0vma1'],'gg'), get_entries_cr(h['gg'], 'gg'))
    print('higgs-only, gg:%f, jj:%f'%(get_entries_cr(h['gg'], 'gg'), get_entries_cr(h['gg'], 'jj')))

    # Get data mH-SB template and normalize
    h['jj'] = h['Run2017B-F_sb_ma0vma1'].Clone()
    h['jj'].Scale(norm['jj'])
    print('sb-only, gg:%f, jj:%f'%(get_entries_cr(h['jj'], 'gg'), get_entries_cr(h['jj'], 'jj')))

    # Contstuct fgg*template_hgg + fjj*template_mH-SB
    s = 'Run2017B-F+GluGluHToGG'
    r = 'sb2sr'
    k = 'ma0vma1'
    srk = '%s_%s_%s'%(s, r, k)
    h[srk] = h['gg'].Clone()
    h[srk].Scale(fgg)
    h[srk].Add(h['jj'], fjj)
    h[srk].Scale(norm['sb2sr'])
    print('sb2sr, gg:%f, jj:%f'%(get_entries_cr(h[srk], 'gg'), get_entries_cr(h[srk], 'jj')))

    # Take ratio of combined template to (normalized) template_mH-SB
    h['%s_ratio'%srk] = h[srk].Clone()
    h['%s_ratio'%srk].Divide(h['jj'])

    # Save all histograms for reference
    # Actual weights to be used during event loop are written to separate file below
    hf[srk] = ROOT.TFile("%s/%s_%s_blind_%s_templates.root"%(workdir, s, r, blind), "RECREATE")
    h['gg'].Write()
    h['jj'].Write()
    h[srk].Write()
    h['%s_ratio'%srk].Write()
    hf[srk].Write()
    hf[srk].Close()

    # TH2 origin @ lower left + (ix, iy)
    # x:lead, y:sublead
    #print('(1,1):',h[srk].GetBinContent(1,1))
    #print('(2,2):',h[srk].GetBinContent(2,2))
    #print('(1,2):',h[srk].GetBinContent(1,2)) #gj
    #print('(2,1):',h[srk].GetBinContent(2,1))

    # hist2array().T origin @ lower left + (row, col) <=> (iy, ix)
    # NOTE: hist2array() drops uflow and ovflow bins => idx -> idx-1
    # row:sublead, col:lead
    #ratio, ma_edges = hist2array(h[srk], return_edges=True) # for testing bin mapping
    ratio, ma_edges = hist2array(h['%s_ratio'%srk], return_edges=True)
    ratio, ma_edges = ratio.T, ma_edges[0]
    #print('(0,0):',ratio[0][0])
    #print('(1,1):',ratio[1][1])
    #print('(0,1):',ratio[0][1])
    #print('(1,0):',ratio[1][0]) # gj

    # Remove unphysical values
    ratio[ratio==0.] = 1.
    ratio[np.isnan(ratio)] = 1.
    #print(ratio[ratio>0].min())
    #print(np.isnan(ratio).any())
    #print(ma_edges)

    # Write out weights to numpy file
    output_dir = 'Weights'
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    #print(get_weight_2dma(0.001, 0.001, ma_edges, ratio))
    #print(get_weight_2dma(-0.5, -0.5, ma_edges, ratio))
    #print(get_weight_2dma(1.5, 1.5, ma_edges, ratio))
    #print(get_weight_2dma(-0.1, 0.001, ma_edges, ratio))
    #print(get_weight_2dma(1.1999, 1.5, ma_edges, ratio))
    #print(get_weight_2dma(1.199, 1.199, ma_edges, ratio))
    np.savez("%s/%s_%s_blind_%s_wgts.npz"%(output_dir, s, r, blind), ma_edges=ma_edges, wgts=ratio)

    #nf = np.load("Weights/%s_%s_blind_%s_wgts.npz"%(s, r, blind))
    #print(get_weight_2dma(-0.1, 0.001, nf['ma_edges'], nf['wgts']))

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

def get_combined_template_wgt(tree, ma_edges, wgts):
    '''
    Convenience fn for returning 2d-ma wgt for an event loaded into `tree`
    '''
    return get_weight_2d(tree.ma0, tree.ma1, ma_edges, wgts)

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
