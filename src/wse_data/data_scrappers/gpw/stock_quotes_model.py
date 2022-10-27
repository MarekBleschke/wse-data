from datetime import date

from pydantic import BaseModel, Field
from decimal import Decimal


class StockQuotesModel(BaseModel):
    date_: date = Field(..., alias="date")
    company_name: str
    company_isin: str
    opening: Decimal
    closing: Decimal
    max: Decimal
    min: Decimal
    volume: int
