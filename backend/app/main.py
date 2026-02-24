from fastapi import FastAPI

app = FastAPI(
    title="Crewboard Project",
    description="API for optimizing flight operations and work distribution",
    version="0.1.0"
)

# Register sub-routes here



# Sub routes end

@app.get("/health")
async def health_check():
    return {"status": 200}

@app.get("/")
async def root():
    return {"message": "Welcome on board"}
