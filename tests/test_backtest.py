import numpy as np
import pytest

from varval.backtest import (
    basel_traffic_light,
    christoffersen_independence,
    conditional_coverage,
    kupiec_pof,
    var_exceptions,
)


# ---------------------------------------------------------------- exceptions
def test_var_exceptions_flags_losses_beyond_var():
    pnl = np.array([-10.0, -2.0, 3.0, -6.0, -5.0])
    var = np.array([5.0, 5.0, 5.0, 5.0, 5.0])
    exc = var_exceptions(pnl, var)
    assert exc.dtype == bool
    assert list(exc) == [True, False, False, True, False]   # -5 is NOT an exception (strict)


# ---------------------------------------------------------------- Kupiec
def test_kupiec_zero_statistic_when_rate_equals_p():
    lr, p = kupiec_pof(n_exceptions=10, n_obs=1000, alpha=0.99)
    assert lr == pytest.approx(0.0, abs=1e-12)
    assert p == pytest.approx(1.0)


def test_kupiec_rejects_10_exceptions_in_250_days():
    lr, p = kupiec_pof(n_exceptions=10, n_obs=250, alpha=0.99)
    assert lr == pytest.approx(12.955, abs=0.01)
    assert p < 0.01


def test_kupiec_accepts_4_exceptions_in_250_days():
    lr, p = kupiec_pof(n_exceptions=4, n_obs=250, alpha=0.99)
    assert lr == pytest.approx(0.769, abs=0.01)
    assert p > 0.05


def test_kupiec_handles_zero_exceptions():
    """x = 0 needs the 0*ln(0) = 0 convention; too FEW exceptions is also a
    failure (the model is too conservative: capital is wasted)."""
    lr, p = kupiec_pof(n_exceptions=0, n_obs=250, alpha=0.99)
    assert lr == pytest.approx(5.025, abs=0.01)
    assert p < 0.05


# ---------------------------------------------------------------- Christoffersen
def test_christoffersen_detects_clustered_exceptions():
    exc = np.zeros(250, dtype=bool)
    exc[100:105] = True                # five consecutive exceptions
    lr, p = christoffersen_independence(exc)
    assert lr == pytest.approx(30.985, abs=0.01)
    assert p < 1e-6


def test_christoffersen_accepts_spread_exceptions():
    exc = np.zeros(250, dtype=bool)
    exc[[20, 70, 120, 170, 220]] = True   # five isolated exceptions
    lr, p = christoffersen_independence(exc)
    assert lr == pytest.approx(0.205, abs=0.01)
    assert p > 0.05


def test_conditional_coverage_is_sum_of_the_two():
    exc = np.zeros(250, dtype=bool)
    exc[100:105] = True
    lr_pof, _ = kupiec_pof(int(exc.sum()), len(exc), alpha=0.99)
    lr_ind, _ = christoffersen_independence(exc)
    lr_cc, p_cc = conditional_coverage(exc, alpha=0.99)
    assert lr_cc == pytest.approx(lr_pof + lr_ind)
    assert p_cc < 1e-6


# ---------------------------------------------------------------- Basel
@pytest.mark.parametrize("n,zone", [(0, "green"), (4, "green"), (5, "yellow"),
                                    (9, "yellow"), (10, "red"), (15, "red")])
def test_basel_traffic_light(n, zone):
    assert basel_traffic_light(n) == zone
