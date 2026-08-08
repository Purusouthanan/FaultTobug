from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import json
from . import database

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

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is running"}

@app.get("/db-health")
def db_health_check(db: Session = Depends(database.get_db)):
    try:
        # Check database connectivity
        db.execute("SELECT 1")
        return {"status": "ok", "message": "Database is connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
