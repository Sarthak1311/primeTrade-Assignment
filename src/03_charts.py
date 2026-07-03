"""
03_charts.py

Generates the visualizations used in the report:
    1. Win rate & avg PnL per closed trade, by sentiment
    2. Avg daily volume & avg daily PnL, by sentiment
    3. 7-day rolling total daily realized PnL time series
    4. Median trade size by sentiment
    5. Calendar-day counts by sentiment regime

Usage:
    python src/03_charts.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "outputs"
CHART_DIR = OUT_DIR / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.size"] = 11
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False

SENT_ORDER = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]
COLORS = {
    "Extreme Fear": "#8B0000",
    "Fear": "#E06666",
    "Neutral": "#B7B7B7",
    "Greed": "#93C47D",
    "Extreme Greed": "#274E13",
}
BAR_COLORS = [COLORS[s] for s in SENT_ORDER]


def main():
    df = pd.read_csv(OUT_DIR / "merged_trades_with_sentiment.csv", parse_dates=["date"])
    daily = pd.read_csv(OUT_DIR / "daily.csv", parse_dates=["date"])
    fg = pd.read_csv(DATA_DIR / "fear_greed_index.csv")
    fg["date"] = pd.to_datetime(fg["date"])

    # --- Chart 1: Win rate & avg PnL per close ---
    closes = df[df["Closed PnL"] != 0]
    win = closes.groupby("sentiment").apply(lambda x: (x["Closed PnL"] > 0).mean(), include_groups=False).reindex(SENT_ORDER)
    avgpnl = closes.groupby("sentiment")["Closed PnL"].mean().reindex(SENT_ORDER)

    fig, ax1 = plt.subplots(figsize=(9, 5))
    bars = ax1.bar(SENT_ORDER, win.values * 100, color=BAR_COLORS, alpha=0.85)
    ax1.set_ylabel("Win rate (%)")
    ax1.set_ylim(0, 100)
    for b, v in zip(bars, win.values):
        ax1.text(b.get_x() + b.get_width() / 2, v * 100 + 1.5, f"{v*100:.1f}%", ha="center", fontsize=10)
    ax2 = ax1.twinx()
    ax2.plot(SENT_ORDER, avgpnl.values, color="black", marker="o", linewidth=2, label="Avg PnL per close ($)")
    ax2.set_ylabel("Avg Closed PnL per trade ($)")
    ax1.set_title("Win Rate & Average PnL per Closed Trade, by Market Sentiment")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "chart1_winrate_pnl.png", dpi=150)
    plt.close(fig)

    # --- Chart 2: Avg daily volume & PnL ---
    daily_by_sent = daily.groupby("sentiment").agg(
        avg_daily_pnl=("daily_pnl", "mean"), avg_daily_volume=("daily_volume", "mean")
    ).reindex(SENT_ORDER)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    axes[0].bar(SENT_ORDER, daily_by_sent["avg_daily_volume"] / 1e6, color=BAR_COLORS, alpha=0.85)
    axes[0].set_title("Avg Daily Trading Volume ($M)")
    axes[0].set_ylabel("$ Millions")
    axes[0].tick_params(axis="x", rotation=25)

    axes[1].bar(SENT_ORDER, daily_by_sent["avg_daily_pnl"] / 1000, color=BAR_COLORS, alpha=0.85)
    axes[1].set_title("Avg Daily Realized PnL ($K)")
    axes[1].set_ylabel("$ Thousands")
    axes[1].tick_params(axis="x", rotation=25)
    fig.suptitle("Trading Activity & Profitability by Sentiment Regime")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "chart2_volume_pnl.png", dpi=150)
    plt.close(fig)

    # --- Chart 3: Daily PnL time series ---
    daily_sorted = daily.groupby("date").agg(daily_pnl=("daily_pnl", "sum")).reset_index().sort_values("date")
    fig, ax = plt.subplots(figsize=(13, 5))
    ax.plot(daily_sorted["date"], daily_sorted["daily_pnl"].rolling(7, min_periods=1).mean(), color="#1155cc", linewidth=1.8)
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_title("7-Day Rolling Average of Total Daily Realized PnL")
    ax.set_ylabel("Realized PnL ($)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.tight_layout()
    fig.savefig(CHART_DIR / "chart3_pnl_timeseries.png", dpi=150)
    plt.close(fig)

    # --- Chart 4: Median trade size ---
    size_stats = df.groupby("sentiment")["Size USD"].median().reindex(SENT_ORDER)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(SENT_ORDER, size_stats.values, color=BAR_COLORS, alpha=0.85)
    ax.set_title("Median Trade Size (USD) by Sentiment")
    ax.set_ylabel("Median Size USD")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(CHART_DIR / "chart4_tradesize.png", dpi=150)
    plt.close(fig)

    # --- Chart 5: Calendar-day counts by regime ---
    day_counts = (
        fg.set_index("date")
        .loc[daily["date"].min():daily["date"].max()]["classification"]
        .value_counts()
        .reindex(SENT_ORDER)
    )
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(SENT_ORDER, day_counts.values, color=BAR_COLORS, alpha=0.85)
    ax.set_title("Number of Calendar Days by Sentiment Regime (sample window)")
    ax.set_ylabel("Days")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(CHART_DIR / "chart5_daycounts.png", dpi=150)
    plt.close(fig)

    print(f"Charts saved -> {CHART_DIR}")


if __name__ == "__main__":
    main()
