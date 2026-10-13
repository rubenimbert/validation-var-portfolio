## 2026-10-12 — Environnement
- Python 3.13, numpy 2.5.4, pandas 3.0.6, scipy 1.18.1, pytest 9.1.1
- requirements.txt utilise des contraintes >= : pandas 3.x installé alors que le projet a été pensé pour 2.x. À surveiller.
- Suite de tests : 39 failed, 1 passed (squelette, attendu).
## 2026-10-13 — data.py
- La correspondance ticker → instrument_id utilise pandas .map() : un ticker absent de la table instruments devient NaN en silence. L'insertion échoue grâce à la contrainte NOT NULL du schéma, mais avec un message peu explicite. Amélioration possible : vérifier les tickers inconnus et lever une erreur claire.