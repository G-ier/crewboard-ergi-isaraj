from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class FlightCreate(BaseModel):
    id: str = Field(min_length=1, max_length=10)
    From: str = Field(min_length=3, max_length=3)
    To: str = Field(min_length=3, max_length=3)
    aircraft: str
    departure: str
    arrival: str
    duty_hrs: float

    @field_validator("From", "To")
    @classmethod
    def validate_iata(cls, v: str) -> str:
        v = v.strip().upper()
        if len(v) != 3 or not v.isalpha():
            raise ValueError("must be a 3-letter IATA code (e.g. FRA)")
        return v


class FlightRead(BaseModel):
    id: str
    From: str
    To: str
    aircraft: str
    departure: str
    arrival: str
    duty_hrs: float

    class Config:
        from_attributes = True


class ScheduleItem(BaseModel):
    
    type: str = Field(..., description="Either 'flight' or 'rest'")
    flight: Optional[FlightRead] = None
    rest_hours: Optional[float] = None
    date: Optional[str] = None
    
    class Config:
        from_attributes = True


class CrewScheduleResponse(BaseModel):
    
    crew_member_id: str
    schedule: List[ScheduleItem]
    
    class Config:
        from_attributes = True
