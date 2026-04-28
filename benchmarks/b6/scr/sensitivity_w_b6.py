# =============================================================================
# sensitivity_w_b6.py  —  Hybrid Belief Update T-Sensitivity (Benchmark 6)
# Project  : ELS_NEW / P_Base6  (Karst Aquifer-Based)
# Plan ref : how_improve_performance.md §2.7 Item 5; experiment_plan.md §6.5
# Ported   : from P_Base4/scr/sensitivity_w_b4.py — imports and paths adapted for B5
# Date     : 2026-04-25
# Usage    : python scr/sensitivity_w_b6.py
# Outputs  : output/sensitivity_w_results_b6.csv
#            output/sensitivity_w_report_b6.md
# =============================================================================
"""
T-Sensitivity Analysis for Benchmark 6 (Karst Aquifer):
ELS_Phil_T and ELS_Int_T with w ∈ {0.0, 0.25, 0.5, 0.75, 1.0}.

Key B5 differences from B4:
  T=30, CLIMATE_SWITCH_STEP=15, N_OBS=20, N=5, M=3
  Conditions: long-term average (stationary) / conduit desiccation at t=15
  U_T ≈ 0.7–0.9 (GRACE noise + sparse monitoring — highest in suite)
  SIGMA_OBS=45 (wider than B4=35; GRACE footprint aggregation)

Seeding: M_IDX_BASE=100 to avoid collision with run_benchmark_b6 (m_idx 0-15).
"""

import os, sys, time
import numpy as np

_HERE  = os.path.dirname(os.path.abspath(__file__))
_BASE6 = os.path.dirname(_HERE)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from pomdp_env_b6 import (
    N, T, GAMMA, SEED, CLIMATE_SWITCH_STEP, FAILURE_STATE, N_OBS,
    R, T_stat, T_shift, LIKELIHOOD,
    N_MC as DEFAULT_N_MC,
)
from els_methods import ELSPhilT, ELSIntT, ELSInt, ELS_PHYS_UPDATE_METHODS
from run_benchmark_b6 import _run_episode, _update_belief

W_VALUES   = [0.0, 0.25, 0.5, 0.75, 1.0]
CONDITIONS = ["stationary", "nonstationary"]
N_MC       = DEFAULT_N_MC
M_IDX_BASE = 100
OUTPUT_DIR = os.path.join(_BASE6, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def _run_sensitivity_mc(name, policy, stationary, m_idx, n_mc):
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
        _init_s, rew, sts, _acts, _kp = _run_episode(policy, stationary, ep_rng, els_seed)
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
    return {"ucum_mean": float(ucum.mean()), "ucum_sd": float(ucum.std()),
            "pfail": float(pfail), "mttf_mean": mttf_mean}


def main():
    t_start = time.time()
    print("=" * 72)
    print("sensitivity_w_b6.py — T-Sensitivity Analysis (Benchmark 6 Karst Aquifer Dual-Porosity)")
    print(f"  w values : {W_VALUES}")
    print(f"  N_MC={N_MC}  T={T}  GAMMA={GAMMA}  SEED={SEED}")
    print("=" * 72)

    METHOD_DEFS = [("ELS_Phil_T", ELSPhilT), ("ELS_Int_T", ELSIntT)]
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
                    f"P_fail={res['pfail']:.3f}  MTTF={mttf_str}", flush=True,
                )
                records.append({"w": w, "method": name, "condition": cond, **res})

    elapsed = time.time() - t_start
    print(f"\n{'='*72}")
    print(f"B5 sensitivity run complete in {elapsed:.1f}s  ({elapsed/60:.1f} min)")

    csv_path = os.path.join(OUTPUT_DIR, "sensitivity_w_results_b6.csv")
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

    md_path = os.path.join(OUTPUT_DIR, "sensitivity_w_report_b6.md")
    lines_md = [
        "# T-Sensitivity — B5 Karst Aquifer Dual-Porosity  w ∈ {0.0, 0.25, 0.5, 0.75, 1.0}",
        f"**N_MC={N_MC}  T={T}  γ={GAMMA}  SEED={SEED}**  ",
        "**Benchmark:** B5 Karst Aquifer (long-term avg → SSP5-8.5 at step 15)  ", "",
    ]
    for cond in ["stationary", "nonstationary"]:
        lines_md.append(f"## Condition: {cond}")
        lines_md.append("")
        for method in ["ELS_Phil_T", "ELS_Int_T"]:
            lines_md.append(f"### {method}")
            lines_md.append("")
            lines_md.append("| w | U_cum | SD | P_fail | MTTF |")
            lines_md.append("|---|---|---|---|---|")
            for r in records:
                if r["method"] == method and r["condition"] == cond:
                    mttf_s = f"{r['mttf_mean']:.1f}" if not np.isnan(r["mttf_mean"]) else "n/a"
                    lines_md.append(
                        f"| {r['w']:.2f} | {r['ucum_mean']:.1f} | {r['ucum_sd']:.1f} "
                        f"| {r['pfail']:.3f} | {mttf_s} |"
                    )
            lines_md.append("")
    with open(md_path, "w") as f:
        f.write("\n".join(lines_md) + "\n")
    print(f"Report: {md_path}")
    print(f"{'='*72}")
    return records


if __name__ == "__main__":
    main()
