"""varval - Value-at-Risk model validation toolkit.

Conventions used throughout the package (see README, section "Conventions"):
- Returns are daily log returns unless stated otherwise.
- P&L is expressed in portfolio currency; losses are negative P&L.
- VaR and ES are reported as POSITIVE numbers (a loss amount).
- ``alpha`` is the confidence level (0.99 means 99% VaR).
"""

__version__ = "0.1.0"
