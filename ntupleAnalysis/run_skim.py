from __future__ import print_function
import os, glob

import argparse
# Register command line options
parser = argparse.ArgumentParser(description='Run h2aa bkg model.')
parser.add_argument('-i', '--input_dir', default='../ggNtuples/Era24Sep2020_v1/', type=str, help='Input list of ggntuples.')
parser.add_argument('-s', '--sample', default='data2017-Run2017B', type=str, help='[data, h4g][2016-2018]{Run2017B, mA1p0GeV}')
parser.add_argument('-o', '--output_dir', default='ggSkims', type=str, help='Output directory.')
args = parser.parse_args()

input_list = '%s/%s_file_list.txt'(args.input_dir, args.sample)
assert os.isfile(input_list)

output_dir = args.output_dir
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

pyargs = 'skim_ntuple.py -s %s -i %s -o %s'%(args.sample, args.input_list, output_dir)
print(pyargs)
os.system('python %s'%pyargs)
