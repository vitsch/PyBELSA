# =============================================================================
# figures.py  —  Publication-Quality Figures for Benchmark 9
# Project  : ELS_NEW / P_Base  (Benchmark 9 — Indus Basin / HKH Glacial Meltwater Recharge)
# Plan ref : experiment_plan.md §5 Step 6
# Date     : 2026-04-25
# Usage    : python scr/figures_b2.py  (in P_Base2/scr/)
# Inputs   : output/raw_results.npz
# Outputs  : image/fig1_b9_ucum_comparison.png
#            image/fig2_b9_pfail.png
#            image/fig3_b9_nonstationarity.png
#            image/fig4_b9_climate_scenarios.png
#            image/convergence_check_b9.png
# All figures saved at 300 dpi PNG.
# =============================================================================

import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")                 # non-interactive backend (no display needed)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from pomdp_env_b9 import T, GAMMA, SEED, FAILURE_STATE, 999
from stats_analysis import (
    run_analysis, block_bootstrap_ci,
    N_BOOT, BLOCK_SIZE, SEED as STAT_SEED,
    BASELINES_FOR_TEST, ELS_INT,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
NPZ_PATH   = os.path.join(os.path.dirname(_HERE), "output", "raw_results_b9.npz")
IMAGE_DIR  = os.path.join(os.path.dirname(_HERE), "image")
os.makedirs(IMAGE_DIR, exist_ok=True)

DPI        = 300
CONDITIONS = ["stationary", "nonstationary"]

# ---------------------------------------------------------------------------
# Colour / style palette
# ---------------------------------------------------------------------------
# ELS methods: warm   |  Markovian planners: blues   |  others: neutrals
METHOD_COLORS = {
    "ELS_Phil":        "#E07B39",   # orange
    "ELS_Pres":        "#C94040",   # red
    "ELS_Int":         "#8B1A1A",   # dark red
    "ELS_Phil_T":      "#F0A500",   # amber  (hybrid T-variant, Priority 2)
    "ELS_Int_T":       "#A0522D",   # sienna (hybrid T-variant, Priority 2)
    "SARSOP":          "#1A5276",   # deep navy
    "PBVI":            "#2980B9",   # medium blue
    "SDP_S":           "#1A8A6C",   # teal
    "SDP_NS":          "#27AE60",   # green
    "MPC":             "#6C3483",   # purple
    "RDM":             "#884EA0",   # light purple
    "InfoGap":         "#7F8C8D",   # grey
    "AlwaysRestricted":"#BDC3C7",   # light grey
    "MyopicEU":        "#2C3E50",   # charcoal
    "SARSOP_Misspec":  "#5D8AA8",   # steel blue (misspec ablation)
    "SDP_S_Misspec":   "#3B9A57",   # hunter green (misspec ablation)
}

# Short display labels
SHORT_LABEL = {
    "ELS_Phil":        "ELS-Phil",
    "ELS_Pres":        "ELS-Pres",
    "ELS_Int":         "ELS-Int",
    "ELS_Phil_T":      "ELS-Phil-T",
    "ELS_Int_T":       "ELS-Int-T",
    "SARSOP":          "SARSOP",
    "PBVI":            "PBVI",
    "SDP_S":           "SDP-S",
    "SDP_NS":          "SDP-NS",
    "MPC":             "MPC",
    "RDM":             "RDM",
    "InfoGap":         "Info-gap",
    "AlwaysRestricted":"Always-R",
    "MyopicEU":        "Oracle",
    "SARSOP_Misspec":  "SARSOP-M",
    "SDP_S_Misspec":   "SDP-S-M",
}

COND_LABEL  = {"stationary": "long-term average dynamics (base)", "nonstationary": "conduit desiccation (shifted)"}
COND_HATCH  = {"stationary": "",           "nonstationary": "///"}
COND_ALPHA  = {"stationary": 0.85,         "nonstationary": 0.65}

# Global font sizes
TITLE_FS  = 11
LABEL_FS  = 10
TICK_FS   = 9
LEGEND_FS = 9


def _savefig(fig, fname: str) -> str:
    path = os.path.join(IMAGE_DIR, fname)
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    return path


def _style_ax(ax, grid_axis="y"):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if grid_axis:
        ax.grid(axis=grid_axis, linestyle="--", linewidth=0.5, alpha=0.6, zorder=0)


# ===========================================================================
# Fig 1 — U_cum comparison (grouped bar with bootstrap CIs)
# ===========================================================================

def fig1_ucum(res: dict) -> str:
    """
    Grouped horizontal bar chart of mean U_cum per method × condition.
    Methods sorted descending by nonstationary mean U_cum.
    Error bars = 95 % bootstrap CI.
    """
    methods    = res["methods"]
    raw        = res["raw"]
    ci         = res["ci"]

    # Sort by nonstationary mean (ascending for horizontal bar left→right)
    order = sorted(methods, key=lambda m: raw[m]["nonstationary"]["ucum"].mean())
    n = len(order)

    fig, axes = plt.subplots(1, 2, figsize=(13, 6), sharey=True)
    fig.subplots_adjust(wspace=0.05)

    for ax, cond in zip(axes, CONDITIONS):
        ypos  = np.arange(n)
        means = [raw[m][cond]["ucum"].mean() for m in order]
        los   = [ci[m][cond]["ucum"][0]      for m in order]
        his   = [ci[m][cond]["ucum"][1]      for m in order]
        errs  = [[m - l for m, l in zip(means, los)],
                 [h - m for m, h in zip(means, his)]]
        colors = [METHOD_COLORS[m] for m in order]

        bars = ax.barh(ypos, means, xerr=errs, color=colors,
                       edgecolor="white", linewidth=0.5,
                       error_kw=dict(ecolor="black", capsize=3, lw=1.2),
                       alpha=0.88, zorder=2)

        ax.set_yticks(ypos)
        ax.set_yticklabels(
            [SHORT_LABEL[m] for m in order],
            fontsize=TICK_FS,
        )
        ax.set_xlabel("Mean U_cum  ($/ML-equiv, discounted (B2 MAR))", fontsize=LABEL_FS)
        ax.set_title(COND_LABEL[cond], fontsize=TITLE_FS, fontweight="bold")
        ax.axvline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.4)
        _style_ax(ax, grid_axis="x")

        # Annotate InfoGap separately (tiny value, bar barely visible)
        ig_idx  = order.index("InfoGap")
        ig_mean = means[ig_idx]
        ax.text(ig_mean + 20, ig_idx, f"{ig_mean:.0f}",
                va="center", ha="left", fontsize=8, color="grey")

    axes[0].set_ylabel("Policy", fontsize=LABEL_FS)

    # Colour legend (ELS vs planners vs others)
    els_patch   = mpatches.Patch(color="#C94040", label="ELS methods")
    plan_patch  = mpatches.Patch(color="#1A5276", label="Markovian planners")
    other_patch = mpatches.Patch(color="#7F8C8D", label="Heuristic / extreme")
    fig.legend(handles=[els_patch, plan_patch, other_patch],
               loc="lower center", ncol=3, fontsize=LEGEND_FS,
               bbox_to_anchor=(0.5, -0.04), frameon=False)

    fig.suptitle("Fig 1 — Discounted Cumulative Reward (B2 MAR) by Policy and Condition",
                 fontsize=TITLE_FS + 1, y=1.01)
    return _savefig(fig, "fig1_b9_ucum_comparison.png")


# ===========================================================================
# Fig 2 — P_fail and MTTF comparison
# ===========================================================================

def fig2_pfail(res: dict) -> str:
    """
    Two-panel bar chart: P_fail (left) and MTTF (right) per method × condition.
    """
    methods = res["methods"]
    raw     = res["raw"]
    ci      = res["ci"]

    # Sort by stationary P_fail ascending
    order = sorted(methods, key=lambda m: raw[m]["stationary"]["pfail"].mean())
    n     = len(order)
    x     = np.arange(n)
    w     = 0.35   # bar width

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.subplots_adjust(wspace=0.35)

    # ---- Subplot 1: P_fail ----
    ax = axes[0]
    for c_idx, cond in enumerate(CONDITIONS):
        means  = [raw[m][cond]["pfail"].mean() for m in order]
        los    = [ci[m][cond]["pfail"][0]       for m in order]
        his    = [ci[m][cond]["pfail"][1]        for m in order]
        errs   = [[m - l for m, l in zip(means, los)],
                  [h - m for m, h in zip(means, his)]]
        shift  = (c_idx - 0.5) * w
        colors = [METHOD_COLORS[m] for m in order]
        hatch  = COND_HATCH[cond]
        ax.bar(x + shift, means, width=w, color=colors,
               hatch=hatch, alpha=COND_ALPHA[cond], edgecolor="white",
               linewidth=0.4, yerr=errs,
               error_kw=dict(ecolor="black", capsize=2, lw=0.9),
               label=COND_LABEL[cond], zorder=2)

    ax.set_xticks(x)
    ax.set_xticklabels([SHORT_LABEL[m] for m in order],
                       rotation=40, ha="right", fontsize=TICK_FS)
    ax.set_ylabel("P_fail  (fraction of episodes)", fontsize=LABEL_FS)
    ax.set_title("(a) Probability of Aquifer Failure", fontsize=TITLE_FS)
    ax.set_ylim(0, 1.1)
    ax.axhline(0.5, color="grey", linestyle=":", lw=0.8, alpha=0.6)
    _style_ax(ax)

    stat_patch  = mpatches.Patch(facecolor="grey", alpha=0.85,
                                  label="Stationary")
    ns_patch    = mpatches.Patch(facecolor="grey", alpha=0.65, hatch="///",
                                  label="Non-stationary")
    ax.legend(handles=[stat_patch, ns_patch], fontsize=LEGEND_FS, frameon=False)

    # ---- Subplot 2: MTTF ----
    ax = axes[1]
    for c_idx, cond in enumerate(CONDITIONS):
        mttf_arr = [raw[m][cond]["mttf"] for m in order]
        means    = [float(np.nanmean(a)) if np.any(~np.isnan(a)) else 0.0
                    for a in mttf_arr]
        # Bootstrap CI on non-NaN MTTF values
        ci_mttf = []
        for a in mttf_arr:
            a_clean = a[~np.isnan(a)]
            if len(a_clean) >= BLOCK_SIZE:
                lo, hi = block_bootstrap_ci(a_clean, seed=SEED + 5555)
                ci_mttf.append((lo, hi))
            elif len(a_clean) > 0:
                ci_mttf.append((np.nanmean(a_clean), np.nanmean(a_clean)))
            else:
                ci_mttf.append((0.0, 0.0))
        errs = [[m - l for m, (l, _) in zip(means, ci_mttf)],
                [h - m for m, (_, h) in zip(means, ci_mttf)]]
        errs[0] = [max(0, e) for e in errs[0]]
        errs[1] = [max(0, e) for e in errs[1]]
        shift  = (c_idx - 0.5) * w
        colors = [METHOD_COLORS[m] for m in order]
        hatch  = COND_HATCH[cond]
        ax.bar(x + shift, means, width=w, color=colors,
               hatch=hatch, alpha=COND_ALPHA[cond], edgecolor="white",
               linewidth=0.4, yerr=errs,
               error_kw=dict(ecolor="black", capsize=2, lw=0.9),
               zorder=2)

    ax.set_xticks(x)
    ax.set_xticklabels([SHORT_LABEL[m] for m in order],
                       rotation=40, ha="right", fontsize=TICK_FS)
    ax.set_ylabel("MTTF  (steps to first failure)", fontsize=LABEL_FS)
    ax.set_title("(b) Mean Time to First Failure", fontsize=TITLE_FS)
    _style_ax(ax)
    ax.legend(handles=[stat_patch, ns_patch], fontsize=LEGEND_FS, frameon=False)

    fig.suptitle("Fig 2 — Storage Failure Metrics (B2 MAR) by Policy and Condition",
                 fontsize=TITLE_FS + 1)
    return _savefig(fig, "fig2_b9_pfail.png")


# ===========================================================================
# Fig 3 — Per-step mean reward trajectory (nonstationary condition)
# ===========================================================================

def fig3_nonstationarity(npz) -> str:
    """
    Line plot of mean per-step reward at each t for selected methods,
    nonstationary condition.  Vertical dashed line at t = 999.

    Shows step-level undiscounted reward to make the regime effect visible.
    """
    HIGHLIGHT = ["ELS_Int", "ELS_Phil", "SDP_NS", "MPC", "SARSOP"]
    LINESTYLES = {
        "ELS_Int":  ("-",  2.2),
        "ELS_Phil": ("--", 1.8),
        "SDP_NS":   ("-",  1.8),
        "MPC":      (":",  1.6),
        "SARSOP":   ("-.", 1.8),
    }

    steps = np.arange(T)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=False)
    fig.subplots_adjust(wspace=0.35)

    for ax, cond in zip(axes, CONDITIONS):
        for name in HIGHLIGHT:
            rewards = npz[f"{name}__{cond}__rewards"]   # (N_MC, T)
            mean_r  = rewards.mean(axis=0)
            se_r    = rewards.std(axis=0, ddof=1) / np.sqrt(rewards.shape[0])
            ls, lw  = LINESTYLES[name]
            color   = METHOD_COLORS[name]
            ax.plot(steps, mean_r, linestyle=ls, linewidth=lw,
                    color=color, label=SHORT_LABEL[name], zorder=3)
            ax.fill_between(steps,
                            mean_r - 1.96 * se_r,
                            mean_r + 1.96 * se_r,
                            alpha=0.10, color=color, zorder=1)

        ax.axvline(999, color="firebrick", linestyle="--",
                   linewidth=1.2, alpha=0.75, label=f"SSP585 onset (t={999})",
                   zorder=4)

        ax.set_xlabel("Time step  t", fontsize=LABEL_FS)
        ax.set_ylabel("Mean reward  R(a_t, θ_{t+1})", fontsize=LABEL_FS)
        ax.set_title(COND_LABEL[cond], fontsize=TITLE_FS, fontweight="bold")
        ax.set_xlim(0, T - 1)
        _style_ax(ax)

    axes[0].legend(fontsize=LEGEND_FS, frameon=False, ncol=2)

    fig.suptitle("Fig 3 — Per-Step Mean Reward Trajectory",
                 fontsize=TITLE_FS + 1)
    return _savefig(fig, "fig3_b9_nonstationarity.png")


# ===========================================================================
# Fig 4 — Climate scenario value (EVOI B2)
# ===========================================================================

def fig4_evoi(res: dict) -> str:
    """
    Two-panel bar chart showing:
    (a) Absolute U_cum means for SDP_S, SDP_NS, ELS_Int, ELS_Phil per condition
        with 95 % CI error bars — quantifies ELS-vs-SDP gap.
    (b) EVOI = U_cum(SDP_NS) − U_cum(SDP_S) per condition,
        with 95 % bootstrap CI of the difference.
    """
    raw = res["raw"]
    ci  = res["ci"]

    FOCAL = ["ELS_Phil", "ELS_Int", "SDP_S", "SDP_NS"]
    x     = np.arange(len(FOCAL))
    w     = 0.35

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    fig.subplots_adjust(wspace=0.38)

    # ---- (a) Absolute U_cum ----
    ax = axes[0]
    for c_idx, cond in enumerate(CONDITIONS):
        means  = [raw[m][cond]["ucum"].mean() for m in FOCAL]
        los    = [ci[m][cond]["ucum"][0]       for m in FOCAL]
        his    = [ci[m][cond]["ucum"][1]        for m in FOCAL]
        errs   = [[m - l for m, l in zip(means, los)],
                  [h - m for m, h in zip(means, his)]]
        shift  = (c_idx - 0.5) * w
        colors = [METHOD_COLORS[m] for m in FOCAL]
        hatch  = COND_HATCH[cond]
        ax.bar(x + shift, means, width=w, color=colors,
               hatch=hatch, alpha=COND_ALPHA[cond], edgecolor="white",
               linewidth=0.4, yerr=errs,
               error_kw=dict(ecolor="black", capsize=3, lw=1.0),
               label=COND_LABEL[cond], zorder=2)

    ax.set_xticks(x)
    ax.set_xticklabels([SHORT_LABEL[m] for m in FOCAL], fontsize=TICK_FS)
    ax.set_ylabel("Mean U_cum  (£/ML-equiv)", fontsize=LABEL_FS)
    ax.set_title("(a) ELS vs SDP Absolute Performance", fontsize=TITLE_FS)
    stat_patch = mpatches.Patch(facecolor="grey", alpha=0.85, label="Stationary")
    ns_patch   = mpatches.Patch(facecolor="grey", alpha=0.65, hatch="///",
                                 label="Non-stationary")
    ax.legend(handles=[stat_patch, ns_patch], fontsize=LEGEND_FS, frameon=False)
    _style_ax(ax)

    # ---- (b) EVOI bars ----
    ax = axes[1]
    evoi_info = res["evoi"]
    cond_labels = [COND_LABEL[c] for c in CONDITIONS]
    evoi_means  = [evoi_info[c]["mean"]   for c in CONDITIONS]
    evoi_los    = [evoi_info[c]["ci_lo"]  for c in CONDITIONS]
    evoi_his    = [evoi_info[c]["ci_hi"]  for c in CONDITIONS]
    errs_lo = [max(0, m - l) for m, l in zip(evoi_means, evoi_los)]
    errs_hi = [max(0, h - m) for m, h in zip(evoi_means, evoi_his)]

    bar_colors = ["#1A8A6C", "#27AE60"]
    bars = ax.bar([0, 1], evoi_means, color=bar_colors, alpha=0.85,
                  width=0.5, edgecolor="white", linewidth=0.5,
                  yerr=[errs_lo, errs_hi],
                  error_kw=dict(ecolor="black", capsize=6, lw=1.5),
                  zorder=2)

    ax.set_xticks([0, 1])
    ax.set_xticklabels(cond_labels, fontsize=TICK_FS)
    ax.set_ylabel("EVOI  (£/ML-equiv)", fontsize=LABEL_FS)
    ax.set_title("(b) EVOI: E[SDP-NS] − E[SDP-S]", fontsize=TITLE_FS)
    ax.axhline(0, color="black", linewidth=0.9, linestyle="--", alpha=0.5)
    _style_ax(ax)

    # Annotate mean values
    for i, (m, cond) in enumerate(zip(evoi_means, CONDITIONS)):
        ax.text(i, m + (10 if m >= 0 else -25),
                f"{m:+.1f}", ha="center", fontsize=9, fontweight="bold")

    ax.text(0.5, 0.03,
            "Negative EVOI: EM estimation noise exceeds\nregime-detection benefit (CI includes 0)",
            transform=ax.transAxes, ha="center", fontsize=7.5,
            color="grey", style="italic")

    fig.suptitle("Fig 4 — Climate Scenario Value (B2 MAR) (EVOI) Decomposition",
                 fontsize=TITLE_FS + 1)
    return _savefig(fig, "fig4_b9_climate_scenarios.png")


# ===========================================================================
# Fig 5 — Convergence check (SE vs N_MC)
# ===========================================================================

def fig5_convergence(res: dict) -> str:
    """
    Line plot of SE(mean U_cum) vs N_MC for selected methods,
    both conditions.  Confirms N_MC = 200 is sufficient.
    """
    FOCAL     = ["ELS_Phil", "ELS_Pres", "ELS_Int", "SARSOP", "SDP_S", "AlwaysRestricted"]
    NS_VALS   = [50, 100, 150, 200]
    LINESTYLES_CONV = {
        "ELS_Phil":        "--",
        "ELS_Pres":        "--",
        "ELS_Int":         "--",
        "SARSOP":          "-",
        "SDP_S":           "-",
        "AlwaysRestricted":"-.",
    }

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=False)
    fig.subplots_adjust(wspace=0.32)

    for ax, cond in zip(axes, CONDITIONS):
        for name in FOCAL:
            ucum = res["raw"][name][cond]["ucum"]
            ses  = [ucum[:n].std(ddof=1) / np.sqrt(n) for n in NS_VALS]
            ls   = LINESTYLES_CONV[name]
            color = METHOD_COLORS[name]
            ax.plot(NS_VALS, ses, linestyle=ls, linewidth=1.8,
                    marker="o", markersize=4, color=color,
                    label=SHORT_LABEL[name])

        ax.axvline(200, color="grey", linestyle=":", lw=0.8, alpha=0.6)
        ax.set_xlabel("N_MC (episodes)", fontsize=LABEL_FS)
        ax.set_ylabel("SE of mean U_cum", fontsize=LABEL_FS)
        ax.set_title(COND_LABEL[cond], fontsize=TITLE_FS, fontweight="bold")
        ax.set_xticks(NS_VALS)
        _style_ax(ax)
        if cond == CONDITIONS[0]:
            ax.legend(fontsize=LEGEND_FS - 1, frameon=False, ncol=2)

    fig.suptitle("Fig 5 — Convergence Check: SE of Mean U_cum vs N_MC",
                 fontsize=TITLE_FS + 1)
    return _savefig(fig, "convergence_check_b9.png")


# ===========================================================================
# Main
# ===========================================================================

def main() -> None:
    import time
    t0 = time.time()
    print("=" * 64)
    print("figures.py — Publication-Quality Figures (300 dpi PNG)")
    print(f"  NPZ: {NPZ_PATH}")
    print(f"  Output: {IMAGE_DIR}")
    print("=" * 64)

    print("Loading NPZ and running analysis...", flush=True)
    npz = np.load(NPZ_PATH, allow_pickle=False)
    res = run_analysis(NPZ_PATH)

    figs = [
        ("Fig 1 — U_cum comparison",          lambda: fig1_ucum(res)),
        ("Fig 2 — P_fail / MTTF",             lambda: fig2_pfail(res)),
        ("Fig 3 — Per-step reward trajectory", lambda: fig3_nonstationarity(npz)),
        ("Fig 4 — Climate scenario value (EVOI B2)",         lambda: fig4_evoi(res)),
        ("Fig 5 — Convergence check",          lambda: fig5_convergence(res)),
    ]

    saved = []
    for label, fn in figs:
        print(f"  Rendering {label}...", end=" ", flush=True)
        path = fn()
        size = os.path.getsize(path) // 1024
        print(f"{os.path.basename(path)}  ({size} KB)")
        saved.append(path)

    print(f"\nDone in {time.time() - t0:.1f}s")
    print("Saved figures:")
    for p in saved:
        print(f"  {p}")
    print("=" * 64)


if __name__ == "__main__":
    main()
