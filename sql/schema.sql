-- ============================================================================
-- varval - database schema (SQLite dialect; portable to PostgreSQL with minor
-- changes: SERIAL/IDENTITY for ids, DATE type instead of TEXT).
--
-- Design notes (a validator reads a schema the way an auditor reads accounts):
--   * prices has a composite primary key (instrument_id, date): a duplicate
--     price for the same day is a data error, and the DB must refuse it.
--   * Every VaR figure is attached to a "run": the model, the confidence level,
--     the horizon and the window are stored, so any number can be reproduced.
--   * exception_flag is stored, not recomputed on the fly: the backtest is an
--     auditable table, not an opinion.
-- ============================================================================

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS instruments (
    instrument_id   INTEGER PRIMARY KEY,
    ticker          TEXT NOT NULL UNIQUE,      -- e.g. 'TTE.PA'
    name            TEXT NOT NULL,
    asset_class     TEXT NOT NULL CHECK (asset_class IN ('equity','bond','commodity','fx','index')),
    currency        TEXT NOT NULL              -- ISO code, e.g. 'EUR'
);

CREATE TABLE IF NOT EXISTS prices (
    instrument_id   INTEGER NOT NULL REFERENCES instruments(instrument_id),
    date            TEXT    NOT NULL,          -- ISO 'YYYY-MM-DD'
    close           REAL    NOT NULL CHECK (close > 0),
    source          TEXT    NOT NULL DEFAULT 'yfinance',
    loaded_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (instrument_id, date)
);

CREATE TABLE IF NOT EXISTS portfolios (
    portfolio_id    INTEGER PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    base_currency   TEXT NOT NULL,
    market_value    REAL NOT NULL CHECK (market_value > 0)   -- V, in base currency
);

CREATE TABLE IF NOT EXISTS positions (
    portfolio_id    INTEGER NOT NULL REFERENCES portfolios(portfolio_id),
    instrument_id   INTEGER NOT NULL REFERENCES instruments(instrument_id),
    weight          REAL    NOT NULL,          -- fraction of market_value; weights of a portfolio sum to 1
    PRIMARY KEY (portfolio_id, instrument_id)
);

CREATE TABLE IF NOT EXISTS var_runs (
    run_id          INTEGER PRIMARY KEY,
    portfolio_id    INTEGER NOT NULL REFERENCES portfolios(portfolio_id),
    model           TEXT    NOT NULL CHECK (model IN ('parametric','ewma','historical','monte_carlo','fhs')),
    confidence      REAL    NOT NULL CHECK (confidence > 0 AND confidence < 1),   -- e.g. 0.99
    horizon_days    INTEGER NOT NULL DEFAULT 1,
    window_days     INTEGER NOT NULL,          -- estimation window, e.g. 250
    params          TEXT,                      -- JSON: lambda, n_sims, seed, distribution...
    run_at          TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS var_results (
    run_id          INTEGER NOT NULL REFERENCES var_runs(run_id),
    date            TEXT    NOT NULL,          -- the day the VaR applies to (forecast made with data strictly before)
    var_value       REAL    NOT NULL CHECK (var_value >= 0),
    es_value        REAL,                      -- NULL until ES is implemented
    realized_pnl    REAL,                      -- NULL until the day's P&L is known
    exception_flag  INTEGER CHECK (exception_flag IN (0, 1)),
    PRIMARY KEY (run_id, date)
);

CREATE TABLE IF NOT EXISTS backtest_summary (
    run_id                  INTEGER PRIMARY KEY REFERENCES var_runs(run_id),
    period_start            TEXT NOT NULL,
    period_end              TEXT NOT NULL,
    n_obs                   INTEGER NOT NULL,
    n_exceptions            INTEGER NOT NULL,
    kupiec_lr               REAL,
    kupiec_pvalue           REAL,
    christoffersen_lr       REAL,
    christoffersen_pvalue   REAL,
    cc_lr                   REAL,              -- conditional coverage (Kupiec + independence)
    cc_pvalue               REAL,
    traffic_light           TEXT CHECK (traffic_light IN ('green','yellow','red'))
);

CREATE INDEX IF NOT EXISTS idx_prices_date ON prices(date);
CREATE INDEX IF NOT EXISTS idx_var_results_date ON var_results(date);
