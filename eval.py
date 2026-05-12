import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import wilcoxon

runs = list(range(1, 11))


# STATE REDUCTION

pta_states = [498, 461, 455, 504, 470, 510, 492, 462, 475, 466]

tail2_v1_states = [100, 103, 88, 106, 106,
                   113, 107, 101, 106, 111]

tail3_v1_states = [130, 103, 108, 65, 91,
                   121, 88, 105, 105, 116]

adaptive_states = [107, 101, 108, 65, 102,
                   118, 88, 74, 109, 116]

tail2_v2_states = [119, 147, 164, 137, 158,
                   149, 169, 148, 145, 134]

tail3_v2_states = [147, 219, 238, 236, 231,
                   225, 230, 228, 232, 230]


# BCR


bcr_pta = [0.6833, 0.6667, 0.6556, 0.6778, 0.6944,
           0.7111, 0.6833, 0.6500, 0.6500, 0.6556]

bcr_tail2_v1 = [0.8167, 0.7500, 0.7389, 0.7944, 0.7389,
                0.7667, 0.7833, 0.7167, 0.7500, 0.7333]

bcr_tail3_v1 = [0.7667, 0.8667, 0.8556, 0.9833, 0.8889,
                0.8111, 0.9222, 0.8333, 0.8500, 0.8222]

bcr_adaptive = [0.8000, 0.8000, 0.8556, 0.9833, 0.8000,
                0.8444, 0.9222, 0.9000, 0.8167, 0.8222]

bcr_tail2_v2 = [0.5278, 0.5278, 0.5556, 0.6389, 0.5556,
                0.6389, 0.5278, 0.5556, 0.5833, 0.6111]

bcr_tail3_v2 = [0.5206, 0.5206, 0.5556, 0.5833, 0.5556,
                0.6111, 0.5278, 0.5556, 0.5833, 0.6111]


# TIME


time_tail2_v1 = [14.41, 7.37, 8.54, 13.62, 10.11,
                 12.73, 13.20, 9.04, 8.30, 8.00]

time_tail3_v1 = [7.64, 3.66, 2.98, 2.36, 3.87,
                 7.73, 5.62, 3.93, 6.07, 3.01]

time_adaptive = [612.04, 688.61, 501.92, 947.03, 617.60,
                 841.15, 759.44, 787.42, 481.47, 590.67]

time_tail2_v2 = [0.00763] * 10
time_tail3_v2 = [0.00424] * 10


# NEURAL NETWORK RESULTS


# Adaptive NN
adaptive_nn = [0.7167, 0.7389, 0.7000, 0.7500, 0.6944,
               0.7778, 0.7833, 0.7556, 0.7444, 0.7278]

# Multi-model MLP
multi_mlp = [0.7611, 0.7667, 0.7333, 0.7000, 0.7111,
             0.7667, 0.7611, 0.7278, 0.7778, 0.7278]

# Single-model MLP
single_mlp = [0.7722, 0.7667, 0.7389, 0.7056, 0.7389,
              0.7722, 0.7556, 0.7111, 0.7278, 0.7111]

# DATAFRAMES


states_df = pd.DataFrame({
    "Run": runs,
    "PTA": pta_states,
    "2-tail V1": tail2_v1_states,
    "3-tail V1": tail3_v1_states,
    "Adaptive": adaptive_states,
    "2-tail V2": tail2_v2_states,
    "3-tail V2": tail3_v2_states
})

bcr_df = pd.DataFrame({
    "Run": runs,
    "PTA": bcr_pta,
    "2-tail V1": bcr_tail2_v1,
    "3-tail V1": bcr_tail3_v1,
    "Adaptive": bcr_adaptive,
    "2-tail V2": bcr_tail2_v2,
    "3-tail V2": bcr_tail3_v2
})

time_df = pd.DataFrame({
    "Run": runs,
    "2-tail V1": time_tail2_v1,
    "3-tail V1": time_tail3_v1,
    "Adaptive": time_adaptive,
    "2-tail V2": time_tail2_v2,
    "3-tail V2": time_tail3_v2
})

nn_df = pd.DataFrame({
    "Run": runs,
    "Adaptive NN": adaptive_nn,
    "Single-model MLP": single_mlp,
    "Multi-model MLP": multi_mlp
})


# PRINT TABLES


print("\nSTATE REDUCTION")
print(states_df)

print("\nAVERAGE STATES")
print(states_df.mean(numeric_only=True))

print("\nBCR")
print(bcr_df)

print("\nAVERAGE BCR")
print(bcr_df.mean(numeric_only=True))

print("\nTIME")
print(time_df)

print("\nAVERAGE TIME")
print(time_df.mean(numeric_only=True))

print("\nNEURAL NETWORK RESULTS")
print(nn_df)

print("\nAVERAGE NN")
print(nn_df.mean(numeric_only=True))


# EFFECT SIZE (A12)


def a12(lst1, lst2):

    more = 0.0
    same = 0.0

    for x in lst1:
        for y in lst2:

            if x > y:
                more += 1

            elif x == y:
                same += 1

    return (more + 0.5 * same) / (len(lst1) * len(lst2))


# STATISTICAL TEST FUNCTION


def statistical_test(name1, data1, name2, data2):

    stat, p = wilcoxon(data1, data2)

    effect = a12(data1, data2)

    print("\n")
    print(f"{name1} vs {name2}")
    print("")

    print("Wilcoxon statistic :", stat)
    print("p-value            :", round(p, 6))
    print("A12 effect size    :", round(effect, 4))

    if p < 0.05:
        print("Result             : Statistically significant")
    else:
        print("Result             : NOT statistically significant")


# REQUIRED HYPOTHESIS TESTS




statistical_test(
    "k-tail (k=2)",
    bcr_tail2_v1,
    "Adaptive",
    bcr_adaptive
)



statistical_test(
    "Adaptive",
    adaptive_nn,
    "Multi-model MLP",
    multi_mlp
)



statistical_test(
    "Adaptive",
    adaptive_nn,
    "Single-model MLP",
    single_mlp
)



statistical_test(
    "Multi-model MLP",
    multi_mlp,
    "Single-model MLP",
    single_mlp
)



statistical_test(
    "k-tail (k=2)",
    bcr_tail2_v1,
    "Multi-model MLP",
    multi_mlp
)



statistical_test(
    "k-tail (k=2)",
    bcr_tail2_v1,
    "Single-model MLP",
    single_mlp
)



states_df.to_csv("states.csv", index=False)
bcr_df.to_csv("bcr.csv", index=False)
time_df.to_csv("time.csv", index=False)
nn_df.to_csv("nn.csv", index=False)



plt.figure()

plt.plot(runs, bcr_tail2_v1, label="2-tail V1")
plt.plot(runs, bcr_tail3_v1, label="3-tail V1")
plt.plot(runs, bcr_adaptive, label="Adaptive")
plt.plot(runs, bcr_tail2_v2, label="2-tail V2")
plt.plot(runs, bcr_tail3_v2, label="3-tail V2")

plt.title("BCR Comparison")
plt.xlabel("Run")
plt.ylabel("BCR")

plt.legend()
plt.grid()

plt.savefig("bcr_line.png")
plt.close()



plt.figure()

plt.boxplot([
    pta_states,
    tail2_v1_states,
    tail3_v1_states,
    adaptive_states,
    tail2_v2_states,
    tail3_v2_states
],
tick_labels=["PTA", "2V1", "3V1", "Adaptive", "2V2", "3V2"])

plt.title("State Reduction Comparison")

plt.savefig("states_boxplot.png")
plt.close()



plt.figure()

plt.boxplot([
    bcr_pta,
    bcr_tail2_v1,
    bcr_tail3_v1,
    bcr_adaptive,
    bcr_tail2_v2,
    bcr_tail3_v2
],
tick_labels=["PTA", "2V1", "3V1", "Adaptive", "2V2", "3V2"])

plt.title("BCR Comparison")

plt.savefig("bcr_boxplot.png")
plt.close()


plt.figure()

plt.boxplot([
    time_tail2_v1,
    time_tail3_v1,
    time_tail2_v2,
    time_tail3_v2
],
tick_labels=["2V1", "3V1", "Adaptive", "2V2", "3V2"])

plt.title("Execution Time Comparison")

plt.savefig("time_boxplot.png")
plt.close()

plt.figure()

plt.boxplot(
    [adaptive_nn, single_mlp, multi_mlp],
    tick_labels=["Adaptive", "Single MLP", "Multi MLP"]
)

plt.title("Neural Network Comparison")

plt.savefig("nn_boxplot.png")
plt.close()


print("\nALL OUTPUTS GENERATED SUCCESSFULLY")