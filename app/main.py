from fastapi import FastAPI
from fastapi.responses import JSONResponse


# Create the FastAPI application.
app = FastAPI(
    title="FaceAttend",
    description="Smart Face Recognition Attendance System",
    version="1.0.0",
)


@app.get("/")
def home():
    """
    Basic home endpoint.

    This endpoint is used to confirm that
    the FastAPI server is running correctly.
    """

    return {
        "success": True,
        "message": "FaceAttend API is running",
    }


@app.get("/health")
def health():
    """
    Health-check endpoint.

    This will later be used by the dashboard
    to check whether the API is online.
    """

    return {
        "success": True,
        "status": "online",
    }