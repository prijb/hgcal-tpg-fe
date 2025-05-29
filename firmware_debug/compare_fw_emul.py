# This code takes an existing FwEmulProp file and compares them
import os
import sys
import argparse
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Analyze an FwEmulProp file.')
parser.add_argument('--infile', type=str, help='Input FwEmulProp file')
parser.add_argument('--outdir', type=str, help='Output directory for the plot')
parser.add_argument('--offset', type=int, default=0, help='Offset for the Rx')
parser.add_argument('--window', type=str, default='None,None', help='Window for the plot, e.g., "0,200"')

args = parser.parse_args()
infile = args.infile
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

data = pd.read_csv(infile)
features = ["E_T", "E_EM", "GCTBits", "FractionInCE_E", "FractionInCoreCE_E", "FractionInEarlyCE_E", "FirstLayer", "W_eta", "W_phi", "W_z", "N_TCs", "QualFlags", "Sigma_E", "LastLayer", "ShowerLength", "Sigma_z", "Sigma_phi", "CoreShowerLength", "Sigma_eta", "Sigma_roz"]
print("\nData")
print(data.head())

# Get the lost Rx word mask (aka where nTCs are NOT equal)
emul_ntcs = data["EmulN_TCs"].values
fw_ntcs = data["FwN_TCs"].values
lost_frames = np.array([])
i_frame = 0
while i_frame < len(emul_ntcs):
    if emul_ntcs[i_frame] != fw_ntcs[i_frame]:
        lost_frames = np.append(lost_frames, np.arange(i_frame, i_frame + 31))
        i_frame += 31
    else:
        i_frame += 1

#lost_rx = emul_ntcs != fw_ntcs
#lost_frames_v1 = data["FrameNumber"][lost_rx].values
#print(f"\nFrames with lost Rx (v1): {lost_frames_v1}")
print(f"Frames with lost Rx (v2): {lost_frames}")
lost_rx = np.isin(data["FrameNumber"].values, lost_frames)
#print(lost_rx)

# Set the lost frame values to NaN
for feature in features:
    emul_feature = f"Emul{feature}"
    fw_feature = f"Fw{feature}"
    data.loc[lost_rx, emul_feature] = np.nan
    data.loc[lost_rx, fw_feature] = np.nan

# Plot the nTCs vs frame
x = np.append(data["FrameNumber"].values, data["FrameNumber"].values[-1] + 1)
fig, ax = plt.subplots()
ax.stairs(data["EmulN_TCs"].values, x, label="Emul", color='blue', alpha=0.6)
ax.stairs(data["FwN_TCs"].values, x, label="Fw", color='red', alpha=0.6)
ax.set_xlabel("Frame Number")
ax.set_ylabel("nTCs")
ax.set_title(f"nTCs vs Frame (Rx Offset: {offset})")#
ax.set_xlim(x_low, x_high)
ax.legend()
plt.savefig(f"{args.outdir}/nTCs.png")

# Plot the other features
for feature in features:
    if feature == "N_TCs":
        continue

    print(f"Plotting {feature} vs Frame")

    fw_features = f"Fw{feature}"
    emul_features = f"Emul{feature}"

    fig, ax = plt.subplots()
    ax.stairs(data[emul_features].values, x, label="Emul", color='blue', alpha=0.6)
    ax.stairs(data[fw_features].values, x, label="Fw", color='red', alpha=0.6)
    ax.set_xlabel("Frame Number")
    ax.set_ylabel(feature)
    ax.set_title(f"{feature} vs Frame (Rx Offset: {offset})")
    ax.set_xlim(x_low, x_high)
    ax.legend()
    plt.savefig(f"{args.outdir}/{feature}.png")


