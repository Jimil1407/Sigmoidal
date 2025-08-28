from fastapi import APIRouter, HTTPException
from prisma import Prisma

prisma = Prisma()

router = APIRouter(prefix="/api/v1/portfolio", tags=["portfolio"])

@router.get("/all")
async def get_all_portfolios():
    await prisma.connect()
    try:
        portfolios = await prisma.portfolio.find_many()
        return [portfolio.model_dump() for portfolio in portfolios]
    finally:
        await prisma.disconnect()


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
