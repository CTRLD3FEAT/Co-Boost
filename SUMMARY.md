# Co-Boost — Summary

## The problem

Food-price shocks reach low-income households before the people responsible
for monitoring food security can compare the signal with its history. 
Most of the time they get to know after the food prices hit the market. Official
price tables show what happened, but not which Colombo staple prices are
abnormal, likely to move next week, or supported by enough evidence to act on.

Co-Boost is a decision-support system for a Colombo food-security or
consumer-protection officer. It ranks the item-level risks that deserve
verification, field monitoring, or an advisory response. Though the
the officer's expertise remains essential. 

## What the system delivers

The dashboard turns 324 official Department of Census & Statistics weekly
retail-price PDFs into a verified time series of 34,535 rows and 146
commodities covering December 2019 to November 2026. It provides:

1. A ranked next-week spike-risk list.
2. A p10/p50/p90 forecast range rather than a false-precision point estimate.
3. Statistical anomaly signals for unusual highs, lows, calm periods, and
   one-week moves.
4. A monitoring view for commodities with fewer than 26 observations. (When Data is not enough for a prediction)
5. Source, history, confidence, and next-step context for verification.

This is insight computed from the data: the officer does not need to manually
compare every commodity with its own 26-week history and holdout-calibrated
spike behavior.

## Co-Boost Engine

| Model | Role |
|---|---|
| Naive persistence | Honest point-forecast anchor |
| MLP spike classifier | Early-warning radar |
| Quantile boosters | p10/p50/p90 budgeting range |
| Z-score anomaly engine | Velocity and regime detection |

The features use recent returns (`r1`, `r2`, `r4`), a 26-week price z-score,
drawdown from the 26-week maximum, volatility ratio, directional streak,
cyclical month features, and food inflation. Missing histories are not
silently imputed: thin series are shown as monitoring-only.

## Co-Boost Calibration Gate (G1-G4)

All model claims use chronological holdouts covering 2024–2026.

| Gate | Result | Status |
|---|---:|---|
| MLP spike PR-AUC target ≥ 0.18 | 0.198 vs 0.054 random base rate | PASS |
| High-tier precision target ≥ 0.34 | 0.342 across 184 flagged weeks | PASS |
| Probability calibration | Chronological holdout check | PASS |
| p10–p90 coverage target [0.75, 0.85] | 76.26% | PASS |

The naive persistence baseline remains the price-level anchor; the ML layer is
used to rank spike risk and provide a range, not to claim that a complex model
beats every simple forecast.

## Data honesty and limits

DCS is the operational primary source and represents a Colombo District
aggregate, not a separate series for every named market. PDFs can have missing
weeks, stale labels, inconsistent names, and incompatible units; the parser
records provenance and excludes unsafe rows rather than guessing. Alongside DCS, WFP Food inflation is used to build more relationships with food price --> inflation to help make the predictions. CBSL,Open-meteo and
other enrichment are contextual or future scope, not silently merged into the
current DCS model.

If a source is stale or a history is too short, the system exposes that
limitation and lowers or withholds a predictive signal. The data describes
commodity prices, not identifiable people. Public sources are credited in the
README and the repository retains extraction notes.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The live dashboard is the submission demonstration: select an alert, inspect
the forecast range and anomaly explanation, then show the monitoring view for
an item where the data cannot support a forecast.
