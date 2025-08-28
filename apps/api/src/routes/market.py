from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import yfinance as yf

router = APIRouter(prefix="/api/v1/market", tags=["market"])


@router.get("/quote/{symbol}")
async def get_current_price(symbol: str):
    ticker = yf.Ticker(symbol).history(interval="1m", period="1d")
    price = float(ticker['Close'][0])
    return {"symbol": symbol, "price": price}


@router.get("/quote")
async def get_prices_multiple(symbols: str = Query(..., description="Comma Separated Symbols")):
    results = []
    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]

    for symbol in symbol_list:
        ticker_data = yf.Ticker(symbol).history(interval="1m", period="1d")

        if ticker_data.empty or 'Close' not in ticker_data or ticker_data['Close'].isnull().all():
            results.append({
                "symbol": symbol,
                "error": "no data found"
            })
        else:
            close_prices = ticker_data['Close'].dropna()
            if not close_prices.empty:
                price = float(close_prices.iloc[-1])
                results.append({
                    "symbol": symbol,
                    "price": price
                })
            else:
                results.append({
                    "symbol": symbol,
                    "price": "no close price"
                })

    return results


@router.get("/history/{symbol}")
async def get_historical_data(
    symbol: str,
    period: str = Query("1mo", description="Data period (e.g. 1d, 5d, 1mo, 6mo, 1y, 5y, max)"),
    interval: str = Query("1d", description="Data interval (e.g. 1m, 5m, 15m, 1h, 1d, 1wk, 1mo)")
):
    df = yf.Ticker(symbol).history(period=period, interval=interval)
    df = df.reset_index()
    df["Date"] = df["Date"].astype(str)
    result = df.to_dict(orient="records")
    return JSONResponse(content=result)


