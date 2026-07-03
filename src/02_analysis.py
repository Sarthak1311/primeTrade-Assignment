"""
02_analysis.py

Computes win rate, PnL, volume, leverage/side-mix, coin- and account-level
breakdowns of trader performance by market sentiment regime.

Usage:
    python src/02_analysis.py
"""
import pandas as pd
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
MERGED_PATH = OUT_DIR / "merged_trades_with_sentiment.csv"

SENT_ORDER = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]


def main():
    if not MERGED_PATH.exists():
        raise FileNotFoundError(
            f"{MERGED_PATH} not found. Run `python src/01_data_prep.py` first."
        )

    df = pd.read_csv(MERGED_PATH, parse_dates=["date"])
    df["is_close_event"] = df["Closed PnL"] != 0

    print("=" * 70)
    print("1. TRADE ROWS BY SENTIMENT")
    print("=" * 70)
    print(df["sentiment"].value_counts().reindex(SENT_ORDER))

    print("=" * 70)
    print("2. CLOSED PnL BY SENTIMENT")
    print("=" * 70)
    print(df.groupby("sentiment")["Closed PnL"].agg(["sum", "mean", "median", "count"]).reindex(SENT_ORDER))

    print("=" * 70)
    print("3. WIN RATE ON CLOSE EVENTS BY SENTIMENT")
    print("=" * 70)
    closes = df[df["is_close_event"]]
    win = closes.groupby("sentiment").apply(lambda x: (x["Closed PnL"] > 0).mean(), include_groups=False)
    avgpnl = closes.groupby("sentiment")["Closed PnL"].mean()
    cnt = closes.groupby("sentiment")["Closed PnL"].count()
    summary = pd.DataFrame({"win_rate": win, "avg_pnl_per_close": avgpnl, "n_closes": cnt}).reindex(SENT_ORDER)
    print(summary)

    print("=" * 70)
    print("4. TRADE SIZE (USD) BY SENTIMENT")
    print("=" * 70)
    print(df.groupby("sentiment")["Size USD"].agg(["mean", "median", "sum"]).reindex(SENT_ORDER))

    print("=" * 70)
    print("5. BUY vs SELL MIX BY SENTIMENT")
    print("=" * 70)
    print(df.groupby("sentiment")["Side"].value_counts(normalize=True).unstack().reindex(SENT_ORDER))

    print("=" * 70)
    print("6. DAILY AGGREGATES (volume, PnL, trade count) BY SENTIMENT")
    print("=" * 70)
    daily = df.groupby(["date", "sentiment"]).agg(
        daily_pnl=("Closed PnL", "sum"),
        daily_volume=("Size USD", "sum"),
        n_trades=("Closed PnL", "count"),
    ).reset_index()
    daily_by_sent = daily.groupby("sentiment").agg(
        avg_daily_pnl=("daily_pnl", "mean"),
        avg_daily_volume=("daily_volume", "mean"),
        avg_trades_per_day=("n_trades", "mean"),
        n_days=("daily_pnl", "count"),
    ).reindex(SENT_ORDER)
    print(daily_by_sent)
    daily.to_csv(OUT_DIR / "daily.csv", index=False)

    print("=" * 70)
    print("7. TOP COINS (by volume): REALIZED PnL BY SENTIMENT")
    print("=" * 70)
    coin_sent = df.groupby(["Coin", "sentiment"])["Closed PnL"].sum().reset_index()
    top_coins = df.groupby("Coin")["Size USD"].sum().sort_values(ascending=False).head(8).index
    pivot = coin_sent[coin_sent["Coin"].isin(top_coins)].pivot(
        index="Coin", columns="sentiment", values="Closed PnL"
    ).fillna(0)
    print(pivot)

    print("=" * 70)
    print("8. TOP 10 ACCOUNTS (by volume): AVG PnL BY SENTIMENT BUCKET")
    print("=" * 70)
    top_accts = df.groupby("Account")["Size USD"].sum().sort_values(ascending=False).head(10).index
    acct_sent = df[df["Account"].isin(top_accts)].groupby(
        ["Account", "sentiment_bucket"]
    )["Closed PnL"].mean().unstack()
    print(acct_sent)

    print("=" * 70)
    print("9. LIQUIDATION / AUTO-DELEVERAGING EVENTS BY SENTIMENT")
    print("=" * 70)
    risk_events = df[df["Direction"].isin(["Auto-Deleveraging", "Liquidated Isolated Short"])]
    print(risk_events.groupby("sentiment")["Direction"].count())

    print("\nDone. Daily aggregates saved -> outputs/daily.csv")


if __name__ == "__main__":
    main()
