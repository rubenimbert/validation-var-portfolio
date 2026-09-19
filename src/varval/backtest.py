"""Backtesting statistics. Implement FOURTH. This is the heart of the
validation: a VaR model is not "right" because the formula is right, it is
acceptable because its exceptions behave like a 1% coin toss.

Notation: N observations, x exceptions, p = 1 - alpha the expected exception
rate (0.01 for a 99% VaR).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def var_exceptions(pnl: pd.Series | np.ndarray, var: pd.Series | np.ndarray) -> np.ndarray:
    """Boolean array: True on days where the loss exceeded the VaR, i.e.
    ``pnl < -var``. Both inputs are aligned day by day (var_t is the forecast
    made for day t with information up to t-1).
    """
    raise NotImplementedError


def kupiec_pof(n_exceptions: int, n_obs: int, alpha: float = 0.99) -> tuple[float, float]:
    """Kupiec (1995) proportion-of-failures test.

        LR_pof = -2 ln[ (1-p)^(N-x) p^x ] + 2 ln[ (1-x/N)^(N-x) (x/N)^x ]

    Under H0 (the true exception rate is p), LR_pof ~ chi2(1).
    Returns ``(LR_pof, p_value)``. Convention 0 * ln(0) = 0 (needed when x = 0).

    Sanity checks the tests use: x/N == p gives LR = 0 and p-value = 1;
    10 exceptions in 250 days at 99% gives LR ~ 12.96 and p-value < 0.01.
    """
    raise NotImplementedError


def christoffersen_independence(exceptions: np.ndarray) -> tuple[float, float]:
    """Christoffersen (1998) independence test.

    Count transitions between consecutive days: n_ij = number of days where
    state i (0 = no exception, 1 = exception) is followed by state j.

        pi_01 = n_01 / (n_00 + n_01)     P(exception tomorrow | none today)
        pi_11 = n_11 / (n_10 + n_11)     P(exception tomorrow | exception today)
        pi    = (n_01 + n_11) / (n_00 + n_01 + n_10 + n_11)

        LR_ind = -2 ln[ (1-pi)^(n_00+n_10) pi^(n_01+n_11) ]
                 + 2 ln[ (1-pi_01)^n_00 pi_01^n_01 (1-pi_11)^n_10 pi_11^n_11 ]

    Under H0 (exceptions are independent, pi_01 = pi_11), LR_ind ~ chi2(1).
    Returns ``(LR_ind, p_value)``. Use 0 * ln(0) = 0 wherever a count is 0.

    This is the test that catches what Kupiec cannot: 10 exceptions spread
    over a year look like bad luck; 10 exceptions in the same two weeks of
    March 2020 mean the model does not react to volatility.
    """
    raise NotImplementedError


def conditional_coverage(exceptions: np.ndarray, alpha: float = 0.99) -> tuple[float, float]:
    """Christoffersen conditional coverage: LR_cc = LR_pof + LR_ind ~ chi2(2).

    Returns ``(LR_cc, p_value)``.
    """
    raise NotImplementedError


def basel_traffic_light(n_exceptions: int) -> str:
    """Basel Committee (1996) traffic-light zone for 250 daily observations
    at 99%: 'green' for 0-4 exceptions, 'yellow' for 5-9, 'red' for 10+.

    The zone drives the capital multiplier (green: 3.0; yellow: 3.4 to 3.85;
    red: 4.0). Optional extension: return the multiplier as well.
    """
    raise NotImplementedError
