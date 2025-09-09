from fastapi import APIRouter, HTTPException, Request
from prisma import Prisma
from pydantic import BaseModel
import os
from jose import jwt
import httpx

prisma = Prisma()

async def get_prisma():
    """Get Prisma client, connect if not already connected"""
    try:
        await prisma.connect()
    except Exception:
        # Already connected or connection error, continue
        pass
    return prisma

class TradeRequest(BaseModel):
    stockSymbol: str
    tradeType: str  # "BUY" or "SELL"
    quantity: int
    price: float = 0.0
    status: str = "PENDING"  # default value

router = APIRouter(prefix="/api/v1/portfolio", tags=["portfolio"])


@router.get("/myportfolio")
async def get_portfolio(request: Request):
    db = await get_prisma()
    try:
        token = request.headers.get("Authorization")
        userId = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"]) ["id"]
        portfolio_detail = await db.portfolio.find_first(where={"userId": userId})
        if portfolio_detail is None:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        return portfolio_detail.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/myportfolio/positions")
async def get_positions(request: Request):
    db = await get_prisma()
    try:
        token = request.headers.get("Authorization")
        userId = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"]) ["id"]
        portfolio_detail = await db.portfolio.find_first(where={"userId": userId})
        position_detail = await db.position.find_many(where={"portfolioId": portfolio_detail.id})
        return [position.model_dump() for position in position_detail]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/myportfolio/trades")
async def get_trades(request: Request):
    db = await get_prisma()
    try:
        token = request.headers.get("Authorization")
        userId = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"]) ["id"]
        portfolio_detail = await db.portfolio.find_first(where={"userId": userId})
        trades_detail = await db.trade.find_many(where={"portfolioId": portfolio_detail.id})
        return [trade.model_dump() for trade in trades_detail]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/myportfolio/trade")
async def make_trade(trade: TradeRequest, request: Request):
    db = await get_prisma()
    try:
        # Fetch live price directly
        symbol = trade.stockSymbol.upper()
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"http://localhost:8080/api/v1/market/quote/{symbol}")
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=f"Failed to fetch price for {symbol}: {resp.text}")
            live = resp.json()
            current_price = float(live.get("price"))
            if not current_price or current_price <= 0:
                raise HTTPException(status_code=400, detail=f"Invalid live price for {symbol}")

        # Ensure Stock exists to satisfy FK constraints (auto-create if missing)
        try:
            await db.stock.upsert(
                where={"symbol": symbol},
                data={
                    "create": {"symbol": symbol, "name": symbol},
                    "update": {"name": symbol},
                },
            )
        except Exception:
            # If upsert not supported in this client version, fallback to find-or-create
            existing = await db.stock.find_unique(where={"symbol": symbol})
            if not existing:
                await db.stock.create(data={"symbol": symbol, "name": symbol})

        # Validate portfolio exists
        token = request.headers.get("Authorization")
        userId = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"]) ["id"]
        portfolio = await db.portfolio.find_first(where={"userId": userId})
        if not portfolio:
            raise HTTPException(status_code=404, detail=f"Portfolio with ID {userId} not found")
        
        # Transaction: create/update position, update portfolio, create trade and mark COMPLETED
        async with db.tx() as tx:
            # Get existing position by (portfolioId, stockSymbol)
            existing_position = await tx.position.find_first(
                where={
                    "portfolioId": portfolio.id,
                    "stockSymbol": trade.stockSymbol,
                }
            )

            trade_qty = trade.quantity
            trade_type = trade.tradeType.upper()

            if not existing_position:
                if trade_type == "SELL":
                    raise HTTPException(status_code=400, detail="Cannot sell a position you don't own")
                position = await tx.position.create(data={
                    "portfolioId": portfolio.id,
                    "stockSymbol": trade.stockSymbol,
                    "quantity": trade_qty,
                    "avgPrice": current_price,
                })
            else:
                if trade_type == "BUY":
                    new_quantity = existing_position.quantity + trade_qty
                    new_avg_price = (
                        (existing_position.avgPrice * existing_position.quantity + current_price * trade_qty) / new_quantity
                    ) if new_quantity > 0 else 0
                else:  # SELL
                    new_quantity = existing_position.quantity - trade_qty
                    if new_quantity < 0:
                        raise HTTPException(status_code=400, detail="Sell quantity exceeds position size")
                    # Average price typically unchanged on sell; reset to 0 if flat
                    new_avg_price = existing_position.avgPrice if new_quantity > 0 else 0

                position = await tx.position.update(
                    where={"id": existing_position.id},
                    data={
                        "quantity": new_quantity,
                        "avgPrice": new_avg_price,
                    }
                )

            # Update portfolio totals depending on trade type
            delta = trade_qty * current_price
            if trade_type == "BUY":
                new_total = portfolio.totalValue + delta
                new_cash = portfolio.cash - delta
            else:
                new_total = portfolio.totalValue - delta
                new_cash = portfolio.cash + delta

            await tx.portfolio.update(
                where={"id": portfolio.id},
                data={
                    "totalValue": new_total,
                    "cash": new_cash,
                }
            )

            # Create trade as PENDING, then mark COMPLETED
            created_trade = await tx.trade.create(
                data={
                    "portfolioId": portfolio.id,
                    "stockSymbol": trade.stockSymbol,
                    "tradeType": trade_type,
                    "quantity": trade_qty,
                    "price": current_price,
                    "status": "PENDING",
                }
            )

            completed = await tx.trade.update(
                where={"id": created_trade.id},
                data={"status": "COMPLETED"}
            )

        return completed.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
