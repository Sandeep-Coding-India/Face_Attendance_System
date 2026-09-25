from fastapi import FastAPI


app = FastAPI(
    title="Face Attendance System",
    description="Advanced Multi-Company Face Attendance Management System",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "success": True,
        "message": "Face Attendance System API is running",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    return {
        "success": True,
        "status": "healthy",
    }