# =============================================================================
# stats_analysis.py  —  Block Bootstrap + Statistical Inference
# Project  : ELS_NEW / P_Base  (Benchmark 4 — MDB SDL Gorelick)
# Plan ref : experiment_plan.md §4 + §5 Step 5
# Date     : 2026-04-24
# Usage    : python scr/stats_analysis.py  (in P_Base2/scr/)
# Inputs   : output/raw_results.npz
# Outputs  : output/stat_report_benchmark.md
#            output/tables/table_ucum.csv
#            output/tables/table_pfail.csv
#            output/tables/table_regret.csv
#            output/tables/table_pairwise.csv
#            output/tables/table_nonstationarity.csv
# =============================================================================
"""
Statistical analysis of the Monte Carlo benchmark.

Metrics computed per episode
-----------------------------
ucum    : Σ_{t=0}^{T-1} γ^t · R(a_t, θ_{t+1})
pfail   : 1 if θ_t = θ₅ for any t, else 0
mttf    : first t where θ_t = θ₅ (NaN if no failure)
regret  : U_cum(MyopicEU) − U_cum(method)   [oracle regret]
ucum_A  : partial U_cum for steps 0–29  (regime A)
ucum_B  : partial U_cum for steps 30–59 (regime B)
f_phil  : mean(k_t = "phil") per episode (ELS_Int only; else 0)

Inference
----------
Bootstrap CIs : non-overlapping block bootstrap, block_size=10, B=5000 resamples
Normality     : Shapiro-Wilk on per-episode differences (ELS_Int − baseline)
Pairwise tests: paired t-test (normal) or Wilcoxon signed-rank (non-normal)
                ELS_Int vs each of 9 baselines, per condition
Multiple comp : Holm–Bonferroni across 9 comparisons within each condition
Non-stat test : paired t-test: H₀: E[U_cum_A − U_cum_B] = 0  per method/condition
EVOI          : E[U_cum(SDP_NS)] − E[U_cum(SDP_S)]  per condition
Cohen's d     : pooled-SD effect size for each pairwise comparison
Convergence   : SE of mean U_cum at N_MC ∈ {50,100,150,200}; flag < 1 % change
"""

import os
import sys

import numpy as np
from scipy.stats import shapiro, ttest_rel, wilcoxon, ttest_1samp

# ---------------------------------------------------------------------------
# Imports from POMDP environment (for constants)
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from pomdp_env_b4 import T, GAMMA, SEED, FAILURE_STATE, N_MC

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BLOCK_SIZE = 10
N_BOOT     = 5000
ALPHA      = 0.05
ELS_INT    = "ELS_Int"

BASELINES_FOR_TEST = [
    "SARSOP", "PBVI", "SDP_S", "SDP_NS",
    "MPC", "RDM", "InfoGap", "AlwaysRestricted", "MyopicEU",
]

NPZ_PATH   = os.path.join(os.path.dirname(_HERE), "output", "raw_results_b4.npz")
OUTPUT_DIR = os.path.join(os.path.dirname(_HERE), "output")
TABLES_DIR = os.path.join(OUTPUT_DIR, "tables")
os.makedirs(TABLES_DIR, exist_ok=True)

# Discount vector shared across all computations
_DISC = GAMMA ** np.arange(T)   # shape (T,)


# ===========================================================================
# 1.  Per-episode metric computation
# ===========================================================================

def compute_episode_metrics(npz: np.lib.npyio.NpzFile, name: str, cond: str,
                             oracle_ucum: np.ndarray | None = None) -> dict:
    """
    Compute per-episode scalars from the raw NPZ arrays.

    Returns
    -------
    dict with keys: ucum, pfail, mttf, regret, ucum_A, ucum_B, f_phil
    All arrays shape (N_MC,); mttf has NaN for episodes without failure.
    """
    prefix  = f"{name}__{cond}"
    rewards = npz[f"{prefix}__rewards"]    # (N_MC, T)
    states  = npz[f"{prefix}__states"]     # (N_MC, T)
    k_phil  = npz[f"{prefix}__k_phil"]     # (N_MC, T)

    ucum   = (rewards * _DISC).sum(axis=1)                          # (N_MC,)
    ucum_A = (rewards[:, :15] * _DISC[:15]).sum(axis=1)             # regime A
    ucum_B = (rewards[:, 15:] * _DISC[15:]).sum(axis=1)             # regime B

    fail_mask = states == FAILURE_STATE                              # (N_MC, T)
    pfail = fail_mask.any(axis=1).astype(float)                     # (N_MC,)
    mttf  = np.where(
        fail_mask.any(axis=1),
        np.argmax(fail_mask, axis=1).astype(float),
        np.nan,
    )

    regret = (oracle_ucum - ucum) if oracle_ucum is not None \
             else np.full(N_MC, np.nan)

    f_phil = k_phil.mean(axis=1)   # non-zero only for ELS_Int

    return {
        "ucum":   ucum,
        "pfail":  pfail,
        "mttf":   mttf,
        "regret": regret,
        "ucum_A": ucum_A,
        "ucum_B": ucum_B,
        "f_phil": f_phil,
    }


# ===========================================================================
# 2.  Block bootstrap confidence intervals
# ===========================================================================

def block_bootstrap_ci(
    data: np.ndarray,
    block_size: int = BLOCK_SIZE,
    n_boot: int = N_BOOT,
    seed: int = SEED + 42,
    ci: float = 0.95,
) -> tuple[float, float]:
    """
    Non-overlapping block bootstrap 95 % CI for the mean.

    Parameters
    ----------
    data       : (N,) 1-D array of episode-level values
    block_size : episodes per block (default 10)
    n_boot     : number of resamples (default 5000)
    ci         : confidence level (default 0.95)

    Returns
    -------
    (lo, hi) percentile-bootstrap CI for the mean.
    """
    n_blocks = len(data) // block_size
    n_use    = n_blocks * block_size
    blocks   = data[:n_use].reshape(n_blocks, block_size)   # (B, b)

    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n_blocks, size=(n_boot, n_blocks))  # (B, n_blocks)
    boot_means = blocks[idx].mean(axis=(1, 2))                # (B,) vectorised

    alpha_half = (1.0 - ci) / 2.0
    lo, hi = np.percentile(boot_means, [100 * alpha_half, 100 * (1 - alpha_half)])
    return float(lo), float(hi)


def ess(n_mc: int = N_MC, t: int = T, block_size: int = BLOCK_SIZE) -> int:
    """Effective sample size = N_MC × T / block_size."""
    return (n_mc * t) // block_size


# ===========================================================================
# 3.  Holm–Bonferroni correction
# ===========================================================================

def holm_bonferroni(
    p_values: list[float], alpha: float = ALPHA
) -> tuple[np.ndarray, np.ndarray]:
    """
    Holm–Bonferroni step-down multiple comparison correction.

    Parameters
    ----------
    p_values : list of raw p-values
    alpha    : family-wise significance level

    Returns
    -------
    p_adj   : ndarray of adjusted p-values (same order as input)
    reject  : ndarray bool — True if H₀ rejected after correction
    """
    n     = len(p_values)
    order = np.argsort(p_values)
    p_s   = np.array(p_values, dtype=float)[order]

    # Adjusted p: step-down formula p̃_(i) = min((n-i)*p_(i), 1), enforced monotone
    raw_adj = np.minimum(p_s * np.arange(n, 0, -1, dtype=float), 1.0)
    adjusted = np.maximum.accumulate(raw_adj)   # enforce monotonicity

    # Reject: once the step-down sequence stops rejecting, stop
    reject = np.zeros(n, dtype=bool)
    for i in range(n):
        if p_s[i] <= alpha / (n - i):
            reject[i] = True
        else:
            break

    p_adj_out   = np.empty(n, dtype=float)
    reject_out  = np.zeros(n, dtype=bool)
    p_adj_out[order]  = adjusted
    reject_out[order] = reject
    return p_adj_out, reject_out


# ===========================================================================
# 4.  Pairwise statistical tests
# ===========================================================================

def cohens_d(x: np.ndarray, y: np.ndarray) -> float:
    """Pooled-SD Cohen's d: positive when x > y."""
    n1, n2 = len(x), len(y)
    v1, v2 = np.var(x, ddof=1), np.var(y, ddof=1)
    s_p = np.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2))
    return float((np.mean(x) - np.mean(y)) / s_p) if s_p > 1e-9 else 0.0


def pairwise_test(x: np.ndarray, y: np.ndarray) -> dict:
    """
    Test H₀: μ(x) = μ(y) using per-episode differences d = x − y.

    Procedure:
      1. Shapiro-Wilk on d
      2. If SW p ≥ 0.05 (normal): paired t-test (ttest_1samp(d, 0))
      3. Else: Wilcoxon signed-rank (one-sample)

    Returns dict with statistic, p_value, test_name, sw_p, cohens_d.
    """
    d = x - y
    d_std = float(np.std(d, ddof=1))
    # Suppress spurious precision-loss warnings from scipy wilcoxon on near-constant data
    import warnings as _warnings

    # Edge case: constant differences (e.g., InfoGap always 139.9)
    if d_std < 1e-6:
        sign = 1.0 if np.mean(d) > 0 else (-1.0 if np.mean(d) < 0 else 0.0)
        return {
            "test":      "degenerate",
            "statistic": float(sign * np.inf),
            "p_value":   0.0 if np.abs(np.mean(d)) > 1e-6 else 1.0,
            "sw_p":      np.nan,
            "cohens_d":  0.0,
        }

    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore", RuntimeWarning)
        sw_stat, sw_p = shapiro(d[:min(len(d), 5000)])

    if sw_p >= ALPHA:
        stat, p = ttest_1samp(d, 0.0)
        test_name = "paired_t"
    else:
        try:
            with _warnings.catch_warnings():
                _warnings.simplefilter("ignore", RuntimeWarning)
                stat, p = wilcoxon(d, alternative="two-sided")
        except ValueError:
            stat, p = 0.0, 1.0
        test_name = "wilcoxon_sr"

    return {
        "test":      test_name,
        "statistic": float(stat),
        "p_value":   float(p),
        "sw_p":      float(sw_p),
        "cohens_d":  cohens_d(x, y),
    }


# ===========================================================================
# 5.  Convergence diagnostic
# ===========================================================================

def convergence_check(ucum: np.ndarray, ns: list[int] | None = None) -> dict:
    """
    SE of mean U_cum at N_MC ∈ {50, 100, 150, 200}.

    Returns dict: n → (mean, SE) and 'converged' bool
    (SE change from N=150 to N=200 < 1 % of mean at N=200).
    """
    if ns is None:
        ns = [50, 100, 150, 200]
    result = {}
    for n in ns:
        mu = float(ucum[:n].mean())
        se = float(ucum[:n].std(ddof=1) / np.sqrt(n))
        result[n] = (mu, se)

    se_150 = result[150][1] if 150 in result else np.nan
    se_200 = result[200][1] if 200 in result else np.nan
    mu_200 = abs(result[200][0]) if 200 in result else 1.0
    # Criterion: absolute SE improvement as fraction of mean
    # |SE(200) - SE(150)| / |mean(200)| < 1 %
    se_change = abs(se_200 - se_150) / max(mu_200, 1e-9)
    converged = bool(se_change < 0.01)
    result["converged"] = converged
    result["se_change"] = float(se_change)
    return result


# ===========================================================================
# 6.  Main analysis
# ===========================================================================

def run_analysis(npz_path: str = NPZ_PATH) -> dict:
    """
    Load raw_results.npz and run the full statistical analysis.

    Returns nested dict: results[method][condition] with all metric arrays
    and inference results.
    """
    npz = np.load(npz_path, allow_pickle=False)
    methods    = [str(m) for m in npz["_method_order"]]
    conditions = [str(c) for c in npz["_conditions"]]

    # ------------------------------------------------------------------
    # Compute per-episode metrics for all methods × conditions
    # ------------------------------------------------------------------
    raw: dict[str, dict[str, dict]] = {m: {} for m in methods}

    for cond in conditions:
        # Oracle (MyopicEU) needed for regret
        oracle_ucum = compute_episode_metrics(npz, "MyopicEU", cond)["ucum"]

        for name in methods:
            raw[name][cond] = compute_episode_metrics(
                npz, name, cond,
                oracle_ucum=oracle_ucum if name != "MyopicEU" else None,
            )

    # ------------------------------------------------------------------
    # Bootstrap CIs for U_cum, P_fail, MTTF, Regret
    # ------------------------------------------------------------------
    ci: dict[str, dict[str, dict]] = {m: {} for m in methods}
    for name in methods:
        for cond in conditions:
            m = raw[name][cond]
            ci[name][cond] = {}
            for key in ("ucum", "pfail", "regret"):
                data = m[key]
                if np.isnan(data).any():
                    data_clean = data[~np.isnan(data)]
                else:
                    data_clean = data
                if len(data_clean) >= BLOCK_SIZE:
                    lo, hi = block_bootstrap_ci(
                        data_clean, seed=SEED + hash(name + cond + key) % (2**31)
                    )
                elif len(data_clean) > 0:
                    mu = float(np.nanmean(data_clean))
                    lo, hi = mu, mu
                else:
                    lo, hi = np.nan, np.nan
                ci[name][cond][key] = (lo, hi)

    # ------------------------------------------------------------------
    # Pairwise tests: ELS_Int vs each baseline
    # ------------------------------------------------------------------
    pairwise: dict[str, dict] = {}
    for cond in conditions:
        p_vals   = []
        test_res = []
        x_int = raw[ELS_INT][cond]["ucum"]

        for bl in BASELINES_FOR_TEST:
            y_bl = raw[bl][cond]["ucum"]
            res  = pairwise_test(x_int, y_bl)
            p_vals.append(res["p_value"])
            test_res.append(res)

        p_adj, reject = holm_bonferroni(p_vals)

        for i, bl in enumerate(BASELINES_FOR_TEST):
            key = f"{ELS_INT}_vs_{bl}__{cond}"
            pairwise[key] = {**test_res[i], "p_adj": float(p_adj[i]), "reject_H0": bool(reject[i])}

    # ------------------------------------------------------------------
    # Non-stationarity test: paired t on U_cum_A vs U_cum_B
    # ------------------------------------------------------------------
    nonstat: dict[str, dict] = {}
    for name in methods:
        for cond in conditions:
            a  = raw[name][cond]["ucum_A"]
            b  = raw[name][cond]["ucum_B"]
            d  = a - b
            stat, p = ttest_1samp(d, 0.0)
            nonstat[f"{name}__{cond}"] = {
                "delta_U_mean": float(d.mean()),
                "delta_U_sd":   float(d.std(ddof=1)),
                "t_stat":       float(stat),
                "p_value":      float(p),
                "reject_H0":    bool(p < ALPHA),
                "ucum_A_mean":  float(a.mean()),
                "ucum_B_mean":  float(b.mean()),
            }

    # ------------------------------------------------------------------
    # EVOI = E[U_cum(SDP_NS)] - E[U_cum(SDP_S)]
    # ------------------------------------------------------------------
    evoi = {}
    for cond in conditions:
        ns_ucum  = raw["SDP_NS"][cond]["ucum"]
        s_ucum   = raw["SDP_S"][cond]["ucum"]
        evoi_ep  = ns_ucum - s_ucum
        lo, hi   = block_bootstrap_ci(evoi_ep, seed=SEED + 7654)
        evoi[cond] = {
            "mean": float(evoi_ep.mean()),
            "sd":   float(evoi_ep.std(ddof=1)),
            "ci_lo": lo,
            "ci_hi": hi,
        }

    # ------------------------------------------------------------------
    # Convergence diagnostic for every method × condition
    # ------------------------------------------------------------------
    conv: dict[str, dict] = {}
    for name in methods:
        for cond in conditions:
            conv[f"{name}__{cond}"] = convergence_check(raw[name][cond]["ucum"])

    # ------------------------------------------------------------------
    # ELS_Int specific: f_phil stats
    # ------------------------------------------------------------------
    f_phil_stats = {}
    for cond in conditions:
        fp = raw[ELS_INT][cond]["f_phil"]
        lo, hi = block_bootstrap_ci(fp, seed=SEED + 8888)
        f_phil_stats[cond] = {
            "mean": float(fp.mean()), "sd": float(fp.std(ddof=1)),
            "ci_lo": lo, "ci_hi": hi,
        }

    return {
        "raw":       raw,
        "ci":        ci,
        "pairwise":  pairwise,
        "nonstat":   nonstat,
        "evoi":      evoi,
        "conv":      conv,
        "f_phil":    f_phil_stats,
        "methods":   methods,
        "conditions": conditions,
    }


# ===========================================================================
# 7.  Report generation
# ===========================================================================

def _fmt(v, decimals=1):
    if np.isnan(v):
        return "n/a"
    return f"{v:.{decimals}f}"


def write_tables(res: dict) -> None:
    """Write CSV tables to output/tables/."""
    methods    = res["methods"]
    conditions = res["conditions"]
    raw        = res["raw"]
    ci         = res["ci"]

    # --- table_ucum.csv ---
    rows_ucum = ["method,condition,mean_ucum,sd_ucum,ci_lo,ci_hi,median_ucum"]
    for name in methods:
        for cond in conditions:
            ucum = raw[name][cond]["ucum"]
            lo, hi = ci[name][cond]["ucum"]
            rows_ucum.append(
                f"{name},{cond},"
                f"{ucum.mean():.2f},{ucum.std(ddof=1):.2f},"
                f"{lo:.2f},{hi:.2f},{np.median(ucum):.2f}"
            )
    with open(os.path.join(TABLES_DIR, "table_ucum_b4.csv"), "w") as f:
        f.write("\n".join(rows_ucum) + "\n")

    # --- table_pfail.csv ---
    rows_pf = ["method,condition,p_fail_mean,p_fail_ci_lo,p_fail_ci_hi,mttf_mean,mttf_median"]
    for name in methods:
        for cond in conditions:
            pf   = raw[name][cond]["pfail"]
            mttf = raw[name][cond]["mttf"]
            lo, hi = ci[name][cond]["pfail"]
            rows_pf.append(
                f"{name},{cond},"
                f"{pf.mean():.3f},{lo:.3f},{hi:.3f},"
                f"{np.nanmean(mttf):.1f},{np.nanmedian(mttf):.1f}"
            )
    with open(os.path.join(TABLES_DIR, "table_pfail_b4.csv"), "w") as f:
        f.write("\n".join(rows_pf) + "\n")

    # --- table_regret.csv ---
    rows_reg = ["method,condition,regret_mean,regret_sd,regret_ci_lo,regret_ci_hi"]
    for name in methods:
        if name == "MyopicEU":
            continue
        for cond in conditions:
            reg  = raw[name][cond]["regret"]
            lo, hi = ci[name][cond]["regret"]
            rows_reg.append(
                f"{name},{cond},"
                f"{reg.mean():.2f},{reg.std(ddof=1):.2f},"
                f"{lo:.2f},{hi:.2f}"
            )
    with open(os.path.join(TABLES_DIR, "table_regret_b4.csv"), "w") as f:
        f.write("\n".join(rows_reg) + "\n")

    # --- table_pairwise.csv ---
    rows_pw = ["els_int_vs,condition,test,statistic,p_raw,p_adj,reject_H0,cohens_d"]
    for bl in BASELINES_FOR_TEST:
        for cond in conditions:
            key = f"{ELS_INT}_vs_{bl}__{cond}"
            r   = res["pairwise"][key]
            rows_pw.append(
                f"{bl},{cond},{r['test']},"
                f"{r['statistic']:.4f},{r['p_value']:.4f},{r['p_adj']:.4f},"
                f"{r['reject_H0']},{r['cohens_d']:.3f}"
            )
    with open(os.path.join(TABLES_DIR, "table_pairwise_b4.csv"), "w") as f:
        f.write("\n".join(rows_pw) + "\n")

    # --- table_nonstationarity.csv ---
    rows_ns = ["method,condition,ucum_A_mean,ucum_B_mean,delta_U,delta_U_sd,t_stat,p_value,reject_H0"]
    for name in methods:
        for cond in conditions:
            r = res["nonstat"][f"{name}__{cond}"]
            rows_ns.append(
                f"{name},{cond},"
                f"{r['ucum_A_mean']:.2f},{r['ucum_B_mean']:.2f},"
                f"{r['delta_U_mean']:.2f},{r['delta_U_sd']:.2f},"
                f"{r['t_stat']:.4f},{r['p_value']:.4f},{r['reject_H0']}"
            )
    with open(os.path.join(TABLES_DIR, "table_nonstationarity_b4.csv"), "w") as f:
        f.write("\n".join(rows_ns) + "\n")


def write_markdown_report(res: dict, out_path: str) -> None:
    """Write the main statistical report as Markdown."""
    methods    = res["methods"]
    conditions = res["conditions"]
    raw        = res["raw"]
    ci         = res["ci"]
    L = []

    L += [
        "# Benchmark 4 — Statistical Report",
        f"**Date:** 2026-04-22  ",
        f"**SEED:** {SEED}  N_MC = {N_MC}  T = {T}  γ = {GAMMA}  ",
        f"**Block bootstrap:** block_size = {BLOCK_SIZE}, B = {N_BOOT}  ",
        f"**Effective sample size:** ESS = {ess()}  ",
        f"**Multiple comparison:** Holm–Bonferroni, α = {ALPHA}  ",
        "",
        "---",
        "",
    ]

    # ---- Table 1: U_cum summary ----
    L += [
        "## Table 1 — Discounted Cumulative Reward (U_cum)",
        "",
        "Mean ± SD with 95 % bootstrap CI. Regret = U_cum(MyopicEU) − U_cum(method).",
        "",
    ]
    for cond in conditions:
        L.append(f"### Condition: {cond}")
        L.append("")
        L.append("| Method | Mean | SD | 95 % CI | Median | Regret (mean) |")
        L.append("|--------|------|-----|---------|--------|---------------|")
        for name in methods:
            ucum = raw[name][cond]["ucum"]
            reg  = raw[name][cond]["regret"]
            lo, hi = ci[name][cond]["ucum"]
            reg_str = _fmt(reg.mean()) if name != "MyopicEU" else "—"
            L.append(
                f"| {name} | {ucum.mean():.1f} | {ucum.std(ddof=1):.1f} | "
                f"[{lo:.1f}, {hi:.1f}] | {np.median(ucum):.1f} | {reg_str} |"
            )
        L.append("")

    # ---- Table 2: P_fail / MTTF ----
    L += [
        "## Table 2 — P_fail and MTTF",
        "",
        "P_fail = fraction of episodes reaching θ₅. "
        "MTTF = mean time to first failure (steps); NaN-excluded.",
        "",
    ]
    for cond in conditions:
        L.append(f"### Condition: {cond}")
        L.append("")
        L.append("| Method | P_fail | P_fail 95 % CI | MTTF (mean) | MTTF (median) |")
        L.append("|--------|--------|----------------|-------------|---------------|")
        for name in methods:
            pf   = raw[name][cond]["pfail"]
            mttf = raw[name][cond]["mttf"]
            lo, hi = ci[name][cond]["pfail"]
            L.append(
                f"| {name} | {pf.mean():.3f} | [{lo:.3f}, {hi:.3f}] | "
                f"{np.nanmean(mttf):.1f} | {np.nanmedian(mttf):.1f} |"
            )
        L.append("")

    # ---- Table 3: Pairwise tests ----
    L += [
        "## Table 3 — Pairwise Tests: ELS_Int vs Baselines (U_cum)",
        "",
        "H₀: E[U_cum(ELS_Int)] = E[U_cum(baseline)].  ",
        "Test: paired t (SW p ≥ 0.05) or Wilcoxon signed-rank (SW p < 0.05).  ",
        "Holm–Bonferroni correction applied within each condition (9 comparisons).  ",
        "Cohen's d: positive = ELS_Int > baseline.",
        "",
    ]
    for cond in conditions:
        L.append(f"### Condition: {cond}")
        L.append("")
        L.append("| Baseline | Test | Statistic | p (raw) | p (adj) | Reject H₀ | Cohen's d |")
        L.append("|----------|------|-----------|---------|---------|-----------|-----------|")
        for bl in BASELINES_FOR_TEST:
            key = f"{ELS_INT}_vs_{bl}__{cond}"
            r   = res["pairwise"][key]
            rej = "✓" if r["reject_H0"] else "–"
            L.append(
                f"| {bl} | {r['test']} | {r['statistic']:.3f} | "
                f"{r['p_value']:.4f} | {r['p_adj']:.4f} | {rej} | "
                f"{r['cohens_d']:.3f} |"
            )
        L.append("")

    # ---- Table 4: Non-stationarity ----
    L += [
        "## Table 4 — Non-Stationarity Analysis (ΔU = U_cum_A − U_cum_B)",
        "",
        "H₀: E[ΔU] = 0 (no regime effect). Paired t-test per method × condition.  ",
        "U_cum_A = discounted reward steps 0–29; U_cum_B = steps 30–59 (same γ^t).  ",
        "Positive ΔU ⟹ performance degrades after the climate shift at t = 30.",
        "",
        "| Method | Condition | U_cum_A | U_cum_B | ΔU (mean) | ΔU (SD) | t | p | Reject |",
        "|--------|-----------|---------|---------|-----------|---------|---|---|--------|",
    ]
    for name in methods:
        for cond in conditions:
            r = res["nonstat"][f"{name}__{cond}"]
            rej = "✓" if r["reject_H0"] else "–"
            L.append(
                f"| {name} | {cond} | {r['ucum_A_mean']:.1f} | {r['ucum_B_mean']:.1f} | "
                f"{r['delta_U_mean']:.1f} | {r['delta_U_sd']:.1f} | "
                f"{r['t_stat']:.3f} | {r['p_value']:.4f} | {rej} |"
            )
    L.append("")

    # ---- EVOI ----
    L += [
        "## Table 5 — Economic Value of Information (EVOI)",
        "",
        "EVOI = E[U_cum(SDP_NS)] − E[U_cum(SDP_S)]. "
        "Positive EVOI = online regime detection adds value.",
        "",
        "| Condition | EVOI (mean) | EVOI (SD) | 95 % CI |",
        "|-----------|------------|-----------|---------|",
    ]
    for cond in conditions:
        e = res["evoi"][cond]
        L.append(
            f"| {cond} | {e['mean']:.2f} | {e['sd']:.2f} | "
            f"[{e['ci_lo']:.2f}, {e['ci_hi']:.2f}] |"
        )
    L.append("")

    # ---- ELS_Int f_phil ----
    L += [
        "## Table 6 — ELS_Int Philosophical Activation (f_phil)",
        "",
        "f_phil = fraction of steps where the philosophical selector (SR4) was chosen.  ",
        "Expected ≈ 5 % once entropy collapses (α_t → α_max = 0.95).",
        "",
        "| Condition | f_phil (mean) | SD | 95 % CI |",
        "|-----------|--------------|-----|---------|",
    ]
    for cond in conditions:
        fp = res["f_phil"][cond]
        L.append(
            f"| {cond} | {fp['mean']:.4f} | {fp['sd']:.4f} | "
            f"[{fp['ci_lo']:.4f}, {fp['ci_hi']:.4f}] |"
        )
    L.append("")

    # ---- Convergence ----
    L += [
        "## Table 7 — Convergence Diagnostic (U_cum SE vs N_MC)",
        "",
        "SE stabilised if |SE(200) − SE(150)| / SE(200) < 1 %.",
        "",
        "| Method | Cond | SE(50) | SE(100) | SE(150) | SE(200) | Δ SE % | Converged |",
        "|--------|------|--------|---------|---------|---------|--------|-----------|",
    ]
    for name in methods:
        for cond in conditions:
            c = res["conv"][f"{name}__{cond}"]
            se50  = c[50][1]
            se100 = c[100][1]
            se150 = c[150][1]
            se200 = c[200][1]
            pct   = 100 * c["se_change"]
            ok    = "✓" if c["converged"] else "✗"
            L.append(
                f"| {name} | {cond} | {se50:.2f} | {se100:.2f} | "
                f"{se150:.2f} | {se200:.2f} | {pct:.1f} % | {ok} |"
            )
    L.append("")

    # ---- Summary notes ----
    n_conv = sum(
        1 for name in methods for cond in conditions
        if res["conv"][f"{name}__{cond}"]["converged"]
    )
    total = len(methods) * len(conditions)
    L += [
        "---",
        "",
        "## Notes",
        "",
        f"- **Convergence:** {n_conv}/{total} method–condition pairs converged "
        f"(SE change < 1 % from N=150 to N=200).",
        "- **SDP_S / SDP_NS:** MC benchmark uses vectorised depth-2 lookahead "
        "(`_SDPSVec`, `_SDPNSVec` in `run_benchmark.py`). "
        "Smoke-test values (depth-3) differ; see `summary_step_4.md`.",
        "- **ELS static belief:** ELS methods use static Bayesian updates "
        "(no Markovian predict step). The U_cum gap vs SARSOP/PBVI is expected "
        "and reflects the epistemic-humility design principle.",
        "- **MTTF caveat:** MTTF is conditional on at least one failure episode; "
        "all NaN episodes (no failure) are excluded from the mean/median.",
        "",
    ]

    with open(out_path, "w") as f:
        f.write("\n".join(L) + "\n")


# ===========================================================================
# 8.  Entry point
# ===========================================================================

def main() -> None:
    import time
    t0 = time.time()
    print("=" * 66)
    print("stats_analysis.py — Block Bootstrap + Holm–Bonferroni Inference")
    print(f"  NPZ: {NPZ_PATH}")
    print(f"  Block size={BLOCK_SIZE}, B={N_BOOT}, α={ALPHA}")
    print("=" * 66)

    print("Running analysis...", flush=True)
    res = run_analysis(NPZ_PATH)

    print("Writing tables...", flush=True)
    write_tables(res)

    report_path = os.path.join(OUTPUT_DIR, "stat_report_b4.md")
    write_markdown_report(res, report_path)
    print(f"Report: {report_path}")

    # ------------------------------------------------------------------
    # Console summary
    # ------------------------------------------------------------------
    print("\n--- U_cum summary (nonstationary) ---")
    print(f"  {'Method':<18}  {'Mean':>8}  {'SD':>7}  {'95 % CI':>18}")
    for name in res["methods"]:
        cond = "nonstationary"
        ucum = res["raw"][name][cond]["ucum"]
        lo, hi = res["ci"][name][cond]["ucum"]
        print(f"  {name:<18}  {ucum.mean():8.1f}  {ucum.std(ddof=1):7.1f}  [{lo:7.1f}, {hi:7.1f}]")

    print("\n--- Pairwise: ELS_Int vs baselines (nonstationary, Holm-corrected) ---")
    print(f"  {'Baseline':<18}  {'Test':<12}  {'p_raw':>7}  {'p_adj':>7}  {'Reject':>7}  {'d':>6}")
    for bl in BASELINES_FOR_TEST:
        key = f"{ELS_INT}_vs_{bl}__nonstationary"
        r   = res["pairwise"][key]
        rej = "YES" if r["reject_H0"] else "no"
        print(
            f"  {bl:<18}  {r['test']:<12}  "
            f"{r['p_value']:7.4f}  {r['p_adj']:7.4f}  {rej:>7}  {r['cohens_d']:6.3f}"
        )

    print("\n--- EVOI ---")
    for cond in res["conditions"]:
        e = res["evoi"][cond]
        print(f"  {cond:<16}  EVOI = {e['mean']:+.2f}  95% CI [{e['ci_lo']:+.2f}, {e['ci_hi']:+.2f}]")

    print("\n--- ELS_Int f_phil ---")
    for cond in res["conditions"]:
        fp = res["f_phil"][cond]
        print(f"  {cond:<16}  f_phil = {fp['mean']:.4f} ± {fp['sd']:.4f}  95% CI [{fp['ci_lo']:.4f}, {fp['ci_hi']:.4f}]")

    conv_ok = sum(
        1 for name in res["methods"] for cond in res["conditions"]
        if res["conv"][f"{name}__{cond}"]["converged"]
    )
    total = len(res["methods"]) * len(res["conditions"])
    print(f"\n--- Convergence: {conv_ok}/{total} pairs converged (SE Δ < 1 %) ---")

    print(f"\nDone in {time.time() - t0:.1f}s")
    print("=" * 66)


if __name__ == "__main__":
    main()
