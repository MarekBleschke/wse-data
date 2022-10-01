from pydantic import BaseModel


class CompanyModel(BaseModel):
    gpw_id: str
    name: str
    ticker: str
