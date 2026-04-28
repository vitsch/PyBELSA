# =============================================================================
# sensitivity_w_adapt.py  —  Adaptive w Trade-off Curve (Benchmark 1)
# Project  : ELS_NEW / P_Base
# Plan ref : BDT_concept_impr.md §3.1 and §7 "ELS-T adaptive weight"
# Date     : 2026-04-24
# Usage    : python scr/sensitivity_w_adapt.py
# Outputs  : output/sensitivity_w_adapt_results.csv
#            output/sensitivity_w_adapt_report.md
#            image/fig_w_adapt_tradeoff.png
# =============================================================================
"""
Trade-off curve analysis: fixed-w vs adaptive-w model trust.

Compares three method families on Benchmark 1 (stationary & nonstationary):
  1. Fixed-w sweep (ELS_Phil_T, ELS_Int_T)  — loads existing sensitivity_w_results.csv
  2. Adaptive-w (ELS_Phil_Adapt, ELS_Int_Adapt) — eta ∈ {0.1, 0.5, 1.0}
  3. Reference points (ELS_Phil, SARSOP, AlwaysRestricted) — from raw_results.npz

Key figure: U_cum vs effective-mean-w trade-off curve
  X = w (fixed) or mean(w_trajectory) (adaptive)
  Y = U_cum mean over N_MC episodes
  Adaptive points appear as ★ markers; fixed-w as solid lines

Seeding: m_idx 200+ to avoid collision with run_benchmark (0–15)
         and sensitivity_w (100–109).
"""

import os
import sys
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

_HERE = os.path.dirname(os.path.abspath(__file__))
_BASE = os.path.dirname(_HERE)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from pomdp_env import (
    N, M, N_OBS, T, GAMMA, SEED, CLIMATE_SWITCH_STEP, FAILURE_STATE,
    R, T_stat, T_shift, LIKELIHOOD, N_MC as DEFAULT_N_MC,
)
from els_methods import ELSInt, L_PHIL, L_PRES
from els_adapt import ELSPhilAdapt, ELSIntAdapt

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
N_MC        = DEFAULT_N_MC           # 200
CONDITIONS  = ["stationary", "nonstationary"]
ETA_VALUES  = [0.1, 0.5, 1.0]       # adaptation learning rates to evaluate
W_INIT      = 0.5                    # starting w for all adaptive runs
M_IDX_BASE  = 200                    # seed offset to avoid collisions
OUTPUT_DIR  = os.path.join(_BASE, "output")
IMAGE_DIR   = os.path.join(_BASE, "image")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR,  exist_ok=True)

# Reference values from run_benchmark.py (raw_results.npz / stat_report)
REFS = {
    "SARSOP":           {"stationary": 1707.0, "nonstationary": 1561.9},
    "AlwaysRestricted": {"stationary": 1439.2, "nonstationary": 1356.2},
    "ELS_Phil":         {"stationary": 1054.7, "nonstationary":  976.5},
    "ELS_Int":          {"stationary":  947.6, "nonstationary":  838.8},
}


# ---------------------------------------------------------------------------
# Episode runner — custom, passes action to phys_belief_update
# ---------------------------------------------------------------------------

def _run_adapt_episode(
    policy,
    stationary: bool,
    ep_rng: np.random.Generator,
    els_seed: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Run one episode, correctly routing belief update for adaptive variants.

    Unlike run_benchmark._run_episode, this always passes action to
    phys_belief_update so that ELSPhilAdapt / ELSIntAdapt can compute
    the T-prediction accuracy signal.

    Returns
    -------
    rewards : (T,)
    states  : (T,) int8
    """
    if isinstance(policy, ELSInt):
        policy.reset(seed=els_seed)
    else:
        policy.reset()

    b      = policy.initial_belief()
    s      = int(ep_rng.integers(0, N))
    rewards = np.empty(T, dtype=float)
    states  = np.empty(T, dtype=np.int8)

    for t in range(T):
        a = policy.act(b, t)

        # Environment step (condition-aware)
        T_use   = T_stat if (stationary or t < CLIMATE_SWITCH_STEP) else T_shift
        s_next  = int(ep_rng.choice(N, p=T_use[a, s]))
        obs_idx = int(ep_rng.choice(N_OBS, p=LIKELIHOOD[s_next]))
        reward  = float(R[a, s_next])

        # Belief update — always pass action for adaptation signal
        b = policy.phys_belief_update(b, obs_idx, action=a)

        rewards[t] = reward
        states[t]  = np.int8(s_next)
        s = s_next

    return rewards, states


# ---------------------------------------------------------------------------
# MC runner — adaptive variants
# ---------------------------------------------------------------------------

def _run_adapt_mc(
    name: str,
    policy,
    stationary: bool,
    m_idx: int,
    n_mc: int,
    verbose: bool = True,
) -> dict:
    """
    Run n_mc episodes with an adaptive-w policy.

    Returns summary dict including w trajectory statistics.
    """
    c_idx       = int(not stationary)
    discount    = GAMMA ** np.arange(T)
    all_ucum    = np.empty(n_mc, dtype=float)
    all_pfail   = np.empty(n_mc, dtype=bool)
    all_w_traj  = []         # list of (T,) arrays, one per episode

    for ep in range(n_mc):
        ep_rng   = np.random.default_rng([SEED, m_idx, c_idx, ep])
        els_seed = int(
            np.random.default_rng([SEED + 7000, m_idx, ep]).integers(0, 2**31)
        ) if isinstance(policy, ELSInt) else None

        rewards, states = _run_adapt_episode(policy, stationary, ep_rng, els_seed)
        all_ucum[ep]  = float((rewards * discount).sum())
        all_pfail[ep] = bool(np.any(states == FAILURE_STATE))

        # capture w trajectory (reset in next episode's policy.reset())
        if hasattr(policy, "w_trajectory") and len(policy.w_trajectory) == T:
            all_w_traj.append(np.array(policy.w_trajectory))

    ucum_mean  = float(all_ucum.mean())
    ucum_sd    = float(all_ucum.std())
    pfail      = float(all_pfail.mean())
    # w trajectory statistics across episodes
    if all_w_traj:
        w_mat     = np.stack(all_w_traj, axis=0)       # (n_mc, T)
        w_mean_ep = float(w_mat.mean())                 # grand mean
        w_final   = float(w_mat[:, -1].mean())          # mean final w
        w_traj_mean = w_mat.mean(axis=0)                # (T,) mean trajectory
    else:
        w_mean_ep   = float("nan")
        w_final     = float("nan")
        w_traj_mean = np.full(T, float("nan"))

    if verbose:
        cond_str = "stat" if stationary else "ns  "
        print(
            f"  {name:<20}  {cond_str}  "
            f"U_cum={ucum_mean:7.1f}±{ucum_sd:5.1f}  "
            f"P_fail={pfail:.3f}  "
            f"w_mean={w_mean_ep:.3f}  w_final={w_final:.3f}",
            flush=True,
        )

    return {
        "name":        name,
        "stationary":  stationary,
        "ucum_mean":   ucum_mean,
        "ucum_sd":     ucum_sd,
        "pfail":       pfail,
        "w_mean":      w_mean_ep,
        "w_final":     w_final,
        "w_traj_mean": w_traj_mean,   # (T,) for plotting
    }


# ---------------------------------------------------------------------------
# Load existing fixed-w results
# ---------------------------------------------------------------------------

def _load_fixed_w_results(csv_path: str) -> list[dict]:
    """Load sensitivity_w_results.csv into a list of dicts."""
    records = []
    with open(csv_path) as f:
        header = f.readline().strip().split(",")
        for line in f:
            vals = line.strip().split(",")
            rec = {k: v for k, v in zip(header, vals)}
            rec["w"]         = float(rec["w"])
            rec["ucum_mean"] = float(rec["ucum_mean"])
            rec["ucum_sd"]   = float(rec["ucum_sd"])
            rec["pfail"]     = float(rec["pfail"])
            rec["mttf_mean"] = float(rec["mttf_mean"]) if rec["mttf_mean"] != "nan" else float("nan")
            records.append(rec)
    return records


# ---------------------------------------------------------------------------
# Figure — trade-off curve + w trajectory
# ---------------------------------------------------------------------------

def _make_figure(fixed_records: list[dict], adapt_results: list[dict], out_path: str) -> None:
    """
    4-panel figure:
      Top row:    U_cum vs w trade-off curve (stat | ns)
      Bottom row: mean w trajectory over episode steps (stat | ns)
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.suptitle(
        "Adaptive vs Fixed Model-Trust Weight  (Benchmark 1, N_MC=200)",
        fontsize=13, fontweight="bold"
    )

    # Colour scheme
    C_PHIL_T     = "#E07B39"     # orange — ELS_Phil_T (fixed)
    C_INT_T      = "#2980B9"     # blue   — ELS_Int_T (fixed)
    C_PHIL_ADAPT = "#D62728"     # red    — ELS_Phil_Adapt
    C_INT_ADAPT  = "#1F77B4"     # dark blue — ELS_Int_Adapt
    C_SARSOP     = "#1A5276"
    C_ALWAYS     = "#BDC3C7"
    C_PHIL_BASE  = "#E07B39"     # same orange but dashed

    for col, cond in enumerate(["stationary", "nonstationary"]):
        ax_top = axes[0, col]
        ax_bot = axes[1, col]

        # --- Fixed-w curves ---
        for method, color, ls in [
            ("ELS_Phil_T", C_PHIL_T,  "-"),
            ("ELS_Int_T",  C_INT_T,   "-"),
        ]:
            recs = sorted(
                [r for r in fixed_records if r["method"] == method and r["condition"] == cond],
                key=lambda x: x["w"],
            )
            ws    = [r["w"] for r in recs]
            ucums = [r["ucum_mean"] for r in recs]
            sds   = [r["ucum_sd"] for r in recs]
            ax_top.plot(ws, ucums, marker="o", color=color, ls=ls,
                        label=f"{method} (fixed w)", zorder=3)
            ax_top.fill_between(
                ws,
                [u - 0.5 * s for u, s in zip(ucums, sds)],
                [u + 0.5 * s for u, s in zip(ucums, sds)],
                color=color, alpha=0.15,
            )

        # --- Adaptive variants ---
        for method, color, marker in [
            ("ELS_Phil_Adapt", C_PHIL_ADAPT, "*"),
            ("ELS_Int_Adapt",  C_INT_ADAPT,  "*"),
        ]:
            # Group by eta value; only the main eta matters for the star
            sub = [
                r for r in adapt_results
                if r["name"] == method and r["stationary"] == (cond == "stationary")
            ]
            # Best eta (highest U_cum) gets the prominent star; others get small markers
            if sub:
                sub_sorted = sorted(sub, key=lambda x: x["ucum_mean"], reverse=True)
                for i, r in enumerate(sub_sorted):
                    ms   = 18 if i == 0 else 10
                    lbl  = f"{method} (η={r['eta']:.1f})" if i == 0 else None
                    ax_top.plot(
                        r["w_mean"], r["ucum_mean"],
                        marker=marker, markersize=ms, color=color,
                        linestyle="none", label=lbl, zorder=5,
                        markeredgecolor="black", markeredgewidth=0.8,
                    )
                    # error bar
                    ax_top.errorbar(
                        r["w_mean"], r["ucum_mean"], yerr=r["ucum_sd"] * 0.5,
                        fmt="none", color=color, capsize=4, alpha=0.6,
                    )

        # --- Reference lines ---
        for ref_name, color_r, lbl_r in [
            ("SARSOP",           C_SARSOP, "SARSOP"),
            ("AlwaysRestricted", C_ALWAYS, "AlwaysRestricted"),
            ("ELS_Phil",         C_PHIL_BASE, "ELS_Phil (w=0)"),
        ]:
            val = REFS[ref_name][cond]
            ax_top.axhline(val, color=color_r, ls="--", lw=1.2, alpha=0.8, label=lbl_r)

        ax_top.set_title(f"Condition: {cond}", fontsize=11)
        ax_top.set_xlabel("Model-trust weight  w  (or effective mean w for adaptive)")
        ax_top.set_ylabel("U_cum (mean discounted reward)")
        ax_top.set_xlim(-0.05, 1.05)
        ax_top.legend(fontsize=7, loc="lower right", ncol=2)
        ax_top.grid(True, alpha=0.3)

        # --- Bottom row: mean w trajectory ---
        for method, color in [
            ("ELS_Phil_Adapt", C_PHIL_ADAPT),
            ("ELS_Int_Adapt",  C_INT_ADAPT),
        ]:
            sub = [
                r for r in adapt_results
                if r["name"] == method
                   and r["stationary"] == (cond == "stationary")
            ]
            for r in sorted(sub, key=lambda x: x["eta"]):
                ax_bot.plot(
                    np.arange(T), r["w_traj_mean"],
                    color=color, alpha=0.7,
                    label=f"{method.replace('ELS_', '')} η={r['eta']:.1f}",
                    lw=1.5,
                )

        ax_bot.axhline(W_INIT, color="grey", ls=":", lw=1, label=f"w_init={W_INIT}")
        ax_bot.set_xlabel("Episode step  t")
        ax_bot.set_ylabel("Mean w over episodes")
        ax_bot.set_title(f"w trajectory  ({cond})", fontsize=10)
        ax_bot.set_xlim(0, T - 1)
        ax_bot.set_ylim(-0.05, 1.05)
        ax_bot.legend(fontsize=7, loc="upper left")
        ax_bot.grid(True, alpha=0.3)
        if cond == "nonstationary":
            ax_bot.axvline(CLIMATE_SWITCH_STEP, color="red", ls="--", lw=1.2,
                           alpha=0.7, label="climate switch")
            ax_bot.legend(fontsize=7, loc="upper left")

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Figure: {out_path}")


# ---------------------------------------------------------------------------
# CSV output
# ---------------------------------------------------------------------------

def _save_csv(adapt_results: list[dict], out_path: str) -> None:
    """Save adaptive results to CSV."""
    header = "method,condition,eta,w_init,ucum_mean,ucum_sd,pfail,w_mean,w_final"
    lines = [header]
    for r in adapt_results:
        cond = "stationary" if r["stationary"] else "nonstationary"
        lines.append(
            f"{r['name']},{cond},{r['eta']:.2f},{r['w_init']:.2f},"
            f"{r['ucum_mean']:.2f},{r['ucum_sd']:.2f},{r['pfail']:.4f},"
            f"{r['w_mean']:.4f},{r['w_final']:.4f}"
        )
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  CSV: {out_path}")


# ---------------------------------------------------------------------------
# Report output
# ---------------------------------------------------------------------------

def _save_report(
    fixed_records: list[dict],
    adapt_results: list[dict],
    out_path: str,
) -> None:
    """Write a Markdown summary report."""
    lines = [
        "# Adaptive w Trade-off Analysis — Benchmark 1",
        "**Date:** 2026-04-24  ",
        f"**N_MC = {N_MC}  T = {T}  γ = {GAMMA}  SEED = {SEED}**  ",
        "**Method:** ELS_Phil_Adapt and ELS_Int_Adapt (els_adapt.py, Idea 3.1)**  ",
        "",
        "## 1. Fixed-w Reference (from sensitivity_w_results.csv)",
        "",
        "| Method | Condition | w | U_cum | SD | P_fail |",
        "|---|---|---|---|---|---|",
    ]
    for r in fixed_records:
        lines.append(
            f"| {r['method']} | {r['condition']} | {r['w']:.2f} "
            f"| {r['ucum_mean']:.1f} | {r['ucum_sd']:.1f} | {r['pfail']:.3f} |"
        )

    lines += [
        "",
        "## 2. Adaptive w Results (ELS_Phil_Adapt / ELS_Int_Adapt)",
        "",
        "| Method | Condition | η | w_init | U_cum | SD | P_fail | w_mean | w_final |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in sorted(adapt_results, key=lambda x: (x["name"], x["stationary"], x["eta"])):
        cond = "stationary" if r["stationary"] else "nonstationary"
        lines.append(
            f"| {r['name']} | {cond} | {r['eta']:.1f} | {r['w_init']:.2f} "
            f"| {r['ucum_mean']:.1f} | {r['ucum_sd']:.1f} | {r['pfail']:.3f} "
            f"| {r['w_mean']:.3f} | {r['w_final']:.3f} |"
        )

    lines += [
        "",
        "## 3. Reference Values (run_benchmark.py, N_MC=200)",
        "",
        "| Method | Stationary U_cum | NS U_cum | Stat P_fail | NS P_fail |",
        "|---|---|---|---|---|",
        "| SARSOP | 1707.0 | 1561.9 | 0.405 | 0.650 |",
        "| AlwaysRestricted | 1439.2 | 1356.2 | 0.465 | 0.660 |",
        "| ELS_Phil (w=0) | 1054.7 | 976.5 | 0.855 | 0.960 |",
        "| ELS_Int (w=0) | 947.6 | 838.8 | 0.885 | 0.960 |",
    ]

    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  Report: {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(n_mc: int = N_MC) -> None:
    t_start = time.time()

    print("=" * 72)
    print("sensitivity_w_adapt.py — Adaptive w Trade-off Curve (Benchmark 1)")
    print(f"  N_MC={n_mc}  T={T}  γ={GAMMA}  SEED={SEED}")
    print(f"  eta values : {ETA_VALUES}  w_init={W_INIT}")
    print("=" * 72)

    # ------------------------------------------------------------------
    # 1. Load existing fixed-w results
    # ------------------------------------------------------------------
    fixed_csv = os.path.join(OUTPUT_DIR, "sensitivity_w_results.csv")
    print(f"\n[1] Loading fixed-w reference from {fixed_csv}")
    if not os.path.exists(fixed_csv):
        print("    WARNING: sensitivity_w_results.csv not found. "
              "Run sensitivity_w.py first.")
        fixed_records = []
    else:
        fixed_records = _load_fixed_w_results(fixed_csv)
        print(f"    Loaded {len(fixed_records)} fixed-w records.")

    # ------------------------------------------------------------------
    # 2. Run adaptive variants
    # ------------------------------------------------------------------
    print("\n[2] Running adaptive variants ...")
    print(f"  {'Method':<22}  {'Cond':<6}  {'U_cum':>14}  {'P_fail':>8}  "
          f"{'w_mean':>7}  {'w_final':>8}")
    print(f"  {'-'*72}")

    ADAPT_DEFS = [
        ("ELS_Phil_Adapt", ELSPhilAdapt),
        ("ELS_Int_Adapt",  ELSIntAdapt),
    ]

    adapt_results = []
    m_base = M_IDX_BASE    # 200

    for eta_idx, eta in enumerate(ETA_VALUES):
        print(f"\n  η = {eta:.1f}")

        for m_sub, (name, cls) in enumerate(ADAPT_DEFS):
            m_idx = m_base + eta_idx * len(ADAPT_DEFS) + m_sub

            for cond in CONDITIONS:
                stationary = (cond == "stationary")

                # Fresh policy per (eta, method, condition)
                if name == "ELS_Phil_Adapt":
                    policy = cls(w_init=W_INIT, eta=eta)
                else:
                    policy = cls(seed=SEED, w_init=W_INIT, eta=eta)

                res = _run_adapt_mc(name, policy, stationary, m_idx, n_mc)
                res["eta"]    = eta
                res["w_init"] = W_INIT
                adapt_results.append(res)

    elapsed = time.time() - t_start
    print(f"\n  [Adaptive runs complete: {elapsed:.1f}s]")

    # ------------------------------------------------------------------
    # 3. Save outputs
    # ------------------------------------------------------------------
    print("\n[3] Saving outputs ...")

    csv_path    = os.path.join(OUTPUT_DIR, "sensitivity_w_adapt_results.csv")
    report_path = os.path.join(OUTPUT_DIR, "sensitivity_w_adapt_report.md")
    fig_path    = os.path.join(IMAGE_DIR,  "fig_w_adapt_tradeoff.png")

    _save_csv(adapt_results, csv_path)
    _save_report(fixed_records, adapt_results, report_path)

    # ------------------------------------------------------------------
    # 4. Generate figure
    # ------------------------------------------------------------------
    print("\n[4] Generating trade-off figure ...")
    try:
        _make_figure(fixed_records, adapt_results, fig_path)
    except Exception as exc:
        print(f"  WARNING: figure generation failed: {exc}")

    print(f"\n{'='*72}")
    print(f"sensitivity_w_adapt.py — complete  ({time.time() - t_start:.1f}s)")
    print(f"{'='*72}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ELS adaptive-w trade-off analysis")
    parser.add_argument("--n-mc", type=int, default=N_MC,
                        help=f"Override N_MC (default: {N_MC})")
    args = parser.parse_args()
    main(n_mc=args.n_mc)
