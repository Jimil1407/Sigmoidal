from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException
from prisma import Prisma
from pydantic import BaseModel, EmailStr
from jose import jwt
import os
from passlib.context import CryptContext
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/users", tags=["users"])
prisma = Prisma()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

secret = os.getenv("JWT_SECRET")

class UserRequest(BaseModel):
    email: EmailStr
    password: str

class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str
    username: str

class UserPublic(BaseModel):
    id: str | None
    email: EmailStr
    username: str | None

@router.get("/allUsers")
async def getUsers():
    await prisma.connect()
    try:
        users_detail = await prisma.user.find_many()
        return users_detail
    finally:
        await prisma.disconnect()

@router.get("/{user_id}")
async def getUser(user_id: str):
    await prisma.connect()
    try:
        user_detail = await prisma.user.find_unique(where={"id": user_id})
        if not user_detail:
            raise HTTPException(status_code=404, detail="User not found")
        return user_detail
    finally:
        await prisma.disconnect()

@router.post("/createUser", response_model=UserPublic)
async def createUser(user: UserCreateRequest):
    await prisma.connect()
    try:
        # Ensure unique email
        existing = await prisma.user.find_unique(where={"email": user.email})
        if existing:
            raise HTTPException(status_code=409, detail="An account with this email already exists")
        # Optionally ensure unique username
        if user.username:
            existing_username = await prisma.user.find_unique(where={"username": user.username})
            if existing_username:
                raise HTTPException(status_code=409, detail="This username is already taken")
        # Hash password and create user
        hashed = pwd_context.hash(user.password)
        normalized_username = user.username.strip()
        created = await prisma.user.create(data={"email": user.email, "password": hashed, "username": normalized_username})
        portfolio = await prisma.portfolio.create(data={"userId": created.id, "name": normalized_username + "'s Portfolio", "totalValue": 0.0, "cash": 0.0})
        return {"id": getattr(created, "id", None), "email": created.email, "username": getattr(created, "username", None), "portolio created with id": portfolio.id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create user {user.email}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create user")
    finally:
        await prisma.disconnect()

@router.post("/login")
async def login(user: UserRequest):
    await prisma.connect()
    try:
        user_detail = await prisma.user.find_unique(where={"email": user.email})
        if not user_detail:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not pwd_context.verify(user.password, getattr(user_detail, "password", "")):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        payload = {
            "id": getattr(user_detail, "id", None),
            "email": getattr(user_detail, "email", None),
            "username": getattr(user_detail, "username", None),
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
        }
        token = jwt.encode(payload, secret, algorithm="HS256")
        return {"token": token}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to login user {user.email}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to login user")
    finally:
        await prisma.disconnect()
