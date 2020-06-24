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

def run_combined_sbfit(fgg=None, fjj=None, norm=1., derive_fit=False, do_pt_reweight=False, do_ptomGG=False, blind='sg'):

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
    fgg, flo, fhi = fit_templates_sb(blind, output_dir, derive_fit)

    return fgg, flo, fhi
    #return 1., 0., 0.

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
            if s == 'GluGluHToGG' and 'sb' in r: continue
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

    regions = [sb, 'sr']

    # Run both SB and SR to bkg processes
    ma_inputs = glob.glob('MAntuples/%s_mantuple.root'%sample)
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

    output_dir = 'Weights'
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    k = keys[0]
    #for tgt in ['sblo', 'sr', 'sbhi']:
    for tgt in ['sr']:

        # Ratio is SR/SB
        #h[tgt+'%s_ratio'%k] = h['%s_%s_%s'%(sample, tgt, k)].Clone()
        #h[tgt+'%s_ratio'%k].Divide(h['%s_%s_%s'%(sample, sb, k)])
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

def fit_templates_sb(blind='sg', workdir='Templates', derive_fit=False):
    '''
    Fit for fraction of hgg and data mH-low, mH-high SB templates in data mH-SR, fgg, flo, fhi, resp.
    Normalize each template to have unit Integral() first.
    '''
    h, hf = {}, {}
    samples = ['Run2017B-F', 'GluGluHToGG']
    #regions = ['sb', 'sr']
    regions = ['sblo', 'sbhi', 'sr']
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
    #scale_num = 1.e3 #100., 1.
    scale_num = 5.e3 #100., 1.

    #h['Run2017B-F_sr_ma0vma1'].Scale(1./h['Run2017B-F_sr_ma0vma1'].Integral())
    print('sr integral:',h['Run2017B-F_sr_ma0vma1'].Integral())
    #h['Run2017B-F_sr_ma0vma1'].Scale(scale_num/h['Run2017B-F_sr_ma0vma1'].Integral())

    h['gg'] = h['GluGluHToGG_sr_ma0vma1'].Clone()
    #norm['gg'] = get_entries_cr(h['Run2017B-F_sr_ma0vma1'],'gg')/get_entries_cr(h['gg'], 'gg')
    #h['gg'].Scale(norm['gg'])
    #h['gg'].Scale(1./h['gg'].Integral())
    print('hgg integral:',h['gg'].Integral())
    hggscale = 2.27e-3*48.58*41.9e3*h['gg'].Integral()/214099989.445038
    hggscale /= h['Run2017B-F_sr_ma0vma1'].Integral()
    #print('hgg lumi-wgt:',2.27e3*33.4*41.9e3*h['gg'].Integral()/214099989.445038)
    print('hgg lumi-wgt:',hggscale)
    h['gg'].Scale(scale_num/h['gg'].Integral())
    h['gg'] = floor_hist(h['gg'])
    #print('gg:',get_entries_cr(h['Run2017B-F_sr_ma0vma1'],'gg'), get_entries_cr(h['gg'], 'gg'))
    print('higgs-only, gg:%f, jj:%f'%(get_entries_cr(h['gg'], 'gg'), get_entries_cr(h['gg'], 'jj')))

    #h['jj'] = h['Run2017B-F_sb_ma0vma1'].Clone()
    #norm['jj'] = get_entries_cr(h['Run2017B-F_sr_ma0vma1'],'jj')/get_entries_cr(h['jj'], 'jj')
    #h['jj'].Scale(norm['jj'])
    ##print('jj:',get_entries_cr(h['Run2017B-F_sr_ma0vma1'],'jj'), get_entries_cr(h['jj'], 'jj'))
    #print('sb-only, gg:%f, jj:%f'%(get_entries_cr(h['jj'], 'gg'), get_entries_cr(h['jj'], 'jj')))
    #print('sr-obs, gg:%f, jj:%f'%(get_entries_cr(h['Run2017B-F_sr_ma0vma1'], 'gg'), get_entries_cr(h['Run2017B-F_sr_ma0vma1'], 'jj')))

    h['jjlo'] = h['Run2017B-F_sblo_ma0vma1'].Clone()
    print('sblo integral:',h['jjlo'].Integral(), h['jjlo'].Integral()/h['Run2017B-F_sr_ma0vma1'].Integral())
    #norm['jjlo'] = get_entries_cr(h['Run2017B-F_sr_ma0vma1'],'jj')/get_entries_cr(h['jjlo'], 'jj')
    #h['jjlo'].Scale(norm['jjlo'])
    #h['jjlo'].Scale(1./h['jjlo'].Integral())
    h['jjlo'].Scale(scale_num/h['jjlo'].Integral())
    #print('jjlo:',get_entries_cr(h['Run2017B-F_sr_ma0vma1'],'jj'), get_entries_cr(h['jjlo'], 'jj'))
    print('sb-only, gg:%f, jjlo:%f'%(get_entries_cr(h['jjlo'], 'gg'), get_entries_cr(h['jjlo'], 'jj')))
    print('sr-obs, gg:%f, jjlo:%f'%(get_entries_cr(h['Run2017B-F_sr_ma0vma1'], 'gg'), get_entries_cr(h['Run2017B-F_sr_ma0vma1'], 'jj')))

    h['jjhi'] = h['Run2017B-F_sbhi_ma0vma1'].Clone()
    print('sbhi integral:',h['jjhi'].Integral(), h['jjhi'].Integral()/h['Run2017B-F_sr_ma0vma1'].Integral())
    #norm['jjhi'] = get_entries_cr(h['Run2017B-F_sr_ma0vma1'],'jj')/get_entries_cr(h['jjhi'], 'jj')
    #h['jjhi'].Scale(norm['jjhi'])
    #h['jjhi'].Scale(1./h['jjhi'].Integral())
    h['jjhi'].Scale(scale_num/h['jjhi'].Integral())
    #print('jjhi:',get_entries_cr(h['Run2017B-F_sr_ma0vma1'],'jj'), get_entries_cr(h['jjhi'], 'jj'))
    print('sb-only, gg:%f, jjhi:%f'%(get_entries_cr(h['jjhi'], 'gg'), get_entries_cr(h['jjhi'], 'jj')))
    print('sr-obs, gg:%f, jjhi:%f'%(get_entries_cr(h['Run2017B-F_sr_ma0vma1'], 'gg'), get_entries_cr(h['Run2017B-F_sr_ma0vma1'], 'jj')))

    h['Run2017B-F_sr_ma0vma1'].Scale(scale_num/h['Run2017B-F_sr_ma0vma1'].Integral())
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
    fgg = 4.06623e-01
    flo = 3.30289e-01
    fhi = 1.87576e-01
    fgg = 3.02932e-01
    flo = 3.70054e-01
    fjj = 3.15643e-01

    fgg = 0.
    flo = 5.17282e-01
    fhi = 4.57097e-01

    #no bdt
    fgg = 0.
    flo = 5.08462e-01
    fhi = 4.91340e-01

    #bdt > -0.9
    #fgg = 0.
    #flo = 5.20326e-01
    #fhi = 4.79670e-01

    #fgg = 4.22085e-03
    #flo = 5.04898e-01
    #fhi = 4.90865e-01

    fgg = 3.04455e-02
    flo = 4.91381e-01
    fhi = 4.78163e-01

    fgg = fgg/(fgg+flo+fhi)
    flo = flo/(fgg+flo+fhi)
    fhi = fhi/(fgg+flo+fhi)

    if derive_fit:
        mc = ROOT.TObjArray()
        mc.Add(h['gg'])
        mc.Add(h['jjlo'])
        mc.Add(h['jjhi'])
        fit = ROOT.TFractionFitter(h['Run2017B-F_sr_ma0vma1'], mc)
        #fit.Constrain(0, 0., 1.)
        fit.Constrain(0, 0., hggscale)
        fit.Constrain(1, 0., 1.)
        fit.Constrain(2, 0., 1.)
        fitResult = fit.Fit() # seg faults at deconstruction (not supported in PyROOT)
        print('fit status:', int(fitResult))
        chi2 = fit.GetChisquare()
        ndof = fit.GetNDF()
        pval = fit.GetProb()
        print('chi2 / ndf: %f / %f = %f'%(chi2, ndof, chi2/ndof))
        #print('chi2 / (ndf-nDiag): %f / %f = %f'%(chi2, ndof-nDiag, chi2/(ndof-nDiag)))
        print('p-val:',pval)
        cor = fitResult.GetCorrelationMatrix()
        cov = fitResult.GetCovarianceMatrix()
        cor.Print()
        cov.Print()

    '''
    k = 'Run2017B-F_sb2sr_ma0vma1'
    #h[k] = h['gg'].Clone()
    #h[k].Scale(fgg)
    h[k] = h['jjlo'].Clone()
    h[k].Scale(flo)
    #print(get_entries_cr(h[k],'gg'))
    #h[k].Add(h['jjlo'], flo)
    h[k].Add(h['jjhi'], fhi)
    #print(h[k].Integral())
    h[k].Scale(1./h[k].Integral())
    #print(h[k].Integral())

    print('sb2sr, gg:%f, jj:%f'%(get_entries_cr(h[k], 'gg'), get_entries_cr(h[k], 'jj')))
    norm['sb2sr'] = get_entries_cr(h['Run2017B-F_sr_ma0vma1'], 'jj')/get_entries_cr(h[k], 'jj')
    h[k].Scale(norm['sb2sr'])
    print('sb2sr, gg:%f, jj:%f'%(get_entries_cr(h[k], 'gg'), get_entries_cr(h[k], 'jj')))
    print('gg ratio:',get_entries_cr(h['Run2017B-F_sr_ma0vma1'], 'gg')/get_entries_cr(h[k], 'gg'))
    '''

    print('fgg: %f, flo:%f, fhi:%f'%(fgg, flo, fhi))
    #return fgg, fjj, norm
    return fgg, flo, fhi

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
    #regions = ['sb', 'sr']
    regions = ['sblo', 'sbhi', 'sr']
    keys = ['ma0vma1']
    load_hists(h, hf, samples, regions, keys, blind, workdir)

    # Get hgg template and normalize
    #h['gg'] = h['GluGluHToGG_sr_ma0vma1'].Clone()
    #h['gg'].Scale(norm['gg'])
    #print('higgs-only, gg:%f, jj:%f'%(get_entries_cr(h['gg'], 'gg'), get_entries_cr(h['gg'], 'jj')))

    # Get data mH-SB template and normalize
    h['jjlo'] = h['Run2017B-F_sblo_ma0vma1'].Clone()
    h['jjlo'].Scale(1./h['jjlo'].Integral())
    print('sb-only, gg:%f, jjlo:%f'%(get_entries_cr(h['jjlo'], 'gg'), get_entries_cr(h['jjlo'], 'jj')))

    h['jjhi'] = h['Run2017B-F_sbhi_ma0vma1'].Clone()
    h['jjhi'].Scale(1./h['jjhi'].Integral())
    print('sb-only, gg:%f, jjhi:%f'%(get_entries_cr(h['jjhi'], 'gg'), get_entries_cr(h['jjhi'], 'jj')))

    # Contstuct fgg*template_hgg + fjj*template_mH-SB
    s = 'Run2017B-F+GluGluHToGG'
    r = 'sb2sr'
    k = 'ma0vma1'
    srk = '%s_%s_%s'%(s, r, k)
    #h[srk] = h['gg'].Clone()
    #h[srk].Scale(fgg)
    #h[srk].Add(h['jj'], fjj)
    #h[srk].Scale(norm['sb2sr'])
    h[srk] = h['jjlo'].Clone()
    h[srk].Scale(flo)
    h[srk].Add(h['jjhi'], fhi)
    h[srk].Scale(1./h[srk].Integral())
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
