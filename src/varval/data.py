"""Data access layer: market data download and SQL persistence.

Implementation order: this module comes SECOND (after returns.py), because the
first thing you want is a working pipeline prices -> DB -> returns.

Everything here is deliberately thin. The point is not the code; the point is
that every number in the report can be traced back to a row in `prices`.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "sql" / "schema.sql"


def init_db(conn: sqlite3.Connection, schema_path: Path = SCHEMA_PATH) -> None:
    """Create all tables from sql/schema.sql on an open connection.

    Fully implemented: reading a .sql file and calling ``executescript`` is not
    where you learn anything.
    """
    sql = Path(schema_path).read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.commit()


def download_prices(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    """Download daily closing prices with yfinance.

    Returns a *long* DataFrame with columns ``["ticker", "date", "close"]``,
    one row per (ticker, day), ``date`` as ISO string 'YYYY-MM-DD', sorted by
    ticker then date, with rows where ``close`` is NaN dropped.

    Notes for the implementer
    -------------------------
    * ``yfinance.download(tickers, start=..., end=..., auto_adjust=True)``
      returns a wide DataFrame (MultiIndex columns when several tickers).
      Use adjusted closes so that dividends/splits do not create fake returns.
    * Reshape wide -> long with ``.stack()`` or ``.melt()``.
    * There is no unit test for this function (it needs the network). Test it
      by hand in a notebook, then save the result to data/raw/prices.csv so
      the rest of the project is reproducible offline.
    """
    raise NotImplementedError


def upsert_instruments(conn: sqlite3.Connection, instruments: pd.DataFrame) -> None:
    """Insert instruments (columns: ticker, name, asset_class, currency).

    Use ``INSERT OR IGNORE`` so the function is idempotent (running it twice
    must not fail and must not duplicate rows).
    """
    sql = "INSERT OR IGNORE INTO instruments(ticker, name, asset_class, currency) VALUES (?, ?, ?, ?)"
    lignes = instruments[["ticker", "name", "asset_class", "currency"]].itertuples(index=False)
    conn.executemany(sql, lignes)
    conn.commit()  


def load_prices_to_db(conn: sqlite3.Connection, prices: pd.DataFrame,
                      source: str = "yfinance") -> int:
    """Write a long price DataFrame (ticker, date, close) into ``prices``.

    * Map ``ticker`` -> ``instrument_id`` through the ``instruments`` table
      (a JOIN in SQL, or a dict built with one SELECT).
    * Use ``INSERT OR REPLACE`` (or ``INSERT ... ON CONFLICT DO UPDATE``) so a
      re-run refreshes prices instead of crashing on the primary key.
    * Return the number of rows written.

    Tested by tests/test_sql.py::test_prices_round_trip.
    """
    correspondance = dict(conn.execute("SELECT ticker, instrument_id FROM instruments").fetchall())
    ids = prices["ticker"].map(correspondance)
    sql = "INSERT OR REPLACE INTO prices(instrument_id, date, close, source) VALUES (?, ?, ?, ?)"
    lignes = list(zip(ids, prices["date"], prices["close"], [source] * len(prices)))
    conn.executemany(sql, lignes)
    conn.commit()
    return len(lignes)


def read_prices(conn: sqlite3.Connection, tickers: list[str] | None = None) -> pd.DataFrame:
    """Read closes back as a *wide* DataFrame: index = DatetimeIndex, one
    column per ticker, sorted by date.

    Write the SELECT with a JOIN on ``instruments`` to get tickers, then pivot
    in pandas. ``tickers=None`` means all instruments.

    Tested by tests/test_sql.py::test_prices_round_trip.
    """
    raise NotImplementedError

