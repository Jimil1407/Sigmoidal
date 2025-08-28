from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/predictions", tags=["predictions"])


@router.get("/predict/{symbol}")
async def get_prediction(symbol: str):
    return {"symbol": symbol, "prediction": 0}


@router.post("/train/{symbol}")
async def start_train(symbol: str):
    return {"symbol": symbol, "status": "training_started"}


@router.get("/model/status/{symbol}")
async def check_status(symbol: str):
    return {"symbol": symbol, "status": "idle"}


