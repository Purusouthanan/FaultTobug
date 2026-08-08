import os
import yaml
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .database import get_db
from .models import User

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# Dummy token scheme for the simulator
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def load_rbac_config():
    config_path = os.path.join(os.path.dirname(__file__), '../config/rbac.yaml')
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        return {"roles": {}}

RBAC_CONFIG = load_rbac_config()

@auth_router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # For simulation, we just use the username as the token
    return {"access_token": user.username, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

class PermissionChecker:
    def __init__(self, resource: str, action: str):
        self.resource = resource
        self.action = action

    def __call__(self, user: User = Depends(get_current_user)):
        user_role = user.role
        
        # Load fresh config in case it changed for an experiment
        config = load_rbac_config()
        role_rules = config.get("roles", {}).get(user_role, [])
        
        decision = "Deny"
        
        for rule in role_rules:
            if (rule.get("resource") == self.resource or rule.get("resource") == "*") and \
               (rule.get("action") == self.action or rule.get("action") == "*"):
                decision = rule.get("decision", "Deny")
                
        if decision != "Allow":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Denied: {user_role} cannot {self.action} {self.resource}"
            )
        return True

def require_permission(resource: str, action: str):
    return PermissionChecker(resource, action)
