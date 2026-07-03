"""
01_data_prep.py

Merges Hyperliquid trade history with the Bitcoin Fear & Greed Index
by calendar date, and writes the merged dataset to outputs/.

Usage:
    python src/01_data_prep.py
"""
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
OUT_DIR.mkdir(exist_ok=True)


def bucket(classification: str) -> str:
    """Collapse the 5-class sentiment label into Fear / Neutral / Greed."""
    if classification in ("Fear", "Extreme Fear"):
        return "Fear"
    if classification in ("Greed", "Extreme Greed"):
        return "Greed"
    return "Neutral"


def main():
    trades = pd.read_csv(DATA_DIR / "historical_data.csv")
    fg = pd.read_csv(DATA_DIR / "fear_greed_index.csv")

    # ---- Parse dates ----
    trades["Timestamp IST"] = pd.to_datetime(trades["Timestamp IST"], format="%d-%m-%Y %H:%M")
    trades["date"] = pd.to_datetime(trades["Timestamp IST"].dt.date)

    fg["date"] = pd.to_datetime(fg["date"])
    fg_small = fg[["date", "classification", "value"]].rename(
        columns={"classification": "sentiment", "value": "fg_value"}
    )
    fg_small["sentiment_bucket"] = fg_small["sentiment"].apply(bucket)

    # ---- Merge on calendar date ----
    merged = trades.merge(fg_small, on="date", how="left")

    print(f"Rows before merge: {len(trades):,}")
    print(f"Rows after merge:  {len(merged):,}")
    print(f"Unmatched dates (no sentiment): {merged['sentiment'].isna().sum()}")

    merged.to_csv(OUT_DIR / "merged_trades_with_sentiment.csv", index=False)
    print(f"Saved -> {OUT_DIR / 'merged_trades_with_sentiment.csv'}")


if __name__ == "__main__":
    main()
