from enum import Enum, auto

from pydantic import BaseModel, Field


class MarketEnum(str, Enum):
    GPW = "GPW"
    NEW_CONNECT = "NEW-CONNECT"


class CompanyModel(BaseModel):
    isin: str = Field(..., min_length=1)  # International Securities Identification Number
    name: str = Field(..., min_length=1)  # Company name
    ticker: str = Field(..., min_length=1)  # Stock symbol
    market: MarketEnum  # Stock market
