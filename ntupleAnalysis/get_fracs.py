import numpy as np

#flo = 0.687281137302 #evt-wgtd
flo = 0.756 #QCD frac

#fA*A + (1-fA)*B, B
#flo*fA*A + [flo*(1-fA) + (1-flo)]*B

fA = 0.85

f1 = flo*fA
print(f1, f1/flo)

f2 = flo*(1-fA) + (1-flo)
#print(f2, 1.-f1)

#A, fA*A + (1-fA)*B
#[flo + (1-flo)*fA]*A + (1-flo)*(1-fA)*B

fA = 0.24

f1 = flo + (1-flo)*fA
print(f1, f1/flo)

f2 = (1-flo)*(1-fA)
#print(f2, 1.-f1)
