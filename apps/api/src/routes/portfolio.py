from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/portfolio", tags=["portfolio"])


@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: str):
    return {"portfolio_id": portfolio_id, "data": 0}


