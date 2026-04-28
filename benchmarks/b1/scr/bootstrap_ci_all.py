# =============================================================================
# bootstrap_ci_all.py  —  Cross-Benchmark Bootstrap Confidence Intervals
# Project  : PyBELSA (all benchmarks B1–B10)
# Date     : 2026-04-27
# Usage    : python scr/bootstrap_ci_all.py   (run from benchmarks/b1/)
# Inputs   : benchmarks/b1/output/raw_results.npz
#            benchmarks/b2..10/output/raw_results_b2..10.npz
# Outputs  : output/bootstrap_ci_all.csv
# =============================================================================
"""
Consolidated block-bootstrap 95 % confidence intervals for every
method × benchmark × condition combination.

One row per (benchmark, method, condition):
  benchmark, method, condition,
  ucum_mean, ucum_sd, ucum_ci_lo, ucum_ci_hi,
  pfail_mean, pfail_ci_lo, pfail_ci_hi

Parameters
----------
BLOCK_SIZE : 10 episodes per block (same as per-benchmark stats_analysis.py)
N_BOOT     : 2000 resamples  (matches paper SI-G.3 specification)
BOOT_SEED  : SEED + 42 = 2066  (same seed as per-benchmark scripts)
"""

import os
import sys
import time

import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_HERE    = os.path.dirname(os.path.abspath(__file__))
_BASE    = os.path.dirname(_HERE)           # benchmarks/b1/
OUTPUT   = os.path.join(_BASE, "output")
OUT_CSV  = os.path.join(OUTPUT, "bootstrap_ci_all.csv")

# ---------------------------------------------------------------------------
# Bootstrap parameters  (must match per-benchmark stats_analysis.py)
# ---------------------------------------------------------------------------
BLOCK_SIZE = 10
N_BOOT     = 2000
BOOT_SEED  = 2024 + 42    # SEED + 42 = 2066
CI_LEVEL   = 0.95

# ---------------------------------------------------------------------------
# Benchmark configurations
# ---------------------------------------------------------------------------
# Each entry: (label, npz_path, T, GAMMA, FAILURE_STATE)
# T determines the discount vector; FAILURE_STATE identifies the failure state.
# B1 has T=60; B2–B10 have T=30.
GAMMA        = 0.97
FAILURE_STATE = 4

BENCHMARKS = [
    (
        "B1",
        os.path.join(_BASE, "output", "raw_results.npz"),
        60,
    ),
] + [
    (
        f"B{n}",
        os.path.join(_BASE, f"../b{n}/output/raw_results_b{n}.npz"),
        30,
    )
    for n in range(2, 11)
]


# ---------------------------------------------------------------------------
# Block bootstrap CI
# ---------------------------------------------------------------------------
def block_bootstrap_ci(
    data: np.ndarray,
    block_size: int = BLOCK_SIZE,
    n_boot: int = N_BOOT,
    seed: int = BOOT_SEED,
    ci: float = CI_LEVEL,
) -> tuple[float, float]:
    """
    Non-overlapping block bootstrap 95 % CI for the mean.

    Parameters
    ----------
    data       : (N,) episode-level values
    block_size : episodes per block
    n_boot     : number of bootstrap resamples
    seed       : RNG seed
    ci         : confidence level

    Returns
    -------
    (lo, hi) percentile-bootstrap CI for the mean.
    """
    n_blocks = len(data) // block_size
    n_use    = n_blocks * block_size
    blocks   = data[:n_use].reshape(n_blocks, block_size)

    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n_blocks, size=(n_boot, n_blocks))
    boot_means = blocks[idx].mean(axis=(1, 2))

    alpha_half = (1.0 - ci) / 2.0
    lo = float(np.percentile(boot_means, 100 * alpha_half))
    hi = float(np.percentile(boot_means, 100 * (1.0 - alpha_half)))
    return lo, hi


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    t0 = time.time()

    rows = [
        "benchmark,method,condition,"
        "ucum_mean,ucum_sd,ucum_ci_lo,ucum_ci_hi,"
        "pfail_mean,pfail_ci_lo,pfail_ci_hi"
    ]

    for label, npz_path, T in BENCHMARKS:
        print(f"  {label} ...", flush=True)

        if not os.path.isfile(npz_path):
            print(f"    WARNING: not found — {npz_path}", flush=True)
            continue

        npz  = np.load(npz_path, allow_pickle=True)
        disc = GAMMA ** np.arange(T)

        methods    = [str(m) for m in npz["_method_order"]]
        conditions = [str(c) for c in npz["_conditions"]]

        for method in methods:
            for cond in conditions:
                prefix = f"{method}__{cond}"
                key_r  = f"{prefix}__rewards"
                key_s  = f"{prefix}__states"

                if key_r not in npz.files:
                    print(f"    MISSING key: {key_r}", flush=True)
                    continue

                rewards = npz[key_r]   # (N_MC, T)
                states  = npz[key_s]   # (N_MC, T)

                ucum  = (rewards * disc).sum(axis=1)          # (N_MC,)
                pfail = (states == FAILURE_STATE).any(axis=1).astype(float)

                ucum_lo,  ucum_hi  = block_bootstrap_ci(ucum)
                pfail_lo, pfail_hi = block_bootstrap_ci(pfail)

                rows.append(
                    f"{label},{method},{cond},"
                    f"{ucum.mean():.4f},{ucum.std(ddof=1):.4f},"
                    f"{ucum_lo:.4f},{ucum_hi:.4f},"
                    f"{pfail.mean():.4f},{pfail_lo:.4f},{pfail_hi:.4f}"
                )

    os.makedirs(OUTPUT, exist_ok=True)
    with open(OUT_CSV, "w") as f:
        f.write("\n".join(rows) + "\n")

    n_rows = len(rows) - 1   # exclude header
    print(f"\nWrote {n_rows} rows → {OUT_CSV}")
    print(f"Done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    print("bootstrap_ci_all.py — cross-benchmark bootstrap CIs")
    print(f"  BLOCK_SIZE={BLOCK_SIZE}  N_BOOT={N_BOOT}  SEED={BOOT_SEED}  CI={CI_LEVEL}")
    print(f"  Benchmarks: B1–B10")
    print()
    main()
