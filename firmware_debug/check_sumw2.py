# Looks for cases where sum x_i^2 is smaller than (sum x_i)^2
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

sumw = data_accumulator["SumW"].values
sumw2 = data_accumulator["SumW2"].values
sumwz = data_accumulator["SumWZ"].values
sumwz2 = data_accumulator["SumWZ2"].values
sumwphi = data_accumulator["SumWPhi"].values
sumwphi2 = data_accumulator["SumWPhi2"].values
sumwro = data_accumulator["SumWRoZ"].values
sumwro2 = data_accumulator["SumWRoZ2"].values

# Unphysical cases are where sumw2 < sumw^2
unphysical_mask = sumw2 <= (sumw**2)
unphysical_z_mask = sumwz2 <= (sumwz**2)
unphysical_phi_mask = sumwphi2 <= (sumwphi**2)
unphysical_ro_mask = sumwro2 <= (sumwro**2)

print(f"Number of entries: {len(data_accumulator)}")
print(f"Unphysical cases: {np.sum(unphysical_mask)}")
print(f"Unphysical cases in Z: {np.sum(unphysical_z_mask)}")
print(f"Unphysical cases in Phi: {np.sum(unphysical_phi_mask)}")
print(f"Unphysical cases in Ro: {np.sum(unphysical_ro_mask)}")

# Calculate disagreement fractions for the data
total = len(data_cluster)
feature_disagreement_fraction = np.zeros(len(features_cluster))
for i_feature, feature in enumerate(features_cluster):
    print(f"Feature: {feature}")
    emul_feature = f"Emul{feature}"
    fw_feature = f"Fw{feature}"

    # Check number of agreements and disagreements
    agreements = np.sum(data_cluster[emul_feature] == data_cluster[fw_feature])
    disagreements = np.sum(data_cluster[emul_feature] != data_cluster[fw_feature])
    #print(f"Agreements: {agreements}, Disagreements: {disagreements}")
    feature_disagreement_fraction[i_feature] = disagreements / total

# Calculate disagreements for physical and unphysical W sum
data_cluster_physical = data_cluster[~unphysical_mask]
data_cluster_unphysical = data_cluster[unphysical_mask]
total_physical = len(data_cluster_physical)
total_unphysical = len(data_cluster_unphysical)
feature_disagreement_fraction_physical = np.zeros(len(features_cluster))
feature_disagreement_fraction_unphysical = np.zeros(len(features_cluster))

for i_feature, feature in enumerate(features_cluster):
    emul_feature = f"Emul{feature}"
    fw_feature = f"Fw{feature}"

    # Physical cases
    agreements_physical = np.sum(data_cluster_physical[emul_feature] == data_cluster_physical[fw_feature])
    disagreements_physical = np.sum(data_cluster_physical[emul_feature] != data_cluster_physical[fw_feature])
    feature_disagreement_fraction_physical[i_feature] = disagreements_physical / total_physical

    # Unphysical cases
    agreements_unphysical = np.sum(data_cluster_unphysical[emul_feature] == data_cluster_unphysical[fw_feature])
    disagreements_unphysical = np.sum(data_cluster_unphysical[emul_feature] != data_cluster_unphysical[fw_feature])
    feature_disagreement_fraction_unphysical[i_feature] = disagreements_unphysical / total_unphysical

# Wz case
data_cluster_physical_wz = data_cluster[~unphysical_z_mask]
data_cluster_unphysical_wz = data_cluster[unphysical_z_mask]
total_physical_wz = len(data_cluster_physical_wz)
total_unphysical_wz = len(data_cluster_unphysical_wz)
feature_disagreement_fraction_physical_wz = np.zeros(len(features_cluster))
feature_disagreement_fraction_unphysical_wz = np.zeros(len(features_cluster))

for i_feature, feature in enumerate(features_cluster):
    emul_feature = f"Emul{feature}"
    fw_feature = f"Fw{feature}"

    # Physical cases
    agreements_physical_wz = np.sum(data_cluster_physical_wz[emul_feature] == data_cluster_physical_wz[fw_feature])
    disagreements_physical_wz = np.sum(data_cluster_physical_wz[emul_feature] != data_cluster_physical_wz[fw_feature])
    feature_disagreement_fraction_physical_wz[i_feature] = disagreements_physical_wz / total_physical_wz

    # Unphysical cases
    agreements_unphysical_wz = np.sum(data_cluster_unphysical_wz[emul_feature] == data_cluster_unphysical_wz[fw_feature])
    disagreements_unphysical_wz = np.sum(data_cluster_unphysical_wz[emul_feature] != data_cluster_unphysical_wz[fw_feature])
    feature_disagreement_fraction_unphysical_wz[i_feature] = disagreements_unphysical_wz / total_unphysical_wz

# Wphi case
data_cluster_physical_wphi = data_cluster[~unphysical_phi_mask]
data_cluster_unphysical_wphi = data_cluster[unphysical_phi_mask]
total_physical_wphi = len(data_cluster_physical_wphi)
total_unphysical_wphi = len(data_cluster_unphysical_wphi)
feature_disagreement_fraction_physical_wphi = np.zeros(len(features_cluster))
feature_disagreement_fraction_unphysical_wphi = np.zeros(len(features_cluster))

for i_feature, feature in enumerate(features_cluster):
    emul_feature = f"Emul{feature}"
    fw_feature = f"Fw{feature}"

    # Physical cases
    agreements_physical_wphi = np.sum(data_cluster_physical_wphi[emul_feature] == data_cluster_physical_wphi[fw_feature])
    disagreements_physical_wphi = np.sum(data_cluster_physical_wphi[emul_feature] != data_cluster_physical_wphi[fw_feature])
    feature_disagreement_fraction_physical_wphi[i_feature] = disagreements_physical_wphi / total_physical_wphi

    # Unphysical cases
    agreements_unphysical_wphi = np.sum(data_cluster_unphysical_wphi[emul_feature] == data_cluster_unphysical_wphi[fw_feature])
    disagreements_unphysical_wphi = np.sum(data_cluster_unphysical_wphi[emul_feature] != data_cluster_unphysical_wphi[fw_feature])
    feature_disagreement_fraction_unphysical_wphi[i_feature] = disagreements_unphysical_wphi / total_unphysical_wphi

# Wroz case
data_cluster_physical_wro = data_cluster[~unphysical_ro_mask]
data_cluster_unphysical_wro = data_cluster[unphysical_ro_mask]
total_physical_wro = len(data_cluster_physical_wro)
total_unphysical_wro = len(data_cluster_unphysical_wro)
feature_disagreement_fraction_physical_wro = np.zeros(len(features_cluster))
feature_disagreement_fraction_unphysical_wro = np.zeros(len(features_cluster))
for i_feature, feature in enumerate(features_cluster):
    emul_feature = f"Emul{feature}"
    fw_feature = f"Fw{feature}"

    # Physical cases
    agreements_physical_wro = np.sum(data_cluster_physical_wro[emul_feature] == data_cluster_physical_wro[fw_feature])
    disagreements_physical_wro = np.sum(data_cluster_physical_wro[emul_feature] != data_cluster_physical_wro[fw_feature])
    feature_disagreement_fraction_physical_wro[i_feature] = disagreements_physical_wro / total_physical_wro

    # Unphysical cases
    agreements_unphysical_wro = np.sum(data_cluster_unphysical_wro[emul_feature] == data_cluster_unphysical_wro[fw_feature])
    disagreements_unphysical_wro = np.sum(data_cluster_unphysical_wro[emul_feature] != data_cluster_unphysical_wro[fw_feature])
    feature_disagreement_fraction_unphysical_wro[i_feature] = disagreements_unphysical_wro / total_unphysical_wro





print(f"\nFeatures: {features_cluster}")
print(f"Feature disagreement fractions: {feature_disagreement_fraction}")
#print(f"Feature disagreement fractions (physical): {feature_disagreement_fraction_physical}")
#print(f"Feature disagreement fractions (unphysical): {feature_disagreement_fraction_unphysical}")
#print(f"Feature disagreement fractions (physical Wz): {feature_disagreement_fraction_physical_wz}")
#print(f"Feature disagreement fractions (unphysical Wz): {feature_disagreement_fraction_unphysical_wz}")
#print(f"Feature disagreement fractions (physical Wphi): {feature_disagreement_fraction_physical_wphi}")
#print(f"Feature disagreement fractions (unphysical Wphi): {feature_disagreement_fraction_unphysical_wphi}")
#print(f"Feature disagreement fractions (physical Wro): {feature_disagreement_fraction_physical_wro}")
#print(f"Feature disagreement fractions (unphysical Wro): {feature_disagreement_fraction_unphysical_wro}")

################### Disagreement fraction ####################
# Plot the disagreement fraction
plt.figure()
plt.bar(features_cluster, feature_disagreement_fraction)
plt.xlabel("")
plt.ylabel(f"Disagreement Fraction (Rx Offset: {offset})")
#plt.ylim(0, 1)
#plt.yscale('log')
plt.title("Emul-FW Disagreement Fractions")
plt.xticks(rotation=45, ha="right")
plt.tight_layout() 
plt.savefig(f"{args.outdir}/feature_disagreement_fractions.png")

# Plot the disagreement fraction for physical and unphysical cases
plt.figure()
plt.bar(features_cluster, feature_disagreement_fraction_physical, label=r"$\Sigma w_{i}^{2} > (\Sigma w_{i})^2$", alpha=0.6, color='blue')
plt.bar(features_cluster, feature_disagreement_fraction_unphysical, label=r"$\Sigma w_{i}^{2} > (\Sigma w_{i})^2$"r"$\Sigma w_{i}^{2} \leq (\Sigma w_{i})^2$", alpha=0.6, color='red')
plt.xlabel("")
plt.ylabel(f"Disagreement Fraction (Rx Offset: {offset})")
#plt.ylim(0, 1)
#plt.yscale('log')
plt.title("Emul-FW Disagreement Fractions (Physical vs Unphysical)")
plt.xticks(rotation=45, ha="right")
plt.legend()
plt.tight_layout()
plt.savefig(f"{args.outdir}/feature_disagreement_fractions_physical_unphysical_w.png")

# Wz
plt.figure()
plt.bar(features_cluster, feature_disagreement_fraction_physical_wz, label=r"$\Sigma wz_{i}^{2} > (\Sigma wz_{i})^2$", alpha=0.6, color='blue')
plt.bar(features_cluster, feature_disagreement_fraction_unphysical_wz, label=r"$\Sigma wz_{i}^{2} \leq (\Sigma wz_{i})^2$", alpha=0.6, color='red')
plt.xlabel("")
plt.ylabel(f"Disagreement Fraction (Rx Offset: {offset})")
#plt.ylim(0, 1)
#plt.yscale('log')
plt.title("Emul-FW Disagreement Fractions (Physical vs Unphysical Wz)")
plt.xticks(rotation=45, ha="right")
plt.legend()
plt.tight_layout()
plt.savefig(f"{args.outdir}/feature_disagreement_fractions_physical_unphysical_wz.png")

# Wphi
plt.figure()
plt.bar(features_cluster, feature_disagreement_fraction_physical_wphi, label=r"$\Sigma w\phi_{i}^{2} > (\Sigma w\phi_{i})^2$", alpha=0.6, color='blue')
plt.bar(features_cluster, feature_disagreement_fraction_unphysical_wphi, label=r"$\Sigma w\phi_{i}^{2} \leq (\Sigma w\phi_{i})^2$", alpha=0.6, color='red')
plt.xlabel("")
plt.ylabel(f"Disagreement Fraction (Rx Offset: {offset})")
#plt.ylim(0, 1)
#plt.yscale('log')
plt.title("Emul-FW Disagreement Fractions (Physical vs Unphysical Wphi)")
plt.xticks(rotation=45, ha="right")
plt.legend()
plt.tight_layout()
plt.savefig(f"{args.outdir}/feature_disagreement_fractions_physical_unphysical_wphi.png")   

# Wro
plt.figure()
plt.bar(features_cluster, feature_disagreement_fraction_physical_wro, label=r"$\Sigma wr/z_{i}^{2} > (\Sigma wr/z_{i})^2$", alpha=0.6, color='blue')
plt.bar(features_cluster, feature_disagreement_fraction_unphysical_wro, label=r"$\Sigma wr/z_{i}^{2} \leq (\Sigma wr/z_{i})^2$", alpha=0.6, color='red')
plt.xlabel("")
plt.ylabel(f"Disagreement Fraction (Rx Offset: {offset})")
#plt.ylim(0, 1)
#plt.yscale('log')
plt.title("Emul-FW Disagreement Fractions (Physical vs Unphysical Wro)")
plt.xticks(rotation=45, ha="right")
plt.legend()
plt.tight_layout()
plt.savefig(f"{args.outdir}/feature_disagreement_fractions_physical_unphysical_wro.png")

################### Scatter plots ####################
# Make scatter plots only for cases of disagreement (Fw vs Emul)
os.makedirs(f"{args.outdir}/scatter", exist_ok=True)

for feature in features_cluster:
    emul_feature = f"Emul{feature}"
    fw_feature = f"Fw{feature}"

    # Overall disagreements
    disagreement_mask = data_cluster[emul_feature] != data_cluster[fw_feature]
    fw_vals = data_cluster[fw_feature][disagreement_mask].values
    emul_vals = data_cluster[emul_feature][disagreement_mask].values

    if len(fw_vals) != 0:
        print(f"Plotting disagreement scatter: {emul_feature} vs {fw_feature}")
        fig, ax = plt.subplots()
        ax.scatter(fw_vals, emul_vals, s=10)
        # 45 degree line
        max_value = max(fw_vals.max(), emul_vals.max())
        min_value = min(fw_vals.min(), emul_vals.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature}")
        ax.set_ylabel(f"Emul{feature}")
        ax.set_title(f"Fw vs Emul {feature} all (Rx Offset: {offset})")
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_all.png")

    # For W sum disagreement
    # Physical 
    disagreement_mask = data_cluster_physical[emul_feature] != data_cluster_physical[fw_feature]
    fw_vals_physical = data_cluster_physical[fw_feature][disagreement_mask].values
    emul_vals_physical = data_cluster_physical[emul_feature][disagreement_mask].values

    if len(fw_vals_physical) != 0:
        print(f"Plotting disagreement scatter (physical): {emul_feature} vs {fw_feature}")
        fig, ax = plt.subplots()
        ax.scatter(fw_vals_physical, emul_vals_physical, s=10)
        # 45 degree line
        max_value = max(fw_vals_physical.max(), emul_vals_physical.max())
        min_value = min(fw_vals_physical.min(), emul_vals_physical.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature} (Physical)")
        ax.set_ylabel(f"Emul{feature} (Physical)")
        ax.set_title(f"Fw vs Emul {feature} physical Wsum (Rx Offset: {offset})")
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_physical_w.png")

    # Unphysical
    disagreement_mask = data_cluster_unphysical[emul_feature] != data_cluster_unphysical[fw_feature]
    fw_vals_unphysical = data_cluster_unphysical[fw_feature][disagreement_mask].values
    emul_vals_unphysical = data_cluster_unphysical[emul_feature][disagreement_mask].values  

    if len(fw_vals_unphysical) != 0:
        print(f"Plotting disagreement scatter (unphysical): {emul_feature} vs {fw_feature}")
        fig, ax = plt.subplots()
        ax.scatter(fw_vals_unphysical, emul_vals_unphysical, s=10)
        # 45 degree line
        max_value = max(fw_vals_unphysical.max(), emul_vals_unphysical.max())
        min_value = min(fw_vals_unphysical.min(), emul_vals_unphysical.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature} (Unphysical)")
        ax.set_ylabel(f"Emul{feature} (Unphysical)")
        ax.set_title(f"Fw vs Emul {feature} unphysical Wsum (Rx Offset: {offset})")
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_unphysical_w.png")

    # Plot both on the same plot
    if (len(fw_vals_physical) != 0) and (len(fw_vals_unphysical) != 0):
        fig, ax = plt.subplots()
        ax.scatter(fw_vals_physical, emul_vals_physical, s=10, label=r"$\Sigma w_{i}^{2} > (\Sigma w_{i})^2$", color="blue", alpha=0.6)
        ax.scatter(fw_vals_unphysical, emul_vals_unphysical, s=10, label=r"$\Sigma w_{i}^{2} > (\Sigma w_{i})^2$", color="red", alpha=0.6)
        # 45 degree line
        max_value = max(fw_vals_physical.max(), emul_vals_physical.max(), fw_vals_unphysical.max(), emul_vals_unphysical.max())
        min_value = min(fw_vals_physical.min(), emul_vals_physical.min(), fw_vals_unphysical.min(), emul_vals_unphysical.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature}")
        ax.set_ylabel(f"Emul{feature}")
        ax.set_title(f"Fw vs Emul {feature} Wsum (Rx Offset: {offset})")
        ax.legend()
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_physical_vs_unphysical_w.png")

    # Wz
    # Physical
    disagreement_mask = data_cluster_physical_wz[emul_feature] != data_cluster_physical_wz[fw_feature]
    fw_vals_physical_wz = data_cluster_physical_wz[fw_feature][disagreement_mask].values
    emul_vals_physical_wz = data_cluster_physical_wz[emul_feature][disagreement_mask].values

    if len(fw_vals_physical_wz) != 0:
        print(f"Plotting disagreement scatter (physical Wz): {emul_feature} vs {fw_feature}")
        fig, ax = plt.subplots()
        ax.scatter(fw_vals_physical_wz, emul_vals_physical_wz, s=10)
        # 45 degree line
        max_value = max(fw_vals_physical_wz.max(), emul_vals_physical_wz.max())
        min_value = min(fw_vals_physical_wz.min(), emul_vals_physical_wz.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature} (Physical Wz)")
        ax.set_ylabel(f"Emul{feature} (Physical Wz)")
        ax.set_title(f"Fw vs Emul {feature} physical Wz (Rx Offset: {offset})")
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_physical_wz.png")

    # Unphysical
    disagreement_mask = data_cluster_unphysical_wz[emul_feature] != data_cluster_unphysical_wz[fw_feature]
    fw_vals_unphysical_wz = data_cluster_unphysical_wz[fw_feature][disagreement_mask].values
    emul_vals_unphysical_wz = data_cluster_unphysical_wz[emul_feature][disagreement_mask].values

    if len(fw_vals_unphysical_wz) != 0:
        print(f"Plotting disagreement scatter (unphysical Wz): {emul_feature} vs {fw_feature}")
        fig, ax = plt.subplots()
        ax.scatter(fw_vals_unphysical_wz, emul_vals_unphysical_wz, s=10)
        # 45 degree line
        max_value = max(fw_vals_unphysical_wz.max(), emul_vals_unphysical_wz.max())
        min_value = min(fw_vals_unphysical_wz.min(), emul_vals_unphysical_wz.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature} (Unphysical Wz)")
        ax.set_ylabel(f"Emul{feature} (Unphysical Wz)")
        ax.set_title(f"Fw vs Emul {feature} unphysical Wz (Rx Offset: {offset})")
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_unphysical_wz.png")

    # Plot both on the same plot
    if (len(fw_vals_physical_wz) != 0) and (len(fw_vals_unphysical_wz) != 0):
        fig, ax = plt.subplots()
        ax.scatter(fw_vals_physical_wz, emul_vals_physical_wz, s=10, label=r"$\Sigma wz_{i}^{2} > (\Sigma wz_{i})^2$", color="blue", alpha=0.6)
        ax.scatter(fw_vals_unphysical_wz, emul_vals_unphysical_wz, s=10, label=r"$\Sigma wz_{i}^{2} \leq (\Sigma wz_{i})^2$", color="red", alpha=0.6)
        # 45 degree line
        max_value = max(fw_vals_physical_wz.max(), emul_vals_physical_wz.max(), fw_vals_unphysical_wz.max(), emul_vals_unphysical_wz.max())
        min_value = min(fw_vals_physical_wz.min(), emul_vals_physical_wz.min(), fw_vals_unphysical_wz.min(), emul_vals_unphysical_wz.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature}")
        ax.set_ylabel(f"Emul{feature}")
        ax.set_title(f"Fw vs Emul {feature} Wz (Rx Offset: {offset})")
        ax.legend()
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_physical_vs_unphysical_wz.png")

    # Wphi
    # Physical
    disagreement_mask = data_cluster_physical_wphi[emul_feature] != data_cluster_physical_wphi[fw_feature]
    fw_vals_physical_wphi = data_cluster_physical_wphi[fw_feature][disagreement_mask].values
    emul_vals_physical_wphi = data_cluster_physical_wphi[emul_feature][disagreement_mask].values    

    if len(fw_vals_physical_wphi) != 0:
        print(f"Plotting disagreement scatter (physical Wphi): {emul_feature} vs {fw_feature}")
        fig, ax = plt.subplots()
        ax.scatter(fw_vals_physical_wphi, emul_vals_physical_wphi, s=10)
        # 45 degree line
        max_value = max(fw_vals_physical_wphi.max(), emul_vals_physical_wphi.max())
        min_value = min(fw_vals_physical_wphi.min(), emul_vals_physical_wphi.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature} (Physical Wphi)")
        ax.set_ylabel(f"Emul{feature} (Physical Wphi)")
        ax.set_title(f"Fw vs Emul {feature} physical Wphi (Rx Offset: {offset})")
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_physical_wphi.png")
    
    # Unphysical
    disagreement_mask = data_cluster_unphysical_wphi[emul_feature] != data_cluster_unphysical_wphi[fw_feature]
    fw_vals_unphysical_wphi = data_cluster_unphysical_wphi[fw_feature][disagreement_mask].values
    emul_vals_unphysical_wphi = data_cluster_unphysical_wphi[emul_feature][disagreement_mask].values 

    if len(fw_vals_unphysical_wphi) != 0:
        print(f"Plotting disagreement scatter (unphysical Wphi): {emul_feature} vs {fw_feature}")
        fig, ax = plt.subplots()
        ax.scatter(fw_vals_unphysical_wphi, emul_vals_unphysical_wphi, s=10)
        # 45 degree line
        max_value = max(fw_vals_unphysical_wphi.max(), emul_vals_unphysical_wphi.max())
        min_value = min(fw_vals_unphysical_wphi.min(), emul_vals_unphysical_wphi.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature} (Unphysical Wphi)")
        ax.set_ylabel(f"Emul{feature} (Unphysical Wphi)")
        ax.set_title(f"Fw vs Emul {feature} unphysical Wphi (Rx Offset: {offset})")
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_unphysical_wphi.png")

    # Plot both on the same plot
    if (len(fw_vals_physical_wphi) != 0) and (len(fw_vals_unphysical_wphi) != 0):
        fig, ax = plt.subplots()
        ax.scatter(fw_vals_physical_wphi, emul_vals_physical_wphi, s=10, label=r"$\Sigma w\phi_{i}^{2} > (\Sigma w\phi_{i})^2$", color="blue", alpha=0.6)
        ax.scatter(fw_vals_unphysical_wphi, emul_vals_unphysical_wphi, s=10, label=r"$\Sigma w\phi_{i}^{2} \leq (\Sigma w\phi_{i})^2$", color="red", alpha=0.6)
        # 45 degree line
        max_value = max(fw_vals_physical_wphi.max(), emul_vals_physical_wphi.max(), fw_vals_unphysical_wphi.max(), emul_vals_unphysical_wphi.max())
        min_value = min(fw_vals_physical_wphi.min(), emul_vals_physical_wphi.min(), fw_vals_unphysical_wphi.min(), emul_vals_unphysical_wphi.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature}")
        ax.set_ylabel(f"Emul{feature}")
        ax.set_title(f"Fw vs Emul {feature} Wphi (Rx Offset: {offset})")
        ax.legend()
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_physical_vs_unphysical_wphi.png")
    
    # Wro
    # Physical
    disagreement_mask = data_cluster_physical_wro[emul_feature] != data_cluster_physical_wro[fw_feature]
    fw_vals_physical_wro = data_cluster_physical_wro[fw_feature][disagreement_mask].values
    emul_vals_physical_wro = data_cluster_physical_wro[emul_feature][disagreement_mask].values  

    if len(fw_vals_physical_wro) != 0:
        print(f"Plotting disagreement scatter (physical Wro): {emul_feature} vs {fw_feature}")
        fig, ax = plt.subplots()
        ax.scatter(fw_vals_physical_wro, emul_vals_physical_wro, s=10)
        # 45 degree line
        max_value = max(fw_vals_physical_wro.max(), emul_vals_physical_wro.max())
        min_value = min(fw_vals_physical_wro.min(), emul_vals_physical_wro.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature} (Physical Wro)")
        ax.set_ylabel(f"Emul{feature} (Physical Wro)")
        ax.set_title(f"Fw vs Emul {feature} physical Wro (Rx Offset: {offset})")
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_physical_wro.png")   

    # Unphysical
    disagreement_mask = data_cluster_unphysical_wro[emul_feature] != data_cluster_unphysical_wro[fw_feature]
    fw_vals_unphysical_wro = data_cluster_unphysical_wro[fw_feature][disagreement_mask].values
    emul_vals_unphysical_wro = data_cluster_unphysical_wro[emul_feature][disagreement_mask].values

    if len(fw_vals_unphysical_wro) != 0:
        print(f"Plotting disagreement scatter (unphysical Wro): {emul_feature} vs {fw_feature}")
        fig, ax = plt.subplots()
        ax.scatter(fw_vals_unphysical_wro, emul_vals_unphysical_wro, s=10)
        # 45 degree line
        max_value = max(fw_vals_unphysical_wro.max(), emul_vals_unphysical_wro.max())
        min_value = min(fw_vals_unphysical_wro.min(), emul_vals_unphysical_wro.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature} (Unphysical Wro)")
        ax.set_ylabel(f"Emul{feature} (Unphysical Wro)")
        ax.set_title(f"Fw vs Emul {feature} unphysical Wro (Rx Offset: {offset})")
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_unphysical_wro.png")

    # Plot both on the same plot
    if (len(fw_vals_physical_wro) != 0) and (len(fw_vals_unphysical_wro) != 0):
        fig, ax = plt.subplots()
        ax.scatter(fw_vals_physical_wro, emul_vals_physical_wro, s=10, label=r"$\Sigma wr/z_{i}^{2} > (\Sigma wr/z_{i})^2$", color="blue", alpha=0.6)
        ax.scatter(fw_vals_unphysical_wro, emul_vals_unphysical_wro, s=10, label=r"$\Sigma wr/z_{i}^{2} \leq (\Sigma wr/z_{i})^2$", color="red", alpha=0.6)
        # 45 degree line
        max_value = max(fw_vals_physical_wro.max(), emul_vals_physical_wro.max(), fw_vals_unphysical_wro.max(), emul_vals_unphysical_wro.max())
        min_value = min(fw_vals_physical_wro.min(), emul_vals_physical_wro.min(), fw_vals_unphysical_wro.min(), emul_vals_unphysical_wro.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature}")
        ax.set_ylabel(f"Emul{feature}")
        ax.set_title(f"Fw vs Emul {feature} Wro (Rx Offset: {offset})")
        ax.legend()
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_physical_vs_unphysical_wro.png")

    