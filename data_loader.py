import pandas as pd

DATA_PATH = "data/colombo_prices.csv"

STAPLES = [
    "Rice (white)", "Rice (red nadu)", "Rice (long grain)", "Rice (medium grain)",
    "Wheat flour", "Sugar", "Coconut", "Eggs",
    "Meat (chicken, broiler)", "Fish (skipjack tuna)",
    "Cowpeas (whole, average)", "Lentils",
    "Potatoes (local)", "Onions (red, local)",
    "Chili (red, dry raw)", "Bananas", "Tomatoes", "Cabbage",
]


def load_prices(path: str = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    return df.sort_values(["commodity", "date"]).reset_index(drop=True)


def series(df: pd.DataFrame, commodity: str) -> pd.Series:
    s = df[df.commodity == commodity].set_index("date")["price"].sort_index()
    idx = pd.date_range(s.index.min(), s.index.max(), freq="MS")
    return s.groupby(level=0).first().reindex(idx).ffill(limit=1)
