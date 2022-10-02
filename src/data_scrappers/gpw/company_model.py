from enum import Enum, auto

from pydantic import BaseModel


class MarketEnum(Enum):
    GPW = auto()
    NEW_CONNECT = auto()


class CompanyModel(BaseModel):
    isin: str  # International Securities Identification Number
    name: str  # Company name
    ticker: str  # Stock symbol
    market: MarketEnum  # Stock market
