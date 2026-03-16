from robinhood_core.models import OptionContract


def test_contract_to_row_basic():
    from robinhood_cli.commands.options import _contract_to_row
    c = OptionContract(
        symbol="AAPL",
        expiration="2026-06-20",
        strike=150.0,
        type="call",
    )
    row = _contract_to_row(c)
    assert row[0] == "AAPL"
    assert "150" in row[2]
    assert row[3] == "call"
