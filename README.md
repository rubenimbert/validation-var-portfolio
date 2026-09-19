# VaR Model Validation

Independent validation of Value-at-Risk models on a multi-asset portfolio:
implementation of several VaR estimators, out-of-sample backtesting over a
period that includes the 2020 and 2022 stress episodes, an independent
re-implementation in SAS, and a written validation report structured along
SR 11-7 lines.

*Status: skeleton. Function signatures, tests and database schema are in
place; implementations are being written and are tracked by the test suite.*

## Why this project

A bank's market-risk VaR is only acceptable if its exceptions behave like a
1 % coin toss. This repository asks that question the way a model-validation
team does: several candidate models, the same data, the same backtests, and a
report that says which one fails, where, and why.

## Layout

```
sql/        schema.sql (tables), returns_view.sql, data_quality_checks.sql
src/varval/ returns.py -> data.py -> var_models.py -> backtest.py -> rolling.py
tests/      one test file per module; the suite is the specification
docs/       model description template, validation report outline
sas/        independent re-implementation of the parametric VaR and Kupiec test
notebooks/  exploration only; nothing in the report depends on a notebook
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest                                                 # 40 tests; 1 passes on the bare skeleton
```

## Working method (test-driven)

Every function in `src/varval/` is a stub that raises `NotImplementedError`,
with a docstring stating the formula and the convention the tests pin down.
The tests hold hand-checkable expected values (see `tests/conftest.py`).
Implement in this order and watch the suite turn green:

| Step | Module / file                 | Tests                     | What you learn                                   |
|------|-------------------------------|---------------------------|--------------------------------------------------|
| 1    | `returns.py`                  | `test_returns.py`         | log returns, linear portfolio approximation      |
| 2    | `data.py` + `sql/returns_view.sql` | `test_sql.py`        | schema, idempotent loads, window functions       |
| 3    | `var_models.py`               | `test_var_models.py`      | parametric, historical, ES, EWMA, Monte Carlo    |
| 4    | `backtest.py`                 | `test_backtest.py`        | Kupiec, Christoffersen, Basel traffic light      |
| 5    | `rolling.py`                  | `test_rolling.py`         | out-of-sample forecasts without look-ahead       |
| 6    | notebook + `var_results` table | (none)                   | run the models on real data, store every number  |
| 7    | `sas/`                        | reconciliation            | independent re-implementation, ddof finding      |
| 8    | `docs/validation_report.md`   | (none)                    | the actual deliverable                           |

Run a single file while you work: `pytest tests/test_returns.py -v`.

## Conventions (decided up front, referenced by the report)

- Daily **log** returns; portfolio return is the linear combination `w'r`.
- **Losses are negative P&L; VaR and ES are reported as positive amounts.**
- `alpha` is the confidence level: `alpha = 0.99` is the 99 % VaR.
- Horizon: 1 day. No square-root-of-time scaling in the core results.
- Historical quantile: NumPy default linear interpolation.
- Sample covariance: `ddof = 1`. EWMA: `lambda = 0.94`, initialised on the
  first observation of the window.
- Monte Carlo: multivariate normal, Cholesky factor, seeded generator.
- Estimation windows: 250 and 500 trading days. Backtest sample: 2019-2025.
- Basel traffic light: 250 observations, 99 %: green 0-4, yellow 5-9, red 10+.

## Data

Euro-denominated instruments only (no FX conversion): CAC 40 equities, a
world-equity ETF, a euro-government-bond ETF, a gold ETC. Adjusted closes
from Yahoo Finance, 2015-2025, stored in SQLite (`data/varval.db`, ignored
by git; regenerate with the loader). Data-quality checks are SQL queries in
`sql/data_quality_checks.sql` and their output is a section of the report.

## Deliverables

1. This repository, with a green test suite.
2. `docs/validation_report.pdf`: model description, data, conceptual
   soundness, implementation testing (SAS reconciliation), outcomes analysis
   (backtests), sensitivity and benchmarking, findings rated High/Medium/Low.
3. A five-minute walkthrough of the findings (slides in `docs/`).

## References

- Hull, J. C., *Risk Management and Financial Institutions* (VaR, ES,
  historical simulation, model-building approach, backtesting, Basel).
- Kupiec, P. (1995), "Techniques for verifying the accuracy of risk
  measurement models", *Journal of Derivatives*.
- Christoffersen, P. (1998), "Evaluating interval forecasts",
  *International Economic Review*.
- Basel Committee (1996), *Supervisory framework for the use of
  "backtesting" in conjunction with the internal models approach*.
- Board of Governors of the Federal Reserve System, *SR 11-7: Guidance on
  Model Risk Management* (2011).
- Acerbi, C. and Székely, B. (2014), "Backtesting Expected Shortfall",
  *Risk* (optional extension).
