# =============================================================================
# run_benchmark.py  —  Monte Carlo Evaluation Loop
# Project  : ELS_NEW / P_Base  (Benchmark 9 — Indus Basin / HKH Glacial Meltwater Recharge)
# Plan ref : experiment_plan.md §5 Step 4
# Date     : 2026-04-25
# Usage    : python scr/run_benchmark_b9.py
#            python scr/run_benchmark_b9.py --dry-run   (5 episodes, quick check)
# Outputs  : output/raw_results.npz  (all episode arrays, auditable)
# =============================================================================
"""
Monte Carlo benchmark runner.

Evaluates 12 methods × 2 conditions (stationary / nonstationary) over
N_MC = 200 episodes of T = 30 steps, using GAMMA = 0.97 and SEED = 2024.

Stored arrays per (method, condition)
--------------------------------------
rewards    : (N_MC, T)  float   — R[a_t, θ_{t+1}]  (raw arrival reward)
states     : (N_MC, T)  int8    — true hidden state after each step (0–4)
actions    : (N_MC, T)  int8    — action taken each step (0–2)
init_states: (N_MC,)    int8    — initial hidden state at episode start
k_phil     : (N_MC, T)  bool    — True where ELS_Int selected phil selector
                                   (all zeros for non-ELS_Int methods)

Belief update routing
---------------------
ELS_Phil   : static L_PHIL   (model-averaged σ=3.5/σ=5.5 Gaussian)
ELS_Pres   : static L_PRES   (single σ=4.0 Gaussian)
ELS_Int    : policy.phys_belief_update()  (P_hyb, static, α-weighted)
SARSOP/PBVI: Markovian, always T_stat  (alpha vectors assume T_stat model)
SDP_NS     : Markovian, true-regime T  (matches existing validate() behaviour)
All others : Markovian, condition-aware (T_stat in stationary; true T in NS)

MyopicEU   : oracle swap — in stationary condition uses T_stat throughout
             (no switch at t=30, consistent with the stationary environment)

SDPNonStationary : policy.update(b, a, b_next) called after each step (EM).
SARSOP/PBVI : solve() called once before the MC loop (T_stat offline).
ELSInt      : reset(seed=ep_seed) per episode (deterministic Bernoulli draws).

Seeding strategy
----------------
Environment seed per episode: np.random.default_rng([SEED, m_idx, c_idx, ep_idx])
ELSInt Bernoulli seed  :       np.random.default_rng([SEED+7000, m_idx, ep_idx])
All seeds derived from SEED=2024 — fully reproducible.
"""

import argparse
import os
import sys
import time

import numpy as np

# ---------------------------------------------------------------------------
# Import POMDP environment and policies
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pomdp_env_b9 as env
from pomdp_env_b9 import (
    N, M, N_OBS, T, GAMMA, SEED, FAILURE_STATE,
    R, T_stat, T_shift, T_misspec, T_climate, LIKELIHOOD,
)
from baselines import (
    SARSOPPolicy, PBVIPolicy, SDPStationary, SDPNonStationary,
    MPCPolicy, RDMPolicy, InfoGapPolicy, AlwaysRestricted, MyopicEU,
)
from els_methods import (
    ELSPhil, ELSPres, ELSInt, ELSPhilT, ELSIntT,
    ELS_BELIEF_UPDATE, ELS_PHYS_UPDATE_METHODS,
    W_TRANS,
)

# Shorthand used by vectorised SDP helpers
_L = LIKELIHOOD   # (N, N_OBS)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
N_MC       = env.N_MC       # 200
CONDITIONS = ["stationary", "nonstationary"]
OUTPUT_DIR = os.path.join(os.path.dirname(_HERE), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

METHOD_ORDER = [
    # Core methods (m_idx 0-11) — preserve episode seeds across all runs
    "ELS_Phil", "ELS_Pres", "ELS_Int",
    "SARSOP", "PBVI", "SDP_S", "SDP_NS",
    "MPC", "RDM", "InfoGap", "AlwaysRestricted", "MyopicEU",
    # Priority 1 T-misspecification ablation (m_idx 12-13)
    "SARSOP_Misspec", "SDP_S_Misspec",
    # Priority 2: hybrid-belief T-variants (m_idx 14-15)
    "ELS_Phil_T", "ELS_Int_T",
]

# ---------------------------------------------------------------------------
# Vectorised depth-2 SDP helpers
# ---------------------------------------------------------------------------
def _sdp2_act(belief: np.ndarray, T_mat: np.ndarray) -> int:
    """
    Vectorised 2-step Markovian lookahead: argmax_a V_2(b, a).

      V_2(b, a1) = E[R(a1,θ')|b1] + γ · Σ_o P(o|b1) · max_a2 E[R(a2,θ'')|b2(o)]

    where b1 = T_mat[a1].T @ b, b2(o) ∝ L[:,o] · b1.

    Replaces the depth-3 recursive _lookahead_value for the MC runner to avoid
    Python-loop overhead: ~100× faster with identical per-decision quality for
    well-separated state spaces (see summary_step_4.md §Design decisions).

    Parameters
    ----------
    belief : (N,) current belief
    T_mat  : (M, N, N) transition matrices to use

    Returns
    -------
    best action int (0–M-1)
    """
    # Q[a2, s] = Σ_s' T_mat[a2, s, s'] · R[a2, s'] — depth-1 state-action values
    Q = np.einsum("aij,aj->ai", T_mat, R)   # (M, N)

    vals = np.empty(M, dtype=float)
    for a1 in range(M):
        b1 = T_mat[a1].T @ belief            # (N,)  predicted belief after a1
        r1 = float(b1 @ R[a1])              # expected immediate reward

        p_o = b1 @ _L                       # (N_OBS,)  P(obs=o | b1)
        # Posterior beliefs for all obs (unnormalised)
        b2 = _L.T * b1[None, :]             # (N_OBS, N)  b2[o,s] = L[s,o]·b1[s]
        safe_p = np.where(p_o > 1e-12, p_o, 1.0)
        b2 /= safe_p[:, None]               # row-normalise

        # eu2[o, a2] = E[R(a2, θ'') | b2[o]]; vectorised via precomputed Q
        eu2     = b2 @ Q.T                  # (N_OBS, M)
        best_r2 = eu2.max(axis=1)           # (N_OBS,)

        vals[a1] = r1 + GAMMA * float((p_o * best_r2).sum())

    return int(np.argmax(vals))


class _SDPSVec:
    """
    Vectorised depth-2 SDP (stationary T_stat) for the MC benchmark.

    Uses _sdp2_act() instead of the depth-3 recursive _lookahead_value
    from baselines.SDPStationary.  Provides ~100× speedup; policy quality
    is nearly identical for N=5 well-separated states.
    """
    NAME = "SDP_S"

    def reset(self) -> None:
        pass

    def act(self, belief: np.ndarray, t: int) -> int:
        return _sdp2_act(belief, T_stat)


# ---------------------------------------------------------------------------
# T-misspecification ablation classes (Priority 1)
# ---------------------------------------------------------------------------
class _SARSOPMisspecPolicy(SARSOPPolicy):
    """
    SARSOP solved on T_misspec (+15% depletion) but evaluated in the
    standard environment.  Demonstrates that SARSOP's Benchmark 1
    advantage is contingent on having the correct T.
    The belief update also uses T_misspec (agent's worldmodel is wrong).
    """
    NAME = "SARSOP_Misspec"
    N_BELIEF_PTS = 200

    def __init__(self, seed: int = SEED):
        super().__init__(seed=seed, T_mat=T_misspec)


class _SDPSMisspecVec:
    """
    Vectorised depth-2 SDP using T_misspec (+15% depletion) for both
    action selection and belief update.  Paired with SARSOP_Misspec to
    show misspecification degradation of model-knowing policies.
    """
    NAME = "SDP_S_Misspec"

    def reset(self) -> None:
        pass

    def act(self, belief: np.ndarray, t: int) -> int:
        return _sdp2_act(belief, T_misspec)


class _SDPNSVec(SDPNonStationary):
    """
    Vectorised depth-2 SDP with online EM (non-stationary).

    Inherits reset() and update() from SDPNonStationary; overrides act()
    to use _sdp2_act() with the learned T_est instead of the recursive
    depth-3 _lookahead_value.
    """
    NAME = "SDP_NS"

    def act(self, belief: np.ndarray, t: int) -> int:
        return _sdp2_act(belief, self._T_est)


# ---------------------------------------------------------------------------
# MyopicEU oracle variant for the stationary condition
# ---------------------------------------------------------------------------
class _MyopicEUStat:
    """
    Oracle upper bound for stationary condition.
    Knows the true model is T_stat throughout — no climate switch at t=30.
    """
    NAME = "MyopicEU"

    def reset(self) -> None:
        pass

    def act(self, belief: np.ndarray, t: int) -> int:
        best_a, best_val = 0, -np.inf
        for a in range(M):
            b_pred = T_stat[a].T @ belief
            val = float(b_pred @ R[a])
            if val > best_val:
                best_val, best_a = val, a
        return best_a


# ---------------------------------------------------------------------------
# Policy factory — fresh instances for each condition
# ---------------------------------------------------------------------------
def _make_policies(stationary: bool, sarsop_inst, pbvi_inst, sarsop_misspec_inst) -> dict:
    """
    Return a dict of instantiated policy objects for one condition.
    SARSOP and PBVI are reused (already solved); all others are fresh.
    """
    return {
        "ELS_Phil":        ELSPhil(),
        "ELS_Pres":        ELSPres(),
        "ELS_Int":         ELSInt(seed=SEED),
        # Priority 2: hybrid-belief T-variants
        "ELS_Phil_T":      ELSPhilT(w=W_TRANS),
        "ELS_Int_T":       ELSIntT(seed=SEED, w=W_TRANS),
        "SARSOP":          sarsop_inst,
        "PBVI":            pbvi_inst,
        "SDP_S":           _SDPSVec(),
        "SDP_NS":          _SDPNSVec(),
        "MPC":             MPCPolicy(),
        "RDM":             RDMPolicy(),
        "InfoGap":         InfoGapPolicy(),
        "AlwaysRestricted": AlwaysRestricted(),
        "MyopicEU":        _MyopicEUStat() if stationary else MyopicEU(),
        # Priority 1 misspecification ablation (reuse pre-solved instances)
        "SARSOP_Misspec":  sarsop_misspec_inst,
        "SDP_S_Misspec":   _SDPSMisspecVec(),
    }


# ---------------------------------------------------------------------------
# Environment step (condition-aware, no import side effects)
# ---------------------------------------------------------------------------
def _step(
    state: int, action: int, t: int,
    rng: np.random.Generator, stationary: bool,
) -> tuple[int, int, float]:
    T_use = T_stat if stationary else T_climate(t)
    next_state = int(rng.choice(N, p=T_use[action, state]))
    obs_idx    = int(rng.choice(N_OBS, p=LIKELIHOOD[next_state]))
    reward     = float(R[action, next_state])
    return next_state, obs_idx, reward


# ---------------------------------------------------------------------------
# Belief update dispatch (method-aware, condition-aware)
# ---------------------------------------------------------------------------
def _update_belief(
    policy, b: np.ndarray, obs: int, action: int, t: int, stationary: bool,
) -> np.ndarray:
    """
    Route belief update to the correct method for each policy.

    ELS_Int    → phys_belief_update (P_hyb)
    ELS_Phil/Pres → ELS_BELIEF_UPDATE dispatch (static L_PHIL / L_PRES)
    SARSOP/PBVI → Markovian with T_stat always (alpha vectors assume T_stat)
    All others → Markovian with condition-aware T
    """
    name = policy.NAME

    # ELS_Int / ELS_Phil_T / ELS_Int_T use phys_belief_update(b, obs, action)
    # ELS_Phil / ELS_Pres use the module-level static functions (action-independent)
    if name in ELS_PHYS_UPDATE_METHODS:
        return policy.phys_belief_update(b, obs, action)
    if name in ELS_BELIEF_UPDATE:
        return ELS_BELIEF_UPDATE[name](b, obs)

    # SARSOP / PBVI: always use T_stat (model is solved on T_stat; no adaptation)
    # Misspecified variants use T_misspec for their (wrong) worldmodel belief update
    if name in ("SARSOP", "PBVI"):
        T_use = T_stat
    elif name in ("SARSOP_Misspec", "SDP_S_Misspec"):
        T_use = T_misspec
    elif stationary:
        T_use = T_stat
    else:
        T_use = T_climate(t)

    b_pred = T_use[action].T @ b
    b_new  = LIKELIHOOD[:, obs] * b_pred
    z = b_new.sum()
    if z < 1e-300:
        return b_pred / b_pred.sum()
    return b_new / z


# ---------------------------------------------------------------------------
# Single episode runner
# ---------------------------------------------------------------------------
def _run_episode(
    policy,
    stationary: bool,
    ep_rng: np.random.Generator,
    els_ep_seed: int | None = None,
) -> tuple[int, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Run one episode.

    Returns
    -------
    init_state : int
    rewards    : ndarray (T,)
    states     : ndarray (T,) int8
    actions    : ndarray (T,) int8
    k_phil     : ndarray (T,) bool  — True where ELS_Int selected phil
    """
    init_state = int(ep_rng.integers(0, N))

    # Initial belief: framework-specific for ELS, uniform for all baselines
    b = policy.initial_belief() if hasattr(policy, "initial_belief") \
        else np.full(N, 1.0 / N)

    # Reset policy state
    if isinstance(policy, ELSInt):
        policy.reset(seed=els_ep_seed)
    else:
        policy.reset()

    rewards = np.empty(T, dtype=float)
    states  = np.empty(T, dtype=np.int8)
    actions = np.empty(T, dtype=np.int8)
    k_phil  = np.zeros(T, dtype=bool)

    state = init_state
    for t in range(T):
        a                         = policy.act(b, t)
        next_state, obs, reward   = _step(state, a, t, ep_rng, stationary)
        b_next                    = _update_belief(policy, b, obs, a, t, stationary)

        if isinstance(policy, SDPNonStationary):
            policy.update(b, a, b_next)

        if isinstance(policy, ELSInt):
            k_phil[t] = (policy.last_k_t == "phil")

        rewards[t] = reward
        states[t]  = np.int8(next_state)
        actions[t] = np.int8(a)
        b          = b_next
        state      = next_state

    return init_state, rewards, states, actions, k_phil


# ---------------------------------------------------------------------------
# Monte Carlo evaluation for one (policy, condition)
# ---------------------------------------------------------------------------
def _run_mc(
    name: str,
    policy,
    stationary: bool,
    m_idx: int,
    n_mc: int,
    verbose: bool = True,
) -> dict[str, np.ndarray]:
    """
    Run n_mc episodes and return episode-level arrays.

    Seed scheme (fully deterministic):
      env  seed: [SEED, m_idx, int(stationary), ep]
      ELS_Int   : [SEED + 7000, m_idx, ep]
    """
    c_idx = int(not stationary)   # 0=stationary, 1=nonstationary

    all_rewards     = np.empty((n_mc, T), dtype=float)
    all_states      = np.empty((n_mc, T), dtype=np.int8)
    all_actions     = np.empty((n_mc, T), dtype=np.int8)
    all_k_phil      = np.zeros((n_mc, T), dtype=bool)
    all_init_states = np.empty(n_mc, dtype=np.int8)

    for ep in range(n_mc):
        ep_rng = np.random.default_rng([SEED, m_idx, c_idx, ep])
        els_seed = int(np.random.default_rng([SEED + 7000, m_idx, ep])
                       .integers(0, 2**31)) if isinstance(policy, ELSInt) else None

        init_s, rew, sts, acts, kp = _run_episode(
            policy, stationary, ep_rng, els_seed
        )
        all_rewards[ep]     = rew
        all_states[ep]      = sts
        all_actions[ep]     = acts
        all_k_phil[ep]      = kp
        all_init_states[ep] = np.int8(init_s)

    if verbose:
        discount = GAMMA ** np.arange(T)
        ucum     = (all_rewards * discount).sum(axis=1)
        pfail    = np.any(all_states == FAILURE_STATE, axis=1).mean()
        # MTTF: first step where state == FAILURE_STATE; NaN if never fails
        fail_mask = all_states == FAILURE_STATE
        mttf_vals = np.where(
            fail_mask.any(axis=1),
            np.argmax(fail_mask, axis=1).astype(float),
            np.nan,
        )
        cond_str = "stat" if stationary else "ns  "
        mttf_str = f"{np.nanmean(mttf_vals):.1f}" if np.any(~np.isnan(mttf_vals)) else " n/a"
        print(
            f"  {name:<16}  {cond_str}  "
            f"U_cum={ucum.mean():7.1f}±{ucum.std():5.1f}  "
            f"P_fail={pfail:.3f}  MTTF={mttf_str}",
            flush=True,
        )

    return {
        "rewards":     all_rewards,
        "states":      all_states,
        "actions":     all_actions,
        "k_phil":      all_k_phil,
        "init_states": all_init_states,
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def main(n_mc: int = N_MC, verbose: bool = True) -> str:
    """
    Run the full benchmark and save results to output/raw_results.npz.

    Parameters
    ----------
    n_mc    : number of Monte Carlo episodes (default N_MC=200)
    verbose : print per-method progress

    Returns
    -------
    Path to the saved NPZ file.
    """
    t_start = time.time()

    if verbose:
        print("=" * 72)
        print("run_benchmark_b9.py — MC Evaluation (Benchmark 9)")
        print(f"  N_MC={n_mc}  T={T}  GAMMA={GAMMA}  SEED={SEED}")
        print(f"  Methods : {len(METHOD_ORDER)}")
        print(f"  Conditions: {CONDITIONS}")
        print("=" * 72)

    # ------------------------------------------------------------------
    # Offline solve for alpha-vector methods (T_stat, once for both
    # conditions — alpha vectors assume T_stat regardless of condition)
    # SARSOP_Misspec solved on T_misspec (+15% depletion ablation)
    # ------------------------------------------------------------------
    if verbose:
        print("\nOffline solve (SARSOP / PBVI / SARSOP_Misspec):")
    sarsop         = SARSOPPolicy(seed=SEED)
    pbvi           = PBVIPolicy(seed=SEED)
    sarsop_misspec = _SARSOPMisspecPolicy(seed=SEED)
    for pol, tag in [(sarsop, "SARSOP"), (pbvi, "PBVI"), (sarsop_misspec, "SARSOP_Misspec")]:
        t0 = time.time()
        if verbose:
            print(f"  Solving {tag}...", end=" ", flush=True)
        pol.solve(verbose=False)
        if verbose:
            print(f"done ({time.time() - t0:.1f}s)")

    # ------------------------------------------------------------------
    # Monte Carlo evaluation loop
    # ------------------------------------------------------------------
    results: dict[str, dict[str, dict]] = {name: {} for name in METHOD_ORDER}

    for cond in CONDITIONS:
        stationary = (cond == "stationary")
        if verbose:
            print(f"\nCondition: {cond}")
            print(f"  {'Method':<16}  {'cond':<5}  {'U_cum':>14}  {'P_fail':>8}  {'MTTF':>6}")
            print(f"  {'-'*64}")

        policies = _make_policies(stationary, sarsop, pbvi, sarsop_misspec)

        for m_idx, name in enumerate(METHOD_ORDER):
            policy   = policies[name]
            ep_data  = _run_mc(name, policy, stationary, m_idx, n_mc, verbose)
            results[name][cond] = ep_data

    # ------------------------------------------------------------------
    # Save to NPZ
    # NPZ key format: {method}__{condition}__{array_name}
    # Metadata stored as string arrays
    # ------------------------------------------------------------------
    npz_data: dict[str, np.ndarray] = {}
    for name in METHOD_ORDER:
        for cond in CONDITIONS:
            for key, arr in results[name][cond].items():
                npz_data[f"{name}__{cond}__{key}"] = arr

    # Metadata for downstream consumers
    npz_data["_method_order"] = np.array(METHOD_ORDER)
    npz_data["_conditions"]   = np.array(CONDITIONS)
    npz_data["_config_N_MC"]  = np.array([n_mc])
    npz_data["_config"]       = np.array([n_mc, T, GAMMA, float(SEED)])

    out_path = os.path.join(OUTPUT_DIR, "raw_results_b9.npz")
    np.savez_compressed(out_path, **npz_data)

    elapsed = time.time() - t_start
    if verbose:
        print(f"\n{'='*72}")
        print(f"Benchmark complete in {elapsed:.1f}s  ({elapsed/60:.1f} min)")
        print(f"Output: {out_path}")
        print(f"NPZ keys: {len(npz_data)} arrays")
        print(f"{'='*72}")

    return out_path


# ---------------------------------------------------------------------------
# Validation: quick dry run (5 episodes) to verify no crashes
# ---------------------------------------------------------------------------
def validate_dry_run() -> None:
    """
    Abbreviated run (5 episodes, nonstationary only) to check all methods work.
    """
    print("=" * 72)
    print("run_benchmark.py — dry-run validation (5 episodes, nonstationary)")
    print("=" * 72)
    main(n_mc=5, verbose=True)
    print("Dry-run passed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ELS Benchmark MC runner")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Quick 5-episode test (verifies no crashes; does not replace full run)",
    )
    parser.add_argument(
        "--n-mc", type=int, default=N_MC,
        help=f"Override N_MC (default: {N_MC})",
    )
    args = parser.parse_args()

    if args.dry_run:
        validate_dry_run()
    else:
        main(n_mc=args.n_mc)
