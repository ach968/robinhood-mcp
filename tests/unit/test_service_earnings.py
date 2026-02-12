# tests/unit/test_service_earnings.py
import pytest
from unittest.mock import MagicMock, patch
from robin_stocks_mcp.services.earnings import EarningsService
from robin_stocks_mcp.robinhood.client import RobinhoodClient
from robin_stocks_mcp.robinhood.errors import InvalidArgumentError, RobinhoodAPIError


def test_service_initialization():
    mock_client = MagicMock(spec=RobinhoodClient)
    service = EarningsService(mock_client)
    assert service.client == mock_client


def test_get_earnings_requires_symbol():
    mock_client = MagicMock(spec=RobinhoodClient)
    service = EarningsService(mock_client)

    with pytest.raises(InvalidArgumentError, match="Symbol is required"):
        service.get_earnings("")


def test_get_earnings_success():
    mock_client = MagicMock(spec=RobinhoodClient)
    service = EarningsService(mock_client)

    mock_earnings_data = [
        {
            "symbol": "AAPL",
            "instrument": "https://api.robinhood.com/instruments/abc123/",
            "year": 2025,
            "quarter": 1,
            "eps": {"estimate": "1.50", "actual": "1.65"},
            "report": {"date": "2025-01-30", "timing": "am", "verified": True},
            "call": {
                "datetime": "2025-01-30T17:00:00Z",
                "broadcast_url": "https://example.com/broadcast",
                "replay_url": "https://example.com/replay",
            },
        },
        {
            "symbol": "AAPL",
            "instrument": "https://api.robinhood.com/instruments/abc123/",
            "year": 2024,
            "quarter": 4,
            "eps": {"estimate": "2.10", "actual": "2.18"},
            "report": {"date": "2024-10-31", "timing": "pm", "verified": True},
            "call": {
                "datetime": "2024-10-31T21:00:00Z",
                "broadcast_url": None,
                "replay_url": None,
            },
        },
    ]

    with patch("robin_stocks_mcp.services.earnings.rh") as mock_rh:
        mock_rh.get_earnings.return_value = mock_earnings_data

        earnings = service.get_earnings("AAPL")

        assert len(earnings) == 2

        # Check first quarter
        assert earnings[0].symbol == "AAPL"
        assert earnings[0].year == 2025
        assert earnings[0].quarter == 1
        assert earnings[0].eps.estimate == 1.50
        assert earnings[0].eps.actual == 1.65
        assert earnings[0].report.date == "2025-01-30"
        assert earnings[0].report.timing == "am"
        assert earnings[0].report.verified is True
        assert earnings[0].call.datetime == "2025-01-30T17:00:00Z"
        assert earnings[0].call.broadcast_url == "https://example.com/broadcast"

        # Check second quarter
        assert earnings[1].year == 2024
        assert earnings[1].quarter == 4
        assert earnings[1].eps.actual == 2.18

        mock_rh.get_earnings.assert_called_once_with("AAPL")


def test_get_earnings_empty_response():
    mock_client = MagicMock(spec=RobinhoodClient)
    service = EarningsService(mock_client)

    with patch("robin_stocks_mcp.services.earnings.rh") as mock_rh:
        mock_rh.get_earnings.return_value = []

        earnings = service.get_earnings("INVALID")

        assert earnings == []


def test_get_earnings_none_response():
    mock_client = MagicMock(spec=RobinhoodClient)
    service = EarningsService(mock_client)

    with patch("robin_stocks_mcp.services.earnings.rh") as mock_rh:
        mock_rh.get_earnings.return_value = None

        earnings = service.get_earnings("INVALID")

        assert earnings == []


def test_get_earnings_none_items_filtered():
    """Test that None items in the list are skipped."""
    mock_client = MagicMock(spec=RobinhoodClient)
    service = EarningsService(mock_client)

    mock_data = [
        None,
        {
            "symbol": "AAPL",
            "instrument": None,
            "year": 2025,
            "quarter": 1,
            "eps": {"estimate": "1.50", "actual": None},
            "report": None,
            "call": None,
        },
        None,
    ]

    with patch("robin_stocks_mcp.services.earnings.rh") as mock_rh:
        mock_rh.get_earnings.return_value = mock_data

        earnings = service.get_earnings("AAPL")

        assert len(earnings) == 1
        assert earnings[0].symbol == "AAPL"
        assert earnings[0].eps.estimate == 1.50
        assert earnings[0].eps.actual is None
        assert earnings[0].report is None
        assert earnings[0].call is None


def test_get_earnings_missing_nested_fields():
    """Test earnings with missing nested dict fields."""
    mock_client = MagicMock(spec=RobinhoodClient)
    service = EarningsService(mock_client)

    mock_data = [
        {
            "symbol": "TSLA",
            "instrument": None,
            "year": 2025,
            "quarter": 2,
            "eps": {},
            "report": {},
            "call": {},
        },
    ]

    with patch("robin_stocks_mcp.services.earnings.rh") as mock_rh:
        mock_rh.get_earnings.return_value = mock_data

        earnings = service.get_earnings("TSLA")

        assert len(earnings) == 1
        assert earnings[0].eps.estimate is None
        assert earnings[0].eps.actual is None
        assert earnings[0].report.date is None
        assert earnings[0].report.timing is None
        assert earnings[0].call.datetime is None


def test_get_earnings_api_error():
    mock_client = MagicMock(spec=RobinhoodClient)
    service = EarningsService(mock_client)

    with patch("robin_stocks_mcp.services.earnings.rh") as mock_rh:
        mock_rh.get_earnings.side_effect = Exception("API Error")

        with pytest.raises(RobinhoodAPIError, match="Failed to fetch earnings"):
            service.get_earnings("AAPL")


def test_get_earnings_calls_ensure_session():
    mock_client = MagicMock(spec=RobinhoodClient)
    service = EarningsService(mock_client)

    with patch("robin_stocks_mcp.services.earnings.rh") as mock_rh:
        mock_rh.get_earnings.return_value = []

        service.get_earnings("AAPL")

        mock_client.ensure_session.assert_called_once()


def test_get_earnings_string_year_quarter_coerced():
    """Test that string year/quarter from API are properly coerced to ints."""
    mock_client = MagicMock(spec=RobinhoodClient)
    service = EarningsService(mock_client)

    mock_data = [
        {
            "symbol": "MSFT",
            "instrument": None,
            "year": "2025",
            "quarter": "3",
            "eps": {"estimate": "3.25", "actual": "3.40"},
            "report": None,
            "call": None,
        },
    ]

    with patch("robin_stocks_mcp.services.earnings.rh") as mock_rh:
        mock_rh.get_earnings.return_value = mock_data

        earnings = service.get_earnings("MSFT")

        assert earnings[0].year == 2025
        assert isinstance(earnings[0].year, int)
        assert earnings[0].quarter == 3
        assert isinstance(earnings[0].quarter, int)
        assert earnings[0].eps.estimate == 3.25
        assert isinstance(earnings[0].eps.estimate, float)
