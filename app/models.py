from decimal import Decimal

from pydantic import BaseModel, Field


class TransferRequest(BaseModel):
    amount: Decimal = Field(gt=0)
    vendor: str = Field(min_length=1)
    txhash: str = Field(min_length=4)


class TransferResponse(BaseModel):
    vendor: str
    txhash: str
    amount: Decimal
    txhash_status: str
    vendor_response: dict
