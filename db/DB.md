# Database Setup (`db/`)

This folder contains the database setup scripts for the crewboard project.

## Overview

The `db/` folder holds `setup.py`, which is responsible for:
- Creating the database with the desired schema/tables
- Populating the database with initial seed data (if needed)

## Files

### `setup.py`

The main database setup script. When executed, it:
1. Creates all required tables based on the defined schema
2. Populates the database with initial entries (seed data)

## Usage

To set up the database, run:

```bash
python db/setup.py
```
