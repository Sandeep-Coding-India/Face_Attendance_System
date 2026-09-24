from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Get the project root directory.
BASE_DIR = Path(__file__).resolve().parents[2]


# Create a folder for application data.
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


# Main database stores company information.
DATABASE_FILE = DATA_DIR / "companies.db"

DATABASE_URL = f"sqlite:///{DATABASE_FILE.as_posix()}"


# SQLite engine.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


# Database session factory.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Base class for SQLAlchemy models.
Base = declarative_base()


def get_db():
    """
    Provide a database session to API routes.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def create_main_database():
    """
    Create all tables belonging to the main company database.
    """

    # Import models before creating tables.
    from app.models.company import Company

    Base.metadata.create_all(bind=engine)