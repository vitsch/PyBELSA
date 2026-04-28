# =============================================================================
# sensitivity_w_adapt_b7.py  —  Adaptive w Trade-off Curve (Benchmark 6 — NCP)
# Project  : ELS_NEW / P_Base6  (Coastal Saltwater Intrusion-Based)
# Plan ref : BDT_concept_impr.md §3.1; P_Base/docs/summary_w_update_B4.md
# Ported   : from P_Base4/scr/sensitivity_w_adapt_b4.py — B5 imports and paths
# Date     : 2026-04-25
# Usage    : python scr/sensitivity_w_adapt_b7.py
# Outputs  : output/sensitivity_w_adapt_results_b7.csv
#            output/sensitivity_w_adapt_report_b7.md
#            output/sensitivity_w_report_b6.md  (fixed-w reference, if not present)
#            image/fig_w_adapt_tradeoff_b7.png
# =============================================================================
"""
Adaptive w trade-off analysis for Benchmark 7 (Coastal Saltwater Intrusion).

B5 context: The highest T-uncertainty benchmark (U_T ≈ 0.7–0.9).
GRACE observation noise (σ=45 mm WE) combined with structurally uncertain NCP
depletion dynamics (unknown pumping behaviour, soil/surface water confounding)
makes T_B5_STAT the least reliable model in the suite.  The adaptive mechanism
is predicted to converge to w_mean < B4, potentially approaching w_init=0.5,
representing near-degenerate T-trust where observations dominate over T-prediction.

Predicted behaviour:
  - η=0.1: w_mean ≈ 0.45–0.55 (cannot distinguish T-signal from GRACE noise)
  - η=0.5: w_mean ≈ 0.55–0.65 (slow convergence upward but noisy)
  - Fixed-w spread < 15 pts (flattest plateau in suite — U_T signature)

Seeding: M_IDX_BASE=200 to avoid collision with run_benchmark_b6 (0–15)
         and sensitivity_w_b7 (100–109).
"""

import os, sys, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_HERE  = os.path.dirname(os.path.abspath(__file__))
_BASE7 = os.path.dirname(_HERE)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from pomdp_env_b7 import (
    N, M, N_OBS, T, GAMMA, SEED, CLIMATE_SWITCH_STEP, FAILURE_STATE,
    R, T_stat, T_shift, LIKELIHOOD,
    N_MC as DEFAULT_N_MC,
)
from els_methods import ELSInt
from els_adapt_b7 import ELSPhilAdapt, ELSIntAdapt

N_MC       = DEFAULT_N_MC
CONDITIONS = ["stationary", "nonstationary"]
ETA_VALUES = [0.1, 0.5, 1.0]
W_INIT     = 0.5
M_IDX_BASE = 200
OUTPUT_DIR = os.path.join(_BASE7, "output")
IMAGE_DIR  = os.path.join(_BASE7, "image")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR,  exist_ok=True)

REFS: dict[str, dict[str, float]] = {
    "SARSOP":           {"stationary": float("nan"), "nonstationary": float("nan")},
    "AlwaysRestricted": {"stationary": float("nan"), "nonstationary": float("nan")},
    "ELS_Phil":         {"stationary": float("nan"), "nonstationary": float("nan")},
    "ELS_Int":          {"stationary": float("nan"), "nonstationary": float("nan")},
}


def _try_load_refs() -> None:
    npz_path = os.path.join(OUTPUT_DIR, "raw_results_b7.npz")
    if not os.path.exists(npz_path):
        return
    try:
        data = np.load(npz_path, allow_pickle=True)
        discount = GAMMA ** np.arange(T)
        for method in ["SARSOP", "AlwaysRestricted", "ELS_Phil", "ELS_Int"]:
            for cond in ["stationary", "nonstationary"]:
                key = f"{method}_{cond}_rewards"
                if key in data:
                    ucum = float((data[key] * discount).sum(axis=1).mean())
                    REFS[method][cond] = ucum
    except Exception:
        pass


def _run_adapt_episode(policy, stationary, ep_rng, els_seed=None):
    if isinstance(policy, ELSInt):
        policy.reset(seed=els_seed)
    else:
        policy.reset()

    b       = policy.initial_belief()
    s       = int(ep_rng.integers(0, N))
    rewards = np.empty(T, dtype=float)
    states  = np.empty(T, dtype=np.int8)

    for t in range(T):
        a      = policy.act(b, t)
        T_use  = T_stat if (stationary or t < CLIMATE_SWITCH_STEP) else T_shift
        s_next = int(ep_rng.choice(N, p=T_use[a, s]))
        obs_i  = int(ep_rng.choice(N_OBS, p=LIKELIHOOD[s_next]))
        b      = policy.phys_belief_update(b, obs_i, action=a)
        rewards[t] = float(R[a, s_next])
        states[t]  = np.int8(s_next)
        s = s_next

    return rewards, states


def _run_adapt_mc(name, policy, stationary, m_idx, n_mc, verbose=True):
    c_idx    = int(not stationary)
    discount = GAMMA ** np.arange(T)
    all_ucum   = np.empty(n_mc, dtype=float)
    all_pfail  = np.empty(n_mc, dtype=bool)
    all_w_traj = []

    for ep in range(n_mc):
        ep_rng   = np.random.default_rng([SEED, m_idx, c_idx, ep])
        els_seed = int(
            np.random.default_rng([SEED + 7000, m_idx, ep]).integers(0, 2**31)
        ) if isinstance(policy, ELSInt) else None

        rewards, states = _run_adapt_episode(policy, stationary, ep_rng, els_seed)
        all_ucum[ep]  = float((rewards * discount).sum())
        all_pfail[ep] = bool(np.any(states == FAILURE_STATE))
        if hasattr(policy, "w_trajectory") and len(policy.w_trajectory) == T:
            all_w_traj.append(np.array(policy.w_trajectory))

    ucum_mean = float(all_ucum.mean())
    ucum_sd   = float(all_ucum.std())
    pfail     = float(all_pfail.mean())

    if all_w_traj:
        w_mat       = np.stack(all_w_traj, axis=0)
        w_mean_ep   = float(w_mat.mean())
        w_final     = float(w_mat[:, -1].mean())
        w_traj_mean = w_mat.mean(axis=0)
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

    return {"name": name, "stationary": stationary,
            "ucum_mean": ucum_mean, "ucum_sd": ucum_sd,
            "pfail": pfail, "w_mean": w_mean_ep,
            "w_final": w_final, "w_traj_mean": w_traj_mean}


def _load_fixed_w_results(csv_path):
    records = []
    with open(csv_path) as f:
        header = f.readline().strip().split(",")
        for line in f:
            vals = line.strip().split(",")
            rec  = {k: v for k, v in zip(header, vals)}
            rec["w"]         = float(rec["w"])
            rec["ucum_mean"] = float(rec["ucum_mean"])
            rec["ucum_sd"]   = float(rec["ucum_sd"])
            rec["pfail"]     = float(rec["pfail"])
            rec["mttf_mean"] = float(rec["mttf_mean"]) \
                if rec["mttf_mean"] != "nan" else float("nan")
            records.append(rec)
    return records


def _make_figure(fixed_records, adapt_results, out_path):
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.suptitle(
        "Adaptive vs Fixed Model-Trust Weight  (Benchmark 6 — Coastal Saltwater Intrusion, N_MC=200)",
        fontsize=12, fontweight="bold",
    )
    C_PHIL_T = "#E07B39"; C_INT_T = "#2980B9"
    C_PHIL_A = "#D62728"; C_INT_A = "#1A5276"
    C_ALWAYS = "#95A5A6"; C_PHIL_B = "#E07B39"

    for col, cond in enumerate(["stationary", "nonstationary"]):
        ax_top = axes[0, col]
        ax_bot = axes[1, col]

        for method, color in [("ELS_Phil_T", C_PHIL_T), ("ELS_Int_T", C_INT_T)]:
            recs = sorted(
                [r for r in fixed_records if r["method"] == method and r["condition"] == cond],
                key=lambda x: x["w"],
            )
            if not recs:
                continue
            ws    = [r["w"]         for r in recs]
            ucums = [r["ucum_mean"] for r in recs]
            sds   = [r["ucum_sd"]   for r in recs]
            ax_top.plot(ws, ucums, marker="o", color=color, label=f"{method} (fixed w)", zorder=3)
            ax_top.fill_between(ws,
                [u - 0.5*s for u, s in zip(ucums, sds)],
                [u + 0.5*s for u, s in zip(ucums, sds)],
                color=color, alpha=0.15)

        for method, color, mk in [("ELS_Phil_Adapt", C_PHIL_A, "*"), ("ELS_Int_Adapt", C_INT_A, "*")]:
            sub = [r for r in adapt_results
                   if r["name"] == method and r["stationary"] == (cond == "stationary")]
            if not sub:
                continue
            for i, r in enumerate(sorted(sub, key=lambda x: x["ucum_mean"], reverse=True)):
                ms  = 18 if i == 0 else 10
                lbl = f"{method} (η={r['eta']:.1f})" if i == 0 else None
                ax_top.plot(r["w_mean"], r["ucum_mean"], marker=mk, markersize=ms,
                            color=color, linestyle="none", label=lbl, zorder=5,
                            markeredgecolor="black", markeredgewidth=0.8)
                ax_top.errorbar(r["w_mean"], r["ucum_mean"], yerr=r["ucum_sd"]*0.5,
                                fmt="none", color=color, capsize=4, alpha=0.6)

        for ref_name, cr, lr in [("SARSOP", C_INT_A, "SARSOP"),
                                  ("AlwaysRestricted", C_ALWAYS, "AlwaysRestricted"),
                                  ("ELS_Phil", C_PHIL_B, "ELS_Phil (w=0)")]:
            val = REFS[ref_name][cond]
            if not np.isnan(val):
                ax_top.axhline(val, color=cr, ls="--", lw=1.2, alpha=0.8, label=lr)

        cond_label = "pre-climate coastal dynamics" if cond == "stationary" \
                     else "sea-level rise shift at t=15"
        ax_top.set_title(f"Condition: {cond}  ({cond_label})", fontsize=10)
        ax_top.set_xlabel("Model-trust weight  w  (or effective mean w for adaptive)")
        ax_top.set_ylabel("U_cum (mean discounted $bn/year-equiv)")
        ax_top.set_xlim(-0.05, 1.05)
        ax_top.legend(fontsize=7, loc="lower right", ncol=2)
        ax_top.grid(True, alpha=0.3)

        for method, color in [("ELS_Phil_Adapt", C_PHIL_A), ("ELS_Int_Adapt", C_INT_A)]:
            sub = [r for r in adapt_results
                   if r["name"] == method and r["stationary"] == (cond == "stationary")]
            for r in sorted(sub, key=lambda x: x["eta"]):
                ax_bot.plot(np.arange(T), r["w_traj_mean"], color=color, alpha=0.7,
                            label=f"{method.replace('ELS_', '')} η={r['eta']:.1f}", lw=1.5)

        ax_bot.axhline(W_INIT, color="grey", ls=":", lw=1, label=f"w_init={W_INIT}")
        ax_bot.set_xlabel("Episode step  t  (annual decision year)")
        ax_bot.set_ylabel("Mean w over N_MC episodes")
        ax_bot.set_title(f"w trajectory  ({cond})", fontsize=10)
        ax_bot.set_xlim(0, T - 1)
        ax_bot.set_ylim(-0.05, 1.05)
        ax_bot.legend(fontsize=7, loc="upper left")
        ax_bot.grid(True, alpha=0.3)
        if cond == "nonstationary":
            ax_bot.axvline(CLIMATE_SWITCH_STEP, color="red", ls="--", lw=1.5,
                           alpha=0.8, label="SSP5-8.5 onset")
            ax_bot.legend(fontsize=7)

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Figure: {out_path}")


def _save_csv(adapt_results, out_path):
    header = "method,condition,eta,w_init,ucum_mean,ucum_sd,pfail,w_mean,w_final"
    lines  = [header]
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


def _save_report(fixed_records, adapt_results, out_path):
    def _fmt(v):
        return f"{v:.1f}" if not np.isnan(v) else "—"

    lines = [
        "# Adaptive w Trade-off Analysis — Benchmark 7 (Coastal Saltwater Intrusion)",
        "**Date:** 2026-04-25  ",
        f"**N_MC = {N_MC}  T = {T}  γ = {GAMMA}  SEED = {SEED}**  ",
        "**w_adapt method:** ELS_Phil_Adapt / ELS_Int_Adapt (els_adapt_b7.py)  ", "",
        "## 1. Fixed-w Reference", "",
        "| Method | Condition | w | U_cum | SD | P_fail |",
        "|---|---|---|---|---|---|",
    ]
    for r in fixed_records:
        lines.append(
            f"| {r['method']} | {r['condition']} | {r['w']:.2f} "
            f"| {r['ucum_mean']:.1f} | {r['ucum_sd']:.1f} | {r['pfail']:.3f} |"
        )
    lines += [
        "", "## 2. Adaptive w Results", "",
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
        "", "## 3. Reference Values (run_benchmark_b6.py)", "",
        "| Method | Stat U_cum | NS U_cum |", "|---|---|---|",
        f"| SARSOP | {_fmt(REFS['SARSOP']['stationary'])} | {_fmt(REFS['SARSOP']['nonstationary'])} |",
        f"| AlwaysRestricted | {_fmt(REFS['AlwaysRestricted']['stationary'])} | {_fmt(REFS['AlwaysRestricted']['nonstationary'])} |",
        f"| ELS_Phil (w=0) | {_fmt(REFS['ELS_Phil']['stationary'])} | {_fmt(REFS['ELS_Phil']['nonstationary'])} |",
    ]
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  Report: {out_path}")


def main(n_mc=N_MC):
    t_start = time.time()
    print("=" * 72)
    print("sensitivity_w_adapt_b7.py — Adaptive w Trade-off (Benchmark 7 Coastal Saltwater Intrusion)")
    print(f"  N_MC={n_mc}  T={T}  γ={GAMMA}  SEED={SEED}")
    print(f"  eta values : {ETA_VALUES}  w_init={W_INIT}")
    print("=" * 72)

    _try_load_refs()

    fixed_csv = os.path.join(OUTPUT_DIR, "sensitivity_w_results_b7.csv")
    if not os.path.exists(fixed_csv):
        print(f"\n[1] CSV not found — running sensitivity_w_b7.py ...")
        import sensitivity_w_b7
        sensitivity_w_b7.main()
    else:
        print(f"\n[1] Loading fixed-w reference from {fixed_csv}")
    fixed_records = _load_fixed_w_results(fixed_csv)
    print(f"    Loaded {len(fixed_records)} fixed-w records.")

    print("\n[2] Running adaptive variants ...")
    print(f"  {'Method':<22}  {'Cond':<6}  {'U_cum':>14}  {'P_fail':>8}  "
          f"{'w_mean':>7}  {'w_final':>8}")
    print(f"  {'-'*72}")

    ADAPT_DEFS = [("ELS_Phil_Adapt", ELSPhilAdapt), ("ELS_Int_Adapt", ELSIntAdapt)]
    adapt_results = []

    for eta_idx, eta in enumerate(ETA_VALUES):
        print(f"\n  η = {eta:.1f}")
        for m_sub, (name, cls) in enumerate(ADAPT_DEFS):
            m_idx = M_IDX_BASE + eta_idx * len(ADAPT_DEFS) + m_sub
            for cond in CONDITIONS:
                stationary = (cond == "stationary")
                policy = cls(w_init=W_INIT, eta=eta) if name == "ELS_Phil_Adapt" \
                         else cls(seed=SEED, w_init=W_INIT, eta=eta)
                res = _run_adapt_mc(name, policy, stationary, m_idx, n_mc)
                res["eta"]    = eta
                res["w_init"] = W_INIT
                adapt_results.append(res)

    elapsed = time.time() - t_start
    print(f"\n  [B7 adaptive runs complete: {elapsed:.1f}s]")

    print("\n[3] Saving outputs ...")
    _save_csv(adapt_results, os.path.join(OUTPUT_DIR, "sensitivity_w_adapt_results_b7.csv"))
    _save_report(fixed_records, adapt_results,
                 os.path.join(OUTPUT_DIR, "sensitivity_w_adapt_report_b7.md"))

    print("\n[4] Generating trade-off figure ...")
    try:
        _make_figure(fixed_records, adapt_results,
                     os.path.join(IMAGE_DIR, "fig_w_adapt_tradeoff_b7.png"))
    except Exception as exc:
        print(f"  WARNING: figure generation failed: {exc}")

    print(f"\n{'='*72}")
    print(f"sensitivity_w_adapt_b7.py — complete  ({time.time() - t_start:.1f}s)")
    print(f"{'='*72}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-mc", type=int, default=N_MC)
    args = parser.parse_args()
    main(n_mc=args.n_mc)
