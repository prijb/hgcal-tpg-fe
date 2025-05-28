# This code plots the TCs vs Frame data from the tab separated nTC file
import os
import sys
import argparse
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Plot TCs vs Frame data from a tab separated nTC file.')
parser.add_argument('--infile_rx', type=str, help='Input Rx file containing TCs vs Frame data')
parser.add_argument('--infile_tx', type=str, help='Input Tx file containing TCs vs Frame data')
parser.add_argument('--outdir', type=str, help='Output directory for the plot')
parser.add_argument('--window', type=str, default='None,None', help='Window for the plot, e.g., "0,200"')
parser.add_argument('--offset', type=int, default=0, help='Offset for the x-axis Rx')
args = parser.parse_args()

infile_rx = args.infile_rx
os.makedirs(args.outdir, exist_ok=True)

data_rx = pd.read_csv(infile_rx)
print("\nRx data")
print(data_rx.head())
data_rx = data_rx.loc[:, ["FrameNumber", "nTCs"]]

data_tx = pd.read_csv(args.infile_tx)
print("\nTx data")
print(data_tx.head())
data_tx = data_tx.loc[:, ["FrameNumber", "nTCs"]]

print("\nData Rx")
print(data_rx.head())


# Filter out nTCs with 0
#data_rx = data_rx[data_rx["nTCs"] > 0]
#data_tx = data_tx[data_tx["nTCs"] > 0]


# Get the x and y values for plotting
data_rx_frame_number = data_rx["FrameNumber"].values
data_rx_ntcs = data_rx["nTCs"].values
data_tx_frame_number = data_tx["FrameNumber"].values
data_tx_ntcs = data_tx["nTCs"].values

# Apply offset to Rx frame numbers
data_rx_frame_number += args.offset

x_low = int(args.window.split(',')[0]) if args.window != 'None,None' else 0
x_high = int(args.window.split(',')[1]) if args.window != 'None,None' else None

# Plot the data as a step plot
x_rx = np.append(data_rx_frame_number, data_rx_frame_number[-1] + 1)
x_tx = np.append(data_tx_frame_number, data_tx_frame_number[-1] + 1)
x_rx_centers = (x_rx[:-1] + x_rx[1:]) / 2
x_tx_centers = (x_tx[:-1] + x_tx[1:]) / 2
y_rx = data_rx_ntcs
y_tx = data_tx_ntcs
fig, ax = plt.subplots()
ax.stairs(y_rx, x_rx, label='Rx', color='blue', alpha=0.6)
ax.stairs(y_tx, x_tx, label='Tx', color='red', alpha=0.6)
ax.set_title(f'TCs vs Frame (Rx Offset: {args.offset})')
#ax.plot(x_rx_centers, y_rx, color='tab:blue')
ax.set_xlabel('Frame Number')
ax.set_ylabel('nTCs')
ax.set_xlim(x_low, x_high)
ax.set_ylim(0, 600)
#ax.set_yscale('log')
ax.legend()
plt.savefig(f"{args.outdir}/tcs_vs_frame_{x_low}_{x_high}.png")
