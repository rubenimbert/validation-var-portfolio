"""SQL-side tests. They exercise YOUR view (sql/returns_view.sql) and YOUR
persistence functions (varval.data)."""

import numpy as np
import pandas as pd
import pytest

from tests.conftest import SQL_DIR
from varval.data import load_prices_to_db, read_prices, upsert_instruments


def _seed_instruments(db):
    inst = pd.DataFrame({
        "ticker": ["AAA", "BBB"],
        "name": ["Asset A", "Asset B"],
        "asset_class": ["equity", "bond"],
        "currency": ["EUR", "EUR"],
    })
    upsert_instruments(db, inst)


def test_schema_has_all_tables(db):
    tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    for t in ["instruments", "prices", "portfolios", "positions", "var_runs", "var_results", "backtest_summary"]:
        assert t in tables


def test_upsert_instruments_is_idempotent(db):
    _seed_instruments(db)
    _seed_instruments(db)                       # second call must not fail nor duplicate
    n = db.execute("SELECT COUNT(*) FROM instruments").fetchone()[0]
    assert n == 2


def test_prices_round_trip(db):
    _seed_instruments(db)
    long = pd.DataFrame({
        "ticker": ["AAA", "AAA", "AAA", "BBB", "BBB", "BBB"],
        "date":   ["2024-01-02", "2024-01-03", "2024-01-04"] * 2,
        "close":  [100.0, 110.0, 99.0, 50.0, 50.5, 49.0],
    })
    n = load_prices_to_db(db, long)
    assert n == 6
    n2 = load_prices_to_db(db, long)            # re-run must overwrite, not crash
    assert n2 == 6
    assert db.execute("SELECT COUNT(*) FROM prices").fetchone()[0] == 6

    wide = read_prices(db)
    assert list(wide.columns) == ["AAA", "BBB"]
    assert isinstance(wide.index, pd.DatetimeIndex)
    assert wide.loc["2024-01-03", "AAA"] == pytest.approx(110.0)
    assert wide.loc["2024-01-04", "BBB"] == pytest.approx(49.0)

    only_b = read_prices(db, tickers=["BBB"])
    assert list(only_b.columns) == ["BBB"]


def test_prices_reject_duplicates_and_non_positive(db):
    _seed_instruments(db)
    db.execute("INSERT INTO prices(instrument_id, date, close) VALUES (1, '2024-01-02', 100.0)")
    with pytest.raises(Exception):
        db.execute("INSERT INTO prices(instrument_id, date, close) VALUES (1, '2024-01-02', 101.0)")
    with pytest.raises(Exception):
        db.execute("INSERT INTO prices(instrument_id, date, close) VALUES (1, '2024-01-03', -1.0)")


def test_log_returns_view(db):
    _seed_instruments(db)
    db.executemany("INSERT INTO prices(instrument_id, date, close) VALUES (?, ?, ?)",
                   [(1, "2024-01-02", 100.0), (1, "2024-01-03", 110.0), (1, "2024-01-04", 99.0)])
    db.executescript((SQL_DIR / "returns_view.sql").read_text(encoding="utf-8"))
    rows = db.execute(
        "SELECT date, log_return FROM v_log_returns WHERE instrument_id = 1 ORDER BY date"
    ).fetchall()
    assert len(rows) == 2                                    # first day has no return
    assert rows[0][0] == "2024-01-03"
    assert rows[0][1] == pytest.approx(np.log(1.10))
    assert rows[1][1] == pytest.approx(np.log(0.90))
