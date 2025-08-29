from datetime import datetime
from fastapi import APIRouter, HTTPException
from prisma import Prisma
from pydantic import BaseModel
from jose import jwt

prisma = Prisma()

router = APIRouter(prefix="/api/v1/users", tags=["users"])

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
        user_detail = await prisma.user.create(data=user.model_dump())
        return user_detail.model_dump()
    finally:
        await prisma.disconnect()

@router.post("/login")
async def login(user: UserRequest):
    await prisma.connect()
    try:
        # Validate that user exists
        user_detail = await prisma.user.find_unique(where={"email": user.email, "password": user.password})
        if not user_detail:
            raise HTTPException(status_code=404, detail=f"User with email {user.email} not found")
        
        payload = {
            "id": getattr(user_detail, "id", None),
            "email": getattr(user_detail, "email", None),
            "username": getattr(user_detail, "username", None),
        }
        token = jwt.encode(payload, "secret", algorithm="HS256")
        return {"token": token}
    finally:
        await prisma.disconnect()
