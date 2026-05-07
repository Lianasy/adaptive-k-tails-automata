import pandas as pd
import matplotlib.pyplot as plt

# =========================================================
# FINAL REPORT ANALYSIS CODE
# Adaptive k-tail vs Traditional k-tail vs MLP
# =========================================================

# =========================================================
# 1. INPUT DATA
# =========================================================

runs = list(range(1, 11))

# -------------------------
# NUMBER OF STATES
# -------------------------
pta_states = [498, 461, 455, 504, 470, 510, 492, 462, 475, 466]

tail2_states = [100, 103, 88, 106, 106, 113, 107, 101, 106, 111]

tail3_states = [130, 103, 108, 65, 91, 121, 88, 105, 105, 116]

adaptive_states = [107, 101, 108, 65, 102, 118, 88, 74, 109, 116]


# -------------------------
# BCR RESULTS
# -------------------------
bcr_pta = [
    0.6833, 0.6667, 0.6556, 0.6778, 0.6944,
    0.7111, 0.6833, 0.6500, 0.6500, 0.6556
]

bcr_2tail = [
    0.8167, 0.7500, 0.7389, 0.7944, 0.7389,
    0.7667, 0.7833, 0.7167, 0.7500, 0.7333
]

bcr_3tail = [
    0.7667, 0.8667, 0.8556, 0.9833, 0.8889,
    0.8111, 0.9222, 0.8333, 0.8500, 0.8222
]

bcr_adaptive = [
    0.8000, 0.8000, 0.8556, 0.9833, 0.8000,
    0.8444, 0.9222, 0.9000, 0.8167, 0.8222
]


# -------------------------
# EXECUTION TIME
# -------------------------
time_2tail = [
    14.41, 7.37, 8.54, 13.62, 10.11,
    12.73, 13.20, 9.04, 8.30, 8.00
]

time_3tail = [
    7.64, 3.66, 2.98, 2.36, 3.87,
    7.73, 5.62, 3.93, 6.07, 3.01
]

time_adaptive = [
    612.04, 688.61, 501.92, 947.03, 617.60,
    841.15, 759.44, 787.42, 481.47, 590.67
]


# -------------------------
# NN vs ADAPTIVE (10-state)
# -------------------------
adaptive_nn = [
    0.7167, 0.7389, 0.7000, 0.7500, 0.6944,
    0.7778, 0.7833, 0.7556, 0.7444, 0.7278
]

mlp_bcr = [
    0.7611, 0.7667, 0.7333, 0.7000, 0.7111,
    0.7667, 0.7611, 0.7278, 0.7778, 0.7278
]


# =========================================================
# 2. CREATE DATAFRAMES
# =========================================================

states_df = pd.DataFrame({
    "Run": runs,
    "PTA": pta_states,
    "2-tail": tail2_states,
    "3-tail": tail3_states,
    "Adaptive": adaptive_states
})

bcr_df = pd.DataFrame({
    "Run": runs,
    "PTA": bcr_pta,
    "2-tail": bcr_2tail,
    "3-tail": bcr_3tail,
    "Adaptive": bcr_adaptive
})

time_df = pd.DataFrame({
    "Run": runs,
    "2-tail": time_2tail,
    "3-tail": time_3tail,
    "Adaptive": time_adaptive
})

nn_df = pd.DataFrame({
    "Run": runs,
    "Adaptive": adaptive_nn,
    "MLP": mlp_bcr
})


# =========================================================
# 3. STATE REDUCTION ANALYSIS
# =========================================================

print("\n================================================")
print("STATE REDUCTION ANALYSIS")
print("================================================")
print(states_df)

print("\nAVERAGE NUMBER OF STATES")
print(states_df[["PTA", "2-tail", "3-tail", "Adaptive"]].mean())


# =========================================================
# 4. BCR ANALYSIS
# =========================================================

print("\n================================================")
print("BCR ANALYSIS")
print("================================================")
print(bcr_df)

print("\nAVERAGE BCR")
print(bcr_df[["PTA", "2-tail", "3-tail", "Adaptive"]].mean())


# =========================================================
# 5. TIME ANALYSIS
# =========================================================

print("\n================================================")
print("TIME ANALYSIS")
print("================================================")
print(time_df)

print("\nAVERAGE EXECUTION TIME")
print(time_df[["2-tail", "3-tail", "Adaptive"]].mean())


# =========================================================
# 6. NN vs ADAPTIVE ANALYSIS
# =========================================================

print("\n================================================")
print("NN vs ADAPTIVE (10-state)")
print("================================================")
print(nn_df)

print("\nAVERAGE BCR (NN COMPARISON)")
print(nn_df[["Adaptive", "MLP"]].mean())


# =========================================================
# 7. EXTRA RESULTS PROVIDED BY TEAMMATE
# =========================================================

extra_results = pd.DataFrame({
    "Dataset": [
        "automaton_10_2_5",
        "automaton_10_2_5",
        "automaton_5_2_2",
        "automaton_5_2_2"
    ],
    "k": [2, 3, 2, 3],
    "N": [1000, 1000, 1001, 1001],
    "BCR": [0.6111, 0.5206, 0.7063, 0.6252],
    "Sensitivity": [0.2513, 0.0437, 0.9106, 0.2958],
    "Specificity": [0.9709, 0.9976, 0.5019, 0.9547],
    "States": [103.2, 191.0, 4.6, 50.4],
    "Time(s)": [0.0068, 0.0042, 0.0018, 0.0015]
})

print("\n================================================")
print("ADDITIONAL DATASET RESULTS")
print("================================================")
print(extra_results)


# =========================================================
# 8. FINAL LINE GRAPH (BCR)
# =========================================================

plt.figure(figsize=(10, 5))

plt.plot(runs, bcr_2tail, marker='o', label="2-tail")
plt.plot(runs, bcr_3tail, marker='s', label="3-tail")
plt.plot(runs, bcr_adaptive, marker='^', label="Adaptive")

plt.xlabel("Run Number")
plt.ylabel("BCR Score")
plt.title("BCR Comparison Across Runs")

plt.legend()
plt.grid(True)

plt.savefig("bcr_comparison.png")
plt.close()

# =========================================================
# 9. SAVE TABLES FOR REPORT
# =========================================================

states_df.to_csv("states_analysis.csv", index=False)
bcr_df.to_csv("bcr_analysis.csv", index=False)
time_df.to_csv("time_analysis.csv", index=False)
nn_df.to_csv("nn_analysis.csv", index=False)
extra_results.to_csv("extra_dataset_results.csv", index=False)

print("\n================================================")
print("ALL ANALYSIS FILES SAVED SUCCESSFULLY")
print("================================================")