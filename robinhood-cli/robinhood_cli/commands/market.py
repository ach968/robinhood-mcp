from typing import Annotated, List, Optional

import typer
from rich.table import Table

from robinhood_core.services.market_data import MarketDataService
from robinhood_cli.auth import get_client
from robinhood_cli.output import (
    console,
    format_currency,
    format_change,
    format_percent,
    print_json,
    POSITIVE,
    NEGATIVE,
)


def _quote_to_row(q) -> list:
    price = format_currency(q.last_price)
    change_val = None
    if q.previous_close is not None and q.last_price is not None:
        change_val = q.last_price - q.previous_close
    change_str = format_change(change_val)
    pct_str = format_percent(q.change_percent)
    return [q.symbol, price, change_str, pct_str, change_val]


def price_command(
    symbols: Annotated[List[str], typer.Argument(help="Ticker symbols")],
    json_output: Annotated[bool, typer.Option("--json", help="Output raw JSON")] = False,
) -> None:
    """Get current prices for one or more symbols."""
    client = get_client()
    svc = MarketDataService(client)
    quotes = svc.get_current_price(symbols)

    if json_output:
        print_json([q.model_dump() for q in quotes])
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("Symbol")
    table.add_column("Price", justify="right")
    for q in quotes:
        table.add_row(q.symbol, format_currency(q.last_price))
    console.print(table)


def quote_command(
    symbols: Annotated[List[str], typer.Argument(help="Ticker symbols")],
    json_output: Annotated[bool, typer.Option("--json", help="Output raw JSON")] = False,
) -> None:
    """Detailed quote with change and % change."""
    client = get_client()
    svc = MarketDataService(client)
    quotes = svc.get_current_price(symbols)

    if json_output:
        print_json([q.model_dump() for q in quotes])
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("Symbol")
    table.add_column("Price", justify="right")
    table.add_column("Change", justify="right")
    table.add_column("% Change", justify="right")

    for q in quotes:
        row = _quote_to_row(q)
        change_val = row[4]
        style = POSITIVE if (change_val or 0) >= 0 else NEGATIVE
        table.add_row(row[0], row[1], row[2], row[3], style=style)

    console.print(table)


def history_command(
    symbol: Annotated[str, typer.Argument(help="Ticker symbol")],
    interval: Annotated[str, typer.Option(help="5minute, 10minute, hour, day, week")] = "hour",
    span: Annotated[str, typer.Option(help="day, week, month, 3month, year, 5year")] = "week",
    bounds: Annotated[str, typer.Option(help="extended, trading, regular")] = "regular",
    json_output: Annotated[bool, typer.Option("--json", help="Output raw JSON")] = False,
) -> None:
    """Historical OHLCV price data."""
    client = get_client()
    svc = MarketDataService(client)
    candles = svc.get_price_history(symbol, interval, span, bounds)

    if json_output:
        print_json([c.model_dump() for c in candles])
        return

    table = Table(show_header=True, header_style="bold", title=f"{symbol} Price History")
    table.add_column("Timestamp")
    table.add_column("Open", justify="right")
    table.add_column("High", justify="right")
    table.add_column("Low", justify="right")
    table.add_column("Close", justify="right")
    table.add_column("Volume", justify="right")

    for c in candles:
        table.add_row(
            c.timestamp[:16].replace("T", " "),
            format_currency(c.open),
            format_currency(c.high),
            format_currency(c.low),
            format_currency(c.close),
            f"{c.volume:,}" if c.volume else "—",
        )
    console.print(table)


COMMANDS = [
    (price_command, "price", "Current prices for one or more symbols"),
    (quote_command, "quote", "Detailed quote with change and % change"),
    (history_command, "history", "Historical OHLCV price data"),
]
