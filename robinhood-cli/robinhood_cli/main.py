import typer

from robinhood_cli.auth import login_command, logout_command, status_command

app = typer.Typer(
    name="rh",
    help="Robinhood CLI — market data, portfolio, options, and more.",
    no_args_is_help=True,
)

# Auth commands
app.command("login", help="Authenticate with Robinhood")(login_command)
app.command("logout", help="Clear the saved session")(logout_command)
app.command("status", help="Show authentication status")(status_command)


def _register_commands() -> None:
    from robinhood_cli.commands import (
        market,
        portfolio,
        options,
        watchlists,
        news,
        fundamentals,
        orders,
    )

    for module in (market, portfolio, options, watchlists, news, fundamentals, orders):
        for cmd_fn, name, help_text in module.COMMANDS:
            app.command(name, help=help_text)(cmd_fn)


_register_commands()

if __name__ == "__main__":
    app()
