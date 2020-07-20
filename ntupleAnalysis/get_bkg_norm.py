from __future__ import print_function
from multiprocessing import Pool
import numpy as np
import ROOT
import os, glob
from root_numpy import hist2array
from data_utils import *

def bkg_process(s, r, blind, ma_inputs, output_dir, do_combo_template=False, norm=1., do_ptomGG=True, do_pt_reweight=False, nevts=-1, do_mini2aod=False, write_pts=False):
    '''
    Convenience fn for running the background modeling event loop.
    Returns a string for the python command arguments to be executed.
    '''
    print('Running bkg model for sample %s, region: %s, blind: %s'%(s, r, blind))
    pyargs = 'get_bkg_model.py -s %s -r %s -b %s -i %s -t %s -o %s -n %f -e %d'\
            %(s, r, blind, ' '.join(ma_inputs), get_ma_tree_name(s), output_dir, norm, nevts)
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
    print('cmd: %s'%pyargs)

    return pyargs

def run_combined_sbfit(fgg=None, fjj=None, norm=1., derive_fit=False, do_pt_reweight=False, do_ptomGG=False, blind='sg', flo_=None):

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

    output_dir = 'Templates'
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # [1] First run hgg, data mH-SB, data mH-SR with 2d-ma-SR blinded
    # These will output TH2F histograms into root files which will be picked up in [2]
    #blind = 'sg'
    blind = blind
    #blind = None

    # Data mH-SB and mH-SR
    s = 'Run2017[B-F]'
    ma_inputs = glob.glob('MAntuples/%s_mantuple.root'%s)
    print('len(ma_inputs):',len(ma_inputs))
    assert len(ma_inputs) > 0

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

    s = s.replace('[','').replace(']','')
    #regions = ['sb', 'sr']
    regions = ['sblo', 'sbhi', 'sr']
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
    #processes.append(bkg_process(s, r, blind, ma_inputs, output_dir, do_mini2aod=True))
    #processes.append(bkg_process(s, r, blind, ma_inputs, output_dir, do_pt_reweight=do_pt_reweight))

    # Run processes in parallel
    pool = Pool(processes=len(processes))
    pool.map(run_process, processes)
    pool.close()
    pool.join()

    # [2] Fit hgg and mH-SB template fractions into mH-SR:
    # Normalize templates to unit Integral() in the unblinded region.
    # NOTE: TFractionFiter seg faults at deconstruction in PyROOT...
    # need to put in fgg, flo, fhi by hand after, or [TODO] re-implement in C++.
    fgg, flo, fhi = fit_templates_sb(blind, output_dir, derive_fit, flo_)

    return fgg, flo, fhi
    #return 1., 0., 0.

def load_hists(h, hf, samples, regions, keys, blind, input_dir):

    # NOTE: Need to pass file objects `hf` as well for histograms `h`
    # to remain persistent, otherwise segfaults
    for s in samples :
        for r in regions:
            if s == 'GluGluHToGG' and 'sb' in r: continue
            #if 'Run2017' in s and r == 'sr' and blind == None and 'pt0vpt1' not in keys: continue
            sr = '%s_%s'%(s, r)
            hf[sr] = ROOT.TFile("%s/%s_%s_blind_%s_templates.root"%(input_dir, s, r, blind),"READ")
            for k in keys:
                srk = '%s_%s_%s'%(s, r, k)
                h[srk] = hf[sr].Get(k)

def run_ptweights(blind=None, sb='sb', sample='Run2017[B-F]', workdir='Templates', ntuple_dir='MAntuples', output_dir='Weights', do_ptomGG=True, flo_=None):
    '''
    Calculate normalization for the mapping of 2d-ma data mH-SB template(s) to data mH-SR.
    '''

    regions = [sb, 'sr']

    # Run both SB and SR to bkg processes
    ma_inputs = glob.glob('%s/%s_mantuple.root'%(ntuple_dir, sample))
    print('len(ma_inputs):',len(ma_inputs))
    assert len(ma_inputs) > 0
    #ma_inputs = [ma_inputs[0]]

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

    sample = sample.replace('[','').replace(']','')
    processes = [bkg_process(sample, r, blind, ma_inputs, workdir, do_ptomGG=do_ptomGG if r == sb else True, write_pts=True) for r in regions]

    for r in ['sblo', 'sbhi']:
        processes.append(bkg_process(sample, r, blind, ma_inputs, workdir, do_ptomGG=True, write_pts=True))

    # Run processes in parallel
    pool = Pool(processes=len(processes))
    pool.map(run_process, processes)
    pool.close()
    pool.join()

    h, hf = {}, {}
    sample = sample.replace('[','').replace(']','')
    samples = [sample]
    #regions = ['sb', 'sr']
    regions.append('sblo')
    regions.append('sbhi')
    keys = ['pt0vpt1']
    load_hists(h, hf, samples, regions, keys, blind, workdir)
    print(h.keys())

    #output_dir = 'Weights'
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    k = keys[0]
    #for tgt in ['sblo', 'sr', 'sbhi']:
    for tgt in ['sr']:

        '''
        # Ratio is SR/SB
        h['%s_%s_%s'%(sample, tgt, k)].Scale(150.e3/h['%s_%s_%s'%(sample, tgt, k)].Integral())
        h['%s_%s_%s'%(sample, sb, k)].Scale(150.e3/h['%s_%s_%s'%(sample, sb, k)].Integral())
        h[tgt+'%s_ratio'%k] = h['%s_%s_%s'%(sample, tgt, k)].Clone()
        h[tgt+'%s_ratio'%k].Divide(h['%s_%s_%s'%(sample, sb, k)])

        # Save all histograms for reference
        # Actual weights to be used during event loop are written to separate file below
        hf[tgt+'ratios'] = ROOT.TFile("%s/%s_%s2%s_blind_%s_ptwgts.root"%(output_dir, sample, sb, tgt, blind), "RECREATE")
        h['%s_%s_%s'%(sample, tgt, k)].SetName('%s_%s_%s'%(sample, tgt, k))
        h['%s_%s_%s'%(sample, tgt, k)].Write()
        h['%s_%s_%s'%(sample, sb, k)].SetName('%s_%s_%s'%(sample, sb, k))
        h['%s_%s_%s'%(sample, sb, k)].Write()
        h[tgt+'%s_ratio'%k].SetName('%s_ratio'%k)
        h[tgt+'%s_ratio'%k].Write()
        hf[tgt+'ratios'].Close()
        '''

        # Ratio is SR/SB
        norm_scale = 150.e3
        h['%s_%s_%s'%(sample, tgt, k)].Scale(norm_scale/h['%s_%s_%s'%(sample, tgt, k)].Integral())
        if flo_ is None:
            flo_ = h['%s_sblo_%s'%(sample, k)].Integral()/(h['%s_sblo_%s'%(sample, k)].Integral()+h['%s_sbhi_%s'%(sample, k)].Integral())
            print('Nsblo:%f, Nsbhi:%f, Nsr:%f'%(h['%s_sblo_%s'%(sample, k)].Integral(), h['%s_sbhi_%s'%(sample, k)].Integral(), h['%s_%s_%s'%(sample, tgt, k)].Integral()))
        print('flo_:',flo_)
        h['%s_sblo_%s'%(sample, k)].Scale(norm_scale/h['%s_sblo_%s'%(sample, k)].Integral())
        h['%s_sbhi_%s'%(sample, k)].Scale(norm_scale/h['%s_sbhi_%s'%(sample, k)].Integral())
        kcombo = '%s_sbcombo_%s'%(sample, k)
        h[kcombo] = h['%s_sblo_%s'%(sample, k)].Clone()
        #print('sb-lo integral, pre-scale:',h[kcombo].Integral())
        h[kcombo].Scale(flo_)
        #print('sb-lo integral, post-scale:',h[kcombo].Integral())
        h[kcombo].Add(h['%s_sbhi_%s'%(sample, k)], (1.-flo_))
        #print('sb-lo+hi integral, post-scale:',h[kcombo].Integral())
        h[tgt+'%s_ratio'%k] = h['%s_%s_%s'%(sample, tgt, k)].Clone()
        h[tgt+'%s_ratio'%k].Divide(h[kcombo])

        # Save all histograms for reference
        # Actual weights to be used during event loop are written to separate file below
        hf[tgt+'ratios'] = ROOT.TFile("%s/%s_%s2%s_blind_%s_ptwgts.root"%(output_dir, sample, sb, tgt, blind), "RECREATE")
        h['%s_%s_%s'%(sample, tgt, k)].SetName('%s_%s_%s'%(sample, tgt, k))
        h['%s_%s_%s'%(sample, tgt, k)].Write()
        h['%s_sblo_%s'%(sample, k)].SetName('%s_sblo_%s'%(sample, k))
        h['%s_sblo_%s'%(sample, k)].Write()
        h['%s_sbhi_%s'%(sample, k)].SetName('%s_sbhi_%s'%(sample, k))
        h['%s_sbhi_%s'%(sample, k)].Write()
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
        #np.savez("%s/%s_%s2%s_blind_%s_ptwgts.npz"%(output_dir, sample, sb, tgt, blind), pt_edges=pt_edges, pt_wgts=ratio)
        np.savez("%s/%s_%s2%s_blind_%s_ptwgts.npz"\
                %(output_dir, sample, sb, tgt, blind), pt_edges_lead=pt_edges_lead, pt_edges_sublead=pt_edges_sublead, pt_wgts=ratio)

        return flo_

def get_bkg_norm_sb(blind='sg', sb='sb', sample='Run2017[B-F]', sr_sample='Run2017[B-F]', workdir='Templates', do_pt_reweight=False, do_ptomGG=False, run_bkg=True):
    '''
    Calculate relative normalization between data mH-SB templates and data mH-SR.
    sb: sb, sbcombo, sblo, sbhi
    '''

    if not do_ptomGG:
        pass
        assert do_pt_reweight

    regions = [sb]
    #regions = ['sr']
    #if 'lo' in sb:
    #    regions.append('sblo')
    #if 'hi' in sb:
    #    regions.append('sbhi')
    #else:
    #    regions.append(sb)

    # Run both SB and SR to bkg processes
    ma_inputs = glob.glob('MAntuples/%s_mantuple.root'%sample)
    sample = sample.replace('[','').replace(']','')
    sr_sample = sr_sample.replace('[','').replace(']','')
    print('len(ma_inputs):',len(ma_inputs))
    assert len(ma_inputs) > 0
    if run_bkg:
        # For source SB or hgg process
        processes = [bkg_process(sample, r, blind, ma_inputs, workdir,\
                #do_combo_template=True if r == 'sbcombo' else False,\
                do_ptomGG=do_ptomGG if r == sb else True,\
                do_pt_reweight=do_pt_reweight if r == sb else False)\
                #do_pt_reweight=do_pt_reweight if r == sb else False,\
                #do_mini2oad=True if 'GluGluHToGG' in sample else False)
                for r in regions]
        # For target SR process
        processes.append(bkg_process(sr_sample, 'sr', blind, ma_inputs, workdir,\
                do_ptomGG=True,\
                do_pt_reweight=False))

        # Run processes in parallel
        pool = Pool(processes=len(processes))
        pool.map(run_process, processes)
        pool.close()
        pool.join()

    h, hf = {}, {}
    entries = {}
    integral = {}
    #norm = {}

    #keys = ['maxy']
    keys = ['ma0vma1']

    # Read in templates
    hf[sr_sample+'sr'] = ROOT.TFile("%s/%s_%s_blind_%s_templates.root"%(workdir, sr_sample, 'sr', blind),"READ")
    for r in regions:
        hf[sample+r] = ROOT.TFile("%s/%s_%s_blind_%s_templates.root"%(workdir, sample, r, blind),"READ")
    # Get integrals (i.e. wgtd nentries not in under/over-flow)
    for s_r in hf.keys():
        print(s_r)
        for k in keys:
            s_r_k = s_r+k
            h[s_r_k] = hf[s_r].Get(k)
            entries[s_r_k] = h[s_r_k].GetEntries()
            integral[s_r_k] = h[s_r_k].Integral()
            print(integral[s_r_k])

    for r in regions:
        for k in keys:
            #if k != 'maxy': continue
            if k != 'ma0vma1': continue
            #rk = '%s_%s'%(r, k)
            #print(rk)
            #h[rk] = h[rk].Clone()
            #norm['%s2sr'%r] = integral['sr_%s'%k]/integral[rk]
            #print('%s2sr norm: %f'%(r, norm['%s2sr'%r]))
            #norm = integral['sr_%s'%k]/integral[rk]
            norm = integral[sr_sample+'sr'+k]/integral[sample+r+k]
            #norm = (integral[sr_sample+'sr'+k] + integral[sg])/integral[sample+r+k]

    return norm

#def fit_templates_sb(blind='sg', workdir='Templates', derive_fit=False):
def fit_templates_sb(blind=None, workdir='Templates', derive_fit=False, flo_=None):
    '''
    Fit for fraction of hgg and data mH-low, mH-high SB templates in data mH-SR, fgg, flo, fhi, resp.
    Normalize each template to have unit Integral() first.
    '''
    assert flo_ is not None

    h, hf = {}, {}
    samples = ['Run2017B-F', 'GluGluHToGG']
    #regions = ['sb', 'sr']
    regions = ['sblo', 'sbhi', 'sr']
    #keys = ['ma0vma1']
    keys = ['pt0vpt1']
    load_hists(h, hf, samples, regions, keys, blind, workdir)
    print(h.keys())
    print(blind)
    k = keys[0]

    # sb2sr = fgg*gg_normed + fsb*sb_normed
    # 0th ordero: fgg, fsb chosen s.t.
    # to check sb2sr(gg) ~ sr(gg) AND sb2sr(jj) ~ sr(jj)
    # need not be fsb = 1-fgg since normalizations are not completely orthogonal
    # 1st order: do TFractionFitter template fit -> converges but segfaults on exit
    # => need to put in values by hand after fit
    norm = {}
    #scale_num = 1.e3 #100., 1.
    #scale_num = 5.e3 #100., 1.
    scale_num = 1.e4 #100., 1.
    #scale_num = 5.e4 #100., 1.
    #scale_num = 1.e5 #100., 1.
    #scale_num = 5.e5 #100., 1.

    #h['Run2017B-F_sr_ma0vma1'].Scale(1./h['Run2017B-F_sr_ma0vma1'].Integral())
    #print('sr integral:',h['Run2017B-F_sr_ma0vma1'].Integral())
    #h['Run2017B-F_sr_ma0vma1'].Scale(scale_num/h['Run2017B-F_sr_ma0vma1'].Integral())
    nSR = h['Run2017B-F_sr_%s'%k].Integral()

    h['gg'] = h['GluGluHToGG_sr_%s'%k].Clone()
    nHgg = h['gg'].Integral()
    #norm['gg'] = get_entries_cr(h['Run2017B-F_sr_ma0vma1'],'gg')/get_entries_cr(h['gg'], 'gg')
    #h['gg'].Scale(norm['gg'])
    #h['gg'].Scale(1./h['gg'].Integral())
    #print('hgg integral:',h['gg'].Integral())
    #hgguncert = -48.58*5.11e-3
    hgguncert = 0.
    hggscale = 2.27e-3*(48.58+hgguncert)*41.9e3*nHgg/214099989.445038
    hggscale /= nSR
    #print('hgg lumi-wgt:',2.27e3*33.4*41.9e3*h['gg'].Integral()/214099989.445038)
    print('hgg lumi-wgt:',hggscale)
    #h['gg'].Scale(scale_num/h['gg'].Integral())
    #h['gg'] = floor_hist(h['gg'])
    #print('gg:',get_entries_cr(h['Run2017B-F_sr_ma0vma1'],'gg'), get_entries_cr(h['gg'], 'gg'))
    #print('higgs-only, gg:%f, jj:%f'%(get_entries_cr(h['gg'], 'gg'), get_entries_cr(h['gg'], 'jj')))

    h['jjlo'] = h['Run2017B-F_sblo_%s'%k].Clone()
    nSBlo = h['jjlo'].Integral()
    #print('sblo integral:',h['jjlo'].Integral(), h['jjlo'].Integral()/h['Run2017B-F_sr_ma0vma1'].Integral())
    #norm['jjlo'] = get_entries_cr(h['Run2017B-F_sr_ma0vma1'],'jj')/get_entries_cr(h['jjlo'], 'jj')
    #h['jjlo'].Scale(norm['jjlo'])
    #h['jjlo'].Scale(1./h['jjlo'].Integral())
    h['jjlo'].Scale(scale_num/h['jjlo'].Integral())
    #print('jjlo:',get_entries_cr(h['Run2017B-F_sr_ma0vma1'],'jj'), get_entries_cr(h['jjlo'], 'jj'))
    #print('sb-only, gg:%f, jjlo:%f'%(get_entries_cr(h['jjlo'], 'gg'), get_entries_cr(h['jjlo'], 'jj')))
    #print('sr-obs, gg:%f, jjlo:%f'%(get_entries_cr(h['Run2017B-F_sr_ma0vma1'], 'gg'), get_entries_cr(h['Run2017B-F_sr_ma0vma1'], 'jj')))

    h['jjhi'] = h['Run2017B-F_sbhi_%s'%k].Clone()
    nSBhi = h['jjhi'].Integral()
    #print('sbhi integral:',h['jjhi'].Integral(), h['jjhi'].Integral()/h['Run2017B-F_sr_ma0vma1'].Integral())
    #norm['jjhi'] = get_entries_cr(h['Run2017B-F_sr_ma0vma1'],'jj')/get_entries_cr(h['jjhi'], 'jj')
    #h['jjhi'].Scale(norm['jjhi'])
    #h['jjhi'].Scale(1./h['jjhi'].Integral())
    h['jjhi'].Scale(scale_num/h['jjhi'].Integral())
    #print('jjhi:',get_entries_cr(h['Run2017B-F_sr_ma0vma1'],'jj'), get_entries_cr(h['jjhi'], 'jj'))
    #print('sb-only, gg:%f, jjhi:%f'%(get_entries_cr(h['jjhi'], 'gg'), get_entries_cr(h['jjhi'], 'jj')))
    #print('sr-obs, gg:%f, jjhi:%f'%(get_entries_cr(h['Run2017B-F_sr_ma0vma1'], 'gg'), get_entries_cr(h['Run2017B-F_sr_ma0vma1'], 'jj')))

    h['Run2017B-F_sr_%s'%k].Scale(scale_num/h['Run2017B-F_sr_%s'%k].Integral())

    fgg = hggscale
    fsb = 1.-fgg
    #if flo_ is None:
    #    flo = fsb*nSBlo/(nSBlo+nSBhi)
    #    fhi = fsb*nSBhi/(nSBlo+nSBhi)
    #else:
    flo = fsb*flo_
    fhi = fsb*(1.-flo_)

    print('Nsblo:%f, Nsbhi:%f, Nsr:%f'%(nSBlo, nSBhi, nSR))
    print(fgg, flo, fhi, fgg+flo+fhi)

    #if derive_fit:
    #    mc = ROOT.TObjArray()
    #    #mc.Add(h['gg'])
    #    mc.Add(h['jjlo'])
    #    mc.Add(h['jjhi'])
    #    fit = ROOT.TFractionFitter(h['Run2017B-F_sr_%s'%k], mc)
    #    fit.Constrain(0, 0., 1.)
    #    #fit.Constrain(0, 0., hggscale)
    #    fit.Constrain(1, 0., 1.)
    #    #fit.Constrain(2, 0., 1.)
    #    fitResult = fit.Fit() # seg faults at deconstruction (not supported in PyROOT)
    #    print('fit status:', int(fitResult))
    #    chi2 = fit.GetChisquare()
    #    ndof = fit.GetNDF()
    #    pval = fit.GetProb()
    #    print('chi2 / ndf: %f / %f = %f'%(chi2, ndof, chi2/ndof))
    #    #print('chi2 / (ndf-nDiag): %f / %f = %f'%(chi2, ndof-nDiag, chi2/(ndof-nDiag)))
    #    print('p-val:',pval)
    #    #cor = fitResult.GetCorrelationMatrix()
    #    cov = fitResult.GetCovarianceMatrix()
    #    #cor.Print()
    #    cov.Print()

    return fgg, flo, fhi

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
