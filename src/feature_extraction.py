import os
import json
import numpy as np
from collections import defaultdict
import math
import pandas as pd

# LOAD PTA

def load_pta(path):
    with open(path, 'r') as f:
        return json.load(f)


# BUILD GRAPH

def build_graph(pta):
    transitions = {}
    incoming = defaultdict(list)

    for state in pta:
        s = state["state_id"]
        transitions[s] = []

        for label, target in state["T"]:
            t = int(target.replace("S", ""))
            transitions[s].append((label, t))
            incoming[t].append((label, s))

    return transitions, incoming


# DEPTH

def compute_depths(transitions, start=0):
    depths = {start: 0}
    stack = [start]

    while stack:
        node = stack.pop()

        for _, nxt in transitions[node]:
            if nxt not in depths:
                depths[nxt] = depths[node] + 1
                stack.append(nxt)

    return depths


# SYMBOL ORDER FIX

def get_alphabet(transitions):
    symbols = set()

    for s in transitions:
        for label, _ in transitions[s]:
            symbols.add(label)

    return sorted(list(symbols))


# FEATURE EXTRACTION

def extract_features_from_pta(pta, global_alphabet=None):
    transitions, incoming = build_graph(pta)

    num_states = len(pta)

    #  depth
    depths = compute_depths(transitions)
    avg_depth = np.mean(list(depths.values()))
    max_depth = np.max(list(depths.values()))

    #  branching
    branching = [len(transitions[s]) for s in transitions]
    avg_branching = np.mean(branching)

    # accept
    accepted = [1 if s["accepted"] == "Y" else 0 for s in pta]
    accept_ratio = np.mean(accepted)

    # alphabet
    if global_alphabet is None:
        alphabet = get_alphabet(transitions)
    else:
        alphabet = global_alphabet

    #  symbol stats
    symbol_counts = defaultdict(int)
    symbol_successors = defaultdict(list)

    for s in transitions:
        for label, nxt in transitions[s]:
            symbol_counts[label] += 1
            symbol_successors[label].append(nxt)

    total_transitions = sum(symbol_counts.values()) + 1e-8

    symbol_features = []

    for symbol in alphabet:

        freq = symbol_counts[symbol] / total_transitions

        successors = symbol_successors[symbol]

        if len(successors) == 0:
            unique_successors = 0
            entropy = 0
        else:
            unique_successors = len(set(successors))

            counts = defaultdict(int)
            for s in successors:
                counts[s] += 1

            probs = [c / len(successors) for c in counts.values()]
            entropy = -sum(p * math.log(p + 1e-8) for p in probs)

        symbol_features.extend([
            freq,
            unique_successors,
            entropy
        ])

    # final vector
    features = [
        num_states,
        avg_depth,
        max_depth,
        avg_branching,
        accept_ratio
    ]

    features.extend(symbol_features)

    return np.array(features, dtype=np.float32)
def get_feature_names(alphabet):
    feature_names = [
        "num_states",
        "avg_depth",
        "max_depth",
        "avg_branching",
        "accept_ratio"
    ]

    for symbol in alphabet:
        feature_names.extend([
            f"{symbol}_freq",
            f"{symbol}_unique_successors",
            f"{symbol}_entropy"
        ])

    return feature_names

def build_dataset_with_labels(folder_path):
    X = []
    y = []

    files = os.listdir(folder_path)

    pta_files = [f for f in files if f.endswith("_PTA.json")]

    global_symbols = set()

    for file in pta_files:
        pta = load_pta(os.path.join(folder_path, file))
        transitions, _ = build_graph(pta)

        for s in transitions:
            for label, _ in transitions[s]:
                global_symbols.add(label)

    global_alphabet = sorted(list(global_symbols))

    for pta_file in pta_files:

        base_name = pta_file.replace("_PTA.json", "")
        kv_file = base_name + "_optimal_kv.json"

        kv_path = os.path.join(folder_path, kv_file)

        if not os.path.exists(kv_path):
            continue

        pta_path = os.path.join(folder_path, pta_file)
        pta = load_pta(pta_path)

        features = extract_features_from_pta(pta, global_alphabet)
        X.append(features)

        with open(kv_path) as f:
            kv_data = json.load(f)

        k_vector = [kv_data.get(symbol, 1) for symbol in global_alphabet]
        y.append(k_vector)

    # numpy
    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int64)

    # pandas
    feature_names = get_feature_names(global_alphabet)

    X_df = pd.DataFrame(X, columns=feature_names)

    y_columns = [f"k_{symbol}" for symbol in global_alphabet]
    y_df = pd.DataFrame(y, columns=y_columns)

    return X_df, y_df, global_alphabet


folder = "../output/10_state/10_state"

X_df, y_df, alphabet = build_dataset_with_labels(folder)

print(X_df.head())
print(y_df.head())