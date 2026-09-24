from pathlib import Path
import re

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Get the project root directory.
BASE_DIR = Path(__file__).resolve().parents[2]


# Directory where individual company databases are stored.
COMPANIES_DIR = BASE_DIR / "data" / "companies"

COMPANIES_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def create_company_slug(company_name: str) -> str:
    """
    Convert a company name into a safe filename.
    """

    slug = company_name.lower().strip()

    slug = re.sub(
        r"[^a-z0-9]+",
        "_",
        slug,
    )

    slug = slug.strip("_")

    if not slug:
        slug = "company"

    return slug


def get_company_database_path(
    company_name: str,
) -> Path:
    """
    Return the SQLite database path for a company.
    """

    slug = create_company_slug(
        company_name
    )

    return COMPANIES_DIR / f"{slug}.db"


def create_company_database(
    company_name: str,
):
    """
    Create or open a separate database for a company.
    """

    database_path = get_company_database_path(
        company_name
    )

    database_url = (
        f"sqlite:///"
        f"{database_path.as_posix()}"
    )

    engine = create_engine(
        database_url,
        connect_args={
            "check_same_thread": False
        },
    )

    CompanyBase = declarative_base()

    CompanySessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    # Create the employee model for this company's database.
    from app.models.employee import (
        get_employee_model,
    )

    Employee = get_employee_model(
        CompanyBase
    )

    # Create all company-specific tables.
    CompanyBase.metadata.create_all(
        bind=engine
    )

    return {
        "engine": engine,
        "base": CompanyBase,
        "session_local": CompanySessionLocal,
        "database_path": database_path,
        "Employee": Employee,
    }


def get_company_session(
    company_name: str,
):
    """
    Create a database session for a specific company.
    """

    company_database = create_company_database(
        company_name
    )

    session = company_database[
        "session_local"
    ]()

    return session