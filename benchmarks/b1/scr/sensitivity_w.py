# =============================================================================
# sensitivity_w.py  —  Hybrid Belief Update T-Sensitivity Analysis
# Project  : ELS_NEW / P_Base  (Priority 2 — Intervention A1)
# Plan ref : how_improve_performance.md §2.7 Item 5
# Date     : 2026-04-23
# Usage    : python scr/sensitivity_w.py
# Outputs  : output/sensitivity_w_results.csv
#            output/sensitivity_w_report.md
# =============================================================================
"""
T-Sensitivity Analysis: ELS_Phil_T and ELS_Int_T with
w ∈ {0.0, 0.25, 0.5, 0.75, 1.0}

For each w value and each method, runs N_MC=200 episodes in both
stationary and nonstationary conditions and reports U_cum, P_fail, MTTF.

w=0.0 → pure static ELS update (original ELS behaviour)
w=0.5 → recommended hybrid blend (Priority 2 default)
w=1.0 → full Markovian Bayes update (POMDP-equivalent belief update)

Seeding: m_idx offsets start at 100 to avoid collision with run_benchmark.py
         m_idx = 100 + w_idx * 2 + method_idx   (w_idx 0–4, method_idx 0–1)
"""

import os
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from pomdp_env import (
    N, T, GAMMA, SEED, CLIMATE_SWITCH_STEP, FAILURE_STATE, N_OBS,
    R, T_stat, T_shift, T_misspec, LIKELIHOOD,
    N_MC as DEFAULT_N_MC,
)
from els_methods import ELSPhilT, ELSIntT, ELS_PHYS_UPDATE_METHODS
from run_benchmark import _run_episode, _step, _update_belief

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
W_VALUES    = [0.0, 0.25, 0.5, 0.75, 1.0]
CONDITIONS  = ["stationary", "nonstationary"]
N_MC        = DEFAULT_N_MC     # 200
M_IDX_BASE  = 100              # avoid collision with main benchmark m_idx (0-15)
OUTPUT_DIR  = os.path.join(os.path.dirname(_HERE), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Run N_MC episodes for a single (policy, condition, m_idx)
# ---------------------------------------------------------------------------
def _run_sensitivity_mc(
    name: str,
    policy,
    stationary: bool,
    m_idx: int,
    n_mc: int,
) -> dict:
    """
    Run n_mc episodes and compute summary statistics.

    Returns dict with: ucum_mean, ucum_sd, pfail, mttf_mean
    """
    from els_methods import ELSInt   # for isinstance check

    c_idx = int(not stationary)
    all_rewards    = np.empty((n_mc, T), dtype=float)
    all_states     = np.empty((n_mc, T), dtype=np.int8)
    all_actions    = np.empty((n_mc, T), dtype=np.int8)
    discount       = GAMMA ** np.arange(T)

    for ep in range(n_mc):
        ep_rng   = np.random.default_rng([SEED, m_idx, c_idx, ep])
        els_seed = (
            int(np.random.default_rng([SEED + 7000, m_idx, ep]).integers(0, 2**31))
            if isinstance(policy, ELSInt) else None
        )
        init_s, rew, sts, acts, _kp = _run_episode(
            policy, stationary, ep_rng, els_seed
        )
        all_rewards[ep] = rew
        all_states[ep]  = sts
        all_actions[ep] = acts

    ucum      = (all_rewards * discount).sum(axis=1)
    pfail     = np.any(all_states == FAILURE_STATE, axis=1).mean()
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
    print("sensitivity_w.py — T-Sensitivity Analysis (Intervention A1)")
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
                    "w":         w,
                    "method":    name,
                    "condition": cond,
                    "ucum_mean": res["ucum_mean"],
                    "ucum_sd":   res["ucum_sd"],
                    "pfail":     res["pfail"],
                    "mttf_mean": res["mttf_mean"],
                })

    elapsed = time.time() - t_start
    print(f"\n{'='*72}")
    print(f"Sensitivity run complete in {elapsed:.1f}s  ({elapsed/60:.1f} min)")

    # ------------------------------------------------------------------
    # Save CSV
    # ------------------------------------------------------------------
    csv_path = os.path.join(OUTPUT_DIR, "sensitivity_w_results.csv")
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

    # ------------------------------------------------------------------
    # Save Markdown report
    # ------------------------------------------------------------------
    md_path = os.path.join(OUTPUT_DIR, "sensitivity_w_report.md")
    _write_md_report(records, md_path)
    print(f"Report: {md_path}")
    print(f"{'='*72}")

    return records


def _write_md_report(records: list[dict], path: str) -> None:
    """Write a formatted Markdown table for each condition × method pair."""
    lines = [
        "# T-Sensitivity Analysis — Hybrid Belief Update w ∈ {0.0, 0.25, 0.5, 0.75, 1.0}",
        "**Date:** 2026-04-23  ",
        f"**N_MC = {N_MC}  T = {T}  γ = {GAMMA}  SEED = {SEED}**  ",
        "**Intervention A1:** hybrid update = (1−w)·b + w·(T_stat[a]ᵀ·b), then likelihood correction  ",
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

    # Add comparison with original ELS and SARSOP
    lines += [
        "## Reference values (from run_benchmark.py, N_MC=200)",
        "",
        "| Method | Stationary U_cum | NS U_cum | Stat P_fail | NS P_fail |",
        "|--------|-----------------|---------|-------------|-----------|",
        "| ELS_Phil (w=0) | 1054.7 | 976.5 | 0.855 | 0.960 |",
        "| ELS_Int (w=0) | 947.6 | 838.8 | 0.885 | 0.960 |",
        "| SARSOP | 1707.0 | 1561.9 | 0.405 | 0.650 |",
        "| AlwaysRestricted | 1439.2 | 1356.2 | 0.465 | 0.660 |",
        "",
        "> Note: w=0.0 in this script uses the same algorithm as the original ELS methods",
        "> but may differ slightly due to different episode seeds (M_IDX_BASE=100).",
    ]

    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
