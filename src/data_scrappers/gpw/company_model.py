from enum import Enum, auto

from pydantic import BaseModel, Field


class MarketEnum(Enum):
    GPW = auto()
    NEW_CONNECT = auto()


class CompanyModel(BaseModel):
    isin: str = Field(..., min_length=1)  # International Securities Identification Number
    name: str = Field(..., min_length=1)  # Company name
    ticker: str = Field(..., min_length=1)  # Stock symbol
    market: MarketEnum  # Stock market
