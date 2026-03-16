from typing import Annotated

import typer
from rich.table import Table

from robinhood_core.services.watchlists import WatchlistsService
from robinhood_cli.auth import get_client
from robinhood_cli.output import console, print_json


def _watchlist_to_rows(w) -> list:
    return [[w.name, ", ".join(w.symbols)]]


def watchlists_command(
    json_output: Annotated[bool, typer.Option("--json", help="Output raw JSON")] = False,
) -> None:
    """List all watchlists."""
    client = get_client()
    svc = WatchlistsService(client)
    watchlists = svc.get_watchlists()

    if json_output:
        print_json([w.model_dump() for w in watchlists])
        return

    if not watchlists:
        console.print("No watchlists found.")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("Name")
    table.add_column("Symbols")

    for w in watchlists:
        for row in _watchlist_to_rows(w):
            table.add_row(*row)

    console.print(table)


COMMANDS = [
    (watchlists_command, "watchlists", "List all watchlists"),
]
