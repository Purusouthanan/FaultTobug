from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String) # E.g., 'Admin', 'Doctor', 'Nurse'

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    dob = Column(Date)
    status = Column(String)

    prescriptions = relationship("Prescription", back_populates="patient")

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    medication = Column(String)
    instructions = Column(String)

    patient = relationship("Patient", back_populates="prescriptions")

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    status = Column(String, default="OPEN", index=True)
    
    extracted_role = Column(String, nullable=True)
    extracted_action = Column(String, nullable=True)
    extracted_resource = Column(String, nullable=True)
    extracted_endpoint = Column(String, nullable=True)
    extracted_method = Column(String, nullable=True)
    expected_result = Column(String, nullable=True)
    actual_result = Column(String, nullable=True)
    failure_category = Column(String, nullable=True)
    
    reproduction_steps = Column(String, nullable=True) # Will store JSON string for SQLite compatibility

