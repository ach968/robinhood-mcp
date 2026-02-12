# robin_stocks_mcp/services/earnings.py
import requests
import robin_stocks.robinhood as rh
from typing import List
from robin_stocks_mcp.models.earnings import (
    Earnings,
    EarningsEPS,
    EarningsReport,
    EarningsCall,
)
from robin_stocks_mcp.robinhood.client import RobinhoodClient
from robin_stocks_mcp.robinhood.errors import (
    AuthRequiredError,
    InvalidArgumentError,
    RobinhoodAPIError,
)


def _safe_float(value) -> float | None:
    """Safely convert a value to float."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _safe_int(value) -> int | None:
    """Safely convert a value to int."""
    if value is None:
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def _parse_eps(eps_data) -> EarningsEPS | None:
    """Parse EPS data from robin-stocks response."""
    if eps_data is None or not isinstance(eps_data, dict):
        return None
    return EarningsEPS(
        estimate=_safe_float(eps_data.get("estimate")),
        actual=_safe_float(eps_data.get("actual")),
    )


def _parse_report(report_data) -> EarningsReport | None:
    """Parse report data from robin-stocks response."""
    if report_data is None or not isinstance(report_data, dict):
        return None
    return EarningsReport(
        date=report_data.get("date"),
        timing=report_data.get("timing"),
        verified=report_data.get("verified"),
    )


def _parse_call(call_data) -> EarningsCall | None:
    """Parse call data from robin-stocks response."""
    if call_data is None or not isinstance(call_data, dict):
        return None
    return EarningsCall(
        datetime=call_data.get("datetime"),
        broadcast_url=call_data.get("broadcast_url"),
        replay_url=call_data.get("replay_url"),
    )


class EarningsService:
    """Service for earnings operations."""

    def __init__(self, client: RobinhoodClient):
        self.client = client

    def get_earnings(self, symbol: str) -> List[Earnings]:
        """Get earnings data for a symbol.

        Returns a list of Earnings objects, one per quarter.
        """
        if not symbol:
            raise InvalidArgumentError("Symbol is required")

        self.client.ensure_session()

        try:
            data = rh.get_earnings(symbol)

            if not data or data == [None]:
                return []

            results = []
            for item in data:
                if item is None:
                    continue
                earnings = Earnings(
                    symbol=item.get("symbol"),
                    instrument=item.get("instrument"),
                    year=_safe_int(item.get("year")),
                    quarter=_safe_int(item.get("quarter")),
                    eps=_parse_eps(item.get("eps")),
                    report=_parse_report(item.get("report")),
                    call=_parse_call(item.get("call")),
                )
                results.append(earnings)
            return results
        except (RobinhoodAPIError, InvalidArgumentError, AuthRequiredError):
            raise
        except (requests.RequestException, ConnectionError, TimeoutError) as e:
            raise RobinhoodAPIError(f"Failed to fetch earnings: {e}") from e
        except Exception as e:
            raise RobinhoodAPIError(f"Failed to fetch earnings: {e}") from e
