from pydantic import BaseModel


class BillInfo(BaseModel):
    bill_number: str
    bill_type: str
    status: str
    sponsor_name: str
    sponsor_party: str
    last_updated: str
