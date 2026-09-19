# Independent Validation Report — Portfolio VaR models

*Target length 10-15 pages, English. Section numbering follows the logic of
SR 11-7: conceptual soundness, implementation testing, outcomes analysis.*

1. **Executive summary and overall assessment**
   One paragraph per model. Overall rating (e.g. *Fit for purpose with
   findings* / *Not fit for purpose*). Table of findings with severity.
2. **Scope of the validation**
   Models, portfolio, period, what was and was not tested.
3. **Model description** (summary of the developer's document)
4. **Data**
   Sources, coverage, results of each data-quality check (missing days,
   stale prices, outliers, gaps), treatment decisions and their impact.
5. **Conceptual soundness**
   Are the assumptions justified for these assets? Evidence: fat tails
   (kurtosis, QQ-plots), volatility clustering (autocorrelation of squared
   returns), correlation breakdown in 2020. Literature.
6. **Implementation testing**
   Unit tests, independent re-implementation in SAS, reconciliation table
   (Python vs SAS) and explanation of any difference (ddof, quantile method).
7. **Outcomes analysis (backtesting)**
   For each model and window: exceptions, Kupiec, Christoffersen,
   conditional coverage, Basel zone. Full period and sub-periods
   (calm / 2020 / 2022). Plot of P&L against VaR with exceptions marked.
8. **Sensitivity and benchmarking**
   Effect of window length, confidence level, EWMA lambda, distribution
   (normal vs Student-t Monte Carlo). Challenger model comparison.
9. **Findings and recommendations**
   Each finding: description, evidence, severity (High / Medium / Low),
   recommended remediation, owner.
10. **Limitations of this validation**
    What could not be tested, and why.

Appendices: full result tables, reconciliation details, code references.
