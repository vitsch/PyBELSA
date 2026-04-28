# =============================================================================
# figures_adapt_window.py  —  Fig. 3: Adaptive Model-Trust Operational Window
# Project  : ELS_NEW / P_Base
# Plan ref : Summary_Paper_Plan_3.md §3.3
# Date     : 2026-04-26
# Usage    : python scr/figures_adapt_window.py   (run from P_Base/)
# Output   : image/fig3_adapt_window.pdf
#            image/fig3_adapt_window.png
# =============================================================================
"""
Publication-quality Fig. 3 for Nature Water submission.

Single-panel horizontal dot-plot showing ΔP_fail for each of the 10 benchmarks
(stationary and nonstationary) under adaptive w (ELS_Phil_Adapt, η=0.5) relative
to the best fixed-w baseline.

Key design:
  - Benchmarks ordered B1→B10 on vertical axis
  - ΔP_fail on horizontal axis; dashed vertical line at 0
  - Colour by uncertainty type (blue = parametric, red-orange = structural)
  - Filled circle = stationary; open square = nonstationary
  - B5 (worst harm) and B10 (best benefit) annotated
  - Mean w trajectory shown as right-axis tick labels
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

# ---------------------------------------------------------------------------
# 0.  Paths
# ---------------------------------------------------------------------------

_HERE = os.path.dirname(os.path.abspath(__file__))
_BASE = os.path.dirname(_HERE)
_IMAGE = os.path.join(_BASE, "image")
os.makedirs(_IMAGE, exist_ok=True)

# ---------------------------------------------------------------------------
# 1.  Data from summary_plan2_S13.md §2.2
# ---------------------------------------------------------------------------

DATA = [
    # (id, domain,                  U_T, type, dpfail_stat, dpfail_ns, w_mean_stat)
    ("B1",  "Synthetic GW",        0.00, "P", -0.025,  0.000, 0.909),
    ("B2",  "MAR AZ/Spain",        0.50, "P", -0.030, -0.020, 0.850),
    ("B3",  "Gorelick P&T",        0.60, "P", -0.060, -0.015, 0.737),
    ("B4",  "MDB SDL",             0.70, "P", -0.030, +0.025, 0.768),
    ("B5",  "NCP GRACE",           0.80, "P", -0.100, +0.010, 0.786),
    ("B6",  "Karst dual-porosity", 0.90, "S", -0.090,   None, 0.715),
    ("B7",  "Coastal tipping",     0.70, "S", -0.045, -0.040, 0.643),
    ("B8",  "STAS game-theoretic", 0.80, "S", -0.045,  0.000, 0.804),
    ("B9",  "HKH continuous",      0.90, "S", +0.015, +0.015, 0.809),
    ("B10", "LCB/Sahel sparse",    1.00, "S", +0.045, +0.025, 0.799),
]

# ---------------------------------------------------------------------------
# 2.  Colours
# ---------------------------------------------------------------------------

C_PARAM  = "#2166ac"
C_STRUCT = "#d6604d"

# ---------------------------------------------------------------------------
# 3.  Figure
# ---------------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(10, 6.5))
fig.subplots_adjust(left=0.28, right=0.88, top=0.90, bottom=0.14)

y_pos = np.arange(len(DATA))[::-1]   # B1 at top, B10 at bottom

# Reference line
ax.axvline(0, color="black", linestyle="--", linewidth=1.3, zorder=2, label="ΔP_fail = 0")
ax.axvspan(-0.115, 0,     alpha=0.06, color=C_PARAM,  zorder=0)
ax.axvspan(0,      0.055, alpha=0.06, color=C_STRUCT, zorder=0)

for i, (bm_id, domain, ut, utype, dps, dpns, wm) in enumerate(DATA):
    y = y_pos[i]
    col = C_PARAM if utype == "P" else C_STRUCT

    # Stationary — filled circle
    ax.scatter(dps, y, marker="o", s=110, color=col,
               edgecolors="white", linewidths=0.6, zorder=4)

    # Nonstationary — open square
    if dpns is not None:
        ax.scatter(dpns, y, marker="s", s=80,
                   facecolors="none", edgecolors=col, linewidths=1.8,
                   alpha=0.70, zorder=3)

    # Horizontal connector between stat and NS
    if dpns is not None:
        ax.plot([dps, dpns], [y, y], color=col, linewidth=0.8, alpha=0.45, zorder=2)

    # ΔP_fail value label
    xoff = 0.004 if dps >= 0 else -0.004
    ha   = "left"  if dps >= 0 else "right"
    ax.text(dps + xoff, y, f"{dps:+.3f}", va="center", ha=ha,
            fontsize=8.5, color=col, fontweight="bold")

# Y-axis labels — BM id + domain + U_T
y_labels = []
for (bm_id, domain, ut, utype, *rest) in DATA:
    y_labels.append(f"{bm_id}  ({domain},  $U_T={ut:.2f}$)")
ax.set_yticks(y_pos)
ax.set_yticklabels(y_labels[::-1], fontsize=9)
ax.yaxis.set_tick_params(pad=4)

# Type boundary separator
# B5 is last parametric (index 4 from top in reversed order = y=5), B6 starts structural
# In y_pos: B1=9, B2=8, B3=7, B4=6, B5=5, B6=4, B7=3, B8=2, B9=1, B10=0
# Separator between B5 (y=5) and B6 (y=4)
ax.axhline(4.5, color="0.6", linestyle="-", linewidth=1.0, alpha=0.7, zorder=1)
ax.text(0.053, 4.5, " structural →", fontsize=8.5, va="bottom", color=C_STRUCT, style="italic")
ax.text(0.053, 4.5, " ← parametric", fontsize=8.5, va="top",    color=C_PARAM,  style="italic")

# Special annotations
ax.annotate("Worst harm:\nB5 NCP GRACE\n$\\sigma_\\text{obs}=45$mm",
            xy=(-0.100, y_pos[4]),
            xytext=(-0.093, y_pos[4] - 1.8),
            fontsize=8.5, color=C_PARAM,
            arrowprops=dict(arrowstyle="-|>", color=C_PARAM, lw=0.9),
            ha="center")

ax.annotate("Best benefit:\nB10 Sahel sparse\n$\\sigma_\\text{obs}=55$mm",
            xy=(+0.045, y_pos[9]),
            xytext=(+0.040, y_pos[9] - 1.8),
            fontsize=8.5, color=C_STRUCT,
            arrowprops=dict(arrowstyle="-|>", color=C_STRUCT, lw=0.9),
            ha="center")

# Mean w labels on right axis
ax2 = ax.twinx()
ax2.set_ylim(ax.get_ylim())
ax2.set_yticks(y_pos)
wm_labels = [f"$\\bar{{w}}={d[6]:.3f}$" for d in DATA][::-1]
ax2.set_yticklabels(wm_labels, fontsize=8.5, color="0.5")
ax2.yaxis.set_tick_params(pad=2)
ax2.set_ylabel("Mean adaptive $w$ ($\\eta=0.5$, stat)", fontsize=9, color="0.5")

# Zone labels
ax.text(-0.108,  -0.8, "Adaptive worsens $P_\\text{fail}$",
        fontsize=9, color=C_PARAM, style="italic", ha="left")
ax.text( 0.002, -0.8, "Adaptive improves $P_\\text{fail}$",
        fontsize=9, color=C_STRUCT, style="italic", ha="left")

# Labels / title
ax.set_xlabel("$\\Delta P_{\\mathrm{fail}}$ = $P_{\\mathrm{fail}}^{\\mathrm{best\\ fixed\textrm{-}w}}$ "
              "$-$ $P_{\\mathrm{fail}}^{\\mathrm{Adapt}}(\\eta=0.5)$",
              fontsize=11)
ax.set_title("Operational Window of Adaptive Model-Trust ($\\eta=0.5$)",
             fontsize=11, fontweight="bold")
ax.tick_params(labelsize=9)
ax.set_xlim(-0.115, 0.065)

legend_handles = [
    mpatches.Patch(color=C_PARAM,  alpha=0.7, label="Parametric $T$ uncertainty (B1–B5)"),
    mpatches.Patch(color=C_STRUCT, alpha=0.7, label="Structural uncertainty (B6–B10)"),
    Line2D([0],[0], marker="o", color="w", markerfacecolor="grey",
           markersize=9, label="Stationary (filled circle)"),
    Line2D([0],[0], marker="s", color="w", markerfacecolor="none",
           markeredgecolor="grey", markersize=8, label="Non-stationary (open square)"),
    Line2D([0],[0], color="black", linestyle="--", label="$\\Delta P_\\text{fail}=0$ threshold"),
]
ax.legend(handles=legend_handles, fontsize=8.5, loc="lower left",
          framealpha=0.9, edgecolor="0.7")

fig.text(0.50, 0.01,
    "$N_\\text{MC}=200$ per benchmark; SEED=2024.  "
    "$\\Delta P_\\text{fail}>0$: adaptive ELS reduces failure probability vs best fixed-$w$.  "
    "Beneficial in 2/10 benchmarks (B9, B10); worst harm at B5 ($-$0.100).",
    ha="center", fontsize=8.5, style="italic", color="0.4")

# ---------------------------------------------------------------------------
# 4.  Save
# ---------------------------------------------------------------------------

pdf_path = os.path.join(_IMAGE, "fig3_adapt_window.pdf")
png_path = os.path.join(_IMAGE, "fig3_adapt_window.png")
fig.savefig(pdf_path, bbox_inches="tight")
fig.savefig(png_path, dpi=180, bbox_inches="tight")
plt.close(fig)

print(f"Saved: {pdf_path}")
print(f"Saved: {png_path}")

beneficial = [(d[0], d[4]) for d in DATA if d[4] > 0]
harmful    = [(d[0], d[4]) for d in DATA if d[4] < 0]
print(f"\nBeneficial (stat): {beneficial}")
print(f"Harmful    (stat): {harmful}")
print(f"Count: {len(beneficial)} beneficial / {len(DATA)} total")
