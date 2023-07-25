#!/usr/bin/env python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def bin_data(reco_data, sim_data, bins, quant=68, logspace=True):
    """
    reco_data: energy distribution of reconstructed events or after cut. as np.array
    reco_data: energy distribution of reconstructed events or after cut. as np.array
    
    return: return the bin centers, and ratio of passing (triggers, reco, cut) to simulated.
    bins : Number of bins. Shoud be an interger not a list.
    """
    if logspace:
        bins = np.logspace(np.log10(np.min(reco_data)), np.log10(np.max(reco_data)), bins)
    else:
        bins = np.linspace(np.min(reco_data), np.max(reco_data), bins)

    hist1, bin_edges1 = np.histogram(reco_data, bins=bins)
    hist2, bin_edges2 = np.histogram(sim_data, bins=bins)
    ratio = np.divide(hist1, hist2, where=(hist2 !=0))
    
    print(f'# reco event: {hist1} events')
    print(f'# sim events: {hist2} events')
    print(f'# efficiency: {np.round(ratio, 3)} events')
    
    centers = (bins[1:] + bins[:-1]) / 2.0

    return (
        np.array(centers),
        np.array(ratio)
    )
# ----------------------------------------------------------------------

df = pd.read_csv('likelihood_mmsreco_16pmts_mc_truth_seed_70str_standard_unclean_selection.csv', index_col=False)

df2 = pd.read_csv('simulation_sim0005_triggered_16pmts_mc_truth_seed_70str_standard_unclean_selection.csv')

# Checking NaN on entire DataFrame
print(df.isnull().values.any())
# Counte NaN on entire DataFrame
#df = df.dropna(subset=['dirTrackLengthA_reco'])
print(df.isnull().sum())

print('\n')

# Checking NaN on entire DataFrame
print(df2.isnull().values.any())
# Counte NaN on entire DataFrame
print(df2.isnull().sum())

bins = 11
energy_min = 1e3
energy_max = 1e6

df = df.loc[(df['muon_energy'] >= energy_min)]
df2 = df2.loc[(df2['muon_energy'] >= energy_min)]
# Make reference using LDirA > 0 as denominator
#df2 = df.loc[(df['dirTrackLengthA_reco'] > 0)]

# ----------------------------------------------------------------------

plt.figure(dpi=300)
# Efficiency vs muon energy
for LDir in [0, 100, 200, 400, 700]:
    data = df.loc[(df['dirTrackLengthA_reco'] > LDir)]
    reco_energy = data.muon_energy
    sim_energy = df2.muon_energy
    bin_centers, efficiency = bin_data(
        reco_energy, sim_energy, bins=bins, logspace=True
    )
    print('\n\n')
    plt.plot(bin_centers, efficiency, "-", label=f'LDirA > {LDir} m')
plt.xlabel("Muon energy [GeV]")
plt.ylabel("Efficiency")
plt.ylim(0, 1.0)
plt.xlim(energy_min, energy_max)
plt.xscale("log")
plt.grid(b=None, which="both", axis="both", linestyle="--", linewidth=0.3)
plt.legend()
plt.savefig("mmsreco_angular_error_efficiency.png")
plt.show()

# ----------------------------------------------------------------------

bins = 11
bins = np.logspace(np.log10(np.min(df2.muon_energy)), 
                   np.log10(np.max(df2.muon_energy)), bins)
plt.figure(dpi=300)
plt.hist(df2.muon_energy, bins=bins)
plt.xlabel("Muon energy [GeV]")
plt.ylabel("Counts")
plt.xscale('log')
plt.grid(b=None, which="both", axis="both", linestyle="--", linewidth=0.3)
plt.savefig("mmsreco_event_energy_distribution.png")
plt.show()