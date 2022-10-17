from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class ReportCategory(Enum):
    ESPI = "ESPI"
    EBI = "EBI"
    OTHER = "Inny"

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in [member.value for member in cls]


class ReportType(Enum):
    CURRENT = "Bieżący"
    HALF_YEAR = "Półroczny"
    QUARTER = "Kwartalny"
    PERIODIC = "Okresowy"
    YEAR = "Roczny"
    OTHER = "Inny"

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in [member.value for member in cls]


class ReportModel(BaseModel):
    gpw_id: str
    company_isin: str
    # TODO: should be company name or remove it
    name: str
    summary: str
    datetime: datetime
    category: ReportCategory
    type: ReportType
