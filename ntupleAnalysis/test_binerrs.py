import ROOT
import numpy as np


h = ROOT.TH1F('h', 'h', 5, 0., 5.)
h.Sumw2()

for i in range(100):
    h.Fill(0)

print(h.GetBinContent(1))
print(h.GetBinError(1))

h.Draw('')
