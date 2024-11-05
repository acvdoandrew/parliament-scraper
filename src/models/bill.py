from pydantic import BaseModel, Field


class BillInfo(BaseModel):
    bill_number: str = Field(..., description="Bill number (e.g., 's-2')")
    bill_type: str = Field(default="Unknown")
    status: str = Field(default="Unknown")
    sponsor_name: str = Field(default="Unknown")
    sponsor_party: str = Field(default="Unknown")
    last_updated: str = Field(default="Unknown")

    class Config:
        json_schema_extra = {
            "example": {
                "bill_number": "s-2",
                "bill_type": "Senate Public Bill",
                "status": "Royal Assent",
                "sponsor_name": "John Doe",
                "sponsor_party": "Conservative",
                "last_updated": "2024-01-01",
            }
        }
