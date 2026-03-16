---
name: rh-cli
description: Use when the user needs Robinhood financial data - stock prices, portfolio info, options chains, order history, watchlists, news, or fundamentals
---

# Robinhood CLI (rh) Reference

Quick reference for `rh` CLI operations. Run `rh <command> --help` for full details.

## Installation

```bash
git clone https://github.com/ach968/robinhood-tools.git
cd robinhood-tools
uv tool install ./robinhood-cli
```

## Auth

```bash
rh login                    # Interactive login (prompts for username/password)
rh status                   # Show auth status and session file location
rh logout                   # Clear saved session
```

Session stored in `~/.config/robinhood/`.

## Market Data

```bash
rh price AAPL MSFT GOOGL          # Current prices for one or more symbols
rh quote TSLA                     # Detailed quote with change and % change
rh history SPY --interval day --span month   # Historical OHLCV data
rh history AAPL --interval hour --span week  # Intraday data
```

**History options:**
- `--interval`: 5minute, 10minute, hour, day, week
- `--span`: day, week, month, 3month, year, 5year
- `--bounds`: extended, trading, regular

## Portfolio

```bash
rh portfolio                 # Portfolio summary (equity, cash, buying power)
rh positions                 # Open stock positions with unrealized P/L
rh positions AAPL TSLA       # Filter by specific symbols
```

## Options

```bash
rh options-chain SPY                           # All options for symbol
rh options-chain SPY --expiry 2026-06-20       # Filter by expiration
rh options-chain SPY --type call               # Calls only (or put)
rh options-chain SPY --strike 450              # Full Greeks + bid/ask
rh options-positions                           # Open options positions
```

## Orders

```bash
rh orders                              # All order history
rh orders --type stock                 # Stock orders only
rh orders --type option                # Option orders only
rh orders --type crypto                # Crypto orders only
rh orders --symbol AAPL                # Filter by symbol
rh orders --since 2026-03-01           # Orders since date
```

## Watchlists, News, Fundamentals

```bash
rh watchlists                # List all watchlists with symbols
rh news NVDA                 # Latest news for a symbol
rh fundamentals AMD          # Company fundamentals (P/E, market cap, 52-week range)
```

## JSON Output

All commands support `--json` for raw JSON output:

```bash
rh price AAPL --json         # Raw quote data as JSON
rh portfolio --json          # Portfolio summary as JSON
rh options-chain SPY --json  # Full options chain as JSON
```

## Common Patterns

### Check portfolio and top holdings
```bash
rh portfolio
rh positions
```

### Research a stock before trading
```bash
rh quote AAPL
rh fundamentals AAPL
rh news AAPL
rh history AAPL --interval day --span month
```

### Find options for a specific expiration
```bash
rh options-chain SPY --expiry 2026-06-20 --type call
```

### Review recent trading activity
```bash
rh orders --since 2026-03-01
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| "Not logged in" error | Run `rh login` first |
| Session expired | Run `rh login` again to re-authenticate |
| No data returned | Market may be closed; try `--bounds extended` for after-hours |
| Too many options contracts | Use `--expiry` and `--type` to filter |
| Options missing Greeks | Add `--strike <price>` to fetch full details |

## Notes

- All tools are **read-only** — cannot place orders or modify account
- Uses unofficial [robin-stocks](https://github.com/jmfernandes/robin_stocks) API
- Rate limiting may occur with frequent requests
