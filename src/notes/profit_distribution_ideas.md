High‑Octane Portfolio Allocation Plan

Goal

Grow an initial $1,000 into a balanced crypto portfolio. We use an aggressive trading bucket to generate gains and automatically divert part of each sale to two long‑term buckets.

Buckets and their roles

Bucket

Purpose

Funds added

Funds removed

High‑Octane (HO)

Short‑term, high‑risk trades in spot markets only.

• Initial $1,000 seed• Every new $1,000 added each month

A percentage of each sale is routed to the other buckets (see distribution levels).

DCA Bucket

Long‑term buy‑and‑stake of BTC, ETH, SOL, and SUI.

50 % of each HO distribution

Never sells.

Rebalance Bucket

Diversified basket of coins reweighted daily.

50 % of each HO distribution

Only internal reweights.

Distribution levels

When HO closes a position, we look at its equity before the sale and send the stated percentage of the sale’s cash total to the other buckets.

HO equity before sale

% of sale redirected

Example (sell $5,000)

< $20 k

0 %

$5,000 stays in HO

$20 k – < $30 k

20 %

$1,000 goes out → $500 DCA / $500 Rebalance

$30 k – < $40 k

30 %

$1,500 goes out → $750 each

…

…

…

≥ $100 k

100 %

$5,000 goes out → $2,500 each

Money‑flow logic (pseudo‑code)

on_sale(trade_value):
    tier          = floor(HO_equity_pre_sale / 10_000)   # 0‑9
    dist_pct      = min(tier * 10, 100)
    dist_cash     = trade_value * dist_pct / 100

    send(dist_cash / 2, DCA)
    send(dist_cash / 2, REBAL)
    HO_cash      += trade_value - dist_cash

Operating schedule

HO distributions – executed immediately at each trade close.

Rebalance bucket – reweights once per day (method still to choose).

DCA buys – can run right after each distribution or be batched monthly.

Decisions still open

DCA buy timing – after every distribution vs. monthly batch.

Rebalance method and coin list – equal‑weight, volatility parity, etc.

Bot engines – Freqtrade configurations vs. Jesse code for each bucket.

Account setup – separate exchange sub‑accounts vs. one account with internal ledger.

Last updated: 19 Apr 2025