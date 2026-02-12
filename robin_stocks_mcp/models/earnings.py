# robin_stocks_mcp/models/earnings.py
from pydantic import BaseModel
from typing import Optional


class EarningsEPS(BaseModel):
    """Earnings per share data for a quarter."""

    estimate: Optional[float] = None
    actual: Optional[float] = None


class EarningsReport(BaseModel):
    """Earnings report metadata."""

    date: Optional[str] = None
    timing: Optional[str] = None
    verified: Optional[bool] = None


class EarningsCall(BaseModel):
    """Earnings call details."""

    datetime: Optional[str] = None
    broadcast_url: Optional[str] = None
    replay_url: Optional[str] = None


class Earnings(BaseModel):
    """Earnings data for a single quarter."""

    symbol: Optional[str] = None
    instrument: Optional[str] = None
    year: Optional[int] = None
    quarter: Optional[int] = None
    eps: Optional[EarningsEPS] = None
    report: Optional[EarningsReport] = None
    call: Optional[EarningsCall] = None
