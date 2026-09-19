import numpy as np
import pandas as pd
import pytest

from varval.rolling import rolling_historical_var
from varval.var_models import historical_var


def test_rolling_var_shape_and_nans(normal_pnl):
    var = rolling_historical_var(normal_pnl, window=250, alpha=0.99)
    assert isinstance(var, pd.Series)
    assert len(var) == len(normal_pnl)
    assert var.index.equals(normal_pnl.index)
    assert var.iloc[:250].isna().all()
    assert var.iloc[250:].notna().all()


def test_rolling_var_has_no_look_ahead(normal_pnl):
    """VaR for day t must be computed from days [t-window, t), never day t."""
    var = rolling_historical_var(normal_pnl, window=250, alpha=0.99)
    assert var.iloc[250] == pytest.approx(historical_var(normal_pnl.iloc[0:250], 0.99))
    assert var.iloc[300] == pytest.approx(historical_var(normal_pnl.iloc[50:300], 0.99))
    assert var.iloc[-1] == pytest.approx(historical_var(normal_pnl.iloc[-251:-1], 0.99))


def test_rolling_var_reacts_to_a_shock():
    """A large loss on day 260 must not change VaR_260 but must raise VaR_261."""
    rng = np.random.default_rng(0)
    pnl = pd.Series(rng.normal(0, 1.0, size=400), index=pd.bdate_range("2020-01-01", periods=400))
    pnl.iloc[260] = -1_000.0
    var = rolling_historical_var(pnl, window=250, alpha=0.999)
    assert var.iloc[260] < 10.0
    assert var.iloc[261] > 100.0
