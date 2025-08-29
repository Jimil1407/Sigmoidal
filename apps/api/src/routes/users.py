from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException
from prisma import Prisma
from pydantic import BaseModel
from jose import jwt
import os
from passlib.context import CryptContext
prisma = Prisma()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/api/v1/users", tags=["users"])
secret = os.getenv("JWT_SECRET")
class UserRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    email: str
    password: str
    username: str
    

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
        return user_detail
    finally:
        await prisma.disconnect()

@router.post("/createUser")
async def createUser(user: UserResponse):
    await prisma.connect()
    try:
        # hash password before saving
        data = user.model_dump()
        data["password"] = pwd_context.hash(user.password)
        user_detail = await prisma.user.create(data=data)
        return {"id": getattr(user_detail, "id", None), "email": user_detail.email, "username": getattr(user_detail, "username", None)}
    finally:
        await prisma.disconnect()

@router.post("/login")
async def login(user: UserRequest):
    await prisma.connect()
    try:
        # Validate that user exists
        user_detail = await prisma.user.find_unique(where={"email": user.email})
        if not user_detail or not pwd_context.verify(user.password, getattr(user_detail, "password", "")):
            raise HTTPException(status_code=404, detail=f"User with email {user.email} not found")
        
        payload = {
            "id": getattr(user_detail, "id", None),
            "email": getattr(user_detail, "email", None),
            "username": getattr(user_detail, "username", None),
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
        }
        token = jwt.encode(payload, secret, algorithm="HS256")
        return {"token": token}
    finally:
        await prisma.disconnect()
