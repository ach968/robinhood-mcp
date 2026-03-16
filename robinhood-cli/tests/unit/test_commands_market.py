from robinhood_core.models import Quote


def test_quote_to_row_positive_change():
    from robinhood_cli.commands.market import _quote_to_row
    q = Quote(
        symbol="AAPL",
        last_price=213.42,
        timestamp="2026-01-01T00:00:00Z",
        previous_close=211.58,
        change_percent=0.87,
    )
    row = _quote_to_row(q)
    assert row[0] == "AAPL"
    assert "$213.42" in row[1]


def test_quote_to_row_none_change():
    from robinhood_cli.commands.market import _quote_to_row
    q = Quote(
        symbol="TSLA",
        last_price=248.11,
        timestamp="2026-01-01T00:00:00Z",
    )
    row = _quote_to_row(q)
    assert row[0] == "TSLA"
