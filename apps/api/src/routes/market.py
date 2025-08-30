from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
import os
from datetime import datetime, timedelta, timezone
import httpx

router = APIRouter(prefix="/api/v1/market", tags=["market"])


@router.get("/quote/{symbol}")
async def get_current_price(symbol: str):
    api_key = os.getenv("TWELVE_DATA_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="TWELVE_DATA_API_KEY not configured")

    url = "https://api.twelvedata.com/price"
    params = {"symbol": symbol.upper(), "apikey": api_key}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        data = resp.json()
        if "price" not in data:
            # Twelve Data may return an error object with code/message
            message = data.get("message") or data
            raise HTTPException(status_code=404, detail=str(message))
        return {"symbol": symbol.upper(), "price": float(data["price"])}


@router.get("/quote")
async def get_prices_multiple(symbols: str = Query(..., description="Comma Separated Symbols")):
    api_key = os.getenv("TWELVE_DATA_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="TWELVE_DATA_API_KEY not yet configured")

    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    # Twelve Data supports multiple symbols in one call for /price
    url = "https://api.twelvedata.com/price"
    params = {"symbol": ",".join(symbol_list), "apikey": api_key}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, params=params)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        data = resp.json()

    results = []
    # When multiple symbols are requested, response is a dict keyed by symbol
    for sym in symbol_list:
        entry = data.get(sym)
        if not entry:
            results.append({"symbol": sym, "error": "no data found"})
            continue
        if "price" in entry:
            results.append({"symbol": sym, "price": float(entry["price"])})
        else:
            results.append({"symbol": sym, "error": entry.get("message", "no data")})
    return results


@router.get("/history/{symbol}")
async def get_historical_data(
    symbol: str,
    period: str = Query("1mo", description="1d, 5d, 1mo, 6mo, 1y, 5y"),
    interval: str = Query("1d", description="1min, 5min, 15min, 1h, 1day, 1week, 1month")
):
    api_key = os.getenv("TWELVE_DATA_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="TWELVE_DATA_API_KEY not configured")

    # Map to Twelve Data interval values
    interval_map = {
        "1m": "1min",
        "5m": "5min",
        "15m": "15min",
        "1h": "1h",
        "1d": "1day",
        "1wk": "1week",
        "1mo": "1month",
    }
    td_interval = interval_map.get(interval, "1day")

    # Compute date range
    period_map = {
        "1d": timedelta(days=1),
        "5d": timedelta(days=5),
        "1mo": timedelta(days=30),
        "6mo": timedelta(days=182),
        "1y": timedelta(days=365),
        "5y": timedelta(days=365 * 5),
    }
    delta = period_map.get(period, timedelta(days=30))
    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - delta

    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol.upper(),
        "interval": td_interval,
        "start_date": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": end_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": "UTC",
        "apikey": api_key,
    }
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(url, params=params)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        data = resp.json()
        if data.get("status") not in ("ok", None) or "values" not in data:
            raise HTTPException(status_code=404, detail=data.get("message", "no data"))

    values = data.get("values", [])
    records = []
    for v in reversed(values):  # ensure chronological order
        records.append({
            "Date": v.get("datetime"),
            "Open": float(v.get("open")) if v.get("open") is not None else None,
            "High": float(v.get("high")) if v.get("high") is not None else None,
            "Low": float(v.get("low")) if v.get("low") is not None else None,
            "Close": float(v.get("close")) if v.get("close") is not None else None,
            "Volume": int(float(v.get("volume"))) if v.get("volume") is not None else None,
        })

    return JSONResponse(content=records)


