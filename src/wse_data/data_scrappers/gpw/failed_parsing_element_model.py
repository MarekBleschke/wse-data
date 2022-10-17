from pydantic import BaseModel


class FailedParsingElementModel(BaseModel):
    raw_data: bytes
