from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from routes.market import router as market_router
from routes.predictions import router as predictions_router
from routes.portfolio import router as portfolio_router
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

# Mount modular routers
app.include_router(market_router)
app.include_router(predictions_router)
app.include_router(portfolio_router)

