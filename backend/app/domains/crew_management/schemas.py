from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator

class CrewCreate(BaseModel):
    id: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=64)
    email: EmailStr
    base_airport: str = Field(min_length=3, max_length=3)
    qualifications: List[str] = Field(default_factory=list)

    @field_validator("base_airport")
    @classmethod
    def validate_iata(cls, v: str) -> str:
        v = v.strip().upper()
        if len(v) != 3 or not v.isalpha():
            raise ValueError("base_airport must be a 3-letter IATA code (e.g. FRA)")
        return v

    @field_validator("qualifications")
    @classmethod
    def normalize_quals(cls, v: List[str]) -> List[str]:
        return [q.strip().upper() for q in v if q.strip()]


class CrewUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=64)
    email: Optional[EmailStr] = None
    base_airport: Optional[str] = Field(default=None, min_length=3, max_length=3)
    qualifications: Optional[List[str]] = None  # if provided this replaces list

    @field_validator("base_airport")
    @classmethod
    def validate_iata(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip().upper()
        if len(v) != 3 or not v.isalpha():
            raise ValueError("base_airport must be a 3-letter IATA code (e.g. FRA)")
        return v

    @field_validator("qualifications")
    @classmethod
    def normalize_quals(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return None
        return [q.strip().upper() for q in v if q.strip()]


class CrewRead(BaseModel):
    id: str
    name: str
    email: EmailStr
    base_airport: str
    qualifications: List[str]

    class Config:
        from_attributes = True