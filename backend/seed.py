from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def create_tables(engine):
    
    with engine.connect() as conn:
        # Create crew_members table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS crew_members (
                EmployeeID VARCHAR(10) PRIMARY KEY,
                Name VARCHAR(100) NOT NULL,
                Email VARCHAR(100) NOT NULL,
                Qualifications VARCHAR(100),
                Base VARCHAR(10)
            )
        """))
        
        # Create flights table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS flights (
                ID VARCHAR(10) PRIMARY KEY,
                "From" VARCHAR(10) NOT NULL,
                "To" VARCHAR(10) NOT NULL,
                Aircraft VARCHAR(20) NOT NULL,
                Departure VARCHAR(50) NOT NULL,
                Arrival VARCHAR(50) NOT NULL,
                "Duty_hrs" FLOAT NOT NULL
            )
        """))
        
        conn.commit()


def seed_crew_members(engine):
    
    crew_members = [
        {"EmployeeID": "E001", "Name": "Anna Müller", "Email": "anna@crew.io", "Qualifications": "A320, B737", "Base": "FRA"},
        {"EmployeeID": "E002", "Name": "Ben Costa", "Email": "ben@crew.io", "Qualifications": "A320", "Base": "LIS"},
        {"EmployeeID": "E003", "Name": "Clara Johansson", "Email": "clara@crew.io", "Qualifications": "B737, E190", "Base": "ARN"},
        {"EmployeeID": "E004", "Name": "David Petrov", "Email": "david@crew.io", "Qualifications": "A320, B737, E190", "Base": "VIE"},
        {"EmployeeID": "E005", "Name": "Eva Nowak", "Email": "eva@crew.io", "Qualifications": "A320, E190", "Base": "WAW"},
    ]
    
    with engine.connect() as conn:
        for member in crew_members:
            conn.execute(
                text("""
                    INSERT INTO crew_members (EmployeeID, Name, Email, Qualifications, Base)
                    VALUES (:EmployeeID, :Name, :Email, :Qualifications, :Base)
                    ON CONFLICT (EmployeeID) DO NOTHING
                """),
                member
            )
        conn.commit()


def seed_flights(engine):
    
    flights = [
        {"ID": "F1", "From": "FRA", "To": "LIS", "Aircraft": "A320", "Departure": "Feb 1, 06:00", "Arrival": "Feb 1, 08:30", "Duty_hrs": 2.5},
        {"ID": "F2", "From": "FRA", "To": "ARN", "Aircraft": "B737", "Departure": "Feb 1, 07:00", "Arrival": "Feb 1, 09:30", "Duty_hrs": 2.5},
        {"ID": "F3", "From": "LIS", "To": "FRA", "Aircraft": "A320", "Departure": "Feb 1, 14:00", "Arrival": "Feb 1, 16:30", "Duty_hrs": 2.5},
        {"ID": "F4", "From": "ARN", "To": "VIE", "Aircraft": "E190", "Departure": "Feb 1, 20:00", "Arrival": "Feb 1, 22:30", "Duty_hrs": 2.5},
        {"ID": "F5", "From": "FRA", "To": "WAW", "Aircraft": "B737", "Departure": "Feb 2, 06:00", "Arrival": "Feb 2, 08:00", "Duty_hrs": 2.0},
        {"ID": "F6", "From": "VIE", "To": "FRA", "Aircraft": "A320", "Departure": "Feb 2, 12:00", "Arrival": "Feb 2, 13:30", "Duty_hrs": 1.5},
        {"ID": "F7", "From": "WAW", "To": "ARN", "Aircraft": "E190", "Departure": "Feb 3, 08:00", "Arrival": "Feb 3, 10:00", "Duty_hrs": 2.0},
        {"ID": "F8", "From": "FRA", "To": "LIS", "Aircraft": "B737", "Departure": "Feb 3, 13:00", "Arrival": "Feb 3, 15:30", "Duty_hrs": 2.5},
    ]
    
    with engine.connect() as conn:
        for flight in flights:
            conn.execute(
                text("""
                    INSERT INTO flights (ID, "From", "To", Aircraft, Departure, Arrival, "Duty Hrs")
                    VALUES (:ID, :From, :To, :Aircraft, :Departure, :Arrival, :"Duty Hrs")
                    ON CONFLICT (ID) DO NOTHING
                """),
                flight
            )
        conn.commit()


def main():
    
    engine = create_engine(DATABASE_URL)
    
    try:
        print("Creating tables...")
        create_tables(engine)
        
        print("Seeding crew_members table...")
        seed_crew_members(engine)
        
        print("Seeding flights table...")
        seed_flights(engine)
        
        print("Database seeded successfully!")
    except:
        print("Database seed failed!")


if __name__ == "__main__":
    main()
