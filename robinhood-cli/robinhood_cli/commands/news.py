import asyncio
from typing import Annotated

import typer
from rich.table import Table

from robinhood_core.services.news import NewsService
from robinhood_cli.auth import get_client
from robinhood_cli.output import console, print_json


def news_command(
    symbol: Annotated[str, typer.Argument(help="Ticker symbol")],
    json_output: Annotated[bool, typer.Option("--json", help="Output raw JSON")] = False,
) -> None:
    """Latest news for a symbol."""
    client = get_client()
    svc = NewsService(client)
    news = asyncio.run(asyncio.to_thread(svc.get_news, symbol))

    if json_output:
        print_json([n.model_dump() for n in news])
        return

    if not news:
        console.print(f"No news found for {symbol}.")
        return

    table = Table(show_header=True, header_style="bold", title=f"{symbol} News")
    table.add_column("Published")
    table.add_column("Source")
    table.add_column("Headline")

    for n in news:
        published = n.published_at[:10] if n.published_at else "—"
        table.add_row(published, n.source or "—", n.headline)

    console.print(table)


COMMANDS = [
    (news_command, "news", "Latest news for a symbol"),
]
