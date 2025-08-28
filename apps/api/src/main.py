from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import yfinance as yf
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Trading Dashboard API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Trading Dashboard API"}


@app.get("/dashboard/{ticker}")

@app.get("/api/v1/market/quote/{symbol}")
async def getCurrPrice(symbol: str):
    ticker = yf.Ticker(symbol).history(interval="1m", period="1d")
    price = float(ticker['Close'][0])   # convert numpy.float64 → Python float
    return {"symbol": symbol, "price": price}

@app.get("/api/v1/market/history/{symbol}")
async def getHistoricalData(
    symbol: str,
    period: str = Query("1mo", description="Data period (e.g. 1d, 5d, 1mo, 6mo, 1y, 5y, max)"),
    interval: str = Query("1d", description="Data interval (e.g. 1m, 5m, 15m, 1h, 1d, 1wk, 1mo)")
):
    # Fetch data from yfinance
    df = yf.Ticker(symbol).history(period=period, interval=interval)

    # Convert dataframe to JSON serializable format
    df = df.reset_index()
    df["Date"] = df["Date"].astype(str)  # convert Timestamps to strings
    result = df.to_dict(orient="records")

    return JSONResponse(content=result)