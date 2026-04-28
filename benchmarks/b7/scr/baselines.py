# =============================================================================
# baselines.py  —  Standard Solver Baselines for Groundwater POMDP Benchmark
# Project  : ELS_NEW / P_Base  (Benchmark 7 — Karst Aquifer)
# Plan ref : experiment_plan.md §5 Step 2
# Date     : 2026-04-25
# Usage    : from baselines import ALL_BASELINES; policy = ALL_BASELINES["SARSOP"]()
# =============================================================================
"""
Nine baseline policies, each exposing:
    policy.reset()             — call at the start of each episode
    policy.act(belief, t)      — return action int (0–2) given belief and step t

Offline policies (SARSOP, PBVI):
    policy.solve(verbose=False) — pre-compute alpha-vector plan (call once before MC loop)

Policy inventory
----------------
SARSOP          Alpha-vector backward induction, 200 belief pts (near-optimal)
PBVI            Alpha-vector backward induction, 50 belief pts (fast approximation)
SDP_S           3-step lookahead, known stationary T_stat throughout
SDP_NS          3-step lookahead, EM-updated T estimate (detects regime shift)
MPC             1-step greedy EU-max with Markovian predict, known T_stat
RDM             9-scenario regret minimisation (Lempert/RAND approach)
InfoGap         Robustness function ρ(a,b); Ben-Haim info-gap theory
AlwaysRestricted  Always select a₂ (conservative heuristic)
MyopicEU        Oracle 1-step greedy with true regime T (upper bound)
"""

import sys
import os
import numpy as np

# ---------------------------------------------------------------------------
# Import POMDP environment
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pomdp_env_b7 as env
from pomdp_env_b7 import (
    N, M, N_OBS, T, GAMMA, SEED, CLIMATE_SWITCH_STEP,
    R, T_stat, T_shift, LIKELIHOOD,
    expected_reward, entropy_norm, markov_update_belief,
)

# Shorthand
L = LIKELIHOOD   # shape (N, N_OBS)


# ===========================================================================
# Alpha-vector backend  (shared by SARSOP and PBVI)
# ===========================================================================

def _sample_belief_pts(n: int, rng: np.random.Generator) -> np.ndarray:
    """
    n Dirichlet-sampled belief points augmented with N corner points.
    Returns shape (n+N, N).
    """
    corners = np.eye(N, dtype=float)
    interior = rng.dirichlet(np.ones(N), size=n)
    return np.vstack([corners, interior])


def _precompute_alpha_ao(Gamma: np.ndarray, T_mat: np.ndarray) -> np.ndarray:
    """
    Precompute the per-(action, obs, alpha-vector) backed-up vectors.

    alpha_ao[a, o, k, s] = Σ_{s'} T_mat[a, s, s'] · L[s', o] · Gamma[k, s']

    Parameters
    ----------
    Gamma  : (K, N) current alpha vectors
    T_mat  : (M, N, N) transition matrices

    Returns
    -------
    alpha_ao : (M, N_OBS, K, N)
    """
    K = Gamma.shape[0]
    # g[o, k, s'] = L[s', o] · Gamma[k, s']
    # L.T: (N_OBS, N); broadcast -> (N_OBS, K, N)
    g = L.T[:, np.newaxis, :] * Gamma[np.newaxis, :, :]   # (N_OBS, K, N)

    alpha_ao = np.empty((M, N_OBS, K, N), dtype=float)
    for a in range(M):
        # einsum 'ij,okj->oki': T_mat[a] (N×N) × g (N_OBS×K×N_col) → (N_OBS, K, N_row)
        alpha_ao[a] = np.einsum('ij,okj->oki', T_mat[a], g)
    return alpha_ao


def _backup_step(
    Gamma: np.ndarray,
    T_mat: np.ndarray,
    belief_pts: np.ndarray,
) -> np.ndarray:
    """
    One alpha-vector backup step (PBVI-style).

    For each belief point b, compute the best backed-up alpha vector over
    all actions, using the argmax-per-observation selection rule.

    Parameters
    ----------
    Gamma      : (K, N)  alpha vectors for the NEXT step
    T_mat      : (M, N, N)  transition matrices to use
    belief_pts : (B, N)  belief points to back up

    Returns
    -------
    new_vecs : (B, N)  one new alpha vector per belief point (with action embedded)
    """
    alpha_ao = _precompute_alpha_ao(Gamma, T_mat)   # (M, N_OBS, K, N)
    B = belief_pts.shape[0]
    new_vecs = np.empty((B, N), dtype=float)

    for i in range(B):
        b = belief_pts[i]
        best_val = -np.inf
        best_vec = np.zeros(N)

        for a in range(M):
            # vals[o, k] = dot(alpha_ao[a, o, k], b)
            vals = alpha_ao[a] @ b          # (N_OBS, K, N) @ (N,) = (N_OBS, K)
            best_k = np.argmax(vals, axis=1)   # (N_OBS,)

            # Gather best vector per obs and sum
            best_vecs_o = alpha_ao[a, np.arange(N_OBS), best_k, :]  # (N_OBS, N)
            vec_a = R[a] + GAMMA * best_vecs_o.sum(axis=0)            # (N,)

            val = vec_a @ b
            if val > best_val:
                best_val = val
                best_vec = vec_a

        new_vecs[i] = best_vec

    return new_vecs


def _prune_dominated(Gamma: np.ndarray, belief_pts: np.ndarray) -> np.ndarray:
    """
    Remove alpha vectors that are never maximal over the given belief points.
    Keeps at most MAX_VECS vectors.
    """
    MAX_VECS = 400
    if Gamma.shape[0] <= N:
        return Gamma

    # vals[k, b] = Gamma[k] @ belief_pts[b]
    vals = Gamma @ belief_pts.T   # (K, B)
    # Keep k if it is the argmax for at least one b
    winners = np.unique(np.argmax(vals, axis=0))
    Gamma_pruned = Gamma[winners]

    if Gamma_pruned.shape[0] > MAX_VECS:
        Gamma_pruned = Gamma_pruned[:MAX_VECS]

    return Gamma_pruned


def _best_action_alpha(
    Gamma: np.ndarray,
    T_mat: np.ndarray,
    belief: np.ndarray,
    t: int,
    alpha_next: np.ndarray,
) -> int:
    """
    Greedy action selection at step t given alpha vectors for step t+1.
    Returns argmax_a [ R[a] + γ Σ_o max_{α∈alpha_next} α·τ(a,o,b) ] · b
    """
    if alpha_next.shape[0] == 0:
        return int(np.argmax([expected_reward(belief, a) for a in range(M)]))

    alpha_ao = _precompute_alpha_ao(alpha_next, T_mat)   # (M, N_OBS, K, N)
    best_a = 0
    best_val = -np.inf

    for a in range(M):
        vals = alpha_ao[a] @ belief          # (N_OBS, K)
        best_k = np.argmax(vals, axis=1)
        best_vecs_o = alpha_ao[a, np.arange(N_OBS), best_k, :]
        vec_a = R[a] + GAMMA * best_vecs_o.sum(axis=0)
        val = float(vec_a @ belief)
        if val > best_val:
            best_val = val
            best_a = a

    return best_a


# ===========================================================================
# 1. SARSOPPolicy  —  alpha-vector backward induction, 200 belief points
# ===========================================================================

class SARSOPPolicy:
    """
    Approximately optimal POMDP policy via alpha-vector backward induction.

    Offline solve uses T_mat (default T_stat) and 200 random belief points.
    Online act() is O(T_remaining × M × N_OBS × K × N) but K is pruned.

    Offline only: does not adapt when T_shift takes effect at t=30.
    This makes it comparable to SDP-S (both assume stationary T_stat).

    The optional T_mat parameter allows solving on a misspecified transition
    matrix for ablation studies (see Priority 1 T-misspecification ablation).
    """
    NAME = "SARSOP"
    N_BELIEF_PTS = 200

    def __init__(self, seed: int = SEED, T_mat: np.ndarray | None = None):
        self._rng = np.random.default_rng(seed)
        self._belief_pts = _sample_belief_pts(self.N_BELIEF_PTS, self._rng)
        self._alpha_seq: list[np.ndarray] = []   # [t] → (K, N)
        self._solved = False
        self._T_mat = T_mat if T_mat is not None else T_stat

    def solve(self, verbose: bool = False) -> None:
        """Backward induction from t=T down to t=0.  Call once before MC loop."""
        Gamma = np.zeros((1, N), dtype=float)   # terminal: V_{T+1} = 0
        seq = [Gamma]

        for t in range(T - 1, -1, -1):
            new_vecs = _backup_step(Gamma, self._T_mat, self._belief_pts)
            Gamma = _prune_dominated(new_vecs, self._belief_pts)
            seq.insert(0, Gamma)
            if verbose and t % 10 == 0:
                print(f"  {self.NAME} t={t:3d}  |Γ|={Gamma.shape[0]}")

        self._alpha_seq = seq
        self._solved = True

    def reset(self) -> None:
        pass   # stateless at episode level

    def act(self, belief: np.ndarray, t: int) -> int:
        if not self._solved:
            raise RuntimeError("Call solve() before act()")
        t_clamped = min(t, T - 1)
        alpha_next = self._alpha_seq[min(t_clamped + 1, T)]
        return _best_action_alpha(
            self._alpha_seq[t_clamped], self._T_mat, belief, t, alpha_next
        )


# ===========================================================================
# 2. PBVIPolicy  —  same as SARSOP but only 50 belief points (faster)
# ===========================================================================

class PBVIPolicy(SARSOPPolicy):
    """
    Point-based value iteration with 50 belief points.
    Faster offline solve; less accurate than SARSOP in under-covered regions.
    """
    NAME = "PBVI"
    N_BELIEF_PTS = 50


# ===========================================================================
# Lookahead rollout helper  (shared by SDP-S, SDP-NS, MPC, MyopicEU)
# ===========================================================================

def _lookahead_value(
    belief: np.ndarray,
    action: int,
    T_mat: np.ndarray,
    depth: int,
) -> float:
    """
    Recursive expected cumulative reward for given action over `depth` steps,
    averaging over all observations (Markovian belief propagation).

    depth=1 reduces to plain Markovian EU-max (MPC).
    Computation is O(M^depth × N_OBS^depth × N).  Feasible for depth≤3.
    """
    if depth == 0:
        return 0.0

    # Predict next belief after action
    b_pred = T_mat[action].T @ belief   # (N,)

    total = 0.0
    for o in range(N_OBS):
        # Probability of this observation
        p_o = float(L[:, o] @ b_pred)
        if p_o < 1e-12:
            continue

        # Posterior belief
        b_next = L[:, o] * b_pred
        b_next /= b_next.sum()

        # Reward on arrival: E[R(a, θ')] = b_pred · R[action]
        r_now = float(b_pred @ R[action])

        # Greedy next action
        if depth > 1:
            vals = [_lookahead_value(b_next, a2, T_mat, depth - 1) for a2 in range(M)]
            best_future = max(vals)
        else:
            best_future = 0.0

        total += p_o * (r_now + GAMMA * best_future)

    return total


# ===========================================================================
# 3. SDPStationary  —  3-step lookahead, T_stat known and fixed
# ===========================================================================

class SDPStationary:
    """
    Stochastic DP with 3-step Markovian rollout using known stationary T_stat.
    Does not adapt when climate shift occurs at t=30.
    """
    NAME = "SDP_S"
    DEPTH = 3

    def reset(self) -> None:
        pass

    def act(self, belief: np.ndarray, t: int) -> int:
        vals = [_lookahead_value(belief, a, T_stat, self.DEPTH) for a in range(M)]
        return int(np.argmax(vals))


# ===========================================================================
# 4. SDPNonStationary  —  3-step lookahead, online EM-updated T estimate
# ===========================================================================

class SDPNonStationary:
    """
    SDP with online transition-model learning via belief-weighted EM.

    Soft counts accumulate each step:
        Δn[a, s, s'] += b_t(s) · b_{t+1}(s')
    T estimate is the row-normalised posterior mean (Dirichlet):
        T_est[a, s, s'] ∝ prior_count[a,s,s'] + Δn[a,s,s']

    Prior counts initialised from T_stat (scaled by UPDATE_SCALE to set
    prior strength relative to observed transitions).
    """
    NAME = "SDP_NS"
    DEPTH = 3
    UPDATE_FREQ = 5          # recompute T_est every N steps
    PRIOR_SCALE = 20.0       # pseudo-counts for T_stat prior

    def __init__(self):
        self._prior = T_stat * self.PRIOR_SCALE   # (M, N, N)
        self._counts = np.zeros((M, N, N), dtype=float)
        self._T_est = T_stat.copy()
        self._prev_belief: np.ndarray | None = None
        self._prev_action: int | None = None
        self._steps_since_update = 0

    def reset(self) -> None:
        self._counts = np.zeros((M, N, N), dtype=float)
        self._T_est = T_stat.copy()
        self._prev_belief = None
        self._prev_action = None
        self._steps_since_update = 0

    def update(self, belief: np.ndarray, action: int, belief_next: np.ndarray) -> None:
        """Accumulate soft counts for transition (belief → action → belief_next)."""
        # Outer product: b_t(s) · b_{t+1}(s')
        self._counts[action] += np.outer(belief, belief_next)
        self._steps_since_update += 1

        if self._steps_since_update >= self.UPDATE_FREQ:
            # Recompute T_est as Dirichlet posterior mean
            total = self._prior + self._counts
            row_sums = total.sum(axis=2, keepdims=True)
            self._T_est = total / np.where(row_sums > 0, row_sums, 1.0)
            self._steps_since_update = 0

    def act(self, belief: np.ndarray, t: int) -> int:
        vals = [_lookahead_value(belief, a, self._T_est, self.DEPTH) for a in range(M)]
        return int(np.argmax(vals))


# ===========================================================================
# 5. MPCPolicy  —  1-step greedy EU-max with Markovian predict, known T_stat
# ===========================================================================

class MPCPolicy:
    """
    Receding-horizon MPC: 1-step lookahead.
    Action selected as argmax_a E[R(a, θ')] where θ' is predicted via T_stat.

    Differs from SDP_S (depth=3 vs depth=1) and from ELS-Pres (static belief
    update vs Markovian; no cost penalty).
    """
    NAME = "MPC"

    def reset(self) -> None:
        pass

    def act(self, belief: np.ndarray, t: int) -> int:
        # Expected reward after Markovian predict step for each action
        best_a = 0
        best_val = -np.inf
        for a in range(M):
            b_pred = T_stat[a].T @ belief    # predicted next belief
            val = float(b_pred @ R[a])       # E[R(a, θ') | b_pred]
            if val > best_val:
                best_val = val
                best_a = a
        return best_a


# ===========================================================================
# 6. RDMPolicy  —  9-scenario regret minimisation
# ===========================================================================

# Scenario ensemble: 9 T matrices generated by shifting T_stat with different deltas
_RDM_DELTAS = [-0.25, -0.15, -0.08, 0.0, 0.05, 0.10, 0.15, 0.20, 0.25]

def _build_rdm_scenarios() -> list[np.ndarray]:
    """Build 9 scenario T matrices by applying different depletion shifts."""
    scenarios = []
    for delta in _RDM_DELTAS:
        T_s = np.empty_like(T_stat)
        for a in range(M):
            T_new = T_stat[a].copy()
            if delta != 0.0:
                d_a = delta * (0.5 if a == 2 else 1.0)   # a₃ half-shift
                for s in range(N - 1):
                    shift = np.clip(d_a, -T_new[s, s], 1.0 - T_new[s, s])
                    T_new[s, s]     -= shift
                    T_new[s, s + 1]  = np.clip(T_new[s, s + 1] + shift, 0, 1)
                T_new = np.clip(T_new, 0, 1)
                T_new /= T_new.sum(axis=1, keepdims=True)
            T_s[a] = T_new
        scenarios.append(T_s)
    return scenarios

_RDM_SCENARIOS: list[np.ndarray] = _build_rdm_scenarios()


class RDMPolicy:
    """
    Robust Decision Making (Lempert/RAND):
    At each step select the action that minimises maximum regret across
    9 scenario T matrices.

    Regret for action a in scenario s:
        regret(a, s, b) = max_{a'} EU_s(a', b) − EU_s(a, b)
    where EU_s(a, b) = E_{T_s}[R(a, θ')] (Markovian 1-step predict).

    Selected action: argmin_a max_s regret(a, s, b).
    """
    NAME = "RDM"

    def reset(self) -> None:
        pass

    def act(self, belief: np.ndarray, t: int) -> int:
        n_scen = len(_RDM_SCENARIOS)
        # EU[s, a] = expected reward under scenario s, action a
        eu = np.empty((n_scen, M), dtype=float)
        for si, T_s in enumerate(_RDM_SCENARIOS):
            for a in range(M):
                b_pred = T_s[a].T @ belief
                eu[si, a] = float(b_pred @ R[a])

        # Regret[s, a] = max_a' EU[s,a'] - EU[s,a]
        regret = eu.max(axis=1, keepdims=True) - eu   # (n_scen, M)

        # Max regret over scenarios for each action
        max_regret = regret.max(axis=0)   # (M,)
        return int(np.argmin(max_regret))


# ===========================================================================
# 7. InfoGapPolicy  —  robustness function ρ(a, b)
# ===========================================================================

class InfoGapPolicy:
    """
    Info-gap decision theory (Ben-Haim).

    Uncertainty model: at horizon-of-uncertainty α̂, the true expected reward
    could differ from the nominal by up to α̂ × range(a), where
    range(a) = max_θ R[a,θ] − min_θ R[a,θ].

    Robustness function:
        ρ(a, b) = (EU(a, b) − r_c) / range(a)    if range(a) > 0
        ρ(a, b) = +∞                               if EU(a,b) ≥ r_c and range=0

    Critical performance level r_c = 0 (aspiration: avoid negative payoffs).

    Selected action: argmax_a ρ(a, b).
    Tie-break by EU when ρ values are equal.
    """
    NAME = "InfoGap"

    def __init__(self):
        # Precompute range per action
        self._range = R.max(axis=1) - R.min(axis=1)   # (M,)
        self._r_c = 0.0

    def reset(self) -> None:
        pass

    def act(self, belief: np.ndarray, t: int) -> int:
        eu = np.array([expected_reward(belief, a) for a in range(M)])
        safe_range = np.where(self._range > 1e-9, self._range, 1.0)
        rho = np.where(
            self._range > 1e-9,
            (eu - self._r_c) / safe_range,
            np.where(eu >= self._r_c, 1e9, -1e9),
        )
        # Argmax ρ; tie-break by EU
        best = np.lexsort((eu, rho))[-1]   # last is max (primary=rho, secondary=eu)
        return int(best)


# ===========================================================================
# 8. AlwaysRestricted  —  constant conservative heuristic
# ===========================================================================

class AlwaysRestricted:
    """Always select a₂ (restricted, 50 % licence reduction). Heuristic baseline."""
    NAME = "AlwaysRestricted"

    def reset(self) -> None:
        pass

    def act(self, belief: np.ndarray, t: int) -> int:
        return 1


# ===========================================================================
# 9. MyopicEU  —  oracle 1-step greedy with TRUE regime T
# ===========================================================================

class MyopicEU:
    """
    Oracle upper-bound: 1-step greedy EU-max using the TRUE regime T.

    Knows T_stat for t < CLIMATE_SWITCH_STEP and T_shift afterwards.
    This is infeasible for a real agent; it establishes an oracle ceiling
    for model-knowing policies under both regimes.
    """
    NAME = "MyopicEU"

    def reset(self) -> None:
        pass

    def act(self, belief: np.ndarray, t: int) -> int:
        T_true = T_shift if t >= CLIMATE_SWITCH_STEP else T_stat
        best_a = 0
        best_val = -np.inf
        for a in range(M):
            b_pred = T_true[a].T @ belief
            val = float(b_pred @ R[a])
            if val > best_val:
                best_val = val
                best_a = a
        return best_a


# ===========================================================================
# Registry and validation
# ===========================================================================

ALL_BASELINES: dict[str, type] = {
    "SARSOP":           SARSOPPolicy,
    "PBVI":             PBVIPolicy,
    "SDP_S":            SDPStationary,
    "SDP_NS":           SDPNonStationary,
    "MPC":              MPCPolicy,
    "RDM":              RDMPolicy,
    "InfoGap":          InfoGapPolicy,
    "AlwaysRestricted": AlwaysRestricted,
    "MyopicEU":         MyopicEU,
}


def validate(run_sarsop: bool = False, verbose: bool = True) -> None:
    """
    Smoke-test each policy: one episode with SEED+100.
    SARSOP/PBVI offline solve is skipped by default (slow — set run_sarsop=True).
    """
    rng_val = np.random.default_rng(SEED + 100)
    state, b0 = env.reset(rng_val)

    for name, cls in ALL_BASELINES.items():
        policy = cls()
        policy.reset()

        if name in ("SARSOP", "PBVI"):
            if not run_sarsop:
                if verbose:
                    print(f"{name:<20}  skipped (offline solve — pass run_sarsop=True)")
                continue
            policy.solve(verbose=verbose)

        b = b0.copy()
        s = state
        cum_r = 0.0
        rng_ep = np.random.default_rng(SEED + 200)

        for t_step in range(T):
            a = policy.act(b, t_step)
            assert 0 <= a < M, f"{name}: act() returned invalid action {a}"
            s, o, r = env.step(s, a, t_step, rng_ep)
            if isinstance(policy, SDPNonStationary):
                b_next = markov_update_belief(b, o, a, t_step)
                policy.update(b, a, b_next)
                b = b_next
            else:
                b = env.update_belief(b, o)
            cum_r += GAMMA ** t_step * r

        if verbose:
            print(f"{name:<20}  OK  U_cum={cum_r:8.2f}  final_state=θ{s+1}")

    # RDM scenario count check
    assert len(_RDM_SCENARIOS) == 9, "RDM scenario count != 9"
    for si, T_s in enumerate(_RDM_SCENARIOS):
        assert T_s.shape == (M, N, N)
        rs = T_s.sum(axis=2)
        assert np.allclose(rs, 1.0, atol=1e-8), f"RDM scenario {si} row sums"
    if verbose:
        print(f"{'RDM scenarios':<20}  9 matrices, all row sums OK")

    if verbose:
        print("All baseline smoke tests passed.")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--full", action="store_true",
                   help="Include SARSOP/PBVI offline solve (slow ~2 min)")
    args = p.parse_args()
    validate(run_sarsop=args.full, verbose=True)
