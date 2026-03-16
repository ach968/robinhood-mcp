from robinhood_core.models import Watchlist, Fundamentals


def test_watchlist_symbols_joined():
    from robinhood_cli.commands.watchlists import _watchlist_to_rows
    w = Watchlist(id="1", name="Tech", symbols=["AAPL", "TSLA", "MSFT"])
    rows = _watchlist_to_rows(w)
    assert rows[0][0] == "Tech"
    assert "AAPL" in rows[0][1]


def test_fundamentals_pe_formatted():
    from robinhood_cli.commands.fundamentals import _fundamentals_rows
    f = Fundamentals(
        market_cap=3_000_000_000_000.0,
        pe_ratio=32.5,
        dividend_yield=0.005,
        week_52_high=260.0,
        week_52_low=164.0,
    )
    rows = _fundamentals_rows(f)
    labels = [r[0] for r in rows]
    assert "P/E Ratio" in labels
    assert "Market Cap" in labels
