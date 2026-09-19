# Model Description — Portfolio VaR v1.0

*Written in the role of the model developer. One to two pages. The validation
report will challenge every sentence below, so be precise: a validator's
findings are usually sentences that are missing from this document.*

## 1. Purpose and use
What the model measures (1-day 99 % VaR of portfolio P), what decision it
supports (limits, capital, reporting), who uses it.

## 2. Scope
Instruments covered, currency, portfolio composition and market value,
rebalancing assumption (fixed weights).

## 3. Methodology
Estimator (parametric / historical / Monte Carlo / EWMA), estimation window,
confidence level, horizon, distributional assumptions, treatment of the mean,
quantile convention, ddof convention, EWMA initialisation.

## 4. Data
Source, frequency, adjustment for corporate actions, calendar alignment
rule, missing-data rule, history used for calibration.

## 5. Implementation
Language, libraries, where the code lives, how results are stored
(`var_runs` / `var_results`), how a figure can be reproduced.

## 6. Known limitations (as stated by the developer)
Normality, linear portfolio approximation, no intraday risk, no liquidity
horizon, stale-price handling, ...

## 7. Monitoring
How and how often the model is backtested, what triggers a review.
