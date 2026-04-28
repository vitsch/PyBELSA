# =============================================================================
# els_adapt.py  —  ELS Adaptive Model-Trust Variants (Idea 3.1)
# Project  : ELS_NEW / P_Base  (Benchmark 1 — w-adaptation experiment)
# Plan ref : BDT_concept_impr.md §3.1 "Adaptive w (w as Learnable Parameter)"
#            how_improve_performance.md §2.2 Intervention A1
# Date     : 2026-04-24
# Usage    : from scr.els_adapt import ELSPhilAdapt, ELSIntAdapt
# =============================================================================
"""
ELS_Phil_Adapt and ELS_Int_Adapt: ELS variants with online-adaptive
model-trust weight w.

Background
----------
ELSPhilT and ELSIntT (els_methods.py, Priority 2) implement the hybrid
belief update with a *fixed* model-trust weight w:

    b_blend = (1−w)·b + w·(T_stat[a]ᵀ·b)
    b_new  ∝ L[:, obs] · b_blend

The optimal w is problem-dependent: high w is best when T is accurate
(Benchmark 1 stationary), low w is better when T is wrong or shifting.
A fixed w requires prior knowledge of T-accuracy.

Idea 3.1 (BDT_concept_impr.md §3.1) proposes making w a learnable
parameter that updates online based on empirical T-prediction accuracy:

    ll_T  = log P(obs | T_stat[a]ᵀ · b)   [T-propagated belief likelihood]
    ll_s  = log P(obs | b)                  [static prior likelihood]
    δ     = η · (ll_T − ll_s)               [positive → T predicted better]
    logit(w_new) = logit(w) + δ
    w_new  = clip(sigmoid(logit(w_new)), w_min, w_max)

This implements a form of online Bayesian model selection: at each step,
the agent asks "did using T improve my prediction of the observation?",
and adjusts w accordingly.

Key properties
--------------
- w starts at w_init each episode (call reset() before each episode)
- w_trajectory records w after each step (for analysis/plotting)
- Action selection (SR4 / SR3.2) is inherited unchanged from ELSPhilT / ELSIntT
- The adaptation only affects the belief update
- η = 0 → fixed w (identical to ELSPhilT / ELSIntT with w=w_init)
- Large η → w jumps rapidly to 0 or 1 based on single observations
- Recommended η = 0.5 gives gradual adaptation over T=60 steps

Design note
-----------
These classes do NOT modify els_methods.py. They extend the existing
ELSPhilT / ELSIntT hierarchy with a single override of phys_belief_update.
All existing code is fully backward-compatible.
"""

import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from els_methods import (
    ELSPhilT, ELSIntT, ELSInt,
    W_TRANS, SEED, C_TEF,
    T_stat, L_PHIL, L_PRES,
)


# ===========================================================================
# 1.  ELSPhilAdapt  —  Philosophical + Online-Adaptive w
# ===========================================================================

class ELSPhilAdapt(ELSPhilT):
    """
    Philosophical framework with adaptive (online-learned) model-trust weight w.

    Action selection is unchanged from ELSPhilT (SR4 satisficing + info-gain).
    Only the belief update is modified: after each observation, w is updated
    in logit space based on the log-likelihood ratio (T-prediction vs static).

    Parameters
    ----------
    w_init : float, default W_TRANS=0.5
        Initial model-trust weight at the start of each episode.
    eta : float, default 0.5
        Adaptation learning rate.
        0 → fixed w; ∞ → instantaneous max-likelihood w selection.
    w_min : float, default 0.0
        Hard lower bound on w (clip floor).
    w_max : float, default 1.0
        Hard upper bound on w (clip ceiling).

    Attributes
    ----------
    w_trajectory : list[float]
        w value recorded after each phys_belief_update call.
        Length == T steps per episode; reset to [] by reset().
    """

    NAME = "ELS_Phil_Adapt"

    def __init__(
        self,
        w_init: float = W_TRANS,
        eta: float = 0.5,
        w_min: float = 0.0,
        w_max: float = 1.0,
    ):
        super().__init__(w=w_init)
        self._w_init = float(w_init)
        self._eta    = float(eta)
        self._w_min  = float(w_min)
        self._w_max  = float(w_max)
        self.w_trajectory: list[float] = []

    def reset(self) -> None:
        """Reset w to w_init and clear the trajectory."""
        super().reset()                  # ELSPhil.reset() (no-op) + w is not touched
        self._w = self._w_init           # explicit reset (parent sets _w once in __init__)
        self.w_trajectory = []

    def phys_belief_update(
        self,
        b: np.ndarray,
        obs: int,
        action: int | None = None,
    ) -> np.ndarray:
        """
        Hybrid belief update using current w, then update w for next step.

        Steps
        -----
        1. Compute b_new with current self._w via ELSPhilT.phys_belief_update.
        2. Compute T-prediction accuracy signal (if action is available).
        3. Update self._w in logit space (clipped to [w_min, w_max]).
        4. Append new w to w_trajectory.
        """
        # Step 1: belief update with current w (ELSPhilT handles L_PHIL + T_stat)
        b_new = super().phys_belief_update(b, obs, action)

        # Step 2–3: w adaptation (requires action to compute b_pred)
        if action is not None and self._eta > 1e-12:
            b_pred = T_stat[action].T @ b                         # T-propagated prior
            ll_T   = float(np.log(max(float(L_PHIL[:, obs] @ b_pred), 1e-300)))
            ll_s   = float(np.log(max(float(L_PHIL[:, obs] @ b),      1e-300)))
            delta  = self._eta * (ll_T - ll_s)
            # logit update avoids hard 0/1 collapse
            w_safe  = float(np.clip(self._w, 1e-6, 1.0 - 1e-6))
            logit_w = np.log(w_safe / (1.0 - w_safe)) + delta
            self._w = float(np.clip(
                1.0 / (1.0 + np.exp(-logit_w)),
                self._w_min,
                self._w_max,
            ))

        # Step 4: record
        self.w_trajectory.append(self._w)
        return b_new


# ===========================================================================
# 2.  ELSIntAdapt  —  Integrated Bernoulli + Online-Adaptive w
# ===========================================================================

class ELSIntAdapt(ELSIntT):
    """
    Integrated Bernoulli framework with adaptive (online-learned) model-trust weight w.

    Combines ELSInt's entropy-driven Bernoulli hard switching with online w-adaptation.
    The P_hyb likelihood (α-weighted L_PHIL / L_PRES) is used for both the belief
    update and the T-accuracy measurement, so the adaptation signal is consistent
    with the effective observation model in use at each step.

    Parameters
    ----------
    seed   : int, default SEED
    c_tef  : float, default C_TEF
    w_init : float, default W_TRANS=0.5
    eta    : float, default 0.5  — adaptation learning rate
    w_min  : float, default 0.0
    w_max  : float, default 1.0

    Attributes
    ----------
    w_trajectory : list[float]
        w value after each phys_belief_update call; reset by reset().
    """

    NAME = "ELS_Int_Adapt"

    def __init__(
        self,
        seed: int = SEED,
        c_tef: float = C_TEF,
        w_init: float = W_TRANS,
        eta: float = 0.5,
        w_min: float = 0.0,
        w_max: float = 1.0,
    ):
        super().__init__(seed=seed, c_tef=c_tef, w=w_init)
        self._w_init = float(w_init)
        self._eta    = float(eta)
        self._w_min  = float(w_min)
        self._w_max  = float(w_max)
        self.w_trajectory: list[float] = []

    def reset(self, seed: int | None = None) -> None:
        """Reset w to w_init, clear trajectory, and reset parent ELSIntT/ELSInt state."""
        super().reset(seed=seed)
        self._w = self._w_init
        self.w_trajectory = []

    def phys_belief_update(
        self,
        b: np.ndarray,
        obs: int,
        action: int | None = None,
    ) -> np.ndarray:
        """
        Hybrid belief update using current w (via ELSIntT), then update w.

        Uses P_hyb = (1−α_prev)·L_PHIL + α_prev·L_PRES for T-accuracy
        measurement (same likelihood as the belief update itself), so the
        adaptation signal is self-consistent with the Bernoulli mixing.

        Note: self._alpha_prev is set by act() before this method is called.
        """
        # Step 1: belief update with current w (ELSIntT uses P_hyb + T_stat)
        b_new = super().phys_belief_update(b, obs, action)

        # Step 2–3: w adaptation using P_hyb likelihood
        if action is not None and self._eta > 1e-12:
            # alpha_prev was updated by act() just before this call
            P_hyb  = (1.0 - self._alpha_prev) * L_PHIL + self._alpha_prev * L_PRES
            b_pred = T_stat[action].T @ b
            ll_T   = float(np.log(max(float(P_hyb[:, obs] @ b_pred), 1e-300)))
            ll_s   = float(np.log(max(float(P_hyb[:, obs] @ b),      1e-300)))
            delta  = self._eta * (ll_T - ll_s)
            w_safe  = float(np.clip(self._w, 1e-6, 1.0 - 1e-6))
            logit_w = np.log(w_safe / (1.0 - w_safe)) + delta
            self._w = float(np.clip(
                1.0 / (1.0 + np.exp(-logit_w)),
                self._w_min,
                self._w_max,
            ))

        # Step 4: record
        self.w_trajectory.append(self._w)
        return b_new


# ===========================================================================
# Registry supplement (for downstream scripts; does not modify els_methods.py)
# ===========================================================================

ELS_ADAPT_METHODS: dict[str, type] = {
    "ELS_Phil_Adapt": ELSPhilAdapt,
    "ELS_Int_Adapt":  ELSIntAdapt,
}

# Names that use phys_belief_update(b, obs, action=<required>)
ELS_ADAPT_PHYS_UPDATE = {"ELS_Phil_Adapt", "ELS_Int_Adapt"}


# ===========================================================================
# Validation (smoke test — one episode per variant)
# ===========================================================================

def validate(verbose: bool = True) -> None:
    """Smoke-test each ELS-Adapt policy through one complete episode."""
    import pomdp_env as env_mod
    from pomdp_env import N, M, T, SEED as _SEED

    rng_val = np.random.default_rng(_SEED + 700)
    state   = int(rng_val.integers(0, N))

    tests = [
        ("ELS_Phil_Adapt", ELSPhilAdapt(w_init=0.5, eta=0.5), None),
        ("ELS_Int_Adapt",  ELSIntAdapt(seed=_SEED + 1, w_init=0.5, eta=0.5), _SEED + 1),
    ]

    for name, policy, ep_seed in tests:
        if isinstance(policy, ELSInt):
            policy.reset(seed=ep_seed)
        else:
            policy.reset()

        b     = policy.initial_belief()
        s     = state
        cum_r = 0.0
        rng_ep = np.random.default_rng(_SEED + 800)

        for t_step in range(T):
            a = policy.act(b, t_step)
            assert 0 <= a < M, f"{name}: invalid action {a} at t={t_step}"
            s_next, obs, r = env_mod.step(s, a, t_step, rng_ep)
            b = policy.phys_belief_update(b, obs, action=a)
            assert np.isclose(b.sum(), 1.0, atol=1e-6), \
                f"{name}: belief not normalised at t={t_step}"
            cum_r += env_mod.GAMMA ** t_step * r
            s = s_next

        assert len(policy.w_trajectory) == T, \
            f"{name}: w_trajectory has {len(policy.w_trajectory)} entries, expected {T}"

        w_arr   = np.array(policy.w_trajectory)
        w_mean  = float(w_arr.mean())
        w_range = (float(w_arr.min()), float(w_arr.max()))

        if verbose:
            print(
                f"{name:<18}  OK  U_cum={cum_r:8.2f}  "
                f"w_mean={w_mean:.3f}  "
                f"w_range=[{w_range[0]:.3f}, {w_range[1]:.3f}]  "
                f"final_state=θ{s+1}"
            )

    if verbose:
        print("ELS-Adapt smoke tests passed.")


if __name__ == "__main__":
    validate(verbose=True)
