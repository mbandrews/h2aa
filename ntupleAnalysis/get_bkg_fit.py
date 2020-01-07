import ROOT

def get_bkg_fit(sample, blind='sg'):

    hf, h = {}, {}
    entries = {}
    integral = {}

    regions = ['sb', 'sr']
    #keys = ['ma0vma1', 'maxy']
    keys = ['ma0vma1']

    samples = ['Run2017B-F', 'GluGluHToGG']
    for s in samples :
        for r in regions:
            sr = '%s_%s'%(s, r)
            hf[r] = ROOT.TFile("Templates/%s_%s_blind_%s_templates.root"%(s, r, blind),"READ")
            for k in keys:
                srk = '%s_%s_%s'%(s, r, k)
                #if rk == 'sr_maxy': c[rk] = ROOT.TCanvas("c%s"%rk,"c%s"%rk, wd, ht)
                h[srk] = hf[sr].Get(k)
                #h[rk].Draw("")
                entries[srk] = h[srk].GetEntries()
                integral[srk] = h[srk].Integral()

    for s in samples :
        for r in regions:
            sr = '%s_%s'%(s, r)
            hf[r] = ROOT.TFile("Templates/%s_%s_blind_%s_templates.root"%(s, r, blind),"READ")
            for k in keys:

    # plot ratio
    # derive 1sigma uncert vs ma
