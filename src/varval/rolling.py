"""Rolling (out-of-sample) VaR forecasts. Implement FIFTH.

The single most common bug in a VaR backtest is look-ahead: computing the
VaR for day t with a window that includes day t. The test in
tests/test_rolling.py checks that the forecast for day t uses exactly the
``window`` observations strictly before t.
"""

from __future__ import annotations

import pandas as pd

from varval.var_models import historical_var


def rolling_historical_var(pnl: pd.Series, window: int = 250, alpha: float = 0.99) -> pd.Series:
    """For each day t >= window, VaR_t = historical_var(pnl[t-window : t], alpha).

    Returns a Series indexed like ``pnl``; the first ``window`` entries are NaN
    (no forecast can be made yet). A plain Python loop is perfectly fine here:
    clarity beats cleverness, and 2 500 iterations take well under a second.

    Once this works, write the parametric and EWMA versions on the same
    pattern (they need the returns DataFrame, not just the P&L series).
    """
    raise NotImplementedError
