from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float, DateTime
from sqlalchemy.orm import relationship
import datetime
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
    generated_test_code = Column(String, nullable=True)
    baseline_test_code = Column(String, nullable=True)

    executions = relationship("TestExecution", back_populates="incident")

class TestExecution(Base):
    __tablename__ = "test_executions"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    status = Column(String) # PASS, FAIL, ERROR
    execution_time = Column(Float, nullable=True) # in seconds
    logs = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    incident = relationship("Incident", back_populates="executions")

class RegressionTest(Base):
    __tablename__ = "regression_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    test_code = Column(String)
    registered_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    incident = relationship("Incident")

class SuiteExecution(Base):
    __tablename__ = "suite_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    execution_time = Column(Float, nullable=True) # in seconds
    logs = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
