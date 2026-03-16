import asyncio
from typing import Annotated, Optional

import typer
from rich.table import Table

from robinhood_core.services.orders import OrdersService
from robinhood_cli.auth import get_client
from robinhood_cli.output import console, format_currency, print_json, POSITIVE, NEGATIVE


def orders_command(
    order_type: Annotated[str, typer.Option("--type", help="stock, option, crypto, or all")] = "all",
    symbol: Annotated[Optional[str], typer.Option("--symbol", help="Filter by symbol")] = None,
    since: Annotated[Optional[str], typer.Option("--since", help="Start date YYYY-MM-DD")] = None,
    json_output: Annotated[bool, typer.Option("--json", help="Output raw JSON")] = False,
) -> None:
    """Order history (stock, option, crypto)."""
    client = get_client()
    svc = OrdersService(client)
    history = asyncio.run(asyncio.to_thread(svc.get_order_history, order_type, symbol, since))

    if json_output:
        print_json(history.model_dump())
        return

    if history.stock_orders:
        table = Table(show_header=True, header_style="bold", title="Stock Orders")
        table.add_column("Date")
        table.add_column("Symbol")
        table.add_column("Side")
        table.add_column("State")
        table.add_column("Qty", justify="right")
        table.add_column("Avg Price", justify="right")

        for o in history.stock_orders:
            date = (o.created_at or "")[:10]
            side_color = "green" if o.side == "buy" else "red"
            table.add_row(
                date,
                o.symbol or "—",
                f"[{side_color}]{o.side or '—'}[/{side_color}]",
                o.state or "—",
                f"{o.cumulative_quantity:.4g}" if o.cumulative_quantity else "—",
                format_currency(o.average_price),
            )
        console.print(table)

    if history.option_orders:
        table = Table(show_header=True, header_style="bold", title="Option Orders")
        table.add_column("Date")
        table.add_column("Symbol")
        table.add_column("Direction")
        table.add_column("State")
        table.add_column("Qty", justify="right")
        table.add_column("Premium", justify="right")

        for o in history.option_orders:
            date = (o.created_at or "")[:10]
            table.add_row(
                date,
                o.chain_symbol or "—",
                o.direction or "—",
                o.state or "—",
                f"{o.processed_quantity:.4g}" if o.processed_quantity else "—",
                format_currency(o.processed_premium),
            )
        console.print(table)

    if history.crypto_orders:
        table = Table(show_header=True, header_style="bold", title="Crypto Orders")
        table.add_column("Date")
        table.add_column("Side")
        table.add_column("State")
        table.add_column("Qty", justify="right")
        table.add_column("Avg Price", justify="right")

        for o in history.crypto_orders:
            date = (o.created_at or "")[:10]
            side_color = "green" if o.side == "buy" else "red"
            table.add_row(
                date,
                f"[{side_color}]{o.side or '—'}[/{side_color}]",
                o.state or "—",
                f"{o.cumulative_quantity:.4g}" if o.cumulative_quantity else "—",
                format_currency(o.average_price),
            )
        console.print(table)

    total = len(history.stock_orders) + len(history.option_orders) + len(history.crypto_orders)
    if total == 0:
        console.print("No orders found.")


COMMANDS = [
    (orders_command, "orders", "Order history (stock, option, crypto)"),
]
