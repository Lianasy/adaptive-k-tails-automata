import pandas as pd
import matplotlib.pyplot as plt



runs = list(range(1, 11))



# STATE REDUCTION

pta_states = [498, 461, 455, 504, 470, 510, 492, 462, 475, 466]

tail2_v1_states = [100, 103, 88, 106, 106, 113, 107, 101, 106, 111]
tail3_v1_states = [130, 103, 108, 65, 91, 121, 88, 105, 105, 116]

adaptive_states = [107, 101, 108, 65, 102, 118, 88, 74, 109, 116]

tail2_v2_states = [119, 147, 164, 137, 158, 149, 169, 148, 145, 134]
tail3_v2_states = [147, 219, 238, 236, 231, 225, 230, 228, 232, 230]



# BCR

bcr_pta = [0.6833, 0.6667, 0.6556, 0.6778, 0.6944, 0.7111, 0.6833, 0.6500, 0.6500, 0.6556]

bcr_tail2_v1 = [0.8167, 0.7500, 0.7389, 0.7944, 0.7389, 0.7667, 0.7833, 0.7167, 0.7500, 0.7333]
bcr_tail3_v1 = [0.7667, 0.8667, 0.8556, 0.9833, 0.8889, 0.8111, 0.9222, 0.8333, 0.8500, 0.8222]

bcr_adaptive = [0.8000, 0.8000, 0.8556, 0.9833, 0.8000, 0.8444, 0.9222, 0.9000, 0.8167, 0.8222]

bcr_tail2_v2 = [0.5278, 0.5278, 0.5556, 0.6389, 0.5556, 0.6389, 0.5278, 0.5556, 0.5833, 0.6111]
bcr_tail3_v2 = [0.5206, 0.5206, 0.5556, 0.5833, 0.5556, 0.6111, 0.5278, 0.5556, 0.5833, 0.6111]



# TIME

time_tail2_v1 = [14.41, 7.37, 8.54, 13.62, 10.11, 12.73, 13.20, 9.04, 8.30, 8.00]
time_tail3_v1 = [7.64, 3.66, 2.98, 2.36, 3.87, 7.73, 5.62, 3.93, 6.07, 3.01]

time_adaptive = [612.04, 688.61, 501.92, 947.03, 617.60, 841.15, 759.44, 787.42, 481.47, 590.67]

time_tail2_v2 = [0.00763]*10
time_tail3_v2 = [0.00424]*10



# NN

adaptive_nn = [0.7167, 0.7389, 0.7000, 0.7500, 0.6944, 0.7778, 0.7833, 0.7556, 0.7444, 0.7278]
mlp_bcr = [0.7611, 0.7667, 0.7333, 0.7000, 0.7111, 0.7667, 0.7611, 0.7278, 0.7778, 0.7278]



# DATAFRAMES

states_df = pd.DataFrame({
    "Run": runs,
    "PTA": pta_states,
    "2-tail (V1)": tail2_v1_states,
    "3-tail (V1)": tail3_v1_states,
    "Adaptive": adaptive_states,
    "2-tail (V2)": tail2_v2_states,
    "3-tail (V2)": tail3_v2_states
})

bcr_df = pd.DataFrame({
    "Run": runs,
    "PTA": bcr_pta,
    "2-tail (V1)": bcr_tail2_v1,
    "3-tail (V1)": bcr_tail3_v1,
    "Adaptive": bcr_adaptive,
    "2-tail (V2)": bcr_tail2_v2,
    "3-tail (V2)": bcr_tail3_v2
})

time_df = pd.DataFrame({
    "Run": runs,
    "2-tail (V1)": time_tail2_v1,
    "3-tail (V1)": time_tail3_v1,
    "Adaptive": time_adaptive,
    "2-tail (V2)": time_tail2_v2,
    "3-tail (V2)": time_tail3_v2
})

nn_df = pd.DataFrame({
    "Run": runs,
    "Adaptive": adaptive_nn,
    "MLP": mlp_bcr
})



# OUTPUT PRINTING (CLEAN REPORT STYLE)

print("\n================ STATE REDUCTION ================")
print(states_df)
print("\nAVERAGE STATES")
print(states_df.mean(numeric_only=True).to_frame("Avg States"))


print("\n================ BCR ANALYSIS ================")
print(bcr_df)
print("\nAVERAGE BCR")
print(bcr_df.mean(numeric_only=True).to_frame("Avg BCR"))


print("\n================ TIME ANALYSIS ================")
print(time_df)
print("\nAVERAGE TIME")
print(time_df.mean(numeric_only=True).to_frame("Avg Time (s)"))


print("\n================ NN COMPARISON ================")
print(nn_df)
print("\nAVERAGE NN BCR")
print(nn_df.mean(numeric_only=True).to_frame("Avg BCR"))


print("\nALL FILES SAVED SUCCESSFULLY")



# SAVE FILES

states_df.to_csv("states.csv", index=False)
bcr_df.to_csv("bcr.csv", index=False)
time_df.to_csv("time.csv", index=False)
nn_df.to_csv("nn.csv", index=False)



# PLOT

plt.figure(figsize=(10, 5))
plt.plot(runs, bcr_tail2_v1, label="2-tail (V1)")
plt.plot(runs, bcr_tail3_v1, label="3-tail (V1)")
plt.plot(runs, bcr_adaptive, label="Adaptive")
plt.plot(runs, bcr_tail2_v2, label="2-tail (V2)")
plt.plot(runs, bcr_tail3_v2, label="3-tail (V2)")

plt.xlabel("Run")
plt.ylabel("BCR")
plt.title("BCR Comparison Across Methods")

plt.legend()
plt.grid(True)

plt.savefig("bcr_comparison.png")
plt.close()