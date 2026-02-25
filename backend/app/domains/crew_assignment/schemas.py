from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AssignmentCreate(BaseModel):

    flight_id: str = Field(min_length=1, max_length=15)
    crew_employee_id: str = Field(min_length=1, max_length=15)


class AssignmentRead(BaseModel):

    id: int
    flight_id: str
    crew_employee_id: str
    created_at: datetime
    removed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AssignmentDelete(BaseModel):

    removed_at: Optional[datetime] = None


class ValidationError(BaseModel):
    
    code: str
    message: str


class AssignmentCreateResponse(BaseModel):

    assignment: AssignmentRead
    warnings: list[str] = Field(default_factory=list)


class AssignmentValidationResult(BaseModel):

    valid: bool
    errors: list[ValidationError] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class AutoAssignmentFailure(BaseModel):
    flight_id: str
    reason: str


class AutoAssignmentSuccess(BaseModel):
    flight_id: str
    crew_member_id: str


class AutoAssignmentResult(BaseModel):
    assigned: list[AutoAssignmentSuccess]
    failed: list[AutoAssignmentFailure]
    total_flights: int
    total_assigned: int
    total_failed: int
