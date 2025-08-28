from fastapi import APIRouter, HTTPException
from prisma import Prisma
from pydantic import BaseModel

prisma = Prisma()

class TradeRequest(BaseModel):
    stockId: int
    tradeType: str  # "BUY" or "SELL"
    quantity: int
    price: float
    status: str = "PENDING"  # default value

router = APIRouter(prefix="/api/v1/portfolio", tags=["portfolio"])


@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: str):
    await prisma.connect()
    try:
        portfolio_detail = await prisma.portfolio.find_unique(where={"id": int(portfolio_id)})
        if portfolio_detail is None:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        return portfolio_detail.model_dump()
    finally:
        await prisma.disconnect()

@router.get("/{portfolio_id}/positions")
async def get_positions(portfolio_id: str):
    await prisma.connect()
    try:
        position_detail = await prisma.position.find_many(where={"portfolioId": int(portfolio_id)})
        return [position.model_dump() for position in position_detail]
    finally:
        await prisma.disconnect()

@router.get("/{portfolio_id}/trades")
async def get_trades(portfolio_id: str):
    await prisma.connect()
    try:
        trades_detail = await prisma.trade.find_many(where={"portfolioId": int(portfolio_id)})
        return [trade.model_dump() for trade in trades_detail]
    finally:
        await prisma.disconnect()

@router.post("/{portfolio_id}/trade")
async def make_trade(portfolio_id: str, trade: TradeRequest):
    await prisma.connect()
    try:
        # Validate that stock exists
        stock = await prisma.stock.find_unique(where={"id": trade.stockId})
        if not stock:
            raise HTTPException(status_code=404, detail=f"Stock with ID {trade.stockId} not found")
        
        # Validate that portfolio exists
        portfolio = await prisma.portfolio.find_unique(where={"id": int(portfolio_id)})
        if not portfolio:
            raise HTTPException(status_code=404, detail=f"Portfolio with ID {portfolio_id} not found")
        
        trades_detail = await prisma.trade.create(
            data={
                "portfolioId": int(portfolio_id),
                "stockId": trade.stockId,
                "tradeType": trade.tradeType,
                "quantity": trade.quantity,
                "price": trade.price,
                "status": trade.status,
            })
        return trades_detail.model_dump()
    finally:
        await prisma.disconnect()
