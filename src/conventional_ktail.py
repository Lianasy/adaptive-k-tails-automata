from collections import deque

from pta import generate_pta
from function import parse_traces, split_train_test

import argparse
import os
import time


def compute_k_tail(state, k):
    future = set()
    q = deque([(state, (), 0)])
    while q:
        cur, path, depth = q.popleft()
        if depth == k:
            future.add((path, cur.is_accepting))
            continue
        for sym, nxt in cur.transitions.items():
            q.append((nxt, path + (sym,), depth + 1))
    return frozenset(future)


def find_mergeable_pair(pta, k):
    seen = {}
    for s in pta.states:
        tail = compute_k_tail(s, k)
        if not tail:
            continue
        if tail in seen:
            return seen[tail], s
        seen[tail] = s
    return None, None


def merge_states(pta, s1, s2):
    if s1.id > s2.id:
        s1, s2 = s2, s1

    rep = {}

    def resolve(s):
        while s.id in rep:
            s = rep[s.id]
        return s

    q = deque([(s1, s2)])
    while q:
        a, b = q.popleft()
        keep, gone = resolve(a), resolve(b)
        if keep.id == gone.id:
            continue
        if keep.id > gone.id:
            keep, gone = gone, keep

        rep[gone.id] = keep
        keep.is_accepting = keep.is_accepting or gone.is_accepting

        for s in pta.states:
            for sym in list(s.transitions):
                s.transitions[sym] = resolve(s.transitions[sym])

        for sym, tgt in gone.transitions.items():
            if sym not in keep.transitions:
                keep.transitions[sym] = tgt
            elif keep.transitions[sym].id != tgt.id:
                lo = min(keep.transitions[sym], tgt, key=lambda s: s.id)
                hi = max(keep.transitions[sym], tgt, key=lambda s: s.id)
                keep.transitions[sym] = lo
                q.append((lo, hi))

    pta.states = [s for s in pta.states if s.id not in rep]
    pta.root = resolve(pta.root)


def conventional_ktail(pos_traces, k):
    pta = generate_pta(pos_traces)
    while True:
        s1, s2 = find_mergeable_pair(pta, k)
        if s1 is None:
            break
        merge_states(pta, s1, s2)
    return pta


def accepts(dfa, trace):
    cur = dfa.root
    for sym in trace:
        if sym not in cur.transitions:
            return False
        cur = cur.transitions[sym]
    return cur.is_accepting


def evaluate_bcr(dfa, test_pos, test_neg):
    tp = sum(1 for t in test_pos if accepts(dfa, t))
    tn = sum(1 for t in test_neg if not accepts(dfa, t))
    fn = len(test_pos) - tp
    fp = len(test_neg) - tn
    sens = tp / len(test_pos) if test_pos else 0.0
    spec = tn / len(test_neg) if test_neg else 0.0
    bcr = (sens + spec) / 2
    return {
        "BCR": bcr,
        "sensitivity": sens,
        "specificity": spec,
        "TP": tp,
        "FN": fn,
        "TN": tn,
        "FP": fp,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--k", type=int, default=2)
    parser.add_argument("--output", default="output")
    args = parser.parse_args()

    pos, neg = parse_traces(args.data)
    train_pos, train_neg, test_pos, test_neg = split_train_test(pos, neg)

    t0 = time.perf_counter()
    dfa = conventional_ktail(train_pos, args.k)
    elapsed = time.perf_counter() - t0

    m = evaluate_bcr(dfa, test_pos, test_neg)

    lines = [
        f"=== Conventional k-tails (k={args.k}) ===",
        f"Data:        {args.data}",
        f"States:      {len(dfa.states)}",
        f"BCR:         {m['BCR']:.4f}",
        f"Sensitivity: {m['sensitivity']:.4f}",
        f"Specificity: {m['specificity']:.4f}",
        f"TP={m['TP']}  FN={m['FN']}  TN={m['TN']}  FP={m['FP']}",
        f"Time:        {elapsed:.2f}s",
    ]
    report = "\n".join(lines)
    print(report)

    os.makedirs(args.output, exist_ok=True)
    stem = os.path.splitext(os.path.basename(args.data))[0]
    out_path = os.path.join(args.output, f"{stem}_k{args.k}_BCR.txt")
    with open(out_path, "w") as f:
        f.write(report + "\n")
    print(f"\nSaved → {out_path}")
