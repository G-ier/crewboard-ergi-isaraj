# Crewboard

A FastAPI web application.

## Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy as ORM
- **Validation**: Pydantic
- **Testing**: pytest
- **Python**: 3.12+

## Project Structure

```
crewboard/
├── backend/          # FastAPI application
│   ├── app/          # Main application code
│   │   ├── api/     # API endpoints (app layer)
│   │   ├── database/ # Database connection/engine
│   │   ├── model/   # Database models
│   │   ├── schema/  # Pydantic schemas
│   │   ├── service/ # Business logic layer
│   │   └── repository/ # Data access layer
│   └── tests/       # Backend tests
├── db/               # Database setup scripts
└── frontend/         # Frontend application
```

## Requirements

Install dependencies with [uv](https://github.com/astral-sh/uv):

```bash
uv sync
```

## Database

Set up the database:

```bash
python db/setup.py
```
