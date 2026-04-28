# =============================================================================
# sensitivity_w_b2.py  —  Hybrid Belief Update T-Sensitivity (Benchmark 2)
# Project  : ELS_NEW / P_Base2  (Arizona/Spain MAR)
# Plan ref : how_improve_performance.md §2.7 Item 5; experiment_plan.md §6.2
# Ported   : from P_Base/scr/sensitivity_w.py — imports and paths adapted for B2
# Date     : 2026-04-24
# Usage    : python scr/sensitivity_w_b2.py
# Outputs  : output/sensitivity_w_results_b2.csv
#            output/sensitivity_w_report_b2.md
# =============================================================================
"""
T-Sensitivity Analysis for Benchmark 2 (MAR Arizona/Spain):
ELS_Phil_T and ELS_Int_T with w ∈ {0.0, 0.25, 0.5, 0.75, 1.0}.

w=0.0 → pure static ELS update (T_SSP245 not used)
w=0.5 → recommended hybrid blend (Priority 2 default)
w=1.0 → full Markovian Bayes update using T_SSP245

Key B2 differences from B1:
  T=30, CLIMATE_SWITCH_STEP=15, N_OBS=20
  Conditions: SSP2-4.5 (stationary) / SSP5-8.5 switch at t=15 (nonstationary)

Seeding: M_IDX_BASE=100 to avoid collision with run_benchmark_b2 (m_idx 0-15).
"""

import os
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_BASE2 = os.path.dirname(_HERE)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from pomdp_env_b2 import (
    N, T, GAMMA, SEED, CLIMATE_SWITCH_STEP, FAILURE_STATE, N_OBS,
    R, T_stat, T_shift, LIKELIHOOD,
    N_MC as DEFAULT_N_MC,
)
from els_methods import ELSPhilT, ELSIntT, ELSInt, ELS_PHYS_UPDATE_METHODS
from run_benchmark_b2 import _run_episode, _update_belief

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
W_VALUES    = [0.0, 0.25, 0.5, 0.75, 1.0]
CONDITIONS  = ["stationary", "nonstationary"]
N_MC        = DEFAULT_N_MC     # 200
M_IDX_BASE  = 100
OUTPUT_DIR  = os.path.join(_BASE2, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# MC runner for one (policy, condition, m_idx)
# ---------------------------------------------------------------------------
def _run_sensitivity_mc(
    name: str,
    policy,
    stationary: bool,
    m_idx: int,
    n_mc: int,
) -> dict:
    c_idx    = int(not stationary)
    discount = GAMMA ** np.arange(T)
    all_rewards = np.empty((n_mc, T), dtype=float)
    all_states  = np.empty((n_mc, T), dtype=np.int8)

    for ep in range(n_mc):
        ep_rng   = np.random.default_rng([SEED, m_idx, c_idx, ep])
        els_seed = (
            int(np.random.default_rng([SEED + 7000, m_idx, ep]).integers(0, 2**31))
            if isinstance(policy, ELSInt) else None
        )
        _init_s, rew, sts, _acts, _kp = _run_episode(
            policy, stationary, ep_rng, els_seed
        )
        all_rewards[ep] = rew
        all_states[ep]  = sts

    ucum  = (all_rewards * discount).sum(axis=1)
    pfail = np.any(all_states == FAILURE_STATE, axis=1).mean()
    fail_mask = all_states == FAILURE_STATE
    mttf_vals = np.where(
        fail_mask.any(axis=1),
        np.argmax(fail_mask, axis=1).astype(float),
        np.nan,
    )
    mttf_mean = float(np.nanmean(mttf_vals)) if np.any(~np.isnan(mttf_vals)) else np.nan

    return {
        "ucum_mean": float(ucum.mean()),
        "ucum_sd":   float(ucum.std()),
        "pfail":     float(pfail),
        "mttf_mean": mttf_mean,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t_start = time.time()

    print("=" * 72)
    print("sensitivity_w_b2.py — T-Sensitivity Analysis (Benchmark 2 MAR)")
    print(f"  w values : {W_VALUES}")
    print(f"  N_MC={N_MC}  T={T}  GAMMA={GAMMA}  SEED={SEED}")
    print("=" * 72)

    METHOD_DEFS = [
        ("ELS_Phil_T", ELSPhilT),
        ("ELS_Int_T",  ELSIntT),
    ]

    records = []

    for w_idx, w in enumerate(W_VALUES):
        print(f"\nw = {w:.2f}")
        print(f"  {'Method':<14}  {'Cond':<6}  {'U_cum':>14}  {'P_fail':>8}  {'MTTF':>6}")
        print(f"  {'-'*56}")

        for m_sub, (name, cls) in enumerate(METHOD_DEFS):
            m_idx  = M_IDX_BASE + w_idx * len(METHOD_DEFS) + m_sub
            policy = cls(w=w) if name == "ELS_Phil_T" else cls(seed=SEED, w=w)

            for cond in CONDITIONS:
                stationary = (cond == "stationary")
                res = _run_sensitivity_mc(name, policy, stationary, m_idx, N_MC)

                mttf_str = f"{res['mttf_mean']:.1f}" if not np.isnan(res["mttf_mean"]) else " n/a"
                cond_str = "stat" if stationary else "ns  "
                print(
                    f"  {name:<14}  {cond_str}  "
                    f"U_cum={res['ucum_mean']:7.1f}±{res['ucum_sd']:5.1f}  "
                    f"P_fail={res['pfail']:.3f}  MTTF={mttf_str}",
                    flush=True,
                )
                records.append({
                    "w": w, "method": name, "condition": cond,
                    "ucum_mean": res["ucum_mean"], "ucum_sd": res["ucum_sd"],
                    "pfail": res["pfail"], "mttf_mean": res["mttf_mean"],
                })

    elapsed = time.time() - t_start
    print(f"\n{'='*72}")
    print(f"B2 sensitivity run complete in {elapsed:.1f}s  ({elapsed/60:.1f} min)")

    # Save CSV
    csv_path = os.path.join(OUTPUT_DIR, "sensitivity_w_results_b2.csv")
    header = "w,method,condition,ucum_mean,ucum_sd,pfail,mttf_mean"
    lines  = [header]
    for r in records:
        mttf_str = f"{r['mttf_mean']:.2f}" if not np.isnan(r["mttf_mean"]) else "nan"
        lines.append(
            f"{r['w']:.2f},{r['method']},{r['condition']},"
            f"{r['ucum_mean']:.2f},{r['ucum_sd']:.2f},{r['pfail']:.4f},{mttf_str}"
        )
    with open(csv_path, "w") as f:
        f.write("\n".join(lines))
    print(f"CSV: {csv_path}")

    # Save Markdown report
    md_path = os.path.join(OUTPUT_DIR, "sensitivity_w_report_b2.md")
    _write_md_report(records, md_path)
    print(f"Report: {md_path}")
    print(f"{'='*72}")
    return records


def _write_md_report(records: list[dict], path: str) -> None:
    lines = [
        "# T-Sensitivity Analysis — B2 MAR  w ∈ {0.0, 0.25, 0.5, 0.75, 1.0}",
        "**Date:** 2026-04-24  ",
        f"**N_MC = {N_MC}  T = {T}  γ = {GAMMA}  SEED = {SEED}**  ",
        "**Benchmark:** B2 Arizona/Spain MAR  (SSP2-4.5 → SSP5-8.5 at step 15)  ",
        "",
    ]
    for cond in ["stationary", "nonstationary"]:
        lines.append(f"## Condition: {cond}")
        lines.append("")
        for method in ["ELS_Phil_T", "ELS_Int_T"]:
            lines.append(f"### {method}")
            lines.append("")
            lines.append("| w | U_cum (mean) | U_cum (SD) | P_fail | MTTF |")
            lines.append("|---|---|---|---|---|")
            for r in records:
                if r["method"] == method and r["condition"] == cond:
                    mttf_s = f"{r['mttf_mean']:.1f}" if not np.isnan(r["mttf_mean"]) else "n/a"
                    lines.append(
                        f"| {r['w']:.2f} | {r['ucum_mean']:.1f} | {r['ucum_sd']:.1f} | "
                        f"{r['pfail']:.3f} | {mttf_s} |"
                    )
            lines.append("")

    lines += [
        "## Reference values (run_benchmark_b2.py, N_MC=200)",
        "",
        "| Method | Stationary U_cum | NS U_cum | Stat P_fail | NS P_fail |",
        "|--------|-----------------|---------|-------------|-----------|",
        "| ELS_Phil (w=0) | 755.9 | 666.9 | 0.795 | — |",
        "| ELS_Int (w=0)  | 698.8 | 648.4 | 0.785 | — |",
        "| ELS_Phil_T (w=0.5) | 1106.7 | 1041.9 | 0.540 | — |",
        "| SARSOP  | 1281.5 | 1181.6 | 0.260 | — |",
        "| AlwaysRestricted | 928.3 | 810.9 | 0.525 | — |",
    ]
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
