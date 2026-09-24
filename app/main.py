from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.database import create_main_database
from app.routes.company import router as company_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Run startup tasks when the FastAPI application starts.
    """

    create_main_database()

    yield


app = FastAPI(
    title="FaceAttend",
    description="Smart Face Recognition Attendance System",
    version="1.0.0",
    lifespan=lifespan,
)


# Register company routes.
app.include_router(company_router)


@app.get("/")
def home():
    """
    Basic API status endpoint.
    """

    return {
        "success": True,
        "message": "FaceAttend API is running",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    """
    Health-check endpoint.
    """

    return {
        "success": True,
        "status": "online",
        "database": "connected",
    }