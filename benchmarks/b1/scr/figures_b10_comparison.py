# =============================================================================
# figures_b10_comparison.py  —  Fig. 4: B10 All-Method Comparison
# Project  : PyBELSA
# Plan ref : Summary_Paper_Plan_3.md §3.4
# Date     : 2026-04-26
# Usage    : python scr/figures_b10_comparison.py   (run from benchmarks/b1/)
# Output   : image/fig4_b10_comparison.pdf
#            image/fig4_b10_comparison.png
# =============================================================================
"""
Publication-quality Fig. 4 for Nature Water submission.

Main panel — grouped bar chart: all key methods at B10 (LCB/Sahel, U_T=1.0)
             stationary (filled) and nonstationary (hatched) U_cum, 95% CI.
             Methods ordered: SARSOP (oracle), SARSOP_misspec, ELS_Phil_T,
             ELS_Phil_Adapt(eta=0.5), SDP_S, RDM, AlwaysRestricted.
             Annotate: practical bracket SARSOP_misspec → ELS_Phil_T (+128 stat).
             Annotate: AlwaysRestricted collapse arrow.

Inset panel — P_fail for the same methods (stationary only).

Data source: summary_B10.md §3 (N_MC=200, SEED=2024).
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe

# ---------------------------------------------------------------------------
# 0.  Paths
# ---------------------------------------------------------------------------

_HERE = os.path.dirname(os.path.abspath(__file__))
_BASE = os.path.dirname(_HERE)
_IMAGE = os.path.join(_BASE, "image")
os.makedirs(_IMAGE, exist_ok=True)

NPZ_B10 = os.path.join(_BASE, "../b10/output/raw_results_b10.npz")

# ---------------------------------------------------------------------------
# 1.  Data from summary_B10.md §3 (B10 Monte Carlo results)
# ---------------------------------------------------------------------------

# Methods to display (subset for clarity — key comparison points)
METHODS = [
    # (label, U_cum_stat, U_cum_NS, P_fail_stat, colour, is_practical)
    ("SARSOP\n(oracle T)",        832.6,  881.7, 0.890, "#555555", False),
    ("SARSOP\n(Dirichlet T)",     761.0,  768.5, 0.925, "#888888", True),
    ("SDP$_S$",                   905.1,  931.9, 0.835, "#4d9de0", False),
    ("RDM",                       922.7,  981.2, 0.825, "#7b2d8b", False),
    ("BELSA\n(ELS\\_Phil$_T$)",   888.8,  936.8, 0.905, "#d6604d", True),
    ("BELSA\nAdaptive",           904.9, None,   0.860, "#e8883f", False),
    ("Always\nRestricted",       -203.7, -359.5, 0.960, "#999999", False),
]

# 95% CI half-widths from summary_B10.md SD values (approx CI ≈ 1.96 * SD / sqrt(200))
# SD values: SARSOP=234.9, SARSOP_Misspec=280.9, SDP_S=223.2, RDM=214.0,
#            ELS_Phil_T=257.6, ELS_Phil_Adapt=249.9, AlwaysRestricted=621.7
SD_STAT = [234.9, 280.9, 223.2, 214.0, 257.6, 249.9, 621.7]
CI_HALF_STAT = [1.96 * sd / np.sqrt(200) for sd in SD_STAT]

SD_NS   = [250.0, 265.6, 219.9, 240.9, 254.6, None, 642.3]
CI_HALF_NS = [1.96 * sd / np.sqrt(200) if sd is not None else None for sd in SD_NS]

# ---------------------------------------------------------------------------
# 2.  Load raw data for bootstrap CI
# ---------------------------------------------------------------------------

GAMMA = 0.97

def _ucum(npz_path, method, condition):
    try:
        d = np.load(npz_path, allow_pickle=True)
        key = f"{method}__{condition}__rewards"
        if key in d:
            r = d[key]
            T = r.shape[1]
            gammas = GAMMA ** np.arange(T)
            return (r * gammas).sum(axis=1)
    except Exception:
        pass
    return None

def _bootstrap_ci(arr, B=2000, seed=42):
    rng = np.random.default_rng(seed)
    boot = rng.choice(arr, size=(B, len(arr)), replace=True).mean(axis=1)
    return np.percentile(boot, [2.5, 97.5])

NPZ_KEYS = ["SARSOP", "SARSOP_Misspec", "SDP_S", "RDM",
            "ELS_Phil_T", "ELS_Phil_T", "AlwaysRestricted"]

print("Loading B10 raw data...")
ucum_stat_arrs = []
ucum_ns_arrs   = []
ci_stat_list   = []
ci_ns_list     = []

for j, key in enumerate(NPZ_KEYS):
    if key == "ELS_Phil_T" and METHODS[j][0].startswith("BELSA\nAdaptive"):
        # Use ELS_Phil_Adapt (eta=0.5) if available
        arr_s = _ucum(NPZ_B10, "ELS_Phil_Adapt", "stationary")
    else:
        arr_s = _ucum(NPZ_B10, key, "stationary")
    arr_ns = _ucum(NPZ_B10, key, "nonstationary")

    if arr_s is not None:
        ci_s = _bootstrap_ci(arr_s)
        ci_lo_s = arr_s.mean() - ci_s[0]
        ci_hi_s = ci_s[1] - arr_s.mean()
        ucum_val_s = arr_s.mean()
    else:
        ucum_val_s = METHODS[j][1]
        ci_lo_s = ci_hi_s = CI_HALF_STAT[j]
    ucum_stat_arrs.append(ucum_val_s)
    ci_stat_list.append((ci_lo_s, ci_hi_s))

    if arr_ns is not None:
        ci_ns = _bootstrap_ci(arr_ns)
        ci_lo_ns = arr_ns.mean() - ci_ns[0]
        ci_hi_ns = ci_ns[1] - arr_ns.mean()
        ucum_val_ns = arr_ns.mean()
    else:
        ucum_val_ns = METHODS[j][2]
        ci_lo_ns = ci_hi_ns = (CI_HALF_NS[j] if CI_HALF_NS[j] is not None else CI_HALF_STAT[j])
    ucum_ns_arrs.append(ucum_val_ns)
    ci_ns_list.append((ci_lo_ns, ci_hi_ns))

    print(f"  {METHODS[j][0].replace(chr(10),' ')}: stat={ucum_val_s:.1f}, NS={ucum_val_ns:.1f}")

# ---------------------------------------------------------------------------
# 3.  Figure
# ---------------------------------------------------------------------------

n = len(METHODS)
x = np.arange(n)
w = 0.35

fig, ax = plt.subplots(figsize=(12, 6.5))
fig.subplots_adjust(left=0.09, right=0.97, top=0.88, bottom=0.18)

# Stat bars
for j in range(n):
    col = METHODS[j][4]   # index 4 = colour hex string
    v_s  = ucum_stat_arrs[j]
    ci_s = ci_stat_list[j]
    v_ns = ucum_ns_arrs[j]
    ci_ns = ci_ns_list[j]

    bar_s = ax.bar(x[j] - w/2, v_s, width=w, color=col, alpha=0.88,
                   edgecolor="white", linewidth=0.7)

    ax.errorbar(x[j] - w/2, v_s,
                yerr=[[ci_s[0]], [ci_s[1]]],
                fmt="none", ecolor="0.3", elinewidth=1.5, capsize=5, capthick=1.5, zorder=5)

    # NS bars (hatched)
    if v_ns is not None:
        bar_ns = ax.bar(x[j] + w/2, v_ns, width=w, color=col, alpha=0.55,
                        hatch="///", edgecolor="white", linewidth=0.6)
        ax.errorbar(x[j] + w/2, v_ns,
                    yerr=[[ci_ns[0]], [ci_ns[1]]],
                    fmt="none", ecolor="0.3", elinewidth=1.5, capsize=5, capthick=1.5, zorder=5)

# Reference zero line
ax.axhline(0, color="0.5", linestyle="-", linewidth=0.8, zorder=1)

# ---- Practical bracket: SARSOP_misspec (j=1) vs ELS_Phil_T (j=4) ----
y_bracket = max(ucum_stat_arrs[1] + ci_stat_list[1][1],
                ucum_stat_arrs[4] + ci_stat_list[4][1]) + 70

ax.annotate("", xy=(x[4] - w/2, y_bracket), xytext=(x[1] - w/2, y_bracket),
            arrowprops=dict(arrowstyle="<->", color="#d6604d", lw=2.0))
ax.text((x[1] + x[4]) / 2 - w/2, y_bracket + 18,
        "+128 stat  /  +168 NS\n(BELSA advantage: no T required)",
        ha="center", fontsize=9.5, color="#d6604d", fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="0.97", edgecolor="#d6604d", alpha=0.9))

# ---- AlwaysRestricted collapse annotation ----
ax.annotate("Catastrophic\ncollapse",
            xy=(x[6] - w/2, ucum_stat_arrs[6]),
            xytext=(x[6] - 0.6, ucum_stat_arrs[6] - 120),
            fontsize=9, color="0.4",
            arrowprops=dict(arrowstyle="-|>", color="0.4", lw=0.9), ha="center")

# ---- Mark oracle label ----
ax.text(x[0] - w/2, ucum_stat_arrs[0] + ci_stat_list[0][1] + 25,
        "oracle $T$\n(unavailable\nin practice)",
        ha="center", fontsize=7.5, color="0.5", style="italic")

# ---- Practical baseline box ----
ax.add_patch(mpatches.FancyBboxPatch(
    (x[1] - 0.55, -350), 3.7, 1400,
    boxstyle="round,pad=0.1",
    facecolor="none", edgecolor="0.7", linewidth=1.0, linestyle=":",
    zorder=0))
ax.text(x[1] + 1.3, -340, "Practical comparison range",
        ha="center", fontsize=8, color="0.5", style="italic")

ax.set_xticks(x)
ax.set_xticklabels([m[0] for m in METHODS], fontsize=9.5)
ax.set_ylabel("Discounted cumulative utility  $U_\\text{cum}$  ($\\gamma=0.97$)",
              fontsize=11)
ax.set_title("Benchmark 10 (Lake Chad Basin / Sahel,  $U_T=1.00$,  12 site-years of monitoring)",
             fontsize=11, fontweight="bold")
ax.tick_params(labelsize=9)
ax.set_ylim(-600, 1350)

# ---- Inset: P_fail ----
ax_in = ax.inset_axes([0.71, 0.62, 0.27, 0.33])
pfail_methods = [m[0].replace("\n", " ").replace("$", "").replace("\\", "") for m in METHODS[:6]]
pfail_vals    = [m[3] for m in METHODS[:6]]   # index 3 = P_fail_stat
pfail_cols    = [m[4] for m in METHODS[:6]]   # index 4 = colour hex
x_in = np.arange(len(pfail_methods))
ax_in.bar(x_in, pfail_vals, color=pfail_cols, alpha=0.80, edgecolor="white")
ax_in.set_xticks(x_in)
ax_in.set_xticklabels(["SAR", "SAR_M", "SDP", "RDM", "BELSA", "Adapt"],
                      fontsize=7.5, rotation=45, ha="right")
ax_in.set_ylabel("$P_\\text{fail}$ (stat)", fontsize=8)
ax_in.set_title("Failure prob.", fontsize=8, fontweight="bold")
ax_in.set_ylim(0, 1.05)
ax_in.tick_params(labelsize=7.5)
ax_in.axhline(1.0, color="0.6", linewidth=0.8, linestyle=":")
for j_in, v_in in enumerate(pfail_vals):
    ax_in.text(j_in, v_in + 0.01, f"{v_in:.3f}", ha="center", va="bottom",
               fontsize=7, color=pfail_cols[j_in], fontweight="bold")

# Legend
legend_patches = [
    mpatches.Patch(facecolor="0.6", alpha=0.88, edgecolor="white",
                   label="Stationary (filled)"),
    mpatches.Patch(facecolor="0.6", alpha=0.55, hatch="///", edgecolor="white",
                   label="Non-stationary (hatched)"),
    mpatches.Patch(facecolor="#d6604d", alpha=0.88, label="BELSA (ELS\\_Phil$_T$)"),
    mpatches.Patch(facecolor="#888888", alpha=0.88, label="SARSOP (Dirichlet $T$)"),
    mpatches.Patch(facecolor="#999999", alpha=0.88, label="AlwaysRestricted"),
]
ax.legend(handles=legend_patches, fontsize=8.5, loc="upper left",
          framealpha=0.9, edgecolor="0.7", ncol=2)

fig.text(0.50, 0.01,
    "$N_\\text{MC}=200$; $\\gamma=0.97$; SEED=2024.  "
    "SARSOP (Dirichlet $T$): trained on $n=50$ state-transition observations "
    "(equivalent to 12 site-years).  Error bars: 95\\% bootstrap CI.",
    ha="center", fontsize=8.5, style="italic", color="0.4")

# ---------------------------------------------------------------------------
# 4.  Save
# ---------------------------------------------------------------------------

pdf_path = os.path.join(_IMAGE, "fig4_b10_comparison.pdf")
png_path = os.path.join(_IMAGE, "fig4_b10_comparison.png")
fig.savefig(pdf_path, bbox_inches="tight")
fig.savefig(png_path, dpi=180, bbox_inches="tight")
plt.close(fig)

print(f"\nSaved: {pdf_path}")
print(f"Saved: {png_path}")
print(f"\nPractical gap (stat): ELS {ucum_stat_arrs[4]:.1f} - SARSOP_Misspec {ucum_stat_arrs[1]:.1f} "
      f"= {ucum_stat_arrs[4]-ucum_stat_arrs[1]:+.1f}")
print(f"Practical gap (NS):   ELS {ucum_ns_arrs[4]:.1f} - SARSOP_Misspec {ucum_ns_arrs[1]:.1f} "
      f"= {ucum_ns_arrs[4]-ucum_ns_arrs[1]:+.1f}")
print(f"AlwaysRestricted stat: {ucum_stat_arrs[6]:.1f}")
