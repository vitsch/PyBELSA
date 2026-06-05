# PyBELSA

**Bayesian Epistemic Logic for Sustainable Aquifers**

A Python implementation of the BELSA decision framework for sequential groundwater management under deep transition-model uncertainty. BELSA decouples observation-based belief updating from transition-model knowledge, enabling principled adaptive management without calibrating a transition model.

Evaluated across **ten real-world and synthetic benchmarks** (B1–B10) spanning six continents, five structural uncertainty types, and a model-uncertainty index U_T from 0.0 to 1.0.

---

## Why All Ten Benchmarks Are Included

The four publication figures each load pre-computed Monte Carlo results (`raw_results_bN.npz`) from the benchmark output directories:

| Figure | Data required | Benchmarks |
|---|---|---|
| Fig. 1 — Price-of-robustness curve | `raw_results_bN.npz` (all ten) | **B1–B10** |
| Fig. 2 — Uncertainty-type crossover | `raw_results_b4.npz`, `raw_results_b7.npz` | B4, B7 |
| Fig. 3 — Adaptive-w operational window | Hard-coded summary data | — |
| Fig. 4 — B10 data-scarcity comparison | `raw_results_b10.npz` | B10 |

Reproducing Fig. 1 — the central result of the paper — requires all ten npz files. Per Nature Water data policy, all data necessary to assess the paper's conclusions and reproduce its figures must be publicly available. All ten benchmarks are therefore included.

**Total data footprint:** ~2.6 MB (npz files) + ~90 KB (CSV tables) + ~2.0 MB (Python source) ≈ **4.6 MB**. No Git LFS required.

---

## Framework Overview

BELSA comprises three variants:

| Variant | Description | Key mechanism |
|---|---|---|
| **ELS_Phil_T** | T-aware philosophical filter (fixed model-trust weight w) | Static belief update + real-options satisficing |
| **ELS_Int** | Integrated Bernoulli framework | Entropy-driven hard switching between philosophical and prescriptive policies |
| **ELS_Adapt** | Online adaptive model-trust | Logit-space w update from per-step log-likelihood ratio |

All variants use a **static observation-likelihood belief update**: beliefs evolve from observations alone, without propagating through any transition model. The transition model enters only through the option-value pre-factor O(a), evaluated once before the episode using a domain prior P₀ (not a calibrated T). The framework is "model-light" — it requires only enough T structure to rank actions, not a calibrated dynamic model.

---

## Key Results

| Benchmark | Domain | U_T | SARSOP − ELS gap | Verdict |
|---|---|---|---|---|
| B1 (synthetic) | UK synthetic anchor | 0.00 | **+170** units (10.0%) | SARSOP wins — price of T-agnosticism |
| B4 (MDB SDL) | Murray–Darling Basin | 0.70 | +45 (not significant) | Parity — parametric U_T=0.70 |
| B7 (coastal) | SE England / Netherlands | 0.70 | **−87** units, CI [−155, −15] | ELS wins — structural tipping-point |
| B8 (STAS) | Stampriet transboundary | 0.80 | **−77** units | ELS wins — game-theoretic T |
| B10 (LCB) | Sahel / Lake Chad Basin | 1.00 | **−128** units (16.8%) | ELS wins — maximal data scarcity |

The price-of-robustness gap (+170 at U_T=0.0) decays with increasing model uncertainty and reverses at structural uncertainty. At the data-scarcest benchmark (B10, 12 site-years of monitoring), ELS outperforms the best achievable SARSOP policy by 128–168 units (16.8–21.8%).

For full benchmark specifications — state/action/reward parameters, transition matrices, observation models, and per-benchmark results — see [`docs/NW_benchmarks_B1_B10.md`](docs/NW_benchmarks_B1_B10.md).

---

## Repository Structure

```
PyBELSA/
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
│
├── benchmarks/
│   ├── b1/                              # Benchmark 1 — Synthetic anchor (U_T=0.00)
│   │   ├── scr/
│   │   │   ├── pomdp_env.py             # 5-state synthetic POMDP (T=60, γ=0.97)
│   │   │   ├── els_methods.py           # ELSPhil, ELSPres, ELSInt, ELSPhilT, ELSIntT
│   │   │   ├── els_adapt.py             # ELSPhilAdapt, ELSIntAdapt (logit-space w)
│   │   │   ├── baselines.py             # SARSOP, PBVI, SDP, MPC, RDM, InfoGap,
│   │   │   │                            #   AlwaysRestricted, MyopicEU
│   │   │   ├── run_benchmark.py         # Monte Carlo engine (--dry-run, --n-mc N)
│   │   │   ├── sensitivity_w.py         # Fixed-w sweep → sensitivity_w_results.csv
│   │   │   ├── sensitivity_w_adapt.py   # Adaptive-w analysis → sensitivity_w_adapt_results.csv
│   │   │   ├── stats_analysis.py        # Wilcoxon + block bootstrap CI
│   │   │   ├── figures_fig1_price_robustness.py  # Fig. 1 (reads all 10 npz)
│   │   │   ├── figures_uncertainty_type.py        # Fig. 2 (reads b4, b7 npz)
│   │   │   ├── figures_adapt_window.py            # Fig. 3 (no npz needed)
│   │   │   └── figures_b10_comparison.py          # Fig. 4 (reads b10 npz)
│   │   └── output/
│   │       ├── raw_results.npz                    # B1 MC results (351 KB)
│   │       ├── sensitivity_w_results.csv
│   │       ├── sensitivity_w_adapt_results.csv
│   │       ├── sensitivity_w_report.md
│   │       ├── sensitivity_w_adapt_report.md
│   │       ├── stat_report_benchmark.md
│   │       └── tables/
│   │           ├── table_ucum.csv
│   │           ├── table_pfail.csv
│   │           ├── table_regret.csv
│   │           ├── table_pairwise.csv
│   │           └── table_nonstationarity.csv
│   │
│   ├── b2/                              # Benchmark 2 — MAR Arizona/Catalonia (U_T=0.50)
│   │   ├── scr/
│   │   │   ├── pomdp_env_b2.py
│   │   │   ├── els_methods.py
│   │   │   ├── els_adapt_b2.py
│   │   │   ├── baselines.py
│   │   │   ├── run_benchmark_b2.py
│   │   │   ├── sensitivity_w_b2.py
│   │   │   ├── sensitivity_w_adapt_b2.py
│   │   │   ├── stats_analysis.py
│   │   │   └── figures_b2.py
│   │   └── output/
│   │       ├── raw_results_b2.npz                 # 247 KB
│   │       ├── sensitivity_w_results_b2.csv
│   │       ├── sensitivity_w_adapt_results_b2.csv
│   │       ├── sensitivity_w_report_b2.md
│   │       ├── sensitivity_w_adapt_report_b2.md
│   │       ├── stat_report_b2.md
│   │       └── tables/
│   │           └── table_{ucum,pfail,regret,pairwise,nonstationarity}_b2.csv
│   │
│   ├── b3/   # Pump-and-treat Gorelick (U_T=0.60) — 234 KB
│   ├── b4/   # Murray–Darling SDL (U_T=0.70) — 252 KB
│   ├── b5/   # NCP GRACE (U_T=0.80) — 253 KB
│   ├── b6/   # Karst dual-porosity (U_T=0.90) — 256 KB
│   ├── b7/   # Coastal tipping-point (U_T=0.70 structural) — 231 KB
│   ├── b8/   # STAS transboundary (U_T=0.80 structural) — 249 KB
│   ├── b9/   # HKH glacier coupling (U_T=0.90 structural) — 253 KB
│   └── b10/  # LCB/Sahel data-scarce (U_T=1.00) — 252 KB
│
├── figures/                             # Publication figures (read-only outputs)
│   ├── fig1_price_of_robustness.pdf / .png
│   ├── fig2_uncertainty_type.pdf / .png
│   ├── fig3_adapt_window.pdf / .png
│   └── fig4_b10_comparison.pdf / .png
│
└── docs/
    └── NW_benchmarks_B1_B10.md         # Full specifications for all 10 benchmarks
```

Each `benchmarks/bN/` directory is self-contained: `els_methods.py`, `baselines.py`, and `stats_analysis.py` are copied into each benchmark to preserve script-level reproducibility without package import dependencies.

---

## Installation

**Requirements:** Python ≥ 3.11

```bash
git clone https://github.com/vitsch/PyBELSA.git
cd PyBELSA
pip install -r requirements.txt
```

`requirements.txt`:
```
numpy>=2.0
scipy>=1.17
matplotlib>=3.10
```

No external POMDP solver library is required. All environments and baseline policies are implemented in pure Python/NumPy. The SARSOP baseline uses pre-computed alpha-vectors stored in `benchmarks/b1/scr/baselines.py`.

---

## Usage

### 1. Reproduce publication figures from pre-computed results

```bash
# Apply path updates above, then from benchmarks/b1/:
python scr/figures_fig1_price_robustness.py   # Fig. 1 — reads all 10 npz files
python scr/figures_uncertainty_type.py         # Fig. 2 — reads b4, b7 npz
python scr/figures_adapt_window.py             # Fig. 3 — no data file needed
python scr/figures_b10_comparison.py           # Fig. 4 — reads b10 npz
```

Figures are written to `benchmarks/b1/output/image/` (PDF + PNG, 180 dpi).

### 2. Re-run Benchmark 1 Monte Carlo from scratch

```bash
cd benchmarks/b1

# Full run (N_MC=200, ~2–5 min on a standard laptop)
python scr/run_benchmark.py

# Quick dry-run (5 episodes — verifies environment, does not overwrite output)
python scr/run_benchmark.py --dry-run

# Custom episode count
python scr/run_benchmark.py --n-mc 50
```

Output written to `output/raw_results.npz` and `output/stat_report_benchmark.md`.

### 3. Re-run sensitivity analyses for Benchmark 1

```bash
cd benchmarks/b1

python scr/sensitivity_w.py         # fixed-w sweep → output/sensitivity_w_results.csv
python scr/sensitivity_w_adapt.py   # adaptive-w analysis → output/sensitivity_w_adapt_results.csv
```

### 4. Regenerate statistical tables for Benchmark 1

```bash
cd benchmarks/b1
python scr/stats_analysis.py
# Output: output/stat_report_benchmark.md
#         output/tables/table_{ucum,pfail,regret,pairwise,nonstationarity}.csv
```

### 5. Re-run any other benchmark

Benchmarks B2–B10 use benchmark-specific script names:

```bash
cd benchmarks/b7
python scr/run_benchmark_b7.py              # full MC run
python scr/run_benchmark_b7.py --dry-run    # quick check
python scr/sensitivity_w_b7.py              # fixed-w sweep
python scr/sensitivity_w_adapt_b7.py        # adaptive-w analysis
python scr/stats_analysis.py                # tables → output/tables/table_*_b7.csv
```

### 6. Use BELSA policies programmatically

```python
from benchmarks.b1.scr.pomdp_env import T_stat, R, LIKELIHOOD, GAMMA
from benchmarks.b1.scr.els_methods import ELSPhilT
from benchmarks.b1.scr.els_adapt import ELSPhilAdapt

# Fixed model-trust (w=0.5)
policy = ELSPhilT(w=0.5)
policy.reset()
action = policy.act(belief, t=0)

# Adaptive model-trust
policy_adapt = ELSPhilAdapt(eta=0.5)
policy_adapt.reset()
action = policy_adapt.act(belief, t=0)

# Benchmark 7 environment (coastal tipping-point)
from benchmarks.b7.scr.pomdp_env_b7 import T_stat as T_B7, R as R_B7
```

---

## Benchmarks

Ten benchmarks spanning parametric and structural uncertainty types. Full specifications — state/action/reward parameters, transition matrices, observation models, and per-benchmark results — are in [`docs/NW_benchmarks_B1_B10.md`](docs/NW_benchmarks_B1_B10.md).

### Parametric uncertainty (T form known, parameters uncertain)

| BM | Domain | Region | U_T | σ_obs | SARSOP − ELS gap |
|---|---|---|---|---|---|
| B1 | Synthetic 5-state aquifer | UK (synthetic) | 0.00 | 4.0 m | **+170** (10.0%) |
| B2 | Managed aquifer recharge | Arizona, US / Catalonia, ES | 0.50 | 35 GL | +175 |
| B3 | Pump-and-treat remediation | Illinois, US (Gorelick) | 0.60 | 28 μg/L | **−66** (ELS wins) |
| B4 | Surface–GW exchange (SDL) | Murray–Darling Basin, AU | 0.70 | 35 GL | +45 |
| B5 | GRACE depletion monitoring | North China Plain, CN | 0.80 | 45 mm WE | +44 |

### Structural uncertainty (T form unknown or unidentifiable)

| BM | Domain | Region | U_T | σ_obs | SARSOP − ELS gap |
|---|---|---|---|---|---|
| B6 | Dual-porosity karst | Dinaric / Mediterranean | 0.90 | 38 L/s | +43 |
| B7 | Coastal saltwater intrusion | SE England / Netherlands | 0.70 | log-normal | **−87**, CI [−155, −15] |
| B8 | Transboundary multi-actor (STAS) | Namibia / Botswana / SA | 0.80 | 42 mm WE | **−77** |
| B9 | Glacier–GW coupling (HKH) | Indus Basin, PK/IN/AF/CN | 0.90 | 48 mm WE | **−63** |
| B10 | Data-scarce pastoral aquifer | Sahel / Lake Chad Basin | 1.00 | 55 mm WE | **−128** vs SARSOP_Misspec |

---

## Data Completeness

All pre-computed outputs verified on 2026-04-27 (Python 3.13, numpy 2.4.3, scipy 1.17.1).

| BM | raw_results.npz | sens_w.csv | sens_w_adapt.csv | tables/ (5 CSVs) | stat_report.md |
|---|---|---|---|---|---|
| B1 | ✓ 351 KB | ✓ | ✓ | ✓ (no suffix) | ✓ stat_report_benchmark.md |
| B2 | ✓ 247 KB | ✓ | ✓ | ✓ _b2 | ✓ stat_report_b2.md |
| B3 | ✓ 234 KB | ✓ | ✓ | ✓ _b3 | ✓ stat_report_b3.md |
| B4 | ✓ 252 KB | ✓ | ✓ | ✓ _b4 | ✓ stat_report_b4.md |
| B5 | ✓ 253 KB | ✓ | ✓ | ✓ _b5 | ✓ stat_report_b5.md |
| B6 | ✓ 256 KB | ✓ | ✓ | ✓ _b6 | ✓ stat_report_b6.md |
| B7 | ✓ 231 KB | ✓ | ✓ | ✓ _b7 | ✓ stat_report_b7.md |
| B8 | ✓ 249 KB | ✓ | ✓ | ✓ _b8 | ✓ stat_report_b8.md |
| B9 | ✓ 253 KB | ✓ | ✓ | ✓ _b9 | ✓ stat_report_b9.md |
| B10 | ✓ 252 KB | ✓ | ✓ | ✓ _b10 | ✓ stat_report_b10.md |

**B1 naming note:** B1 table CSVs use no benchmark suffix (e.g. `table_ucum.csv`); B1 stat report is `stat_report_benchmark.md`. All other benchmarks use `_bN` suffixes.

**B7–B10 fix note:** A copy-paste error in the original `stats_analysis.py` scripts for B7–B10 caused output files to carry a `_b6` suffix. Fixed on 2026-04-27 by updating output filenames in each script and re-running; stale `_b6` files removed.

---

## Evaluation Protocol

| Element              | Specification                                                                                   |
| -------------------- | ----------------------------------------------------------------------------------------------- |
| Episodes             | N_MC = 200 per method per condition                                                             |
| Discount factor      | γ = 0.97                                                                                        |
| Random seed          | SEED = 2024                                                                                     |
| Pairwise test        | Wilcoxon signed-rank, two-sided, Bonferroni α* = 0.0011 (k = 45 pairs)                          |
| Confidence intervals | Percentile block bootstrap, B = 2000, block size = 10, `numpy.random.default_rng(42)`           |
| Evaluation utility   | U_eval(a, θ) = R(a, θ) — raw reward, no framework augmentation                                  |
| Convergence          | Rolling-window SE ratio SE(N)/SE(25) < 0.10 at N = 200 — satisfied for all B1–B10               |
| Compute environment  | Intel Core i7-14700F (20 cores, 5.4 GHz max), 64 GB RAM; Python 3.13, numpy 2.4.3, scipy 1.17.1 |

---

## Data Availability

All pre-computed Monte Carlo results are included in this repository under `benchmarks/bN/output/raw_results_bN.npz`. These files are the authoritative source for all reported U_cum, P_fail, and regret values (γ = 0.97, N_MC = 200, SEED = 2024; bootstrap B = 2000, SEED = 42).

A supplementary deposit including `bootstrap_ci_all.csv` will be made available on Zenodo (DOI: `10.5281/zenodo.XXXXXXX` — to be assigned on acceptance).

---

## Citation

If you use PyBELSA in your research, please cite:

```
Jakaite, L. and Schetinin, V. (2026). An empirical crossover law for model-agnostic POMDP
policies under transition-model misspecification.
Nature Machine Intelligence. [under review]
```

---

## License

MIT License. See [`LICENSE`](LICENSE) for details.
