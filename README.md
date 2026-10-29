# Co-Boost — Sri Lanka Food Security DSS

Weekly retail-price monitoring, forecasting, and **food-price spike early warning**
for the Colombo district, built end-to-end from official DCS (Department of Census
& Statistics) weekly retail price PDFs — 320 reports, Dec 2019 → Oct 2026.

Built for the ModelX 2.0 competition (IEEE CIS Student Chapter, IIT · Team NRZB).

## What it does

1. **Ingest — strict, no-guess parsing** of 320 official DCS-WRP PDFs via
   `Scripts/parse_wrp.py` (three DCS layouts auto-detected; missing prices excluded
   and logged, never imputed; reporting week taken from the filename, with title
   mismatches logged).
2. **Clean canonical dataset** — 34,099 rows × 146 commodities after normalization
   (Unicode-dash name families merged; non-food Betel Leaves/Arecanuts excluded at
   loader level with an auditable exclusion table).
3. **Honest benchmark** — walk-forward, one-step-ahead backtest of naive and
   statistical baselines (`Scripts/backtest_baselines.py`): naive *last price* is the
   price bar (median MAPE **2.7%**, wins 121/121) that any richer model must beat.
4. **ML spike early warning** — classifiers trained on a chronological holdout to
   predict ≥ +10% next-week spikes (`Scripts/spike_ml.py`); best reaches PR-AUC ≈ 0.20
   against a 0.054 random base (≈ 4×). Bundle saved to
   `outputs/spike_ml_bundle.joblib` with p10/p50/p90 quantile regressors for forecast
   bands.
5. **Decision-support dashboard** — `streamlit run app.py`
   - Ranked alert board (Spike risk %, next-week move, signal, High/Medium/Low
     confidence anchored to holdout precision)
   - Monitoring view for short-history items (safe-floor badge, raw chart)
   - Per-commodity drill-down: weekly price chart with ML median forecast + p10/p90
     band, "why this alert" reasoning, source-report next step

## Quickstart

```bash
pip install -r requirements.txt
streamlit run app.py
```

Legacy UIs remain available: `streamlit_app.py` and `Dash_APP/dash_app.py`.

## Repository layout (by phase)

| Phase | Commit | Path |
|---|---|---|
| 1 · Data Acquisition and Preprocessing | `7d88a3b`…`ce8f4a1` (6 commits) | `Dataset/` (320 DCS-WRP PDFs + `food_inflation.csv`), `Scripts/parse_wrp.py`, `Scripts/ingest_official_pdfs.py`, `baseline.py`, `outputs/official_prices_wrp*.csv`, `outputs/DATASET_NOTES.md` |
| 2 · Baselines | `c6065ae` | `Scripts/backtest_baselines.py`, `outputs/backtest_*` |
| 3 · ML spike warning | `e3bdcea` | `Scripts/spike_ml.py`, `outputs/spike_ml_bundle.joblib`, leaderboards |
| 4 · Dashboards | `ac17660` | `app.py`, `streamlit_app.py`, `data.py`, `alerts.py`, `Dash_APP/dash_app.py`, `.streamlit/config.toml`, `requirements.txt` |
| 5 · Docs | (this commit) | `README.md`, `LICENSE`, `legacy/` |

## Data sources (credited)

- **DCS weekly retail prices** (primary): Department of Census & Statistics Sri Lanka — https://www.statistics.gov.lk/InflationAndPrices/StaticalInformation/RetailPrices (publicly available)
- **CBSL daily price reports** (supplementary named-market cross-check): https://www.cbsl.gov.lk/en/statistics/economic-indicators/pricereport (publicly available)
- **Sri Lanka food inflation** (WFP, supplementary factor): https://dataviz.vam.wfp.org/data-explorer/economic/inflation (publicly available)

Tool disclosure: Claude & Grok used for research, planning, drafting and coding, per competition rules; the team owns everything submitted.

## Honesty & audit trail

- Every excluded price is recorded with a reason; anomalies and exclusions are never silently dropped or imputed.
- All reported metrics are out-of-sample, chronological holdouts — no leakage.
- Dataset decisions and their evidence live in `outputs/DATASET_NOTES.md`.
- Legacy stage-1/2 artifacts are archived under `legacy/`.

## License

MIT — see `LICENSE`. Public datasets remain under their own terms; credit them as listed above.
