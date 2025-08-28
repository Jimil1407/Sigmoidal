from fastapi import APIRouter, HTTPException
from ml.model_train import train, preprocess, get_data
from ml.model_predict import predict
import os

router = APIRouter(prefix="/api/v1/predictions", tags=["predictions"])

@router.post("/train/{symbol}")
async def start_train(symbol: str):
    await train(symbol)
    return {"symbol": symbol, "status": "training_completed"}


@router.get("/predict/{symbol}")
async def get_prediction(symbol: str):
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))
    model_path = os.path.join(models_dir, f"{symbol}.keras")
    if os.path.exists(model_path):
        df = get_data(symbol)
        if df is None:
            raise HTTPException(status_code=502, detail="Failed to fetch market data for prediction")
        X_train, X_test, y_train, y_test = preprocess(df)
        prediction = predict(X_test, df, model_path)
    else:
        raise HTTPException(
            status_code=404, 
            detail=f"Model needs to be trained first for '{symbol}' stock"
        )
    return {"symbol": symbol, "prediction": prediction}

@router.get("/model/status/{symbol}")
async def check_status(symbol: str):
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))
    model_path = os.path.join(models_dir, f"{symbol}.keras")
    if os.path.exists(model_path):
        return {"status": f"Model exists for {symbol} stock. Proceed with prediction"}
       
    else:
        raise HTTPException(
            status_code=404, 
            detail=f"Model needs to be trained first for '{symbol}' stock"
        )
    


