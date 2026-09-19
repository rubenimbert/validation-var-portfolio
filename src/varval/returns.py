"""Returns and portfolio P&L. Implement this module FIRST.

Two conventions you must be able to defend in an interview:

1. Log returns, r_t = ln(P_t / P_{t-1}), because they are additive over time
   (a 10-day return is a sum of daily returns) and symmetric.
2. The portfolio return is approximated as the *linear* combination
   sum_i w_i * r_i. For log returns this is an approximation (the exact
   portfolio log return is ln(sum_i w_i * exp(r_i))). Over one day the error
   is negligible; it is one of the "known limitations" you will list in the
   validation report. A validator who cannot explain why it is negligible on
   a 1-day horizon but not on a 1-year horizon has not understood returns.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Daily log returns from a wide price DataFrame (one column per asset).

    The first row (no previous price) is dropped, so the result has
    ``len(prices) - 1`` rows and the same columns.
    """
    raise NotImplementedError


def portfolio_returns(returns: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    """Linear portfolio return r_p,t = sum_i w_i * r_i,t (see module docstring).

    ``weights`` is aligned with ``returns.columns`` and should sum to 1.
    Returns a Series indexed like ``returns``.
    """
    raise NotImplementedError


def portfolio_pnl(returns: pd.DataFrame, weights: np.ndarray, market_value: float) -> pd.Series:
    """P&L in currency: market_value * portfolio_returns(...).

    Positive = gain, negative = loss. VaR functions consume this series.
    """
    raise NotImplementedError
