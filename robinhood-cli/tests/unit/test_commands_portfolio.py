from robinhood_core.models import Position


def test_position_to_row():
    from robinhood_cli.commands.portfolio import _position_to_row
    p = Position(
        symbol="AAPL",
        quantity=10.0,
        average_cost=185.20,
        market_value=2134.20,
        unrealized_pl=490.00,
    )
    row = _position_to_row(p)
    assert row[0] == "AAPL"
    assert "10" in row[1]
    assert "$185.20" in row[2]
    assert "$490.00" in row[4]
