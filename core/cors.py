from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

def setup_cors(app: FastAPI, origins: list[str] | None = None) -> None:
    """
    Setup CORS middleware for the FastAPI app.
    
    Args:
        app: FastAPI application instance
        origins: Optional list of allowed origins. If not provided, uses CORS_ORIGINS from .env
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
