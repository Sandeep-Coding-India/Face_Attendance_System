from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database.company_database import (
    create_company_database,
)
from app.database.database import get_db
from app.models.company import Company
from app.security import (
    create_access_token,
    hash_password,
    verify_password,
)


router = APIRouter(
    prefix="/company",
    tags=["Company"],
)


security = HTTPBearer()


class CompanyRegisterRequest(BaseModel):
    company_name: str
    email: EmailStr
    password: str


class CompanyLoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register_company(
    request: CompanyRegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new company and create its database.
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

    company_database = create_company_database(
        company_name
    )

    database_path = company_database[
        "database_path"
    ]

    database_name = Path(
        database_path
    ).name

    password_hash = hash_password(
        request.password
    )

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
            "created_at": company.created_at,
        },
    }


@router.post("/login")
def login_company(
    request: CompanyLoginRequest,
    db: Session = Depends(get_db),
):
    """
    Login a company and return an access token.
    """

    email = str(request.email).lower().strip()

    company = (
        db.query(Company)
        .filter(
            Company.email == email
        )
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    password_valid = verify_password(
        request.password,
        company.password_hash,
    )

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(
        company.id
    )

    return {
        "success": True,
        "message": "Login successful.",
        "access_token": access_token,
        "token_type": "bearer",
        "company": {
            "id": company.id,
            "company_name": company.company_name,
            "email": company.email,
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


@router.get("/me")
def company_me(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
    db: Session = Depends(get_db),
):
    """
    Return the currently logged-in company.
    """

    try:
        from app.security import decode_access_token

        company_id = decode_access_token(
            credentials.credentials
        )

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token.",
        )

    company = (
        db.query(Company)
        .filter(
            Company.id == company_id
        )
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=401,
            detail="Company not found.",
        )

    return {
        "success": True,
        "company": {
            "id": company.id,
            "company_name": company.company_name,
            "email": company.email,
            "database_name": company.database_name,
        },
    }