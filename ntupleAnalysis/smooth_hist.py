import ROOT
import numpy as np

#fstr = 'data_sb2sr_blind_None_flo0.6475Down_ptwgts.root'
fstr = 'data_sb2sr_blind_None_flo0.6475_ptwgts.root'
#fstr = 'data_sb2sr_blind_None_flo0.6475Up_ptwgts.root'
print(fstr)
eosdir = '/eos/uscms/store/user/lpchaa4g/mandrews/Run2/bkgNoPtWgts-Era22Jun2021v4/bdtgtm0p96_relChgIsolt0p07_etalt1p44/nom-nom/Weights/archive/'
fin = ROOT.TFile.Open(eosdir+fstr)

h = {}

ksr = 'data_sr_pt0vpt1'
ksb = 'data_sbcombo_pt0vpt1'
kratio = 'pt0vpt1_ratio'
ks = [ksr, ksb, kratio]
ks = [kratio]

for k in ks:
    h[k] = fin.Get(k)
    print(k, h[k].GetEntries())
    ix = 30
    iy = 10
    print(ix, iy, h[k].GetBinContent(ix, iy), h[k].GetBinError(ix, iy), h[k].GetBinError(ix, iy)/h[k].GetBinContent(ix, iy))

h[k].SetContour(100)
h[k].Smooth(1)#, "k3a")
h[k].Draw('COLZ')
