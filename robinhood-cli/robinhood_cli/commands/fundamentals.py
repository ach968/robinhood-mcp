import asyncio
from typing import Annotated

import typer
from rich.panel import Panel
from rich.table import Table

from robinhood_core.services.fundamentals import FundamentalsService
from robinhood_cli.auth import get_client
from robinhood_cli.output import console, format_currency, print_json


def _fundamentals_rows(f) -> list:
    def fmt_large(v):
        if v is None:
            return "—"
        if v >= 1_000_000_000_000:
            return f"${v / 1_000_000_000_000:.2f}T"
        if v >= 1_000_000_000:
            return f"${v / 1_000_000_000:.2f}B"
        if v >= 1_000_000:
            return f"${v / 1_000_000:.2f}M"
        return format_currency(v)

    return [
        ["Market Cap", fmt_large(f.market_cap)],
        ["P/E Ratio", f"{f.pe_ratio:.2f}" if f.pe_ratio is not None else "—"],
        ["Dividend Yield", f"{f.dividend_yield:.2%}" if f.dividend_yield is not None else "—"],
        ["52-Week High", format_currency(f.week_52_high)],
        ["52-Week Low", format_currency(f.week_52_low)],
    ]


def fundamentals_command(
    symbol: Annotated[str, typer.Argument(help="Ticker symbol")],
    json_output: Annotated[bool, typer.Option("--json", help="Output raw JSON")] = False,
) -> None:
    """Company fundamentals (P/E, market cap, etc.)."""
    client = get_client()
    svc = FundamentalsService(client)
    f = asyncio.run(asyncio.to_thread(svc.get_fundamentals, symbol))

    if json_output:
        print_json(f.model_dump())
        return

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Field", style="bold")
    table.add_column("Value", justify="right")

    for row in _fundamentals_rows(f):
        table.add_row(*row)

    console.print(Panel(table, title=f"{symbol} Fundamentals", expand=False))


COMMANDS = [
    (fundamentals_command, "fundamentals", "Company fundamentals (P/E, market cap, etc.)"),
]
