import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

class Passenger(Base):
    __tablename__ = "passengers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    journeys = relationship("Journey", back_populates="passenger")

class Journey(Base):
    __tablename__ = "journeys"
    
    id = Column(Integer, primary_key=True, index=True)
    passenger_id = Column(Integer, ForeignKey("passengers.id"))
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    fare = Column(Float, nullable=False)
    journey_date = Column(Date, nullable=False)
    passenger = relationship("Passenger", back_populates="journeys")

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    expense_type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    notes = Column(String)

def init_db():
    """Initialize the database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
