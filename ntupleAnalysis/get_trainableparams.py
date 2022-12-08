from __future__ import print_function
import numpy as np
np.random.seed(0)
import os, glob
import time
import argparse

#'''
import torch
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import *
import torch.nn as nn
#os.environ["CUDA_VISIBLE_DEVICES"]=str(0)
#'''

import ROOT
from array import array

# Register command line options
parser = argparse.ArgumentParser(description='Run STEALTH selection.')
parser.add_argument('-m', '--model', default='Models/model_epoch80_mae0.1906.pkl', type=str, help='Regressor model file.')
args = parser.parse_args()

model = args.model

# Load mass regressor model
import torch_resnet_concat as networks
#epoch = 80
#neg_mass = 300
## AOD
#model_file = glob.glob('../EB_Pi0_massreg_Pt20To100_2017PU_ext3_tzfixed_wrapfix/MODELS/DoublePi0Pt20To100_m0To1600_pythia8_PU2017_genDR10_aodDR16_nPhoN_PhoNeg%dTo0_wgts_EBtzo25_AOD_m0o1.6_ResNet_blocks3_seedPos_FC128x0_MAEloss_lr0.0005_epochs80_n778k_run0/model_epoch%d_*.pkl'%(neg_mass, epoch))
model_file = model #'Models/model_epoch80_mae0.1906.pkl'
resnet = networks.ResNet(2, 3, [16, 32], 128, 0).cuda()
resnet.load_state_dict(torch.load(model_file)['model'])
resnet.eval()

def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

print(count_parameters(resnet))
