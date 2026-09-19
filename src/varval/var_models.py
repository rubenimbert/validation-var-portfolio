"""Value-at-Risk and Expected Shortfall estimators. Implement THIRD.

All functions return a POSITIVE loss amount in the units of the inputs
(currency if you pass P&L or a market value, fraction if you pass returns).

Recommended order: parametric -> historical -> expected_shortfall -> ewma ->
monte_carlo. Each one is a few lines; the value is in understanding why the
answers differ on the same data.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


# --------------------------------------------------------------------------- #
# 1. Parametric (variance-covariance)
# --------------------------------------------------------------------------- #
def parametric_var(cov: np.ndarray, weights: np.ndarray, market_value: float,
                   alpha: float = 0.99) -> float:
    """Normal variance-covariance VaR.

        VaR = z_alpha * sqrt(w' Sigma w) * V

    with z_alpha = Phi^{-1}(alpha) (2.326 for 99%). Mean return is assumed to
    be zero over one day, a standard and defensible simplification: state it
    in the model description.

    ``cov`` is the (n x n) covariance matrix of daily returns, ``weights`` the
    (n,) weight vector.
    """
    raise NotImplementedError


def sample_covariance(returns: pd.DataFrame) -> np.ndarray:
    """Sample covariance matrix of a returns DataFrame, as a NumPy array.

    Deliberate trap: ``numpy.cov`` and ``DataFrame.cov`` use ddof=1 (sample),
    ``numpy.var``/``numpy.std`` use ddof=0 (population) by default. SAS uses
    ddof=1. Pick one, write it down here, and you will have your first
    reconciliation finding when you re-implement this in SAS.

    Expected convention for the tests: ddof=1.
    """
    raise NotImplementedError


# --------------------------------------------------------------------------- #
# 2. EWMA (RiskMetrics) covariance
# --------------------------------------------------------------------------- #
def ewma_covariance(returns: pd.DataFrame, lam: float = 0.94) -> np.ndarray:
    """Exponentially weighted covariance matrix (RiskMetrics, lambda = 0.94).

    Recursion, with r_t the (n,) return vector at time t:

        Sigma_0 = r_0 r_0'                (initialisation on the first observation)
        Sigma_t = lam * Sigma_{t-1} + (1 - lam) * r_t r_t'    for t = 1 .. T-1

    Return Sigma_{T-1}, i.e. the estimate that uses every observation in the
    window. That is the forecast of tomorrow's covariance.

    The initialisation is a modelling choice (RiskMetrics documentation
    initialises differently). The tests pin THIS convention; document it.
    """
    raise NotImplementedError


# --------------------------------------------------------------------------- #
# 3. Historical simulation
# --------------------------------------------------------------------------- #
def historical_var(pnl: pd.Series | np.ndarray, alpha: float = 0.99) -> float:
    """Historical-simulation VaR: the empirical (1 - alpha) quantile of P&L,
    sign-flipped so that the result is a positive loss.

        VaR = -quantile(pnl, 1 - alpha)

    Quantile convention pinned by the tests: NumPy's default *linear*
    interpolation (``np.quantile(x, q)``). With 250 observations and
    alpha = 0.99 the quantile falls between the 2nd and 3rd worst losses;
    another convention (e.g. 'lower') gives a different number. A validator
    always asks which convention the developer used.
    """
    raise NotImplementedError


def expected_shortfall(pnl: pd.Series | np.ndarray, alpha: float = 0.99) -> float:
    """Historical Expected Shortfall: mean loss on the days where the loss is
    at least the VaR.

        ES = -mean( pnl[ pnl <= -VaR ] )    with VaR = historical_var(pnl, alpha)

    Positive number, always >= VaR. This is the measure FRTB adopted instead
    of VaR: be able to say in one sentence why (it looks *into* the tail, and
    it is sub-additive).
    """
    raise NotImplementedError


# --------------------------------------------------------------------------- #
# 4. Monte Carlo
# --------------------------------------------------------------------------- #
def monte_carlo_var(cov: np.ndarray, weights: np.ndarray, market_value: float,
                    alpha: float = 0.99, n_sims: int = 100_000,
                    seed: int | None = 42, mean: np.ndarray | None = None) -> float:
    """Monte Carlo VaR under a multivariate normal.

    1. L = cholesky(cov)                        (lower triangular, cov = L L')
    2. Z ~ N(0, I) of shape (n_sims, n)
    3. simulated returns R = mean + Z @ L.T     (each row ~ N(mean, cov))
    4. simulated P&L = market_value * R @ weights
    5. VaR = historical_var(simulated P&L, alpha)

    ``mean`` defaults to zeros. Use ``np.random.default_rng(seed)`` so the
    result is reproducible (the test checks it).

    Interview question you should now be able to answer: why is the Cholesky
    factor the right object to turn independent normals into correlated ones?
    """
    raise NotImplementedError
