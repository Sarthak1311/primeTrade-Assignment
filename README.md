# Trader Performance vs. Bitcoin Market Sentiment

Analysis of how trader behavior and performance on Hyperliquid relate to Bitcoin
market sentiment, using the [Fear & Greed Index](https://alternative.me/crypto/fear-and-greed-index/).

## Overview

This project merges two datasets:

1. **Hyperliquid historical trades** — 211K+ individual executions (account, coin,
   execution price, size, side, direction, closed PnL, fees, timestamp).
2. **Bitcoin Fear & Greed Index** — daily sentiment classification
   (Extreme Fear → Extreme Greed) with a 0–100 index value.

The two are joined on calendar date to study whether win rate, profitability,
trading volume, and risk events (liquidations / auto-deleveraging) differ across
sentiment regimes.

**Full write-up:** [`reports/Trader_Sentiment_Analysis_Report.docx`](reports/Trader_Sentiment_Analysis_Report.docx)

## Key findings

| Sentiment | Win Rate | Avg PnL / Close | Avg Daily Volume |
|---|---|---|---|
| Extreme Greed | 89.2% | $130.21 | $1.09M |
| Fear | 87.3% | $112.63 | $5.31M |
| Neutral | 82.4% | $71.20 | $2.69M |
| Greed | 76.9% | $85.40 | $1.50M |
| Extreme Fear | 76.2% | $71.03 | $8.18M |

- Win rate is highest at sentiment **extremes** (Extreme Greed, Fear), not
  symmetric between fear and greed.
- Trading **activity spikes 5–7x during Fear/Extreme Fear** vs. Greed, even
  though win rate is lower there — consistent with panic-driven churn.
- **All observed liquidation / auto-deleveraging events occurred on Greed days**,
  suggesting overleveraging builds up during optimistic (not fearful) markets.
- Coin- and account-level behavior varies substantially — sentiment is a useful
  risk-sizing overlay, not a standalone directional signal.

See the full report for methodology notes, limitations, and strategic
recommendations.

## Repo structure

```
.
├── data/                          # Raw input CSVs
│   ├── historical_data.csv
│   └── fear_greed_index.csv
├── src/
│   ├── 01_data_prep.py            # Merge trades with sentiment by date
│   ├── 02_analysis.py             # Win rate, PnL, volume, risk-event breakdowns
│   └── 03_charts.py               # Generates all report charts
├── outputs/
│   ├── merged_trades_with_sentiment.csv
│   ├── daily.csv
│   └── charts/                    # PNG charts used in the report
├── reports/
│   └── Trader_Sentiment_Analysis_Report.docx
├── requirements.txt
└── README.md
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

Run the pipeline in order from the repo root:

```bash
python src/01_data_prep.py      # -> outputs/merged_trades_with_sentiment.csv
python src/02_analysis.py       # prints summary tables, -> outputs/daily.csv
python src/03_charts.py         # -> outputs/charts/*.png
```

## Data sources

- Hyperliquid historical trade data (provided as part of the assignment)
- [Bitcoin Fear & Greed Index](https://alternative.me/crypto/fear-and-greed-index/)

## Limitations

- Only 32 accounts are represented; account-level findings are illustrative,
  not statistically generalizable.
- Sentiment is daily-resolution and matched by calendar date only — it doesn't
  capture intraday sentiment shifts.
- Correlational, not causal — the analysis shows association between sentiment
  and trading behavior, not a causal mechanism.
