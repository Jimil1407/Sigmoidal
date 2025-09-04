from fastapi import APIRouter, HTTPException, Request
from prisma import Prisma
from pydantic import BaseModel
import os
from jose import jwt

prisma = Prisma()

class TradeRequest(BaseModel):
    stockId: int
    tradeType: str  # "BUY" or "SELL"
    quantity: int
    price: float
    status: str = "PENDING"  # default value

router = APIRouter(prefix="/api/v1/portfolio", tags=["portfolio"])


@router.get("/myportfolio")
async def get_portfolio(request: Request):
    await prisma.connect()
    try:
        token = request.headers.get("Authorization")
        userId = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])["id"]
        print(userId)
        portfolio_detail = await prisma.portfolio.find_first(where={"userId": userId})
        if portfolio_detail is None:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        return portfolio_detail.model_dump()
    finally:
        await prisma.disconnect()

@router.get("/myportfolio/positions")
async def get_positions(request: Request):
    await prisma.connect()
    try:
        token = request.headers.get("Authorization")
        userId = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])["id"]
        portfolio_detail = await prisma.portfolio.find_first(where={"userId": userId})
        position_detail = await prisma.position.find_many(where={"portfolioId": portfolio_detail.id})
        return [position.model_dump() for position in position_detail]
    finally:
        await prisma.disconnect()

@router.get("/myportfolio/trades")
async def get_trades(request: Request):
    await prisma.connect()
    try:
        token = request.headers.get("Authorization")
        userId = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])["id"]
        portfolio_detail = await prisma.portfolio.find_first(where={"userId": userId})
        trades_detail = await prisma.trade.find_many(where={"portfolioId": portfolio_detail.id})
        return [trade.model_dump() for trade in trades_detail]
    finally:
        await prisma.disconnect()

@router.post("/myportfolio/trade")
async def make_trade(trade: TradeRequest, request: Request):
    await prisma.connect()
    try:
        # Validate that stock exists
        stock = await prisma.stock.find_unique(where={"id": trade.stockId})
        if not stock:
            raise HTTPException(status_code=404, detail=f"Stock with ID {trade.stockId} not found")
        
        # Validate that portfolio exists
        token = request.headers.get("Authorization")
        userId = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])["id"]
        portfolio = await prisma.portfolio.find_first(where={"userId": userId})
        if not portfolio:
            raise HTTPException(status_code=404, detail=f"Portfolio with ID {userId} not found")
        
        trades_detail = await prisma.trade.create(
            data={
                "portfolioId": portfolio.id,
                "stockId": trade.stockId,
                "tradeType": trade.tradeType,
                "quantity": trade.quantity,
                "price": trade.price,
                "status": trade.status,
            })
        return trades_detail.model_dump()
    finally:
        await prisma.disconnect()
