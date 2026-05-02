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

    # depth
    depths = compute_depths(transitions)
    depth_values = list(depths.values())

    avg_depth = np.mean(depth_values)
    max_depth = np.max(depth_values)
    depth_std = np.std(depth_values)
    depth_min = np.min(depth_values)

    # branching
    branching = [len(transitions[s]) for s in transitions]
    avg_branching = np.mean(branching)
    max_branching = np.max(branching)
    branching_std = np.std(branching)

    # accept
    accepted = [1 if s["accepted"] == "Y" else 0 for s in pta]
    accept_ratio = np.mean(accepted)

    # transitions stats
    num_transitions = sum(len(transitions[s]) for s in transitions)
    density = num_transitions / (num_states + 1e-8)

    leaf_states = sum(1 for s in transitions if len(transitions[s]) == 0)
    leaf_ratio = leaf_states / (num_states + 1e-8)

    # degrees
    in_degrees = [len(incoming[s]) for s in transitions]
    out_degrees = [len(transitions[s]) for s in transitions]

    avg_in_degree = np.mean(in_degrees)
    max_in_degree = np.max(in_degrees)

    avg_out_degree = np.mean(out_degrees)
    max_out_degree = np.max(out_degrees)

    # global entropy
    all_labels = []
    for s in transitions:
        for label, _ in transitions[s]:
            all_labels.append(label)

    label_counts = defaultdict(int)
    for l in all_labels:
        label_counts[l] += 1

    probs = [c / len(all_labels) for c in label_counts.values()] if all_labels else []
    global_entropy = -sum(p * math.log(p + 1e-8) for p in probs) if probs else 0

    # alphabet
    if global_alphabet is None:
        alphabet = get_alphabet(transitions)
    else:
        alphabet = global_alphabet

    # map for accepted lookup
    state_map = {s["state_id"]: s for s in pta}

    # symbol features
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

        # ---- NEW FEATURES ----

        depths_after = []
        branching_after = []
        accept_after = []
        next_labels = set()
        second_step_labels = []
        self_loop_after = 0
        total_after = 0

        for s in transitions:
            for label, nxt in transitions[s]:
                if label == symbol:

                    total_after += 1

                    depths_after.append(depths[nxt])
                    branching_after.append(len(transitions[nxt]))

                    accept_after.append(
                        1 if state_map[nxt]["accepted"] == "Y" else 0
                    )

                    if nxt == s:
                        self_loop_after += 1

                    for l2, _ in transitions[nxt]:
                        next_labels.add(l2)
                        second_step_labels.append(l2)

        avg_depth_after = np.mean(depths_after) if depths_after else 0
        avg_branching_after = np.mean(branching_after) if branching_after else 0
        accept_ratio_after = np.mean(accept_after) if accept_after else 0

        next_label_diversity = len(next_labels)

        if second_step_labels:
            counts = defaultdict(int)
            for l in second_step_labels:
                counts[l] += 1
            probs = [c / len(second_step_labels) for c in counts.values()]
            second_entropy = -sum(p * math.log(p + 1e-8) for p in probs)
        else:
            second_entropy = 0

        self_loop_ratio_after = self_loop_after / (total_after + 1e-8)

        symbol_features.extend([
            freq,
            unique_successors,
            entropy,

            avg_depth_after,
            avg_branching_after,
            accept_ratio_after,

            next_label_diversity,
            second_entropy,

            self_loop_ratio_after
        ])

    # final vector
    features = [
        num_states,
        num_transitions,
        density,

        avg_depth,
        max_depth,
        depth_std,
        depth_min,

        avg_branching,
        max_branching,
        branching_std,

        avg_in_degree,
        max_in_degree,
        avg_out_degree,
        max_out_degree,

        leaf_ratio,
        accept_ratio,

        global_entropy
    ]

    features.extend(symbol_features)

    return np.array(features, dtype=np.float32)

def get_feature_names(alphabet):
    feature_names = [
        "num_states",
        "num_transitions",
        "density",

        "avg_depth",
        "max_depth",
        "depth_std",
        "depth_min",

        "avg_branching",
        "max_branching",
        "branching_std",

        "avg_in_degree",
        "max_in_degree",
        "avg_out_degree",
        "max_out_degree",

        "leaf_ratio",
        "accept_ratio",

        "global_entropy"
    ]

    for symbol in alphabet:
        feature_names.extend([
            f"{symbol}_freq",
            f"{symbol}_unique_successors",
            f"{symbol}_entropy",

            f"{symbol}_avg_depth_after",
            f"{symbol}_avg_branching_after",
            f"{symbol}_accept_ratio_after",

            f"{symbol}_next_label_diversity",
            f"{symbol}_second_entropy",

            f"{symbol}_self_loop_ratio_after"
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