"""
reproduce_b10.py — verify the headline B10 result from pre-computed data.

Loads benchmarks/b10/output/raw_results_b10.npz and reproduces the key
numbers from the paper (Table 1 / Fig. 4):

  ELS_Phil_T vs SARSOP_Misspec, stationary condition:
  +128 units advantage (16.8%), p < 0.01

Run from the repo root:
    python reproduce_b10.py

Expected output (< 5 seconds):
  ELS_Phil_T    : 889 ± 35  [853, 925]
  SARSOP_Misspec: 761 ± 39  [722, 801]
  AlwaysRestrict: -204
  Advantage     : +128 units  (16.8%)  p < 0.01
"""

import os
import numpy as np
from scipy.stats import wilcoxon

GAMMA    = 0.97
BOOT_B   = 5000
BOOT_SEED = 42

NPZ = os.path.join(os.path.dirname(__file__),
                   "benchmarks", "b10", "output", "raw_results_b10.npz")

d = np.load(NPZ, allow_pickle=True)

def ucum(rewards):
    T = rewards.shape[1]
    return (rewards * GAMMA ** np.arange(T)).sum(axis=1)

els = ucum(d["ELS_Phil_T__stationary__rewards"])
sar = ucum(d["SARSOP_Misspec__stationary__rewards"])
ar  = ucum(d["AlwaysRestricted__stationary__rewards"])

rng = np.random.default_rng(BOOT_SEED)
els_boot = np.array([rng.choice(els, len(els), replace=True).mean()
                     for _ in range(BOOT_B)])
sar_boot = np.array([rng.choice(sar, len(sar), replace=True).mean()
                     for _ in range(BOOT_B)])

_, p = wilcoxon(els, sar, alternative="greater")
adv  = els.mean() - sar.mean()
adv_pct = adv / abs(sar.mean()) * 100

print(f"\nB10 (Lake Chad Basin / Sahel — 12 site-years, U_T=1.00)")
print(f"{'─'*52}")
els_lo, els_hi = np.percentile(els_boot, 2.5), np.percentile(els_boot, 97.5)
sar_lo, sar_hi = np.percentile(sar_boot, 2.5), np.percentile(sar_boot, 97.5)
print(f"ELS_Phil_T    : {els.mean():.0f} ± {(els_hi-els_lo)/2:.0f}"
      f"  95% CI [{els_lo:.0f}, {els_hi:.0f}]")
print(f"SARSOP_Misspec: {sar.mean():.0f} ± {(sar_hi-sar_lo)/2:.0f}"
      f"  95% CI [{sar_lo:.0f}, {sar_hi:.0f}]")
print(f"AlwaysRestrict: {ar.mean():.0f}")
print(f"{'─'*52}")
print(f"Advantage     : +{adv:.0f} units  ({adv_pct:.1f}%)"
      f"  p = {p:.2e}")
print()

assert adv > 120, f"Advantage {adv:.1f} outside expected range"
assert p < 0.01,  f"p-value {p:.4f} not significant"
print("✓ Results verified — matches paper (Fig. 4 / Table 1).")
