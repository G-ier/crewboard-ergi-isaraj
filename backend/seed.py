from datetime import datetime
from sqlalchemy import create_engine, text, URL
from dotenv import load_dotenv
import os

load_dotenv()

def create_tables(engine):
    
    with engine.connect() as conn:
        # Create crew_members table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS crew_members (
                id VARCHAR(10) PRIMARY KEY,
                Name VARCHAR(100) NOT NULL,
                Email VARCHAR(100) NOT NULL,
                Qualifications VARCHAR(255),
                Base VARCHAR(10)
            )
        """))
        
        # Create flights table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS flights (
                id VARCHAR(10) PRIMARY KEY,
                "From" VARCHAR(10) NOT NULL,
                "To" VARCHAR(10) NOT NULL,
                Aircraft VARCHAR(20) NOT NULL,
                Departure VARCHAR(50) NOT NULL,
                Arrival VARCHAR(50) NOT NULL,
                "Duty_hrs" FLOAT NOT NULL
            )
        """))

        # Create assignments table

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS crew_assignments (
                id BIGSERIAL PRIMARY KEY,

                flight_id VARCHAR(10) NOT NULL REFERENCES flights(id) ON DELETE CASCADE,
                crew_employee_id VARCHAR(10) NOT NULL REFERENCES crew_members(id) ON DELETE CASCADE,

                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                removed_at TIMESTAMPTZ NULL,

                CONSTRAINT uq_flight_crew UNIQUE (flight_id, crew_employee_id)
            );
        """))
    
        conn.commit()


def seed_crew_members(engine):
    
    crew_members = [
        {"id": "E001", "Name": "Anna Müller", "Email": "anna@crew.io", "Qualifications": "A320, B737", "Base": "FRA"},
        {"id": "E002", "Name": "Ben Costa", "Email": "ben@crew.io", "Qualifications": "A320", "Base": "LIS"},
        {"id": "E003", "Name": "Clara Johansson", "Email": "clara@crew.io", "Qualifications": "B737, E190", "Base": "ARN"},
        {"id": "E004", "Name": "David Petrov", "Email": "david@crew.io", "Qualifications": "A320, B737, E190", "Base": "VIE"},
        {"id": "E005", "Name": "Eva Nowak", "Email": "eva@crew.io", "Qualifications": "A320, E190", "Base": "WAW"},
    ]
    
    with engine.connect() as conn:
        for member in crew_members:
            conn.execute(
                text("""
                    INSERT INTO crew_members (id, Name, Email, Qualifications, Base)
                    VALUES (:id, :Name, :Email, :Qualifications, :Base)
                    ON CONFLICT (id) DO NOTHING
                """),
                member
            )
        conn.commit()


def seed_flights(engine):
    
    flights = [
        {"id": "F1", "From": "FRA", "To": "LIS", "Aircraft": "A320", "Departure": "Feb 1, 06:00", "Arrival": "Feb 1, 08:30", "Duty_hrs": 2.5},
        {"id": "F2", "From": "FRA", "To": "ARN", "Aircraft": "B737", "Departure": "Feb 1, 07:00", "Arrival": "Feb 1, 09:30", "Duty_hrs": 2.5},
        {"id": "F3", "From": "LIS", "To": "FRA", "Aircraft": "A320", "Departure": "Feb 1, 14:00", "Arrival": "Feb 1, 16:30", "Duty_hrs": 2.5},
        {"id": "F4", "From": "ARN", "To": "VIE", "Aircraft": "E190", "Departure": "Feb 1, 20:00", "Arrival": "Feb 1, 22:30", "Duty_hrs": 2.5},
        {"id": "F5", "From": "FRA", "To": "WAW", "Aircraft": "B737", "Departure": "Feb 2, 06:00", "Arrival": "Feb 2, 08:00", "Duty_hrs": 2.0},
        {"id": "F6", "From": "VIE", "To": "FRA", "Aircraft": "A320", "Departure": "Feb 2, 12:00", "Arrival": "Feb 2, 13:30", "Duty_hrs": 1.5},
        {"id": "F7", "From": "WAW", "To": "ARN", "Aircraft": "E190", "Departure": "Feb 3, 08:00", "Arrival": "Feb 3, 10:00", "Duty_hrs": 2.0},
        {"id": "F8", "From": "FRA", "To": "LIS", "Aircraft": "B737", "Departure": "Feb 3, 13:00", "Arrival": "Feb 3, 15:30", "Duty_hrs": 2.5},
    ]
    
    with engine.connect() as conn:
        for flight in flights:
            conn.execute(
                text("""
                    INSERT INTO flights (id, "From", "To", Aircraft, Departure, Arrival, "Duty_hrs")
                    VALUES (:id, :From, :To, :Aircraft, :Departure, :Arrival, :Duty_hrs)
                    ON CONFLICT (id) DO NOTHING
                """),
                flight
            )
        conn.commit()


def main():
    
    DATABASE_URL="postgresql+psycopg://nonroot:crewy11@localhost:5833/crewboard"

    engine = create_engine(DATABASE_URL)
    
    try:
        print("Creating tables...")
        create_tables(engine)
        
        print("Seeding crew_members table...")
        seed_crew_members(engine)
        
        print("Seeding flights table...")
        seed_flights(engine)
        
        print("Database seeded successfully!")
    except Exception as e:
        print(f"Database seed failed! Error: {e}")


if __name__ == "__main__":
    main()
