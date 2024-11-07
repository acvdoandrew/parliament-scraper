from pydantic import BaseModel, Field


class BillInfo(BaseModel):
    bill_number: str = Field(description="Bill number (e.g., 's-2')")
    bill_type: str = Field(default="Unknown")
    status: str = Field(default="Unknown")
    sponsor_name: str = Field(default="Unknown")
    sponsor_party: str = Field(default="Unknown")
    last_updated: str = Field(default="Unknown")

    class Config:
        frozen = True
