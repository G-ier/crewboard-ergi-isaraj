from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.database.engine import get_db_session
from app.domains.crew_assignment.schemas import (
    AssignmentCreate,
    AssignmentRead,
    AssignmentValidationResult,
)
from app.domains.crew_assignment.service import CrewAssignmentService

router = APIRouter(prefix="/assignments", tags=["Crew Assignments"])
service = CrewAssignmentService()


@router.post("", response_model=AssignmentRead, status_code=status.HTTP_201_CREATED)
def create_assignment(
    payload: AssignmentCreate,
    db: Session = Depends(get_db_session),
):

    assignment, validation = service.create_assignment(db, payload)
    
    if not assignment:
        
        errors = [e.model_dump() for e in validation.errors]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Assignment validation failed",
                "errors": errors,
            },
        )
    
    return AssignmentRead.model_validate(assignment)


@router.get("", response_model=list[AssignmentRead])
def list_assignments(
    flight_id: str | None = Query(default=None),
    crew_employee_id: str | None = Query(default=None),
    include_removed: bool = Query(default=False),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db_session),
):

    assignments = service.list_assignments(
        db,
        flight_id=flight_id,
        crew_employee_id=crew_employee_id,
        include_removed=include_removed,
        limit=limit,
        offset=offset,
    )
    return [AssignmentRead.model_validate(a) for a in assignments]


@router.get("/{assignment_id}", response_model=AssignmentRead)
def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db_session),
):

    assignment = service.get_assignment(db, assignment_id)
    return AssignmentRead.model_validate(assignment)


@router.delete("/{assignment_id}", response_model=AssignmentRead)
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db_session),
):

    assignment = service.delete_assignment(db, assignment_id)
    return AssignmentRead.model_validate(assignment)


@router.post("/validate", response_model=AssignmentValidationResult)
def validate_assignment(
    payload: AssignmentCreate,
    db: Session = Depends(get_db_session),
):

    return service.validate_assignment(db, payload.flight_id, payload.crew_employee_id)
