"""
evaluation.py
=============
Parses the BCR output files produced by the Adaptive k-Tails automaton inference
experiments and computes per-run and aggregate evaluation metrics.

Folder / file conventions expected
------------------------------------
2_tail_BCR/
    automaton_10_2_5_0~N.txt_ATM_BCR_Ktail.txt   ← k=2 automaton results
    automaton_10_2_5_0~N.txt_PTA_BCR_Ktail.txt   ← PTA baseline results

3_tail_BCR/
    automaton_10_2_5_0~N.txt_ATM_BCR_Ktail.txt   ← k=3 automaton results

A_Ktail_(k=2&3)_BCR/
    automaton_10_2_5_0~N_ATM_BCR.txt             ← Adaptive k-Tails (k ∈ {2,3})

Usage
-----
    python evaluation.py --base_dir <path_to_output_root>

    # Or point at specific zip-extracted dirs:
    python evaluation.py \
        --k2_dir   2_tail_BCR \
        --k3_dir   3_tail_BCR \
        --ak_dir   "A_Ktail_(k=2&3)_BCR"
"""

import argparse
import os
import re
import statistics
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Regex patterns that match the output file formats
# ---------------------------------------------------------------------------

# ---- ATM files (k=2 and k=3) ----
ATM_KTAIL_PAT = re.compile(
    r"BCR evaluation k=(?P<k>\d+)"
    r".*?ATM states num = (?P<states>\d+)"
    r".*?Positive traces:\s*(?P<pos>\d+)\s*\|\s*Negative traces:\s*(?P<neg>\d+)"
    r".*?TP=(?P<TP>\d+)\s+FN=(?P<FN>\d+)\s+TN=(?P<TN>\d+)\s+FP=(?P<FP>\d+)"
    r".*?Sensitivity \(TPR\):\s*(?P<TPR>[\d.]+)"
    r".*?Specificity \(TNR\):\s*(?P<TNR>[\d.]+)"
    r".*?BCR:\s*(?P<BCR>[\d.]+)"
    r".*?Elapsed time:\s*(?P<time>[\d.]+)",
    re.DOTALL,
)

# ---- ATM files (Adaptive k-Tails) ----
ATM_ADAPTIVE_PAT = re.compile(
    r"BCR evaluation k-vector\s*=\s*(?P<kvec>\{[^}]+\})"
    r".*?ATM states num = (?P<states>\d+)"
    r".*?Positive traces:\s*(?P<pos>\d+)\s*\|\s*Negative traces:\s*(?P<neg>\d+)"
    r".*?TP=(?P<TP>\d+)\s+FN=(?P<FN>\d+)\s+TN=(?P<TN>\d+)\s+FP=(?P<FP>\d+)"
    r".*?Sensitivity \(TPR\):\s*(?P<TPR>[\d.]+)"
    r".*?Specificity \(TNR\):\s*(?P<TNR>[\d.]+)"
    r".*?BCR:\s*(?P<BCR>[\d.]+)"
    r".*?Evaluation time:\s*(?P<time>[\d.]+)",
    re.DOTALL,
)

# ---- PTA baseline files ----
PTA_PAT = re.compile(
    r"PTA evaluation"
    r".*?PTA states num = (?P<states>\d+)"
    r".*?PTA alphabet:\s*(?P<alphabet>\{[^}]+\})"
    r".*?PTA \(BCR\):\s*(?P<BCR>[\d.]+)"
    r".*?PTA \(Sensitivity\):\s*(?P<TPR>[\d.]+)"
    r".*?PTA \(Specificity\):\s*(?P<TNR>[\d.]+)",
    re.DOTALL,
)


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_atm_ktail(path: Path) -> Optional[dict]:
    """Parse a fixed-k ATM result file (k=2 or k=3)."""
    text = _read(path)
    m = ATM_KTAIL_PAT.search(text)
    if not m:
        return None
    d = m.groupdict()
    return {
        "file": path.name,
        "run": _run_index(path.name),
        "k": int(d["k"]),
        "atm_states": int(d["states"]),
        "pos_traces": int(d["pos"]),
        "neg_traces": int(d["neg"]),
        "TP": int(d["TP"]),
        "FN": int(d["FN"]),
        "TN": int(d["TN"]),
        "FP": int(d["FP"]),
        "sensitivity": float(d["TPR"]),
        "specificity": float(d["TNR"]),
        "BCR": float(d["BCR"]),
        "elapsed_sec": float(d["time"]),
    }


def parse_atm_adaptive(path: Path) -> Optional[dict]:
    """Parse an Adaptive k-Tails ATM result file."""
    text = _read(path)
    m = ATM_ADAPTIVE_PAT.search(text)
    if not m:
        return None
    d = m.groupdict()
    return {
        "file": path.name,
        "run": _run_index(path.name),
        "k_vector": d["kvec"],
        "atm_states": int(d["states"]),
        "pos_traces": int(d["pos"]),
        "neg_traces": int(d["neg"]),
        "TP": int(d["TP"]),
        "FN": int(d["FN"]),
        "TN": int(d["TN"]),
        "FP": int(d["FP"]),
        "sensitivity": float(d["TPR"]),
        "specificity": float(d["TNR"]),
        "BCR": float(d["BCR"]),
        "elapsed_sec": float(d["time"]),
    }


def parse_pta(path: Path) -> Optional[dict]:
    """Parse a PTA baseline result file."""
    text = _read(path)
    m = PTA_PAT.search(text)
    if not m:
        return None
    d = m.groupdict()
    return {
        "file": path.name,
        "run": _run_index(path.name),
        "pta_states": int(d["states"]),
        "alphabet": d["alphabet"],
        "sensitivity": float(d["TPR"]),
        "specificity": float(d["TNR"]),
        "BCR": float(d["BCR"]),
    }


def _run_index(filename: str) -> int:
    """Extract the run number (~N) from the filename."""
    m = re.search(r"~(\d+)", filename)
    return int(m.group(1)) if m else -1


# ---------------------------------------------------------------------------
# Aggregate statistics
# ---------------------------------------------------------------------------

def aggregate(records: list[dict], label: str) -> dict:
    if not records:
        return {}

    def _stats(values, key):
        vals = [r[key] for r in values if key in r]
        if not vals:
            return {}
        return {
            "mean":   round(statistics.mean(vals), 4),
            "stdev":  round(statistics.stdev(vals), 4) if len(vals) > 1 else 0.0,
            "min":    round(min(vals), 4),
            "max":    round(max(vals), 4),
            "median": round(statistics.median(vals), 4),
        }

    agg = {
        "label":        label,
        "n_runs":       len(records),
        "BCR":          _stats(records, "BCR"),
        "sensitivity":  _stats(records, "sensitivity"),
        "specificity":  _stats(records, "specificity"),
        "atm_states":   _stats(records, "atm_states"),
        "elapsed_sec":  _stats(records, "elapsed_sec"),
    }

    # Confusion matrix totals
    for key in ("TP", "FN", "TN", "FP"):
        vals = [r[key] for r in records if key in r]
        if vals:
            agg[key + "_total"] = sum(vals)
            agg[key + "_mean"]  = round(statistics.mean(vals), 2)

    return agg


# ---------------------------------------------------------------------------
# Pretty-printing
# ---------------------------------------------------------------------------

def _fmt_stats(d: dict) -> str:
    if not d:
        return "N/A"
    return (
        f"mean={d['mean']:.4f}  stdev={d['stdev']:.4f}  "
        f"min={d['min']:.4f}  max={d['max']:.4f}  median={d['median']:.4f}"
    )


def print_per_run(records: list[dict], title: str):
    sep = "─" * 100
    print(f"\n{'═'*100}")
    print(f"  {title}")
    print(f"{'═'*100}")
    print(
        f"  {'Run':>3}  {'States':>7}  {'TP':>4}  {'FN':>4}  "
        f"{'TN':>4}  {'FP':>4}  {'Sensitivity':>12}  {'Specificity':>12}  "
        f"{'BCR':>8}  {'Time(s)':>10}"
    )
    print(f"  {sep}")
    for r in sorted(records, key=lambda x: x["run"]):
        print(
            f"  {r['run']:>3}  {r.get('atm_states', r.get('pta_states', 0)):>7}  "
            f"{r.get('TP', '-'):>4}  {r.get('FN', '-'):>4}  "
            f"{r.get('TN', '-'):>4}  {r.get('FP', '-'):>4}  "
            f"{r['sensitivity']:>12.4f}  {r['specificity']:>12.4f}  "
            f"{r['BCR']:>8.4f}  {r.get('elapsed_sec', float('nan')):>10.2f}"
        )
    print(f"  {sep}")


def print_aggregate(agg: dict):
    print(f"\n  ── Aggregate ({agg['n_runs']} runs) ──")
    print(f"     BCR         : {_fmt_stats(agg.get('BCR', {}))}")
    print(f"     Sensitivity : {_fmt_stats(agg.get('sensitivity', {}))}")
    print(f"     Specificity : {_fmt_stats(agg.get('specificity', {}))}")
    print(f"     ATM States  : {_fmt_stats(agg.get('atm_states', {}))}")
    print(f"     Elapsed(s)  : {_fmt_stats(agg.get('elapsed_sec', {}))}")
    print(
        f"     Confusion   : TP_mean={agg.get('TP_mean', 'N/A'):.2f}  "
        f"FN_mean={agg.get('FN_mean', 'N/A'):.2f}  "
        f"TN_mean={agg.get('TN_mean', 'N/A'):.2f}  "
        f"FP_mean={agg.get('FP_mean', 'N/A'):.2f}"
    )


def print_comparison_table(agg_list: list[dict]):
    """Side-by-side comparison of all methods."""
    print(f"\n\n{'═'*100}")
    print("  COMPARISON TABLE (mean ± stdev across all runs)")
    print(f"{'═'*100}")
    header = f"  {'Method':<30}  {'BCR':>12}  {'Sensitivity':>14}  {'Specificity':>14}  {'ATM States':>12}  {'Time(s)':>12}"
    print(header)
    print("  " + "─" * 98)
    for agg in agg_list:
        label = agg["label"]
        bcr   = agg.get("BCR", {})
        sens  = agg.get("sensitivity", {})
        spec  = agg.get("specificity", {})
        sta   = agg.get("atm_states", {})
        t     = agg.get("elapsed_sec", {})
        print(
            f"  {label:<30}  "
            f"{bcr.get('mean', float('nan')):>6.4f} ±{bcr.get('stdev', 0):>6.4f}  "
            f"{sens.get('mean', float('nan')):>8.4f} ±{sens.get('stdev', 0):>6.4f}  "
            f"{spec.get('mean', float('nan')):>8.4f} ±{spec.get('stdev', 0):>6.4f}  "
            f"{sta.get('mean', float('nan')):>10.1f} ±{sta.get('stdev', 0):>5.1f}  "
            f"{t.get('mean', float('nan')):>10.2f} ±{t.get('stdev', 0):>5.2f}"
        )
    print("  " + "─" * 98)


def print_adaptive_kvectors(records: list[dict]):
    """Show the k-vector chosen for each adaptive run."""
    print(f"\n\n  ── Adaptive k-Tails: k-vector per run ──")
    for r in sorted(records, key=lambda x: x["run"]):
        print(f"     Run {r['run']:>2}: {r.get('k_vector', 'N/A')}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def load_directory(directory: Path, mode: str) -> list[dict]:
    """
    mode: 'k2'  → fixed k=2 ATM files
          'k3'  → fixed k=3 ATM files
          'ak'  → adaptive k-Tails ATM files
          'pta' → PTA baseline files
    """
    records = []
    if not directory.exists():
        print(f"  [WARN] Directory not found: {directory}")
        return records

    for path in sorted(directory.iterdir()):
        if not path.is_file():
            continue
        text = path.name.lower()
        if mode in ("k2", "k3") and "atm_bcr" in text and "ktail" in text:
            r = parse_atm_ktail(path)
        elif mode == "ak" and "atm_bcr" in text:
            r = parse_atm_adaptive(path)
        elif mode == "pta" and "pta_bcr" in text:
            r = parse_pta(path)
        else:
            continue
        if r:
            records.append(r)
    return records


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate Adaptive k-Tails automaton output files."
    )
    parser.add_argument(
        "--base_dir",
        type=Path,
        default=Path("."),
        help="Root directory containing the three output folders.",
    )
    parser.add_argument("--k2_dir", type=Path, default=None, help="Override path for k=2 output folder.")
    parser.add_argument("--k3_dir", type=Path, default=None, help="Override path for k=3 output folder.")
    parser.add_argument("--ak_dir", type=Path, default=None, help="Override path for Adaptive k-Tails output folder.")
    args = parser.parse_args()

    base = args.base_dir
    k2_dir = args.k2_dir or base / "2_tail_BCR"
    k3_dir = args.k3_dir or base / "3_tail_BCR"
    ak_dir = args.ak_dir or base / "A_Ktail_(k=2&3)_BCR"

    print("\n" + "█" * 100)
    print("  ADAPTIVE k-TAILS AUTOMATA — EVALUATION REPORT")
    print("█" * 100)

    # Load all data
    k2_atm   = load_directory(k2_dir, "k2")
    k2_pta   = load_directory(k2_dir, "pta")
    k3_atm   = load_directory(k3_dir, "k3")
    ak_atm   = load_directory(ak_dir, "ak")

    # ---- Per-run tables ----
    print_per_run(k2_atm,  "k=2  ATM  (fixed k-Tails, BCR evaluation)")
    print_per_run(k2_pta,  "PTA Baseline (from k=2 run folder)")
    print_per_run(k3_atm,  "k=3  ATM  (fixed k-Tails, BCR evaluation)")
    print_per_run(ak_atm,  "Adaptive k-Tails (k ∈ {2,3}, BCR evaluation)")

    # ---- Adaptive k-vector breakdown ----
    if ak_atm:
        print_adaptive_kvectors(ak_atm)

    # ---- Aggregates ----
    agg_k2_atm = aggregate(k2_atm, "k=2 ATM (fixed)")
    agg_k2_pta = aggregate(k2_pta, "PTA Baseline")
    agg_k3_atm = aggregate(k3_atm, "k=3 ATM (fixed)")
    agg_ak_atm = aggregate(ak_atm, "Adaptive k-Tails (k∈{2,3})")

    print_aggregate(agg_k2_atm)
    print_aggregate(agg_k3_atm)
    print_aggregate(agg_ak_atm)

    # ---- Side-by-side comparison ----
    print_comparison_table([agg_k2_pta, agg_k2_atm, agg_k3_atm, agg_ak_atm])

    # ---- BCR improvement over PTA ----
    print(f"\n\n  ── BCR improvement over PTA baseline ──")
    pta_mean = agg_k2_pta.get("BCR", {}).get("mean", float("nan"))
    for agg in [agg_k2_atm, agg_k3_atm, agg_ak_atm]:
        mean_bcr = agg.get("BCR", {}).get("mean", float("nan"))
        diff = mean_bcr - pta_mean
        print(f"     {agg['label']:<30} BCR mean = {mean_bcr:.4f}  Δ vs PTA = {diff:+.4f}")

    print(f"\n{'█'*100}\n")


if __name__ == "__main__":
    main()