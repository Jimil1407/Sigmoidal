from fastapi import APIRouter, HTTPException
from src.ml.model_train import train
from src.ml.model_predict import predict_stock
from src.ml.model_predict import get_data
import os

router = APIRouter(prefix="/api/v1/predictions", tags=["predictions"])

@router.get("/train/{symbol}")
async def start_train(symbol: str):
    await train(symbol)
    return {"symbol": symbol, "status": "training_completed"}


@router.get("/predict/{symbol}")
async def get_prediction(symbol: str):
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))
    model_path = os.path.join(models_dir, f"{symbol}.keras")
    if os.path.exists(model_path):
        df = await get_data(symbol)
        if df is None:
            raise HTTPException(status_code=502, detail="Failed to fetch market data for prediction")
        prediction_result = await predict_stock(symbol)
        
        # Handle error cases
        if prediction_result == 500:
            raise HTTPException(status_code=500, detail="Error making prediction")
        
        # Convert numpy float to Python float for JSON serialization
        if hasattr(prediction_result, 'item'):  # numpy scalar
            prediction_result = prediction_result.item()
        elif isinstance(prediction_result, (int, float)):
            prediction_result = float(prediction_result)
    else:
        raise HTTPException(
            status_code=404, 
            detail=f"Model needs to be trained first for '{symbol}' stock"
        )
    return {"symbol": symbol, "prediction": prediction_result}

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
    


