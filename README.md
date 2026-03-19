# CLK26 vs BZM26 Daily Spread Data

This repository contains daily spread data for the specific futures contracts:
- CL K 2026 (`CLK26.NYM`)
- Brent M 2026 (`BZM26.NYM`)

## Files
- `clk26_bzm26_daily_spread.csv`
- `index.html` — interactive ECharts page

## Columns
- `date`
- `clk26_close`
- `bzm26_close`
- `spread_abs_bzm26_minus_clk26`
- `spread_pct_vs_clk26`

## Notes
- Data source: Yahoo Finance chart endpoint
- This is specific-contract data, not a continuous futures series
