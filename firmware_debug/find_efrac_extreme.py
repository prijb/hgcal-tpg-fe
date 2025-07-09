# Prints out events where FwFractionInCE_E is 255
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
# Make a new column which is the sum of CeeE, CeeECore and CeHEarly
data_accumulator["CeSum"] = data_accumulator["CeeE"] + data_accumulator["CeeECore"] + data_accumulator["CeHEarly"]


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

# Compare the accumulator, firmware and emulator energies
et_accumulator = data_accumulator["TotE"].values
et_accumulator = et_accumulator * 0.00390625 
# Round to nearest integer
et_accumulator_round = np.round(et_accumulator).astype(int)
et_firmware = data_cluster["FwE_T"].values
et_emulator = data_cluster["EmulE_T"].values

disagreement_with_firmware = et_accumulator_round != et_firmware
disagreement_with_emulator = et_accumulator_round != et_emulator
et_accumulator_disagreement_firmware = et_accumulator_round[disagreement_with_firmware]
et_accumulator_disagreement_emulator = et_accumulator_round[disagreement_with_emulator]
et_disagreement_firmware = et_firmware[disagreement_with_firmware]
et_disagreement_emulator = et_emulator[disagreement_with_emulator]

print(f"Total number of events: {len(et_accumulator)}")
print("\nNumber of events with disagreement with firmware: ", np.sum(disagreement_with_firmware))
print(f"Accumulator values (before rounding): {et_accumulator[disagreement_with_firmware]}")
print(f"Accumulator values (after rounding): {et_accumulator_disagreement_firmware}")
print(f"Firmware values: {et_disagreement_firmware}")

print("Number of events with disagreement with emulator: ", np.sum(disagreement_with_emulator))
print(f"Accumulator values (before rounding): {et_accumulator[disagreement_with_emulator]}")
print(f"Accumulator values (after rounding): {et_accumulator_disagreement_emulator}")
print(f"Emulator values: {et_disagreement_emulator}")

# Look at the events where FwFractionInCE_E is 255
data_cluster_fw_255 = data_cluster[data_cluster["FwFractionInCE_E"] == 255]
# Save a CSV of these events
data_cluster_fw_255.to_csv(os.path.join(args.outdir, "events_with_FwFractionInCE_E_255.csv"), index=False)