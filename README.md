# Crewboard

A FastAPI web application for flight crew assignment and scheduling optimization.

## Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy as ORM
- **Validation**: Pydantic
- **Testing**: pytest
- **Python**: 3.12+

## Project Structure

```
crewboard/
├── backend/
│   ├── app/
│   │   ├── database/        # Database connection/engine
│   │   ├── domains/          # Domain modules (bounded contexts)
│   │   │   ├── crew_assignment/    # Crew assignment domain
│   │   │   │   ├── models.py       # SQLAlchemy models
│   │   │   │   ├── repository.py   # Data access layer
│   │   │   │   ├── service.py      # Business logic
│   │   │   │   ├── router.py       # API endpoints
│   │   │   │   └── schemas.py      # Pydantic schemas
│   │   │   ├── crew_management/    # Crew management domain
│   │   │   │   ├── models.py       # SQLAlchemy models
│   │   │   │   ├── repository.py   # Data access layer
│   │   │   │   ├── service.py      # Business logic
│   │   │   │   ├── router.py       # API endpoints
│   │   │   │   └── schemas.py      # Pydantic schemas
│   │   │   └── flights/            # Flights domain
│   │   │       ├── models.py       # SQLAlchemy models
│   │   │       ├── repository.py   # Data access layer
│   │   │       ├── service.py      # Business logic
│   │   │       ├── router.py       # API endpoints
│   │   │       └── schemas.py      # Pydantic schemas
│   │   └── main.py          # FastAPI application entry point
│   ├── tests/
│   │   ├── unit/            # Unit tests
│   │   └── integration/     # Integration tests
│   └── seed.py             # Database seeding script
├── frontend/               # Frontend application - not completed
└── docker-compose.yaml     # Docker composition YAML
```

## Requirements (only for not containerized deployments)

Install dependencies with [uv](https://github.com/astral-sh/uv):

```bash
uv sync
```

## Start system

Run this from root:

```bash
docker compose up -d --build
```

Then seed the database by running:

```bash
cd backend
uv run python seed.py
```

## Running Tests

I would advise to run the tests within the container itself after it has finished building and is running.

First, find the Docker instance ID which should be under the name crewboard-backend-1:

```bash
docker ps -a
```

Copy the ID and run the following:

```bash
docker exec -it <ID> bash
```

After that, run the following commands in the container:

```bash
cd tests
uv run pytest -q -v
```
