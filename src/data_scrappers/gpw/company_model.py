from enum import Enum, auto

from pydantic import BaseModel


class MarketEnum(Enum):
    GPW = auto()
    NEW_CONNECT = auto()


class CompanyModel(BaseModel):
    gpw_id: str
    name: str
    ticker: str
    market: MarketEnum
