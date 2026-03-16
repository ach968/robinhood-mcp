# Robinhood CLI Design

**Date:** 2026-03-16  
**Status:** Approved

---

## Overview

Port all `robinhood-mcp` functionality into a new `robinhood-cli` package (`rh` command), backed by a shared `robinhood-core` library extracted from the existing MCP server. Update `robinhood-mcp` to depend on `robinhood-core`. Rewrite the root README to document the full monorepo.

---

## Package Architecture

```
robinhood-mcp/                  ← repo root
├── docs/plans/                 ← design documents
├── robinhood-core/             ← NEW shared library
│   ├── pyproject.toml
│   └── robinhood_core/
│       ├── __init__.py
│       ├── client.py           ← RobinhoodClient (moved from MCP)
│       ├── errors.py           ← AuthRequiredError, etc. (moved)
│       ├── models/             ← all Pydantic models (moved)
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── fundamentals.py
│       │   ├── market.py
│       │   ├── news.py
│       │   ├── options.py
│       │   ├── orders.py
│       │   ├── portfolio.py
│       │   └── watchlists.py
│       └── services/           ← all service classes (moved)
│           ├── __init__.py
│           ├── fundamentals.py
│           ├── market_data.py
│           ├── news.py
│           ├── options.py
│           ├── orders.py
│           ├── portfolio.py
│           └── watchlists.py
│
├── robinhood-mcp/              ← existing MCP server (import updates only)
│   ├── pyproject.toml          ← adds robinhood-core as local path dep
│   └── robin_stocks_mcp/
│       └── server.py           ← updated imports from robinhood_core.*
│
├── robinhood-cli/              ← NEW CLI tool
│   ├── pyproject.toml
│   └── robinhood_cli/
│       ├── __init__.py
│       ├── main.py             ← Typer app, registers all commands
│       ├── auth.py             ← session load/save helpers
│       ├── output.py           ← shared Rich console, --json flag logic
│       └── commands/
│           ├── __init__.py
│           ├── auth.py         ← rh login / rh logout / rh status
│           ├── market.py       ← rh price / rh quote / rh history
│           ├── options.py      ← rh options-chain / rh options-positions
│           ├── portfolio.py    ← rh portfolio / rh positions
│           ├── watchlists.py   ← rh watchlists
│           ├── news.py         ← rh news
│           ├── fundamentals.py ← rh fundamentals
│           └── orders.py       ← rh orders
│
└── README.md                   ← rewritten: monorepo overview + quickstart for both apps
```

---

## CLI Commands

All commands are flat subcommands under `rh`. The `--json` flag is available on every data command.

### Auth
| Command | Description |
|---|---|
| `rh login` | Interactive prompt for username/password/MFA; saves session to `~/.config/robinhood/session` |
| `rh logout` | Deletes the saved session file |
| `rh status` | Shows auth status and session file path |

### Market Data
| Command | Description |
|---|---|
| `rh price AAPL TSLA` | Current prices for one or more symbols |
| `rh quote AAPL TSLA` | Detailed quote: price, change, % change |
| `rh history AAPL [--interval hour] [--span week] [--bounds regular]` | Historical OHLCV table |

### Portfolio
| Command | Description |
|---|---|
| `rh portfolio` | Summary: equity, cash, buying power, day change |
| `rh positions [AAPL TSLA]` | Open stock positions, optional symbol filter |

### Options
| Command | Description |
|---|---|
| `rh options-chain AAPL [--expiry 2025-06-20] [--type call] [--strike 150.00]` | Options chain (tier 1: browse; tier 2: full Greeks when --strike provided) |
| `rh options-positions` | All open options positions |

### Other
| Command | Description |
|---|---|
| `rh watchlists` | All watchlists with their symbols |
| `rh news AAPL` | Latest news articles for a symbol |
| `rh fundamentals AAPL` | Market cap, P/E, dividend yield, 52-week range |
| `rh orders [--type stock\|option\|crypto\|all] [--symbol AAPL] [--since 2025-01-01]` | Order history |

---

## Output Formatting

### Human-readable (default)
- Rich tables with aligned columns
- Positive values (gains, green), negative values (losses, red)
- Prices formatted as `$213.42`
- Dates formatted as `Jun 20, 2025`
- `rh portfolio` uses a key/value panel layout
- `rh options-chain` renders a strike ladder table

### JSON mode (`--json`)
- Pretty-printed JSON, identical schema to MCP tool responses
- Suitable for piping to `jq` or scripting

---

## Authentication Flow

`rh login` prompts interactively:
1. Username (visible input)
2. Password (hidden input via `typer.prompt(..., hide_input=True)`)
3. MFA code if required

Session is saved to `~/.config/robinhood/session` (same path the MCP supports via `RH_SESSION_PATH`). All other commands load that session silently. No credentials on the command line after login.

---

## Project Config

### `robinhood-core/pyproject.toml`
```toml
[project]
name = "robinhood-core"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "robin-stocks>=3.0.0",
    "pydantic>=2.0.0",
    "requests>=2.25.0",
]
```

### `robinhood-mcp/pyproject.toml` (updated)
```toml
[project]
dependencies = ["mcp>=1.0.0", "robinhood-core"]

[tool.uv.sources]
robinhood-core = { path = "../robinhood-core", editable = true }
```

### `robinhood-cli/pyproject.toml`
```toml
[project]
name = "robinhood-cli"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "robinhood-core",
    "typer>=0.12.0",
    "rich>=13.0.0",
]

[project.scripts]
rh = "robinhood_cli.main:app"

[tool.uv.sources]
robinhood-core = { path = "../robinhood-core", editable = true }
```

---

## Testing Strategy

- **`robinhood-core/tests/`** — inherits existing unit tests from `robinhood-mcp` (models, services, client). No live API calls.
- **`robinhood-cli/tests/`** — unit tests for formatters (table rendering) and command wiring (mock services). No live API calls.
- **`robinhood-mcp/tests/`** — existing tests updated to import from `robinhood_core.*` instead of `robin_stocks_mcp.*`.

---

## Implementation Sequence

1. Create `robinhood-core` — move `client.py`, `errors.py`, `models/`, `services/` from MCP; set up `pyproject.toml`
2. Update `robinhood-mcp` — add core path dep, update all imports, verify existing tests still pass
3. Create `robinhood-cli` — scaffold package, wire Typer app, implement commands one group at a time
4. Rewrite root `README.md`
