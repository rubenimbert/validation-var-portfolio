import numpy as np
import pandas as pd
import pytest

from varval.returns import log_returns, portfolio_pnl, portfolio_returns


def test_log_returns_values(three_day_prices):
    r = log_returns(three_day_prices)
    assert list(r.columns) == ["AAA"]
    assert len(r) == 2                                   # first day dropped
    assert r.index[0] == pd.Timestamp("2024-01-03")
    assert r["AAA"].iloc[0] == pytest.approx(np.log(1.10))   #  0.0953102
    assert r["AAA"].iloc[1] == pytest.approx(np.log(0.90))   # -0.1053605


def test_log_returns_are_additive(three_day_prices):
    r = log_returns(three_day_prices)
    two_day = r["AAA"].sum()
    assert two_day == pytest.approx(np.log(99.0 / 100.0))


def test_portfolio_returns_linear(two_asset_returns):
    w = np.array([0.6, 0.4])
    rp = portfolio_returns(two_asset_returns, w)
    assert isinstance(rp, pd.Series)
    assert rp.iloc[0] == pytest.approx(0.6 * 0.01 + 0.4 * (-0.02))   # -0.002
    assert rp.iloc[1] == pytest.approx(0.6 * 0.03 + 0.4 * 0.01)      #  0.022


def test_portfolio_pnl_scales_with_value(two_asset_returns):
    w = np.array([0.6, 0.4])
    pnl = portfolio_pnl(two_asset_returns, w, market_value=1_000_000.0)
    assert pnl.iloc[0] == pytest.approx(-2_000.0)
    assert pnl.iloc[1] == pytest.approx(22_000.0)
