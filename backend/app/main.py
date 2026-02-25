from fastapi import FastAPI

# Import models first to avoid circular import issues with SQLAlchemy relationships
# This ensures all models are registered before relationships are configured
from app.domains.crew_management.models import CrewMember
from app.domains.flights.models import Flight
from app.domains.crew_assignment.models import CrewAssignment

from app.domains.crew_management.router import router as crew_router
from app.domains.flights.router import router as flight_router
from app.domains.crew_assignment.router import router as assignment_router

app = FastAPI(
    title="Crewboard Project",
    description="API for optimizing flight operations and work distribution",
    version="0.1.2"
)

# Register sub-routes here

app.include_router(crew_router)
app.include_router(flight_router)
app.include_router(assignment_router)

# Sub routes end

@app.get("/health")
async def health_check():
    return {"status": 200}

@app.get("/")
async def root():
    return {"message": "Welcome on board"}
