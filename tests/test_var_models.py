import numpy as np
import pandas as pd
import pytest
from scipy import stats

from varval.var_models import (
    ewma_covariance,
    expected_shortfall,
    historical_var,
    monte_carlo_var,
    parametric_var,
    sample_covariance,
)

Z99 = stats.norm.ppf(0.99)   # 2.3263478740408408


# ---------------------------------------------------------------- parametric
def test_parametric_var_single_asset():
    cov = np.array([[0.0004]])          # sigma = 2% per day
    var = parametric_var(cov, np.array([1.0]), market_value=1_000_000.0, alpha=0.99)
    assert var == pytest.approx(46_526.96, abs=0.05)
    assert var > 0


def test_parametric_var_two_assets():
    cov = np.array([[0.0004, 0.0001], [0.0001, 0.0009]])
    w = np.array([0.5, 0.5])
    var = parametric_var(cov, w, market_value=1.0, alpha=0.99)
    # w' Sigma w = 0.000375 -> sigma_p = 0.0193649 -> VaR = 0.0450495
    assert var == pytest.approx(0.0450495, abs=1e-6)


def test_parametric_var_is_subadditive():
    """Normal VaR is sub-additive: diversification lowers the risk figure."""
    cov = np.array([[0.0004, 0.0001], [0.0001, 0.0009]])
    var_a = parametric_var(cov, np.array([1.0, 0.0]), 1.0)
    var_b = parametric_var(cov, np.array([0.0, 1.0]), 1.0)
    var_p = parametric_var(cov, np.array([0.5, 0.5]), 1.0)
    assert var_p < 0.5 * var_a + 0.5 * var_b


def test_parametric_var_95_is_lower_than_99():
    cov = np.array([[0.0004]])
    assert parametric_var(cov, np.array([1.0]), 1.0, alpha=0.95) < parametric_var(cov, np.array([1.0]), 1.0, alpha=0.99)


def test_sample_covariance_uses_ddof_1(two_asset_returns):
    cov = sample_covariance(two_asset_returns)
    assert cov.shape == (2, 2)
    assert np.allclose(cov, two_asset_returns.cov().to_numpy())   # pandas: ddof=1
    assert cov[0, 1] == pytest.approx(cov[1, 0])


# ---------------------------------------------------------------- EWMA
def test_ewma_single_series_recursion():
    r = pd.DataFrame({"AAA": [0.01, 0.02, -0.01]})
    cov = ewma_covariance(r, lam=0.94)
    # S0 = 1e-4 ; S1 = 0.94e-4 + 0.06*4e-4 = 1.18e-4 ; S2 = 0.94*1.18e-4 + 0.06*1e-4 = 1.1692e-4
    assert cov.shape == (1, 1)
    assert cov[0, 0] == pytest.approx(1.1692e-4, rel=1e-9)


def test_ewma_is_symmetric_psd(normal_pnl):
    rng = np.random.default_rng(7)
    r = pd.DataFrame(rng.normal(0, 0.01, size=(300, 3)), columns=list("ABC"))
    cov = ewma_covariance(r)
    assert np.allclose(cov, cov.T)
    assert np.all(np.linalg.eigvalsh(cov) >= -1e-12)


# ---------------------------------------------------------------- historical
def test_historical_var_linear_quantile(small_pnl):
    # np.quantile(pnl, 0.10): position 0.9 between -5 and -3 -> -3.2
    assert historical_var(small_pnl, alpha=0.90) == pytest.approx(3.2)
    # np.quantile(pnl, 0.20): position 1.8 between -3 and -1 -> -1.4
    assert historical_var(small_pnl, alpha=0.80) == pytest.approx(1.4)


def test_historical_var_accepts_series(small_pnl):
    s = pd.Series(small_pnl)
    assert historical_var(s, alpha=0.90) == pytest.approx(3.2)


def test_historical_var_matches_parametric_on_normal_data(normal_pnl):
    """On gaussian data with 2 000 observations the two methods must agree
    within a few percent: sigma = 20 000 -> parametric 99% VaR = 46 527."""
    hist = historical_var(normal_pnl, alpha=0.99)
    assert hist == pytest.approx(46_527, rel=0.06)


# ---------------------------------------------------------------- ES
def test_expected_shortfall_small(small_pnl):
    # VaR(80%) = 1.4 ; losses <= -1.4 are -5 and -3 -> ES = 4
    assert expected_shortfall(small_pnl, alpha=0.80) == pytest.approx(4.0)


def test_expected_shortfall_exceeds_var(normal_pnl):
    var = historical_var(normal_pnl, alpha=0.99)
    es = expected_shortfall(normal_pnl, alpha=0.99)
    assert es > var
    # for a normal, ES/VaR at 99% is about 2.665 / 2.326 = 1.146
    assert es / var == pytest.approx(1.146, rel=0.08)


# ---------------------------------------------------------------- Monte Carlo
def test_monte_carlo_matches_parametric():
    cov = np.array([[0.0004, 0.0001], [0.0001, 0.0009]])
    w = np.array([0.5, 0.5])
    mc = monte_carlo_var(cov, w, market_value=1.0, alpha=0.99, n_sims=200_000, seed=1)
    assert mc == pytest.approx(0.0450495, rel=0.03)


def test_monte_carlo_is_reproducible():
    cov = np.array([[0.0004]])
    a = monte_carlo_var(cov, np.array([1.0]), 1.0, n_sims=10_000, seed=42)
    b = monte_carlo_var(cov, np.array([1.0]), 1.0, n_sims=10_000, seed=42)
    c = monte_carlo_var(cov, np.array([1.0]), 1.0, n_sims=10_000, seed=43)
    assert a == b
    assert a != c
