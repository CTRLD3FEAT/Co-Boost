"""Food Price Early Warning - UI only (Streamlit).

Alerts = calibrated ML spike probabilities from outputs/spike_ml_bundle.joblib
(trained 2019-2023, validated 2024-2026 chronological holdout). The same
bundle carries quantile regressors (p10/p50/p90) for the next-week change
band shown on the forecast card. Naive still wins price-level MAPE
(2.7% median); this layer only ranks spike risk.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", initial_sidebar_state="expanded",
                   page_title="Co-Boost", page_icon="🛒")

import data as dt
import alerts as al
from Scripts import spike_ml as sml

PAGE_CSS = """
<style>
    header[data-testid="stHeader"] { background: transparent; }
    header[data-testid="stHeader"] svg { color: #6B7A75; }
    .block-container { padding-top: 4.5rem; padding-bottom: 2.5rem; }
    div[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 12px; }
    .kpi-card { border: 1px solid #DDE5E1; border-radius: 14px;
                padding: 1rem 1.1rem .85rem; background: #FFFFFF;
                box-shadow: 0 2px 8px rgba(15,107,87,.06); }
    .kpi-value { font-size: 2.4rem; font-weight: 750; color: #0F6B57;
                 line-height: 1; }
    .kpi-label { color: #6B7A75; font-size: 0.82rem; margin-top: .4rem;
                 letter-spacing: .01em; }
    .section-note { color: #6B7A75; font-size: .82rem; margin: -.35rem 0 1rem; }
    .vintage-box { border: 1px solid #DDE5E1; border-radius: 12px;
                   padding: .55rem .9rem; background: #FFFFFF;
                   text-align: right; }
    .vintage-box .v-label { color: #6B7A75; font-size: .78rem; }
    .vintage-box .v-value { font-weight: 700; color: #1F2A27; }
    .next-step { border: 1.5px solid #0F6B57; border-radius: 12px;
                 padding: .7rem .9rem; background: #FFFFFF; }
    .chg-up { color: #B3261E; font-weight: 600; }
    .chg-down { color: #1E8E4E; font-weight: 600; }
    .cb-brand { text-align: center; margin-bottom: 1.4rem; }
    .cb-wordmark { background: linear-gradient(90deg, #006850, #00A881, #006850);
                   background-size: 200% auto; color: transparent;
                   background-clip: text; -webkit-background-clip: text;
                   font-size: 4.2rem; font-weight: 800;
                   letter-spacing: -.04em; line-height: 1;
                   animation: cbShift 4s ease-in-out infinite; }
    .cb-tagline { color: #6B7A75; font-size: .9rem; margin-top: .35rem; }
    .cb-footer { margin-top: 2rem; padding: 1rem 0 .4rem;
                 border-top: 1px solid #DDE5E1; text-align: center;
                 color: #6B7A75; font-size: .82rem; }
    .cb-footer strong { color: #0F6B57; font-size: 1.15rem; }
    .cb-footer span { display: inline-block; margin-top: .35rem;
                      font-size: .94rem; }
    @keyframes cbShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
</style>
"""
st.markdown(PAGE_CSS, unsafe_allow_html=True)

UP_RED, DOWN_GREEN = "#B3261E", "#1E8E4E"
ANOMALY_LABELS = {
    "high": "Unusually high",
    "low": "Unusually low",
    "calm": "Stable",
    "move": "Unusual move",
}
st.markdown(
    "<div class='cb-brand'><div class='cb-wordmark'>Co-Boost</div>"
    "<div class='cb-tagline'>Food-price early warning system for Colombo district</div></div>",
    unsafe_allow_html=True)


# ------------------------------------------------- cached computations
@st.cache_data(ttl=3600, max_entries=8, show_spinner=False)
def alert_rank(dy, latest):
    return al.compute_spike_alerts(dy, pd.Timestamp(latest))


@st.cache_data(ttl=3600, max_entries=8, show_spinner=False)
def monitoring_rank(dy, latest):
    return al.monitoring_items(dy, pd.Timestamp(latest))


@st.cache_data(ttl=3600, max_entries=8, show_spinner=False)
def anomaly_rank(dy):
    source_df = dy.rename(columns={"week": "observation_date"})
    return sml.anomaly_table(source_df)


# ------------------------------------------------------------- data
dy = dt.load_weekly()
latest_wk = dt.latest_week(dy)
vintage = latest_wk.strftime("%b %Y") if hasattr(latest_wk, "strftime") \
    else str(latest_wk)
alerts, bundle = alert_rank(dy, latest_wk)
THR = float(bundle["threshold"])
monitor = monitoring_rank(dy, latest_wk)
anomalies = anomaly_rank(dy)
anomaly_cols = ["commodity", "flag"]
anomalies = anomalies[anomaly_cols].rename(columns={"commodity": "item"})

# ------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("Filters")
    choices = ["All items"] + dt.items(dy)
    sel_item = st.selectbox("Item", choices, index=0,
                            help="Pick one commodity to focus the table.")
    sel_view = st.segmented_control(
        "View", ["Alerts", "Monitoring"], default="Alerts",
        help="Monitoring = fewer than 26 weeks of history. Predictive "
             "alerts are suppressed there to prevent false signals.")
    st.caption("Source: official DCS weekly retail price reports "
               "(Colombo district)")

# ------------------------------------------------------------- filters
mon_cols = ["item", "category", "weeks", "last_price", "last_week"]
mon = monitor.copy()
mon = mon[mon_cols]
mon["spike_prob"] = 0.0
mon["pred_r1"] = 0.0
mon["pred_move_pct"] = 0.0
mon["sigma_pct"] = 0.0
mon["alert"] = False
mon["score"] = 0.0
mon["threshold"] = THR
mon["confidence"] = "Monitoring only"
mon["monitoring"] = True
mon = mon.merge(anomalies, on="item", how="left")
mon["flag"] = mon["flag"].fillna("")

if sel_view == "Monitoring":
    view = mon.copy()
else:
    view = alerts[alerts["alert"]].copy()
    view["monitoring"] = False
    view = view.merge(anomalies, on="item", how="left")
    view["flag"] = view["flag"].fillna("")
if sel_item != "All items":
    view = view[view["item"] == sel_item]

# ------------------------------------------------------------- KPI cards
if sel_view == "Monitoring":
    mon_view = view[view["monitoring"]]
    reporting_now = pd.to_datetime(
        dy[dy["commodity"].isin(mon_view["item"])]
        .groupby("commodity")["week"].max()).eq(latest_wk).sum()
    kpis = [(len(mon_view), "items tracked"),
            (int(mon_view["weeks"].median()), "median weeks tracked"),
            (int(reporting_now), "still reporting this week")]
else:
    kpi_view = view[view["alert"]]
    kpis = [(len(kpi_view), "active alerts"),
            (int((kpi_view["confidence"] == "High").sum()), "high confidence"),
            (len(alerts), "items scored")]
c1, c2, c3 = st.columns(3)
for col, (num, label) in zip((c1, c2, c3), kpis):
    with col:
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-value'>{num}</div>"
            f"<div class='kpi-label'>{label}</div></div>",
            unsafe_allow_html=True)

# ------------------------------------------------------------- ranked alerts
with st.container(border=True):
    st.subheader("Ranked alerts")
    if sel_view == "Alerts":
        st.markdown(
            "ML-selected spike alerts only · ranked by calibrated next-week "
            "spike probability",
            unsafe_allow_html=False)
    if len(view) == 0:
        st.caption("No alerts for the current filters - all monitored "
                   "prices look normal.")
        selected = None
    else:
        show = view.reset_index(drop=True).copy()
        show.insert(0, "#", show.index + 1)
        show["risk"] = show.apply(
            lambda r: "—" if r["monitoring"]
            else al.proba_label(r["spike_prob"]), axis=1)
        show["move"] = show.apply(
            lambda r: "—" if r["monitoring"]
            else (("▲ " if r["pred_r1"] >= 0 else "▼ ")
                  + al.move_label(r["pred_move_pct"])), axis=1)
        show["anomaly"] = (
            show["flag"].map(ANOMALY_LABELS).fillna("None")
        )

        def risk_cell(v, proba, conf):
            if v == "—":
                return ""
            if conf == "High":
                return f"background-color:#FCE8E6;color:{UP_RED}"
            if conf == "Medium":
                return f"background-color:#FFF4E0;color:#C98A00"
            return f"color:#7A7F7C"

        def move_cell(v):
            if v == "—":
                return ""
            up = v.startswith("▲ ")
            return f"color:{UP_RED if up else DOWN_GREEN};font-weight:600"

        def pill(v):
            colors = {"High": "#0F6B57", "Medium": "#C98A00", "Low": "#7A7F7C",
                      "Monitoring only": "#7A7F7C"}
            return f"background-color:{colors.get(v, '#7A7F7C')};color:#fff"

        tbl = show[["#", "item", "category", "risk", "move",
                    "anomaly", "confidence"]].rename(columns={
                        "item": "Item", "category": "Category",
                        "risk": "Spike risk", "move": "Next-week move",
                        "anomaly": "Anomaly",
                        "confidence": "Confidence"})

        styles = pd.DataFrame("", index=tbl.index, columns=tbl.columns)
        for i, row in show.iterrows():
            styles.loc[i, "Spike risk"] = risk_cell(
                row["risk"], row["spike_prob"], row["confidence"])
            styles.loc[i, "Next-week move"] = move_cell(row["move"])
            styles.loc[i, "Confidence"] = pill(row["confidence"])

        event = st.dataframe(
            tbl.style.apply(lambda _: styles, axis=None),
            on_select="rerun", selection_mode="single-row",
            hide_index=True, key="alerts_tbl", width="stretch",
            alt="Ranked price alerts by ML spike probability and statistical anomaly")
        selected = int(event["selection"]["rows"][0]) \
            if event["selection"]["rows"] else 0

# ------------------------------------------------- bottom row, two cards
left, right = st.columns([1.2, 1])

if selected is not None:
    row = show.iloc[selected]

    # ---------------- forecast card
    with left:
        with st.container(border=True):
            comm_series = dy[dy["commodity"] == row["item"]] \
                .sort_values("week")[["week", "price"]]
            hist = comm_series.tail(30)
            fig = go.Figure()
            MUTED = "#6B7A75"
            axis_max = float(comm_series["price"].max())
            fig.add_trace(go.Scatter(
                x=hist["week"], y=hist["price"], mode="lines",
                line=dict(color="#0F6B57", width=2.5, shape="linear"),
                name="Weekly price",
                hovertemplate="%{x|%d %b %Y}<br>Rs %{y:,.2f}<extra></extra>"))
            last_wk, last_px = hist["week"].iloc[-1], hist["price"].iloc[-1]
            fig.add_trace(go.Scatter(
                x=[last_wk], y=[last_px], mode="markers",
                marker=dict(color="rgba(179,38,30,0.18)", size=22),
                showlegend=False, hoverinfo="skip"))
            fig.add_trace(go.Scatter(
                x=[last_wk], y=[last_px], mode="markers",
                marker=dict(color=UP_RED, size=11, line=dict(color="#fff",
                                                             width=2)),
                name="Latest",
                hovertemplate="%{x|%d %b %Y}<br>Rs %{y:,.2f}"
                              "<extra>latest</extra>"))
            if not row["monitoring"]:
                next_wk = last_wk + pd.Timedelta(weeks=1)
                q10, q50, q90 = row["pred_q10"], row["pred_q50"], row["pred_q90"]
                lo_price = last_px * (1 + q10)
                med_price = last_px * (1 + q50)
                hi_price = last_px * (1 + q90)
                axis_max = max(axis_max, hi_price)
                up = q50 >= 0
                fig.add_trace(go.Scatter(
                    x=[next_wk], y=[hi_price], mode="lines",
                    line=dict(color=UP_RED, width=1.5, dash="dot"),
                    name="Upper bound (p90)",
                    hovertemplate="%{x|%d %b %Y}<br>Rs %{y:,.2f}"
                                  "<extra>Upper bound (p90)</extra>"))
                fig.add_trace(go.Scatter(
                    x=[next_wk], y=[med_price], mode="lines",
                    line=dict(width=0), fill="tonexty",
                    fillcolor="rgba(179,38,30,0.22)", showlegend=False,
                    hoverinfo="skip"))
                fig.add_trace(go.Scatter(
                    x=[next_wk], y=[lo_price], mode="lines",
                    line=dict(color=DOWN_GREEN, width=1.5, dash="dot"),
                    fill="tonexty", fillcolor="rgba(15,107,87,0.20)",
                    name="Lower bound (p10)",
                    hovertemplate="%{x|%d %b %Y}<br>Rs %{y:,.2f}"
                                  "<extra>Lower bound (p10)</extra>"))
                fig.add_trace(go.Scatter(
                    x=[next_wk], y=[med_price], mode="markers",
                    marker=dict(color=DOWN_GREEN, size=12,
                                line=dict(color="#FFFFFF", width=2),
                                symbol="diamond"),
                    name="Best prediction (p50)",
                    hovertemplate="%{x|%d %b %Y}<br>Rs %{y:,.2f}"
                                  "<extra>Best prediction (p50)</extra>"))
                x_max = next_wk + pd.Timedelta(weeks=2)
                title = (f"<span style='color:#1F2A27;font-weight:600;"
                         f"font-size:14px'>Weekly price — {row['item']}</span>")
            else:
                x_max = last_wk + pd.Timedelta(weeks=2)
                title = ("<span style='color:#7A7F7C;font-weight:600;"
                         f"font-size:14px'>Weekly price — {row['item']}<br>"
                         "Not enough data - monitoring only</span>")
            fig.update_layout(
                height=340,
                margin=dict(l=16, r=24, t=18 if title is None else 30, b=16),
                title=dict(text=title, font=dict(size=14)) if title else None,
                plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
                hovermode="x unified",
                hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="#DDE5E1",
                                font=dict(color="#1F2A27", size=13)),
                showlegend=False,
                xaxis=dict(range=[hist["week"].iloc[0] - pd.Timedelta(days=3),
                                  x_max],
                           showgrid=False, zeroline=False,
                           linecolor="#DDE5E1", tickformat="%d %b",
                           tickfont=dict(color=MUTED, size=11)),
                yaxis=dict(range=[0, axis_max * 1.08],
                           gridcolor="#EEF2F0", zeroline=False,
                           tickprefix="Rs ",
                           tickfont=dict(color=MUTED, size=11),
                           tickformat=",.0f"))
            st.plotly_chart(fig, config={"displayModeBar": False},
                            alt="Weekly price with ML forecast band")

    # ---------------- why this alert card
    with right:
        with st.container(border=True):
            st.subheader("Why this alert (selected row)")
            if row["monitoring"]:
                st.markdown("**Status: not enough data - monitoring only**")
                st.markdown(
                    f"Requires at least {al.MIN_HISTORY} weeks of historical "
                    f"observations to establish a baseline z-score. "
                    f"Currently tracking: **{row['weeks']} weeks**. "
                    f"Predictive alerts are suppressed to prevent false "
                    f"signals.")
                st.caption("The raw weekly price chart on the left shows "
                           "everything observed so far.")
            else:
                st.markdown(
                    f"**ML spike probability:** **{al.proba_label(row['spike_prob'])}** "
                    f"(alert threshold {row['threshold']*100:.0f}%).", unsafe_allow_html=False)
                st.markdown(
                    f"**Statistical anomaly:** **{ANOMALY_LABELS.get(row['flag'], 'None')}**.")
                st.markdown(
                    f"**Model expects next-week change:** "
                    f"**{al.move_label(row['pred_q50'] * 100.0)}** "
                    f"(p10..p90 band: "
                    f"{al.move_label(row['pred_q10'] * 100.0)} .. "
                    f"{al.move_label(row['pred_q90'] * 100.0)}; "
                    f"naive baseline = no change).")
                diffs = comm_series["price"].diff().dropna()
                streak = 0
                for v in diffs.iloc[::-1]:
                    if v > 0:
                        streak += 1
                    else:
                        break
                st.markdown(
                    f"**Momentum:** {streak} consecutive weekly "
                    f"{'increase' if streak == 1 else 'increases'} so far.")
                st.markdown(
                    f"**History:** {row['weeks']} weeks of data. "
                    f"Spikes are rare (~5% of weeks) - probabilities are "
                    f"calibrated on a chronological holdout, not on price levels.")
                src = dt.source_files(dy).get(row["item"], "")
                with st.container():
                    src_txt = (f"the source report ({src})" if src
                               else "the source report")
                    st.markdown(
                        f"<div class='next-step'><b>Next step:</b> confirm this "
                        f"risk against {src_txt} and review trader margins / "
                        f"supply costs for <b>{row['item']}</b> with your "
                        f"field team.</div>",
                        unsafe_allow_html=True)
        st.markdown("")

# ------------------------------------------------------------- footer
st.markdown(
    "<div class='cb-footer'>"
    "<strong>Powered By Co-Boost Engine</strong><br>"
    "<span>Naive persistence baseline · ML spike classifier · "
    "Quantile forecast range · Anomaly detector</span>"
    "</div>",
    unsafe_allow_html=True)
