# SAS re-implementation (Step 7)

Goal: reproduce, independently of the Python code, the parametric VaR and
the Kupiec test on the same input, then reconcile the two sets of numbers.
This is what "implementation testing" means in a validation report.

Planned programs

1. `01_import.sas` — PROC IMPORT of `data/raw/prices.csv`; PROC SORT by ticker, date.
2. `02_returns.sas` — DATA step with `LAG(close)` inside a BY group
   (careful: LAG in a BY group needs `first.ticker` handling), `log()` return.
3. `03_var.sas` — PROC CORR COV for the covariance matrix over the window,
   PROC IML (or a DATA step) for w'Sw, VaR = quantile('NORMAL', 0.99) * sigma * V.
4. `04_backtest.sas` — merge VaR forecasts with realised P&L, count
   exceptions, Kupiec LR in a DATA step, p-value with `1 - probchi(LR, 1)`.
5. `05_reconcile.sas` — PROC SQL: join Python results (exported to CSV) with
   SAS results, report absolute and relative differences.

Expected finding: PROC CORR uses the sample covariance (n-1). If the Python
side used NumPy's `np.var`/`np.std` default (n), the VaRs differ by
sqrt(n/(n-1)). Document it either way.

Free environment: SAS OnDemand for Academics (check current availability).
