# Inspect events with no disagreements
# Check physicality and nature of accumulator inputs
import os
import sys
import argparse
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Analyze the firmware accumulator input')
parser.add_argument('--infile_accumulator', type=str, help='Input Accumulator file')
parser.add_argument('--infile_cluster', type=str, help='Input Cluster file')
parser.add_argument('--outdir', type=str, help='Output directory for the plot')
parser.add_argument('--offset', type=int, default=0, help='Offset for the Rx')
parser.add_argument('--window', type=str, default='None,None', help='Window for the plot, e.g., "0,200"')

args = parser.parse_args()
infile_accumulator = args.infile_accumulator
infile_cluster = args.infile_cluster
os.makedirs(args.outdir, exist_ok=True)
offset = args.offset
x_low = args.window.split(',')[0]
x_high = args.window.split(',')[1]
if x_low == 'None':
    x_low = 0
else:
    x_low = int(x_low)
if x_high == 'None':
    x_high = None
else:
    x_high = int(x_high)

data_accumulator = pd.read_csv(infile_accumulator)
data_cluster = pd.read_csv(infile_cluster)
features_accumulator = ["FrameNumber", "NumberOfTcs", "TotE", "CeeE", "CeeECore", "CeHEarly", "SumW", "NumberOfTcsW", "SumW2", "SumWZ", "SumWRoZ", "SumWPhi", "SumWZ2", "SumWRoZ2", "SumWPhi2", "LayerBits" "satTC", "shapeQ"]
features_cluster = ["E_T", "E_EM", "GCTBits", "FractionInCE_E", "FractionInCoreCE_E", "FractionInEarlyCE_E", "FirstLayer", "W_eta", "W_phi", "W_z", "N_TCs", "QualFlags", "Sigma_E", "LastLayer", "ShowerLength", "Sigma_z", "Sigma_phi", "CoreShowerLength", "Sigma_eta", "Sigma_roz"]

data_accumulator = pd.DataFrame(data_accumulator, columns=features_accumulator)

# Get rid of lost frames
emul_ntcs = data_cluster["EmulN_TCs"].values
fw_ntcs = data_cluster["FwN_TCs"].values
lost_frames = np.array([])
i_frame = 0
while i_frame < len(emul_ntcs):
    if emul_ntcs[i_frame] != fw_ntcs[i_frame]:
        lost_frames = np.append(lost_frames, np.arange(i_frame, i_frame + 31))
        i_frame += 31
    else:
        i_frame += 1
lost_rx = np.isin(data_cluster["FrameNumber"].values, lost_frames)
data_accumulator = data_accumulator[~lost_rx]
data_cluster = data_cluster[~lost_rx]

print("\nData (Accumulator)")
print(data_accumulator.head()) 
print("\nData (Cluster)")
print(data_cluster.head()) 

# Skip features for disagreement checks
features_to_skip = ["QualFlags"]

# Find the frames which have no disagreements
agreements = np.full(len(data_accumulator), True)
for i_feature, feature in enumerate(features_cluster):
    if feature in features_to_skip: continue
    print(f"Feature: {feature}")
    emul_feature = f"Emul{feature}"
    fw_feature = f"Fw{feature}"

    # Get the disagreement mask
    disagreement_mask = (data_cluster[emul_feature].values != data_cluster[fw_feature].values)
    agreements = np.logical_and(agreements, ~disagreement_mask)
    
print(f"\nNumber of frames with no disagreements: {np.sum(agreements)}")