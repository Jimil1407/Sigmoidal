from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from src.routes.market import router as market_router
from src.routes.predictions import router as predictions_router
from src.routes.portfolio import router as portfolio_router
from src.routes.users import router as users_router
from prisma import Prisma
from src.websocket import register_websocket
import asyncio

# Configure logging - Set to WARNING to reduce noise and security risks
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Silence all third-party loggers
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)
logging.getLogger("uvicorn.access").setLevel(logging.ERROR)
logging.getLogger("uvicorn.error").setLevel(logging.ERROR)
    

app = FastAPI(title="Trading Dashboard API", version="1.0.0")

# Configure timeout for long-running requests
import uvicorn
from uvicorn.config import Config

# CORS configuration - Temporary permissive setup for deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins temporarily
    allow_credentials=False,  # Set to False when using wildcard origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Trading Dashboard API"}

# Mount modular routers
app.include_router(market_router)
app.include_router(predictions_router)
app.include_router(portfolio_router)
app.include_router(users_router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Trading Dashboard API...")
    try:
        # Test database connection if needed
        logger.info("API startup completed successfully")
    except Exception as e:
        logger.error(f"Startup error: {e}")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return {"error": "Internal server error", "detail": str(exc)}

register_websocket(app)
