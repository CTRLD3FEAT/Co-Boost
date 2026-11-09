# Co-Boost Three-Minute Demo Storyboard

## 0:00–0:25 — Problem and data

Show the Co-Boost title and say: “This system helps a Colombo food-security
officer decide which staple-price signals deserve attention first. It reads
320 official DCS weekly PDFs, not a hand-entered example.”

## 0:25–1:05 — Ranked alert board

Show the Alerts view and point out the ranked rows, spike risk, expected
next-week move, confidence, and anomaly column. Explain that the ranking is
computed from historical behavior and a chronological holdout, not copied from
the source table.

## 1:05–1:55 — Real alert explanation

Select a high-confidence row. Show the historical graph, p10/p50/p90 forecast
band, median move, and “Why this alert” card. Mention the 0.198 PR-AUC,
0.342 high-tier precision, and that the p10–p90 band covered 76.26% of the
holdout observations.

## 1:55–2:25 — Model 4 and safe failure

Point to the anomaly label and explain that the z-score engine adds a separate
statistical view of unusual highs, lows, calm periods, or moves. Switch to
Monitoring and select a short-history item. Emphasize that the system refuses
to invent a forecast when history is insufficient.

## 2:25–3:00 — Trust and close

Show the README or report briefly: DCS is the primary Colombo aggregate,
missingness and source age are disclosed, and the dashboard is decision
support, not a guarantee. Close with the officer’s action: verify the ranked
signal against the source report and field context.
