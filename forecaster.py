import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor


def _features(s: pd.Series) -> pd.DataFrame:
    df = pd.DataFrame({"y": s})
    for lag in (1, 2, 3, 6, 12):
        df[f"lag{lag}"] = df.y.shift(lag)
    df["r3"] = df.y.shift(1).pct_change(3)
    df["r12"] = df.y.shift(1).pct_change(12)
    df["month"] = df.index.month
    df["ctime"] = np.sin(2 * np.pi * df.month / 12)
    return df.drop(columns=["y", "month"])


def forecast(s: pd.Series, horizon: int = 1, fallback_weekly: bool = False) -> pd.DataFrame:
    """Next-period forecasts (monthly series -> next period = ~4 weeks ahead)."""
    hist = s.dropna()
    f = _features(hist)
    mask = f.notna().all(axis=1)
    X, y = f[mask], hist[mask.values]

    model = GradientBoostingRegressor(
        n_estimators=200, learning_rate=0.05, max_depth=3, subsample=0.9, random_state=42
    )
    # Hold-out check when enough data
    mape = None
    if len(y) >= 30:
        Xtr, ytr, Xte, yte = X.iloc[:-12], y.iloc[:-12], X.iloc[-12:], y.iloc[-12:]
        model.fit(Xtr, ytr)
        err = np.mean(np.abs((model.predict(Xte) - yte.values)) / yte.values)
        mape = float(err * 100)

    model.fit(X, y)

    cur, rows, vals = hist.copy(), [], []
    for _ in range(horizon):
        nf = _features(cur).iloc[-1:].ffill()
        nf["ctime"] = np.sin(2 * np.pi * (nf["r12"].index[-1].month - 1 + 1) / 12) if False else np.sin(2 * np.pi * ((cur.index[-1].month % 12) + 1) / 12)
        yhat = float(np.clip(model.predict(nf)[0], 0, None))
        nxt = cur.index[-1] + pd.offsets.MonthBegin(1)
        rows.append(nxt)
        vals.append(yhat)
        cur = pd.concat([cur, pd.Series([yhat], index=[nxt])])

    out = pd.DataFrame({"date": rows, "forecast": vals}).set_index("date")
    resid = y.tail(24).std() if len(y) > 6 else hist.std() * 0.1
    lo = out.forecast - 1.28 * resid
    hi = out.forecast + 1.28 * resid
    out["low"] = lo.clip(lower=0)
    out["high"] = hi
    out["mape"] = mape
    return out


def weekly_projection(s: pd.Series, next_period: pd.DataFrame) -> pd.Series:
    """Spread next-period change evenly over 4 weeks."""
    last_price = float(s.dropna().iloc[-1])
    target = float(next_period.forecast.iloc[0])
    weeks = pd.date_range(s.index[-1] + pd.Timedelta(days=7), periods=4, freq="7D")
    step = (target - last_price) / 4
    return pd.Series([last_price + step * (i + 1) for i in range(4)], index=weeks, name="weekly")
