"""Shared fixtures. Read this file: the fixtures are small on purpose so that
you can recompute every expected value by hand (or in a notebook).
"""

import math
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "sql"


@pytest.fixture
def three_day_prices() -> pd.DataFrame:
    """One asset, three days: 100 -> 110 -> 99."""
    idx = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"])
    return pd.DataFrame({"AAA": [100.0, 110.0, 99.0]}, index=idx)


@pytest.fixture
def two_asset_returns() -> pd.DataFrame:
    idx = pd.to_datetime(["2024-01-03", "2024-01-04"])
    return pd.DataFrame({"AAA": [0.01, 0.03], "BBB": [-0.02, 0.01]}, index=idx)


@pytest.fixture
def small_pnl() -> np.ndarray:
    """Ten P&L values, sorted, easy to reason about by hand."""
    return np.array([-5.0, -3.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0])


@pytest.fixture
def normal_pnl() -> pd.Series:
    """2 000 simulated daily P&L values ~ N(0, 20 000^2), i.e. a 1 000 000
    portfolio with 2% daily volatility. Seeded: the numbers never change."""
    rng = np.random.default_rng(12345)
    idx = pd.bdate_range("2016-01-01", periods=2000)
    return pd.Series(rng.normal(0.0, 20_000.0, size=2000), index=idx)


@pytest.fixture
def db() -> sqlite3.Connection:
    """In-memory SQLite with the project schema loaded and LN() available."""
    conn = sqlite3.connect(":memory:")
    conn.create_function("LN", 1, math.log)   # portable even if SQLite lacks math functions
    conn.executescript((SQL_DIR / "schema.sql").read_text(encoding="utf-8"))
    yield conn
    conn.close()
