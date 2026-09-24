import hashlib
import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database.company_database import create_company_database
from app.database.database import get_db
from app.models.company import Company


router = APIRouter(
    prefix="/company",
    tags=["Company"],
)


def hash_password(password: str) -> str:
    """
    Create a secure password hash using PBKDF2.
    """

    salt = os.urandom(16)

    iterations = 600_000

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
    )

    return (
        f"pbkdf2_sha256${iterations}$"
        f"{salt.hex()}${password_hash.hex()}"
    )


class CompanyRegisterRequest(BaseModel):
    company_name: str
    email: EmailStr
    password: str


@router.post("/register")
def register_company(
    request: CompanyRegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register a company and create its separate database.
    """

    company_name = request.company_name.strip()
    email = str(request.email).lower().strip()

    if not company_name:
        raise HTTPException(
            status_code=400,
            detail="Company name is required.",
        )

    if len(request.password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 6 characters.",
        )

    # Check whether the company already exists.
    existing_company = (
        db.query(Company)
        .filter(
            Company.company_name == company_name
        )
        .first()
    )

    if existing_company:
        raise HTTPException(
            status_code=409,
            detail="Company already exists.",
        )

    # Check whether the email is already registered.
    existing_email = (
        db.query(Company)
        .filter(
            Company.email == email
        )
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered.",
        )

    # Create a separate database for this company.
    company_database = create_company_database(
        company_name
    )

    database_path = company_database["database_path"]

    database_name = Path(
        database_path
    ).name

    # Hash the password.
    password_hash = hash_password(
        request.password
    )

    # Create company record in the main database.
    company = Company(
        company_name=company_name,
        email=email,
        password_hash=password_hash,
        database_name=database_name,
    )

    db.add(company)
    db.commit()
    db.refresh(company)

    return {
        "success": True,
        "message": "Company registered successfully.",
        "company": {
            "id": company.id,
            "company_name": company.company_name,
            "email": company.email,
            "database_name": company.database_name,
            "database_path": str(database_path),
            "created_at": company.created_at,
        },
    }


@router.get("/list")
def list_companies(
    db: Session = Depends(get_db),
):
    """
    Return all registered companies.
    """

    companies = (
        db.query(Company)
        .order_by(Company.id.desc())
        .all()
    )

    return {
        "success": True,
        "companies": [
            {
                "id": company.id,
                "company_name": company.company_name,
                "email": company.email,
                "database_name": company.database_name,
                "created_at": company.created_at,
            }
            for company in companies
        ],
    }