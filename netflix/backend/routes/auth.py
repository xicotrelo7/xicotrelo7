from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os
from datetime import datetime, timedelta
import jwt
from typing import Optional

router = APIRouter(prefix="/auth", tags=["auth"])

# Secret key for JWT - in production, use env variable
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-this')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')  # Default password
ALGORITHM = "HS256"

class LoginRequest(BaseModel):
    password: str

class LoginResponse(BaseModel):
    success: bool
    token: str
    message: str

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Admin login endpoint"""
    if request.password == ADMIN_PASSWORD:
        # Create JWT token
        expires = datetime.utcnow() + timedelta(hours=24)
        token_data = {
            "exp": expires,
            "role": "admin"
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        return LoginResponse(
            success=True,
            token=token,
            message="Login successful"
        )
    else:
        raise HTTPException(status_code=401, detail="Invalid password")

@router.post("/verify")
async def verify_token(token: str):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"success": True, "valid": True}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
