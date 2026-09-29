import os
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models
from datetime import date

# Ensure tables exist
models.Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    try:
        # Check if users already exist
        if db.query(models.User).first():
            print("Database already seeded.")
            return

        print("Seeding database...")

        # Add Users
        admin = models.User(username="admin", role="Admin")
        doctor = models.User(username="dr_smith", role="Doctor")
        nurse = models.User(username="nurse_joy", role="Nurse")
        receptionist = models.User(username="receptionist_amy", role="Receptionist")
        clerk = models.User(username="clerk_bob", role="Billing Clerk")
        db.add_all([admin, doctor, nurse, receptionist, clerk])
        db.commit()

        # Add Patients
        p1 = models.Patient(name="John Doe", dob=date(1980, 5, 15), status="Admitted")
        p2 = models.Patient(name="Jane Roe", dob=date(1992, 11, 23), status="Discharged")
        db.add_all([p1, p2])
        db.commit()
        db.refresh(p1)
        db.refresh(p2)

        # Add Prescriptions
        rx1 = models.Prescription(patient_id=p1.id, medication="Amoxicillin", instructions="500mg every 8 hours")
        rx2 = models.Prescription(patient_id=p2.id, medication="Ibuprofen", instructions="400mg as needed for pain")
        db.add_all([rx1, rx2])
        db.commit()

        print("Database seeding complete.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
