from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
import os
import json
from . import database, models
from .auth import auth_router
from .routers import patients, prescriptions, incidents, regression, baseline, metrics

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Incident-to-Regression Automation Platform")

# Configure CORS
origins_str = os.getenv("CORS_ORIGINS", '["http://localhost:5173"]')
try:
    origins = json.loads(origins_str)
except Exception:
    origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(patients.router)
app.include_router(prescriptions.router)
app.include_router(incidents.router)
app.include_router(regression.router)
app.include_router(baseline.router)
app.include_router(metrics.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is running"}

@app.get("/db-health")
def db_health_check(db: Session = Depends(database.get_db)):
    try:
        # Check database connectivity (SQLAlchemy 2.0 requires text() for raw SQL)
        db.execute(text("SELECT 1"))
        return {"status": "ok", "message": "Database is connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
