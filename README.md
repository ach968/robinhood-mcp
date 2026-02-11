# Robinhood MCP Server

A read-only MCP (Model Context Protocol) server wrapping the robin_stocks Robinhood API.

## Features

- **Read-only access**: Market data, options, portfolio, watchlists, news, and fundamentals
- **Normalized schemas**: Consistent, typed responses with ISO 8601 timestamps
- **Biometric-friendly auth**: Works with app-based authentication flow
- **Lazy authentication**: Authenticates on first tool call, not at startup
- **Optional session caching**: Persist sessions to disk for faster reconnects

## Installation

```bash
pip install -e ".[dev]"
```

## Configuration

Create a `.env` file:

```bash
RH_USERNAME=your_robinhood_username
RH_PASSWORD=your_robinhood_password
RH_SESSION_PATH=./.robinhood_session.json  # Optional
RH_ALLOW_MFA=0  # Set to 1 to enable MFA fallback
```

## Usage

Run the server:

```bash
robinhood-mcp
```

Or directly:

```bash
python -m robin_stocks_mcp.server
```

## Available Tools

### Market Data
- `robinhood.market.current_price` - Get current prices
- `robinhood.market.price_history` - Get historical data
- `robinhood.market.quote` - Get detailed quotes

### Options
- `robinhood.options.chain` - Get options chain

### Portfolio
- `robinhood.portfolio.summary` - Portfolio summary
- `robinhood.portfolio.positions` - Current positions

### Watchlists & News
- `robinhood.watchlists.list` - List watchlists
- `robinhood.news.latest` - Latest news

### Fundamentals
- `robinhood.fundamentals.get` - Company fundamentals

### Auth
- `robinhood.auth.status` - Check authentication status

## Authentication Flow

1. The server starts without attempting login
2. On first tool call, it tries to use a cached session (if `RH_SESSION_PATH` is set)
3. If no valid session exists, it attempts login with credentials
4. If a challenge is required and MFA is disabled, it returns an `AUTH_REQUIRED` error
5. To authenticate using the app: refresh your session in the Robinhood app, then retry

## Testing

Unit tests:
```bash
pytest tests/unit -v
```

Integration tests (requires credentials):
```bash
RH_INTEGRATION=1 pytest tests/integration -v
```

## Security Notes

- This server is read-only and cannot place orders
- Credentials are read from environment variables
- Session tokens can be cached to disk (optional)
- Sensitive values are never logged
