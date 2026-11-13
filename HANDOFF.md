# HANDOFF — Co-Boost Engine

**Project:** Co-Boost — Sri Lanka Food Security DSS (ModelX 2.0, IEEE CIS Student Chapter IIT · Team NRZB) **Repo:** /home/elliot123/Co-Boost **Deadline:** Sunday 1 Nov 2026 (today) **Status:** In progress — dashboard branding done; deliverables remaining

## Goal

Ship the ModelX 2.0 submission: a professional, branded Co-Boost Engine dashboard (`app.py`) + two-page summary + 3-minute video + technical report.

## Current state (verified)

### Built & verified (do not rebuild)

- **Ingest:** 324 DCS-WRP PDFs → canonical panel `outputs/official_prices_dcs.csv` (34,535 rows × 146 commodities, Dec 2019–Nov 2026). Parser: `Scripts/parse_wrp.py`. Exclusions auditable in `outputs/commodity_exclusions.csv` (betel leaves/arecanuts removed, ~5%).

- **Baseline:** naive last-price wins 121/121, median MAPE 2.71% (`outputs/backtest_leaderboard.csv`, `Scripts/backtest_baselines.py`).

- **MLP spike classifier:** `Scripts/spike_ml.py` → `outputs/spike_ml_bundle.joblib`. PR-AUC 0.198 vs 0.054 base rate; High-tier precision 0.342; threshold 0.112; 184 weeks flagged. Gate G1–G3 PASS.

- **Quantile boosters p10/p50/p90:** same bundle. p10–p90 holdout coverage 76.26% (Gate G4 PASS).

- **z-score anomaly engine:** `Scripts/spike_ml.py:anomaly_table()` — flags 🔺🔻🧊🌀 (unusual high/low/stable/move). Currently only surfaced in legacy `streamlit_app.py`; NOT yet in shipping `app.py`.

- **`app.py`** is the shipping dashboard: sidebar filters → 3 KPI cards → Ranked alerts table → forecast fan chart (p10/p90 band + p50 diamond) → "Why this alert" card (ML spike probability, expected move, momentum, history, next step). Launches cleanly (`streamlit run app.py`).

### Dashboard branding applied to `app.py` ✅

- Page title → "Co-Boost"

- Animated Co-Boost wordmark at top (CSS `cbPulse` gradient \#00a881→\#006850 + `cbFadeIn` tagline)

- `st.spinner("Co-Boost Engine loading market data…")` around data load + computation

- Footer naming the 4-model Co-Boost Engine suite + Calibration Gate attribution

### Legacy dashboards moved ✅

- `streamlit_app.py` → `legacy/dashboards/streamlit_app.py`

- `Dash_APP/` → `legacy/dashboards/Dash_APP/`

- README.md still needs its legacy path line updated (currently says "streamlit\_app.py and Dash\_APP/dash\_app.py" — should point to `legacy/dashboards/`)

### Co-Boost Calibration Gate (G1–G4) documented in README.md

- G1 PR-AUC ≥ 0.198, G2 High-tier precision ≥ 0.34, G3 probability sanity, G4 pinball loss + coverage \[0.75,0.85\]. All PASS on MLP.

## The 4 models = "Co-Boost Engine"

| \# | Model | Role | File |
| - | - | - | - |
| 1 | Naive persistence baseline | Point-forecast anchor | `baseline.py` |
| 2 | MLP spike classifier | Early-warning radar | `Scripts/spike_ml.py` |
| 3 | Quantile boosters p10/p50/p90 | Budgeting range engine | `Scripts/spike_ml.py` |
| 4 | z-score anomaly engine | Velocity & regime detector | `Scripts/spike_ml.py:anomaly_table()` |


## Files touched in this session

- `app.py` — branding (title, wordmark, spinner, footer)

- `legacy/dashboards/` — created; moved legacy `streamlit_app.py` + `Dash_APP/` here

- `README.md` — added Calibration Gate section (G1–G4); legacy path line needs update

- `/home/elliot123/.claude/plans/enumerated-orbiting-sunset.md` — plan file

## Open items / next steps (in order)

### 1. Dashboard tweak still pending: Model 4 surface

Surface Model 4 anomaly badges (🔺🔻🧊🌀) in `app.py` ranked-alerts table so the full 4-model Co-Boost Engine is visible on the shipping dashboard. Source of truth: `Scripts/spike_ml.py:anomaly_table()` + `streamlit_app.py` anomaly view (now in legacy/). Import `sml`/`anomaly_table` and render flags alongside the alert table.

### 2. README.md cleanup

Update the "Legacy UIs remain available" line to point to `legacy/dashboards/` instead of old paths.

### 3. Deliverable 1 — Two-page summary (`SUMMARY.md`)

Page 1: problem + Co-Boost Engine 4-model architecture + Calibration Gate (G1–G4) + architecture mermaid (reuse from README). Page 2: results table (PR-AUC 0.198, coverage 76.26%, naive 2.71% MAPE 121/121, threshold 0.112) + data summary + gaps + honest evaluation vs proposal + rejected enrichment families F1/F2/F3 + quickstart.

### 4. Deliverable 2 — 3-minute video

Screen recording of `streamlit run app.py`. Script (~180s):

- 0:00–0:15 title + data context (324 DCS PDFs, 2019–2026)

- 0:15–0:40 KPI cards + ranked list

- 0:40–1:20 click High-confidence alert → fan chart + 76% coverage claim

- 1:20–2:00 "Why this alert" card

- 2:00–2:30 filter interactivity + Monitoring view

- 2:30–3:00 gate report / README + closing `streamlit run app.py` Tooling: OBS/ffmpeg/Zoom if available; else phone-recording-of-laptop-screen fallback.

### 5. Deliverable 3 — Technical report (`docs/TECHNICAL_REPORT.md`)

Expand `docs/architecture/README.md` + README into report: problem & users, architecture (reuse mermaid + diagram assets), stack choice & why, data temporality & gaps (from `outputs/DATASET_NOTES.md`), honest evaluation vs proposal, Calibration Gate, reproducibility.

## Verification checklist

- [ ] 

- `streamlit run app.py` launches cleanly after every edit

- [ ] 

- Every cited number matches `outputs/*.csv` / `gate_report_f2_champion.txt`

- [ ] 

- README legacy paths point to `legacy/dashboards/`

- [ ] 

- Model 4 anomaly badges visible in `app.py`

- [ ] 

- Video ≤ 3:00, claims match live dashboard

- [ ] 

- `SUMMARY.md` every number verified

## Key numbers (source: `outputs/`)

- naive\_last: wins 121/121, median MAPE 2.71% (`backtest_leaderboard.csv`)

- MLP: PR-AUC 0.198, ROC-AUC 0.812, Hi-precision 0.342 (184 wks), threshold 0.112 (`spike_ml_leaderboard.csv`)

- p10–p90 coverage 76.26% (`gate_report_f2_champion.txt`, Gate G4 PASS)

- Direction regressor hist\_gb: MAE 0.0427, dir\_acc 0.500 (`direction_leaderboard.csv`)

- 324 DCS PDFs → 34,535 rows × 146 commodities, Dec 2019 → Nov 2026 (`DATASET_NOTES.md`)


