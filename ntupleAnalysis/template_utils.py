from __future__ import print_function
import ROOT
import os, glob, re
from hist_utils import wd, ht

#def blind_hist(h, to_blind=None, blind_w=0.2):
def blind_hist(h, to_blind=None, blind_w=0.3):
    '''
    Blind `h` in-place.
    '''

    to_blind = str(to_blind)
    iblind_w = h.GetXaxis().FindBin(blind_w)
    iblind_lo = h.GetXaxis().FindBin(0.)
    iblind_hi = h.GetXaxis().FindBin(1.2)

    #print('      .. integral, before to_blind(%s): %f'%(to_blind, h.Integral(iblind_lo, iblind_hi, iblind_lo, iblind_hi)))
    print('      .. integral, to_blind(lo_hi): %f (%f)'%(h.Integral(iblind_lo, iblind_hi, iblind_lo, iblind_hi), h.Integral(iblind_lo, iblind_hi, iblind_lo, iblind_hi)/h.GetEntries()))

    for ix in range(0, h.GetNbinsX()+2):
        blind_x = False
        if 'lo' in to_blind and ix < iblind_lo:
            blind_x = True
        if 'hi' in to_blind and ix >= iblind_hi:
            blind_x = True
        for iy in range(0, h.GetNbinsY()+2):
            blind_y = False
            if 'lo' in to_blind and iy < iblind_lo:
                blind_y = True
            if 'hi' in to_blind and iy >= iblind_hi:
                blind_y = True
            if 'offdiag' in to_blind:
                if abs(ix-iy) >= (iblind_w-iblind_lo):
                    blind_y = True
            elif 'diag' in to_blind:
                if abs(ix-iy) < (iblind_w-iblind_lo):
                    blind_y = True
            if blind_x or blind_y:
                h.SetBinContent(ix, iy, 0.)

    print('      .. integral, after to_blind(%s): %f'%(to_blind, h.Integral(iblind_lo, iblind_hi, iblind_lo, iblind_hi)))

def blind_hist_all(h, hblind, c, sample, to_blind, make_plots=False, k2dma='ma0vma1', k2dpt='pt0vpt1'):
    '''
    For every hist in `h`, create clone in `hblind` and apply blinding.
    '''

    for k in h:

        if k2dma in k:
            kblind = '%s-%s'%(k, to_blind)
            hblind[kblind] = h[k].Clone()
            hblind[kblind].SetName(kblind)
            blind_hist(hblind[kblind], to_blind=to_blind)
            hblind[kblind].GetXaxis().SetRangeUser(0., 1.2)
            hblind[kblind].GetYaxis().SetRangeUser(0., 1.2)
        elif k2dpt in k:
            # No blinding applied to pt
            pass
            kblind = '%s'%(k)
            hblind[kblind] = h[k].Clone()
            hblind[kblind].SetName(kblind)
            #hblind[kblind].GetXaxis().SetRangeUser(0., 200.)
            #hblind[kblind].GetYaxis().SetRangeUser(0., 200.)

        if make_plots:
            c[kblind] = ROOT.TCanvas(kblind+'_', kblind+'_', wd, ht)
            hblind[kblind].Draw('COL Z')
            #c[kblind].SetLogz()
            c[kblind].Draw()
            c[kblind].Update()

    ksr = '%s_sr_%s-%s'%(sample, k2dma, to_blind)
    print('.. nevts[%s]: %f'%(ksr, hblind[ksr].Integral()))

def combine_sblohi(hnorm, flo_in, flo_nom, ksblo, ksbhi, ksb2sr):
    '''
    Add pt re-wighted mh-SB lo+hi templates taking into account nominal vs. input flo
    '''

    # Clone mh-Sblo*(flo_in/flo_nom) template
    hnorm[ksb2sr] = hnorm[ksblo].Clone()
    hnorm[ksb2sr].SetName(ksb2sr)
    hnorm[ksb2sr].Scale(flo_in/flo_nom)

    # Add mh-SBhi*(1-flo_in)/(1-flo_nom) template
    hnorm[ksb2sr].Add(hnorm[ksbhi], (1.-flo_in)/(1.-flo_nom))

def get_sb2sr_norm(h, hnorm, c, flo_in, flo_nom, sample, distns, to_blind='diag_lo_hi', make_plots=True, k2dma='ma0vma1', k2dpt='pt0vpt1'):
    '''
    Get factor for normalizing combined mh-SB lo+hi template to mh-SR event yield in specified blinding.
    '''

    # Apply blinding: sb2sr_norm should be estimated from an unbiased (signal-free) region of 2d-ma
    # No blinding applied to pt
    blind_hist_all(h, hnorm, c, sample, to_blind, make_plots=make_plots, k2dma=k2dma, k2dpt=k2dpt)

    # Get sb2sr normalization
    sb2sr_norm = {}
    for distn in distns:

        # Combine mh-SBlo+hi
        # No blinding applied to pt
        blind_str = '-%s'%to_blind if distn == k2dma else ''
        ksblo = '%s_sblo_%s%s'%(sample, distn, blind_str)
        ksbhi = '%s_sbhi_%s%s'%(sample, distn, blind_str)
        ksb2sr = '%s_sb2sr_%s%s'%(sample, distn, blind_str)
        ksr = '%s_sr_%s%s'%(sample, distn, blind_str)
        combine_sblohi(hnorm, flo_in, flo_nom, ksblo, ksbhi, ksb2sr)

        # Normalize to mh-SR evt yield
        sb2sr_norm[distn] = hnorm[ksr].Integral()/hnorm[ksb2sr].Integral()
        hnorm[ksb2sr].Scale(sb2sr_norm[distn])
        print('.. sb2sr_norm[%s]: %f'%(distn, sb2sr_norm[distn]))
        print('.. hnorm[%s].Integral(): %f'%(ksb2sr, hnorm[ksb2sr].Integral()))

        # For 2d-pt: Divide mh-SR by mh-SBlo+hi to verify flatness
        if distn == k2dpt:
            hnorm[ksb2sr].Divide(hnorm[ksr], hnorm[ksb2sr], 1., 1.)
            hnorm[ksb2sr].SetMaximum(1.1)
            hnorm[ksb2sr].SetMinimum(0.9)

        # Draw
        c[ksb2sr] = ROOT.TCanvas(ksb2sr, ksb2sr, wd, ht)
        hnorm[ksb2sr].Draw('COL Z')
        c[ksb2sr].Draw()
        c[ksb2sr].Update()

    print('.. sb2sr_norm:',sb2sr_norm[k2dma])
    print('.. nevts[%s]: %f'%(ksr, hnorm[ksr].Integral()))
    return sb2sr_norm[k2dma], hnorm[ksr].Integral()

def get_mc2data_norm(sample, campaign, tgt_lumi=41.9e3, xsec=50., eos_basedir='root://cmseos.fnal.gov//store/user/lpchaa4g/mandrews'): # xsec:pb, tgt_lumi:/pb

    # root://cmseos.fnal.gov//store/user/lpchaa4g/mandrews/2018/ggNtuples-Era04Dec2020v1_ggSkim-v1/ggSkims//h4g2018-mA1p2GeV_cut_hists.root
    year = re.findall('(201[6-8])', sample.split('-')[0])[0]
    inpath = '%s/%s/ggNtuples-%s/ggSkims/%s_cut_hists.root'%(eos_basedir, year, campaign, sample)

    # Get cut flow hist
    cut = str(None) # no cuts applied to get gen level event count
    var = 'npho' # any var that has 1 count per evt will do
    key = cut+'_'+var
    hf = ROOT.TFile.Open(inpath, "READ")
    h = hf.Get('%s/%s'%(cut, key))

    # Get nevts
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
    print('>> For sample %s | norm(mc->data) from Ngen: %.f to data int. lumi: %.f /pb @ sg prodn xs: %.f pb: %f'%(sample, nevts_gen, tgt_lumi, xsec, norm))
    return norm

def get_mc2data_norm_interp(sample, campaign, tgt_lumi=41.9e3, xsec=50., eos_basedir='root://cmseos.fnal.gov//store/user/lpchaa4g/mandrews'): # xsec:pb, tgt_lumi:/pb

    # root://cmseos.fnal.gov//store/user/lpchaa4g/mandrews/2018/ggNtuples-Era04Dec2020v1_ggSkim-v1/ggSkims//h4g2018-mA1p2GeV_cut_hists.root
    year = re.findall('(201[6-8])', sample.split('-')[0])[0]

    # If using an interpolated mass, will need to add nevts_gen between
    # upper and lower mass pts used to perform the interpolation
    interp_masses = [0.3, 0.5, 0.7, 0.9, 1.1]
    magen_instr = sample.split('-')[1].replace('mA','').replace('GeV','')
    magen_in = float(magen_instr.replace('p','.'))
    if magen_in in interp_masses:
        magen_tgts = [magen_in-0.1, magen_in+0.1]
    else:
        magen_tgts = [magen_in]

    #print(magen_tgts)
    nevts_gen = 0.
    # In general, one should use sum of wgtd evts to calculate `nevts_gen`
    # not just the raw event count. Only valid for samples with wgt = 1.
    # such as is the case for all h4g sg samples, but not for some bkg mc samples
    for magen_tgt in magen_tgts:

        magen_tgtstr = str(magen_tgt).replace('.','p')
        sample_ = sample.replace(magen_instr, magen_tgtstr)
        #print(sample)
        assert 'h4g' in sample_

        inpath = '%s/%s/ggNtuples-%s/ggSkims/%s_cut_hists.root'%(eos_basedir, year, campaign, sample_)

        # Get cut flow hist
        cut = str(None) # no cuts applied to get gen level event count
        var = 'npho' # any var that has 1 count per evt will do
        key = cut+'_'+var
        hf = ROOT.TFile.Open(inpath, "READ")
        h = hf.Get('%s/%s'%(cut, key))

        # Get nevts
        #nevts_gen = h.GetEntries()
        nevts_gen += h.GetEntries()
        #print(sample_, nevts_gen)

    ## Sum of wgts
    #if sample == 'DiPhotonJets':
    #    nevts_gen = 1118685275.488525
    #elif sample == 'GluGluHToGG':
    #    nevts_gen = 214099989.445038
    #print(nevts_gen)
    norm = xsec*tgt_lumi/nevts_gen
    #print(norm)
    print('>> For sample %s | norm(mc->data) from Ngen: %.f to data int. lumi: %.f /pb @ sg prodn xs: %.f pb: %f'%(sample, nevts_gen, tgt_lumi, xsec, norm))
    return norm

#def get_mceff(sample, selected_path, skim_path):
def get_mcgenevents(sample, eos_basedir, hgg_campaign, skim_campaign):

    # Get nEvtsGen
    inpath = '%s/%s/ggSkims/%s_cut_hists.root'%(eos_basedir, skim_campaign, sample)
    cut = str(None) # no cuts applied to get gen level event count
    var = 'nEvtsWgtd'
    key = cut+'_'+var
    hf = ROOT.TFile.Open(inpath, "READ")
    h = hf.Get('%s/%s'%(cut, key))
    nEvtsGen = h.GetBinContent(2)

    return nEvtsGen

