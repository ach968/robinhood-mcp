from typing import Annotated, List, Optional

import typer
from rich.panel import Panel
from rich.table import Table

from robinhood_core.services.portfolio import PortfolioService
from robinhood_cli.auth import get_client
from robinhood_cli.output import (
    console,
    format_currency,
    format_change,
    print_json,
    POSITIVE,
    NEGATIVE,
)


def _position_to_row(p) -> list:
    pl_str = format_change(p.unrealized_pl)
    return [
        p.symbol,
        f"{p.quantity:.4g}",
        format_currency(p.average_cost),
        format_currency(p.market_value),
        pl_str,
        p.unrealized_pl,
    ]


def portfolio_command(
    json_output: Annotated[bool, typer.Option("--json", help="Output raw JSON")] = False,
) -> None:
    """Portfolio summary: equity, cash, buying power."""
    client = get_client()
    svc = PortfolioService(client)
    summary = svc.get_portfolio_summary()

    if json_output:
        print_json(summary.model_dump())
        return

    day_change_str = format_change(summary.day_change)
    day_change_color = "green" if (summary.day_change or 0) >= 0 else "red"

    lines = [
        f"[bold]Equity[/bold]        {format_currency(summary.equity)}",
        f"[bold]Cash[/bold]          {format_currency(summary.cash)}",
        f"[bold]Buying Power[/bold]  {format_currency(summary.buying_power)}",
        f"[bold]Day Change[/bold]    [{day_change_color}]{day_change_str}[/{day_change_color}]",
    ]
    console.print(Panel("\n".join(lines), title="Portfolio Summary", expand=False))


def positions_command(
    symbols: Annotated[Optional[List[str]], typer.Argument(help="Filter by symbols (optional)")] = None,
    json_output: Annotated[bool, typer.Option("--json", help="Output raw JSON")] = False,
) -> None:
    """Open stock positions."""
    client = get_client()
    svc = PortfolioService(client)
    positions = svc.get_positions(symbols)

    if json_output:
        print_json([p.model_dump() for p in positions])
        return

    if not positions:
        console.print("No open positions.")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("Symbol")
    table.add_column("Qty", justify="right")
    table.add_column("Avg Cost", justify="right")
    table.add_column("Market Value", justify="right")
    table.add_column("Unrealized P/L", justify="right")

    for p in positions:
        row = _position_to_row(p)
        pl_val = row[5]
        style = POSITIVE if (pl_val or 0) >= 0 else NEGATIVE
        table.add_row(row[0], row[1], row[2], row[3], row[4], style=style)

    console.print(table)


COMMANDS = [
    (portfolio_command, "portfolio", "Portfolio summary: equity, cash, buying power"),
    (positions_command, "positions", "Open stock positions"),
]
