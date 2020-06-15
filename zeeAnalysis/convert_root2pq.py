from __future__ import print_function
import numpy as np
np.random.seed(0)
import os, glob, time
import ROOT
import pyarrow as pa
import pyarrow.parquet as pq
from hist_utils_zee import get_weight_1d

# Register command line options
import argparse
parser = argparse.ArgumentParser(description='Run STEALTH selection.')
parser.add_argument('-s', '--sample', default='test', type=str, help='Sample name.')
parser.add_argument('-i', '--img_inputs', default='img_inputs.txt', type=str, help='List file of img inputs.')
parser.add_argument('-o', '--outdir', default='.', type=str, help='Output directory.')
parser.add_argument('-e', '--events', default=10000, type=int, help='N output photons.')
parser.add_argument('-l', '--sel_evtlist', default=None, type=str, help='List of evts to process.')
parser.add_argument('-m', '--img_evtlist', default=None, type=str, help='List of evts to process.')
args = parser.parse_args()

sample = args.sample
n_output_samples = args.events
sel_evtlist_fname = args.sel_evtlist
img_evtlist_fname = args.img_evtlist

def pa_array(d):
    arr = pa.array([d]) if np.isscalar(d) or type(d) == list else pa.array([d.tolist()])
    #print(arr.type)
    ## double to single float
    if arr.type == pa.float64():
        arr = arr.cast(pa.float32())
    elif arr.type == pa.list_(pa.float64()):
        arr = arr.cast(pa.list_(pa.float32()))
    elif arr.type == pa.list_(pa.list_(pa.float64())):
        arr = arr.cast(pa.list_(pa.list_(pa.float32())))
    elif arr.type == pa.list_(pa.list_(pa.list_(pa.float64()))):
        arr = arr.cast(pa.list_(pa.list_(pa.list_(pa.float32()))))
    elif arr.type == pa.list_(pa.list_(pa.list_(pa.list_(pa.float64())))):
        arr = arr.cast(pa.list_(pa.list_(pa.list_(pa.list_(pa.float32())))))
    #else:
    #    print('Unknown type for conversion to (list of) floats',arr.type)
    #print(arr.type)
    return arr

# Crop out EB shower from full EB image
def crop_EBshower(imgEB, ieta, iphi, window=32):

    # NOTE: image window here should correspond to the one used in RHAnalyzer
    off = window//2
    ieta = int(ieta)+1 # seed positioned at [15,15]
    iphi = int(iphi)+1 # seed positioned at [15,15]

    # Wrap-around on left side
    if iphi < off:
        diff = off-iphi
        img_crop = np.concatenate((imgEB[:,ieta-off:ieta+off,-diff:],
                                   imgEB[:,ieta-off:ieta+off,:iphi+off]), axis=-1)
    # Wrap-around on right side
    elif 360-iphi < off:
        diff = off - (360-iphi)
        img_crop = np.concatenate((imgEB[:,ieta-off:ieta+off,iphi-off:],
                                   imgEB[:,ieta-off:ieta+off,:diff]), axis=-1)
    # Nominal case
    else:
        img_crop = imgEB[:,ieta-off:ieta+off,iphi-off:iphi+off]

    return img_crop

def is_barrel_ieta(ieta, window=32):
    off = window//2
    if ieta == -1:
        return False
    elif (ieta+1 < off) or (ieta+1 > 170-off): # seed at idx=15
        return False
    else:
        return True

# Convert list contents to ints
def list_str2int(l):
    return [int(i) for i in l]

def get_evtlist(imgtree):

    print('Making list of img evts...')
    nEvts = imgtree.GetEntries()
    #nEvts = 100000
    idxs = []
    for iEvt in range(nEvts):
        # Initialize event
        imgtree.GetEntry(iEvt)
        if iEvt%100e3==0: print(iEvt,'/',nEvts)
        eventId = [imgtree.runId, imgtree.lumiId, imgtree.eventId, iEvt]
        idxs.append(eventId)

    # Array index on 1st element should be 0, and nEvts-1 on last element
    idxs = np.array(idxs)
    assert idxs[0,-1] == 0 and idxs[-1,-1] == nEvts-1
    print('... done.')

    return idxs

# Return the array index in `evtIds` corresponding to event loaded in `tree`
# Each event uniquely identified by run, lumi, event no.
# Filter first by run then lumi before looking for event no.
# If evt not found, returns `-1`
def idx_where_run_lumi_evt(evtid, evtIds):

    '''
    evtIds = np.array(evtIds)
    # `evtIds` must have shape (nevts,4) where
    # [:,0]: run
    # [:,1]: lumi
    # [:,2]: event
    # [:,3]: idx
    assert evtIds.shape[-1] == 4
    '''

    # This is the target event ID from the main IMG TTree
    #evtid = np.array([tree.runId, tree.lumiId, tree.eventId])

    # Find the index in the friend tree corresponding to target event
    # Filter by run
    iruns = np.argwhere(evtIds[:,0] == evtid[0]).flatten()
    evtIds = evtIds[iruns]
    if len(evtIds) == 0:
        return -1
    # Filter by lumi
    ilumis = np.argwhere(evtIds[:,1] == evtid[1]).flatten()
    evtIds = evtIds[ilumis]
    if len(evtIds) == 0:
        return -1
    # Filter by event
    ievts = np.argwhere(evtIds[:,2] == evtid[2]).flatten()
    evtIds = evtIds[ievts]

    assert len(evtIds) <= 1, 'More than one evt match found!'

    if len(evtIds) == 0:
        return -1
    else:
        return evtIds.flatten()[-1] # return idx

# Read in IMG ntuple list
img_inputs = []
print('Opening img input list:',args.img_inputs)
with open(args.img_inputs, 'r') as img_file:
    for img_input in img_file:
        img_inputs.append(img_input[:-1])
print(img_inputs[0])
print('len(img_inputs):',len(img_inputs))
assert len(img_inputs) > 0

# Load IMG ntuples as main TTree
print('Setting IMG as main TTree')
print('N IMG files:',len(img_inputs))
print('IMG file[0]:',img_inputs[0])
imgtree = ROOT.TChain("fevt/RHTree")
for fi in img_inputs:
    imgtree.Add(fi)
    #break
nEvts = imgtree.GetEntries()
print('N evts in IMG ntuple:',nEvts)

# Make list of evt idxs in imgtree
if os.path.isfile(img_evtlist_fname):
    img_evtIds = np.load(img_evtlist_fname)['img_evtlist']
else:
    img_evtIds = get_evtlist(imgtree)
    np.savez(img_evtlist_fname, img_evtlist=img_evtIds)
assert img_evtIds.shape[-1] == 4

# Read in selected events to process
sel_evtIds, sel_phoIds = [], []
#evtlist_sample = sample[:-1]+'B-F'
#evtlist_sample = sample
#sel_evtlist_fname = 'Templates/%s_selected_event_list.txt'%evtlist_sample
#assert os.path.isfile(sel_evtlist_fname)
with open(sel_evtlist_fname) as evtlist_f:
    for i,l in enumerate(evtlist_f):
        # l = 'run:ls:evt:pho_idxs\n' where pho_idxs is comma-separated
        evt = l.strip('\n').split(':')
        #evtId, phoId = evt[:-1]+[i], evt[-1].split(',')
        evtId, phoId = evt[:-1], evt[-1].split(',')
        sel_evtIds.append(list_str2int(evtId))
        sel_phoIds.append(list_str2int(phoId))
sel_evtIds, sel_phoIds = np.array(sel_evtIds), np.array(sel_phoIds)
assert sel_evtIds.shape[-1] == 3
assert len(sel_evtIds) == len(sel_phoIds)
print('N selected events:',len(sel_evtIds))

# Initialize output parquet filename
pq_outstr = '%s/%s_selected_events_n%dk.parquet.%d'%(args.outdir, sample, n_output_samples//1000, 0)
print('Will write to:',pq_outstr)

# Load pt weights for MC
#wgt_sample = 'DYToEE2Run2017B-F'
wgt_sample = 'DYToEE2Run2017'
k = 'pt1corr' # 'pt1corr':pho, 'elePt1corr':ele
with np.load("Weights/%s_%s_ptwgts.npz"%(wgt_sample, k)) as wgt_f:
    pt_wgts = wgt_f['pt_wgts']
    pt_edges = wgt_f['pt_edges']

# Event range to process
iEvtStart = 0
#iEvtEnd   = nEvts
iEvtEnd   = len(sel_evtIds)
#iEvtEnd   = 200
print(">> Processing entries: [",iEvtStart,"->",iEvtEnd,")")

print_step = 1000
nPhos = 0
data = {} # Arrays to be written to parquet should be saved to data dict
sw = ROOT.TStopwatch()
sw.Start()
# Main event loop follows imgtree
for iEvt in range(iEvtStart,iEvtEnd):

    if iEvt%print_step==0: print('>> %s processed: %d / %d'%(sample, iEvt, iEvtEnd-iEvtStart))
    # Check if this event is in list of selected events
    #evt_idx = idx_where_run_lumi_evt(imgtree, img_evtIds)

    # Get idx of this selected event in img tree
    this_evt = sel_evtIds[iEvt]
    evt_idx = idx_where_run_lumi_evt(this_evt, img_evtIds)
    if evt_idx == -1: continue

    # Get evt from img tree
    evt_status = imgtree.GetEntry(evt_idx)
    if evt_status <= 0: continue

    # Make sure there are photons falling in EB ROI
    idxs_roi = [i for i,ieta in enumerate(imgtree.SC_ieta) if is_barrel_ieta(ieta)]
    if len(idxs_roi) == 0: continue

    # Initialize EB images
    X_EBt = np.array(imgtree.EB_energyT).reshape(1,170,360)
    X_EBz = np.array(imgtree.EB_energyZ).reshape(1,170,360)
    X_tks = np.array(imgtree.TracksPt_EB).reshape(1,170,360)
    X_cms = np.concatenate([X_EBt, X_EBz, X_tks], axis=0)

    # Make image windows over each seed
    #for pho_idx in phoIds[evt_idx]:
    for pho_idx in sel_phoIds[iEvt]:

        if not is_barrel_ieta(imgtree.SC_ieta[pho_idx]): continue

        data['idx'] = [imgtree.runId, imgtree.lumiId, imgtree.eventId, pho_idx]
        data['ieta'] = imgtree.SC_ieta[pho_idx]
        data['iphi'] = imgtree.SC_iphi[pho_idx]
        assert data['ieta'] != -1
        assert data['iphi'] != -1
        data['Xtz'] = crop_EBshower(X_cms, data['ieta'], data['iphi'])

        data['pho_p4'] = [
                imgtree.pho_E[pho_idx],
                imgtree.pho_pT[pho_idx],
                imgtree.pho_eta[pho_idx],
                imgtree.pho_phi[pho_idx]
                ]
        data['pho_vars'] = [
                imgtree.pho_r9[pho_idx]
                ,imgtree.pho_HoE[pho_idx]
                ,imgtree.pho_hasPxlSeed[pho_idx]
                ,imgtree.pho_sieie[pho_idx]
                ,imgtree.pho_phoIso[pho_idx]
                ,imgtree.pho_trkIso[pho_idx]
                ,imgtree.pho_chgIsoCorr[pho_idx]
                ,imgtree.pho_neuIsoCorr[pho_idx]
                ,imgtree.pho_phoIsoCorr[pho_idx]
                ,imgtree.pho_bdt[pho_idx]
                ]
        data['wgt'] = 1. if 'Run' in sample else get_weight_1d(imgtree.pho_pT[pho_idx], pt_edges, pt_wgts)

        # Write to parquet
        pqdata = [pa_array(d) for d in data.values()]
        table = pa.Table.from_arrays(pqdata, data.keys())
        if nPhos == 0:
            writer = pq.ParquetWriter(pq_outstr, table.schema, compression='snappy')
            print('>> Creating:', pq_outstr)
        writer.write_table(table)

        nPhos += 1
        if nPhos%print_step==0: print('>> %s written: %d / %d'%(sample, nPhos, n_output_samples))

    if nPhos >= n_output_samples: break

if nPhos > 0: writer.close()
sw.Stop()
print(">> N photons written: %d / %d"%(nPhos, iEvtEnd-iEvtStart))
print(">> Real time:",sw.RealTime()/60.,"minutes")
print(">> CPU time: ",sw.CpuTime() /60.,"minutes")

# Verify output file
assert os.path.isfile(pq_outstr)
pqIn = pq.ParquetFile(pq_outstr)
print(pq_outstr)
print(pqIn.metadata)
print(pqIn.schema)
print(pqIn.read_row_group(0, columns=['idx','iphi','ieta','wgt','pho_p4']).to_pydict())
