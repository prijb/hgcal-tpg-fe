# Looks for cases where CeE/CeeECore/CeHEarly are greater than TotE
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

unphysical_cee_mask = (data_accumulator["CeeE"] > data_accumulator["TotE"])
unphysical_ceecore_mask = (data_accumulator["CeeECore"] > data_accumulator["TotE"])
unphysical_cehearly_mask = (data_accumulator["CeHEarly"] > data_accumulator["TotE"])
unphysical_ce_mask = unphysical_cee_mask | unphysical_ceecore_mask | unphysical_cehearly_mask
unphysical_cesum_mask = (data_accumulator["CeSum"] > data_accumulator["TotE"])

print(f"\nNumber of entries: {len(data_accumulator)}")
print(f"Number of unphysical CeE: {np.sum(unphysical_cee_mask)}")
print(f"Number of unphysical CeeECore: {np.sum(unphysical_ceecore_mask)}")
print(f"Number of unphysical CeHEarly: {np.sum(unphysical_cehearly_mask)}")
print(f"Number of unphysical Ce: {np.sum(unphysical_ce_mask)}")
print(f"Number of unphysical CeSum: {np.sum(unphysical_cesum_mask)}")

# Calculate disagreement fractions for physical and unphysical cases
# Ce
data_cluster_physical_ce = data_cluster[~unphysical_ce_mask]
data_cluster_unphysical_ce = data_cluster[unphysical_ce_mask]
total_physical_ce = len(data_cluster_physical_ce)
total_unphysical_ce = len(data_cluster_unphysical_ce)
feature_disagreement_fraction_physical_ce = np.zeros(len(features_cluster))
feature_disagreement_fraction_unphysical_ce = np.zeros(len(features_cluster))

for i_feature, feature in enumerate(features_cluster):
    emul_feature = f"Emul{feature}"
    fw_feature = f"Fw{feature}"

    # Physical cases
    agreements_physical_ce = np.sum(data_cluster_physical_ce[emul_feature].values == data_cluster_physical_ce[fw_feature].values)
    disagreements_physical_ce = np.sum(data_cluster_physical_ce[emul_feature].values != data_cluster_physical_ce[fw_feature].values)
    feature_disagreement_fraction_physical_ce[i_feature] = disagreements_physical_ce / total_physical_ce

    # Unphysical cases
    agreements_unphysical_ce = np.sum(data_cluster_unphysical_ce[emul_feature].values == data_cluster_unphysical_ce[fw_feature].values)
    disagreements_unphysical_ce = np.sum(data_cluster_unphysical_ce[emul_feature].values != data_cluster_unphysical_ce[fw_feature].values)
    feature_disagreement_fraction_unphysical_ce[i_feature] = disagreements_unphysical_ce / total_unphysical_ce

#CeE
data_cluster_physical_cee = data_cluster[~unphysical_cee_mask]
data_cluster_unphysical_cee = data_cluster[unphysical_cee_mask]
total_physical_cee = len(data_cluster_physical_cee)
total_unphysical_cee = len(data_cluster_unphysical_cee)
feature_disagreement_fraction_physical_cee = np.zeros(len(features_cluster))
feature_disagreement_fraction_unphysical_cee = np.zeros(len(features_cluster))

for i_feature, feature in enumerate(features_cluster):
    emul_feature = f"Emul{feature}"
    fw_feature = f"Fw{feature}"

    # Physical cases
    agreements_physical_cee = np.sum(data_cluster_physical_cee[emul_feature].values == data_cluster_physical_cee[fw_feature].values)
    disagreements_physical_cee = np.sum(data_cluster_physical_cee[emul_feature].values != data_cluster_physical_cee[fw_feature].values)
    feature_disagreement_fraction_physical_cee[i_feature] = disagreements_physical_cee / total_physical_cee

    # Unphysical cases
    agreements_unphysical_cee = np.sum(data_cluster_unphysical_cee[emul_feature].values == data_cluster_unphysical_cee[fw_feature].values)
    disagreements_unphysical_cee = np.sum(data_cluster_unphysical_cee[emul_feature].values != data_cluster_unphysical_cee[fw_feature].values)
    feature_disagreement_fraction_unphysical_cee[i_feature] = disagreements_unphysical_cee / total_unphysical_cee
  
# CeeECore
data_cluster_physical_ceecore = data_cluster[~unphysical_ceecore_mask]
data_cluster_unphysical_ceecore = data_cluster[unphysical_ceecore_mask]
total_physical_ceecore = len(data_cluster_physical_ceecore)
total_unphysical_ceecore = len(data_cluster_unphysical_ceecore)
feature_disagreement_fraction_physical_ceecore = np.zeros(len(features_cluster))
feature_disagreement_fraction_unphysical_ceecore = np.zeros(len(features_cluster))

for i_feature, feature in enumerate(features_cluster):
    emul_feature = f"Emul{feature}"
    fw_feature = f"Fw{feature}"

    # Physical cases
    agreements_physical_ceecore = np.sum(data_cluster_physical_ceecore[emul_feature].values == data_cluster_physical_ceecore[fw_feature].values)
    disagreements_physical_ceecore = np.sum(data_cluster_physical_ceecore[emul_feature].values != data_cluster_physical_ceecore[fw_feature].values)
    feature_disagreement_fraction_physical_ceecore[i_feature] = disagreements_physical_ceecore / total_physical_ceecore

    # Unphysical cases
    agreements_unphysical_ceecore = np.sum(data_cluster_unphysical_ceecore[emul_feature].values == data_cluster_unphysical_ceecore[fw_feature].values)
    disagreements_unphysical_ceecore = np.sum(data_cluster_unphysical_ceecore[emul_feature].values != data_cluster_unphysical_ceecore[fw_feature].values)
    feature_disagreement_fraction_unphysical_ceecore[i_feature] = disagreements_unphysical_ceecore / total_unphysical_ceecore

# CeHEarly
data_cluster_physical_ceearly = data_cluster[~unphysical_cehearly_mask]
data_cluster_unphysical_ceearly = data_cluster[unphysical_cehearly_mask]
total_physical_ceearly = len(data_cluster_physical_ceearly)
total_unphysical_ceearly = len(data_cluster_unphysical_ceearly)
feature_disagreement_fraction_physical_ceearly = np.zeros(len(features_cluster))
feature_disagreement_fraction_unphysical_ceearly = np.zeros(len(features_cluster))

for i_feature, feature in enumerate(features_cluster):
    emul_feature = f"Emul{feature}"
    fw_feature = f"Fw{feature}"

    # Physical cases
    agreements_physical_ceearly = np.sum(data_cluster_physical_ceearly[emul_feature].values == data_cluster_physical_ceearly[fw_feature].values)
    disagreements_physical_ceearly = np.sum(data_cluster_physical_ceearly[emul_feature].values != data_cluster_physical_ceearly[fw_feature].values)
    feature_disagreement_fraction_physical_ceearly[i_feature] = disagreements_physical_ceearly / total_physical_ceearly

    # Unphysical cases
    agreements_unphysical_ceearly = np.sum(data_cluster_unphysical_ceearly[emul_feature].values == data_cluster_unphysical_ceearly[fw_feature].values)
    disagreements_unphysical_ceearly = np.sum(data_cluster_unphysical_ceearly[emul_feature].values != data_cluster_unphysical_ceearly[fw_feature].values)
    feature_disagreement_fraction_unphysical_ceearly[i_feature] = disagreements_unphysical_ceearly / total_unphysical_ceearly

# CeSum
data_cluster_physical_cesum = data_cluster[~unphysical_cesum_mask]
data_cluster_unphysical_cesum = data_cluster[unphysical_cesum_mask]
total_physical_cesum = len(data_cluster_physical_cesum)
total_unphysical_cesum = len(data_cluster_unphysical_cesum)
feature_disagreement_fraction_physical_cesum = np.zeros(len(features_cluster))
feature_disagreement_fraction_unphysical_cesum = np.zeros(len(features_cluster))

for i_feature, feature in enumerate(features_cluster):
    emul_feature = f"Emul{feature}"
    fw_feature = f"Fw{feature}"

    # Physical cases
    agreements_physical_cesum = np.sum(data_cluster_physical_cesum[emul_feature].values == data_cluster_physical_cesum[fw_feature].values)
    disagreements_physical_cesum = np.sum(data_cluster_physical_cesum[emul_feature].values != data_cluster_physical_cesum[fw_feature].values)
    feature_disagreement_fraction_physical_cesum[i_feature] = disagreements_physical_cesum / total_physical_cesum

    # Unphysical cases
    agreements_unphysical_cesum = np.sum(data_cluster_unphysical_cesum[emul_feature].values == data_cluster_unphysical_cesum[fw_feature].values)
    disagreements_unphysical_cesum = np.sum(data_cluster_unphysical_cesum[emul_feature].values != data_cluster_unphysical_cesum[fw_feature].values)
    feature_disagreement_fraction_unphysical_cesum[i_feature] = disagreements_unphysical_cesum / total_unphysical_cesum

################### Disagreement fraction ####################
# Plot the disagreement fractions
# Ce
plt.figure()
plt.bar(features_cluster, feature_disagreement_fraction_physical_ce, label=r"$E^{tot} \geq$ CeE, CeECore and CeHEarly", alpha=0.6, color='blue')
plt.bar(features_cluster, feature_disagreement_fraction_unphysical_ce, label=r"$E^{tot} <$ CeE, CeECore or CeHEarly", alpha=0.6, color='red')
plt.xlabel("")
plt.ylabel(f"Disagreement Fraction (Rx Offset: {offset})")
plt.title("Emul-FW Disagreement Fractions (Physical vs Unphysical)")
plt.xticks(rotation=45, ha="right")
plt.legend()
plt.tight_layout()
plt.savefig(f"{args.outdir}/feature_disagreement_fractions_physical_unphysical_ce.png")

# CeE
plt.figure()
plt.bar(features_cluster, feature_disagreement_fraction_physical_cee, label=r"$E^{tot} \geq$ CeE", alpha=0.6, color='blue')
plt.bar(features_cluster, feature_disagreement_fraction_unphysical_cee, label=r"$E^{tot} <$ CeE", alpha=0.6, color='red')
plt.xlabel("")
plt.ylabel(f"Disagreement Fraction (Rx Offset: {offset})")
plt.title("Emul-FW Disagreement Fractions (Physical vs Unphysical CeE)")
plt.xticks(rotation=45, ha="right")
plt.legend()
plt.tight_layout()
plt.savefig(f"{args.outdir}/feature_disagreement_fractions_physical_unphysical_cee.png")

# CeeECore
plt.figure()
plt.bar(features_cluster, feature_disagreement_fraction_physical_ceecore, label=r"$E^{tot} \geq$ CeeECore", alpha=0.6, color='blue')
plt.bar(features_cluster, feature_disagreement_fraction_unphysical_ceecore, label=r"$E^{tot} <$ CeeECore", alpha=0.6, color='red')
plt.xlabel("")
plt.ylabel(f"Disagreement Fraction (Rx Offset: {offset})")
plt.title("Emul-FW Disagreement Fractions (Physical vs Unphysical CeeECore)")
plt.xticks(rotation=45, ha="right")
plt.legend()
plt.tight_layout()
plt.savefig(f"{args.outdir}/feature_disagreement_fractions_physical_unphysical_ceecore.png")

# CeHEarly
plt.figure()
plt.bar(features_cluster, feature_disagreement_fraction_physical_ceearly, label=r"$E^{tot} \geq$ CeHEarly", alpha=0.6, color='blue')
plt.bar(features_cluster, feature_disagreement_fraction_unphysical_ceearly, label=r"$E^{tot} <$ CeHEarly", alpha=0.6, color='red')
plt.xlabel("")
plt.ylabel(f"Disagreement Fraction (Rx Offset: {offset})")
plt.title("Emul-FW Disagreement Fractions (Physical vs Unphysical CeHEarly)")
plt.xticks(rotation=45, ha="right")
plt.legend()
plt.tight_layout()
plt.savefig(f"{args.outdir}/feature_disagreement_fractions_physical_unphysical_ceearly.png")

# CeSum
plt.figure()
plt.bar(features_cluster, feature_disagreement_fraction_physical_cesum, label=r"$E^{tot} \geq$ CeSum", alpha=0.6, color='blue')
plt.bar(features_cluster, feature_disagreement_fraction_unphysical_cesum, label=r"$E^{tot} <$ CeSum", alpha=0.6, color='red')
plt.xlabel("")
plt.ylabel(f"Disagreement Fraction (Rx Offset: {offset})")
plt.title("Emul-FW Disagreement Fractions (Physical vs Unphysical CeSum)")
plt.xticks(rotation=45, ha="right")
plt.legend()
plt.tight_layout()
plt.savefig(f"{args.outdir}/feature_disagreement_fractions_physical_unphysical_cesum.png")

################### Scatter plots ####################
# Make scatter plots only for cases of disagreement (Fw vs Emul)
os.makedirs(f"{args.outdir}/scatter", exist_ok=True)

for feature in features_cluster:
    emul_feature = f"Emul{feature}"
    fw_feature = f"Fw{feature}"

    # Ce disagreement
    # Physical
    disagreement_mask = (data_cluster_physical_ce[emul_feature].values != data_cluster_physical_ce[fw_feature].values)
    fw_vals_physical = data_cluster_physical_ce[fw_feature][disagreement_mask].values
    emul_vals_physical = data_cluster_physical_ce[emul_feature][disagreement_mask].values
    
    if len(fw_vals_physical) != 0:
        print(f"Plotting disagreement scatter (physical) Ce: {emul_feature} vs {fw_feature}")
        fig, ax = plt.subplots()
        ax.scatter(fw_vals_physical, emul_vals_physical, s=10)
        # 45 degree line
        max_value = max(fw_vals_physical.max(), emul_vals_physical.max())
        min_value = min(fw_vals_physical.min(), emul_vals_physical.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature} (Physical)")
        ax.set_ylabel(f"Emul{feature} (Physical)")
        ax.set_title(f"Fw vs Emul {feature} physical Ce (Rx Offset: {offset})")
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_physical_ce.png")

    # Unphysical
    disagreement_mask = (data_cluster_unphysical_ce[emul_feature].values != data_cluster_unphysical_ce[fw_feature].values)
    fw_vals_unphysical = data_cluster_unphysical_ce[fw_feature][disagreement_mask].values
    emul_vals_unphysical = data_cluster_unphysical_ce[emul_feature][disagreement_mask].values

    if len(fw_vals_unphysical) != 0:
        print(f"Plotting disagreement scatter (unphysical) Ce: {emul_feature} vs {fw_feature}")
        fig, ax = plt.subplots()
        ax.scatter(fw_vals_unphysical, emul_vals_unphysical, s=10)
        # 45 degree line
        max_value = max(fw_vals_unphysical.max(), emul_vals_unphysical.max())
        min_value = min(fw_vals_unphysical.min(), emul_vals_unphysical.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature} (Unphysical)")
        ax.set_ylabel(f"Emul{feature} (Unphysical)")
        ax.set_title(f"Fw vs Emul {feature} unphysical Ce (Rx Offset: {offset})")
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_unphysical_ce.png")

    # CeE disagreement
    # Physical
    disagreement_mask = (data_cluster_physical_cee[emul_feature].values != data_cluster_physical_cee[fw_feature].values)
    fw_vals_physical = data_cluster_physical_cee[fw_feature][disagreement_mask].values
    emul_vals_physical = data_cluster_physical_cee[emul_feature][disagreement_mask].values

    if len(fw_vals_physical) != 0:
        print(f"Plotting disagreement scatter (physical) CeE: {emul_feature} vs {fw_feature}")
        fig, ax = plt.subplots()
        ax.scatter(fw_vals_physical, emul_vals_physical, s=10)
        # 45 degree line
        max_value = max(fw_vals_physical.max(), emul_vals_physical.max())
        min_value = min(fw_vals_physical.min(), emul_vals_physical.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature} (Physical)")
        ax.set_ylabel(f"Emul{feature} (Physical)")
        ax.set_title(f"Fw vs Emul {feature} physical CeE (Rx Offset: {offset})")
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_physical_cee.png")

    # Unphysical
    disagreement_mask = (data_cluster_unphysical_cee[emul_feature].values != data_cluster_unphysical_cee[fw_feature].values)
    fw_vals_unphysical = data_cluster_unphysical_cee[fw_feature][disagreement_mask].values
    emul_vals_unphysical = data_cluster_unphysical_cee[emul_feature][disagreement_mask].values

    if len(fw_vals_unphysical) != 0:
        print(f"Plotting disagreement scatter (unphysical) CeE: {emul_feature} vs {fw_feature}")
        fig, ax = plt.subplots()
        ax.scatter(fw_vals_unphysical, emul_vals_unphysical, s=10)
        # 45 degree line
        max_value = max(fw_vals_unphysical.max(), emul_vals_unphysical.max())
        min_value = min(fw_vals_unphysical.min(), emul_vals_unphysical.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature} (Unphysical)")
        ax.set_ylabel(f"Emul{feature} (Unphysical)")
        ax.set_title(f"Fw vs Emul {feature} unphysical CeE (Rx Offset: {offset})")
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_unphysical_cee.png")

    # CeeECore disagreement
    # Physical
    disagreement_mask = (data_cluster_physical_ceecore[emul_feature].values != data_cluster_physical_ceecore[fw_feature].values)
    fw_vals_physical = data_cluster_physical_ceecore[fw_feature][disagreement_mask].values
    emul_vals_physical = data_cluster_physical_ceecore[emul_feature][disagreement_mask].values  

    if len(fw_vals_physical) != 0:
        print(f"Plotting disagreement scatter (physical) CeeECore: {emul_feature} vs {fw_feature}")
        fig, ax = plt.subplots()
        ax.scatter(fw_vals_physical, emul_vals_physical, s=10)
        # 45 degree line
        max_value = max(fw_vals_physical.max(), emul_vals_physical.max())
        min_value = min(fw_vals_physical.min(), emul_vals_physical.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature} (Physical)")
        ax.set_ylabel(f"Emul{feature} (Physical)")
        ax.set_title(f"Fw vs Emul {feature} physical CeeECore (Rx Offset: {offset})")
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_physical_ceecore.png")

    # Unphysical
    disagreement_mask = (data_cluster_unphysical_ceecore[emul_feature].values != data_cluster_unphysical_ceecore[fw_feature].values)
    fw_vals_unphysical = data_cluster_unphysical_ceecore[fw_feature][disagreement_mask].values
    emul_vals_unphysical = data_cluster_unphysical_ceecore[emul_feature][disagreement_mask].values

    if len(fw_vals_unphysical) != 0:
        print(f"Plotting disagreement scatter (unphysical) CeeECore: {emul_feature} vs {fw_feature}")
        fig, ax = plt.subplots()
        ax.scatter(fw_vals_unphysical, emul_vals_unphysical, s=10)
        # 45 degree line
        max_value = max(fw_vals_unphysical.max(), emul_vals_unphysical.max())
        min_value = min(fw_vals_unphysical.min(), emul_vals_unphysical.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature} (Unphysical)")
        ax.set_ylabel(f"Emul{feature} (Unphysical)")
        ax.set_title(f"Fw vs Emul {feature} unphysical CeeECore (Rx Offset: {offset})")
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_unphysical_ceecore.png")

    # CeHEarly disagreement
    # Physical
    disagreement_mask = (data_cluster_physical_ceearly[emul_feature].values != data_cluster_physical_ceearly[fw_feature].values)
    fw_vals_physical = data_cluster_physical_ceearly[fw_feature][disagreement_mask].values
    emul_vals_physical = data_cluster_physical_ceearly[emul_feature][disagreement_mask].values

    if len(fw_vals_physical) != 0:
        print(f"Plotting disagreement scatter (physical) CeHEarly: {emul_feature} vs {fw_feature}")
        fig, ax = plt.subplots()
        ax.scatter(fw_vals_physical, emul_vals_physical, s=10)
        # 45 degree line
        max_value = max(fw_vals_physical.max(), emul_vals_physical.max())
        min_value = min(fw_vals_physical.min(), emul_vals_physical.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature} (Physical)")
        ax.set_ylabel(f"Emul{feature} (Physical)")
        ax.set_title(f"Fw vs Emul {feature} physical CeHEarly (Rx Offset: {offset})")
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_physical_ceearly.png")

    # Unphysical
    disagreement_mask = (data_cluster_unphysical_ceearly[emul_feature].values != data_cluster_unphysical_ceearly[fw_feature].values)
    fw_vals_unphysical = data_cluster_unphysical_ceearly[fw_feature][disagreement_mask].values
    emul_vals_unphysical = data_cluster_unphysical_ceearly[emul_feature][disagreement_mask].values

    if len(fw_vals_unphysical) != 0:
        print(f"Plotting disagreement scatter (unphysical) CeHEarly: {emul_feature} vs {fw_feature}")
        fig, ax = plt.subplots()
        ax.scatter(fw_vals_unphysical, emul_vals_unphysical, s=10)
        # 45 degree line
        max_value = max(fw_vals_unphysical.max(), emul_vals_unphysical.max())
        min_value = min(fw_vals_unphysical.min(), emul_vals_unphysical.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature} (Unphysical)")
        ax.set_ylabel(f"Emul{feature} (Unphysical)")
        ax.set_title(f"Fw vs Emul {feature} unphysical CeHEarly (Rx Offset: {offset})")
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_unphysical_ceearly.png")

    # CeSum disagreement
    # Physical
    disagreement_mask = (data_cluster_physical_cesum[emul_feature].values != data_cluster_physical_cesum[fw_feature].values)
    fw_vals_physical = data_cluster_physical_cesum[fw_feature][disagreement_mask].values
    emul_vals_physical = data_cluster_physical_cesum[emul_feature][disagreement_mask].values

    if len(fw_vals_physical) != 0:
        print(f"Plotting disagreement scatter (physical) CeSum: {emul_feature} vs {fw_feature}")
        fig, ax = plt.subplots()
        ax.scatter(fw_vals_physical, emul_vals_physical, s=10)
        # 45 degree line
        max_value = max(fw_vals_physical.max(), emul_vals_physical.max())
        min_value = min(fw_vals_physical.min(), emul_vals_physical.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature} (Physical)")
        ax.set_ylabel(f"Emul{feature} (Physical)")
        ax.set_title(f"Fw vs Emul {feature} physical CeSum (Rx Offset: {offset})")
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_physical_cesum.png")

    # Unphysical
    disagreement_mask = (data_cluster_unphysical_cesum[emul_feature].values != data_cluster_unphysical_cesum[fw_feature].values)
    fw_vals_unphysical = data_cluster_unphysical_cesum[fw_feature][disagreement_mask].values
    emul_vals_unphysical = data_cluster_unphysical_cesum[emul_feature][disagreement_mask].values

    if len(fw_vals_unphysical) != 0:
        print(f"Plotting disagreement scatter (unphysical) CeSum: {emul_feature} vs {fw_feature}")
        fig, ax = plt.subplots()
        ax.scatter(fw_vals_unphysical, emul_vals_unphysical, s=10)
        # 45 degree line
        max_value = max(fw_vals_unphysical.max(), emul_vals_unphysical.max())
        min_value = min(fw_vals_unphysical.min(), emul_vals_unphysical.min())
        ax.plot([min_value, max_value], [min_value, max_value], color='black', linestyle='--')
        ax.set_xlabel(f"Fw{feature} (Unphysical)")
        ax.set_ylabel(f"Emul{feature} (Unphysical)")
        ax.set_title(f"Fw vs Emul {feature} unphysical CeSum (Rx Offset: {offset})")
        plt.savefig(f"{args.outdir}/scatter/{fw_feature}_vs_{emul_feature}_unphysical_cesum.png")