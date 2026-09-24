from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database.company_database import (
    create_company_database,
)
from app.database.database import get_db
from app.models.company import Company
from app.security import decode_access_token


router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)


security = HTTPBearer()


class EmployeeCreateRequest(BaseModel):
    employee_id: str
    name: str
    email: EmailStr
    department: Optional[str] = None
    phone: Optional[str] = None


def get_logged_in_company(
    credentials: HTTPAuthorizationCredentials,
    db: Session,
):
    """
    Find the company associated with the JWT token.
    """

    try:
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

    return company


@router.post("/")
def add_employee(
    request: EmployeeCreateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
    db: Session = Depends(get_db),
):
    """
    Add an employee to the currently logged-in company's database.
    """

    company = get_logged_in_company(
        credentials,
        db,
    )

    employee_id = (
        request.employee_id.strip()
    )

    name = request.name.strip()

    if not employee_id:
        raise HTTPException(
            status_code=400,
            detail="Employee ID is required.",
        )

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Employee name is required.",
        )

    company_database = create_company_database(
        company.company_name
    )

    Employee = company_database["Employee"]

    company_session = company_database[
        "session_local"
    ]()

    try:
        existing_employee = (
            company_session.query(Employee)
            .filter(
                Employee.employee_id
                == employee_id
            )
            .first()
        )

        if existing_employee:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Employee ID already exists "
                    "in this company."
                ),
            )

        employee = Employee(
            employee_id=employee_id,
            name=name,
            email=str(request.email).lower(),
            department=request.department,
            phone=request.phone,
            face_registered=False,
        )

        company_session.add(employee)
        company_session.commit()
        company_session.refresh(employee)

        return {
            "success": True,
            "message": (
                "Employee added successfully."
            ),
            "company": company.company_name,
            "employee": {
                "id": employee.id,
                "employee_id": employee.employee_id,
                "name": employee.name,
                "email": employee.email,
                "department": employee.department,
                "phone": employee.phone,
                "face_registered": (
                    employee.face_registered
                ),
                "created_at": employee.created_at,
            },
        }

    finally:
        company_session.close()


@router.get("/")
def get_employees(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
    db: Session = Depends(get_db),
):
    """
    Return only employees belonging to the logged-in company.
    """

    company = get_logged_in_company(
        credentials,
        db,
    )

    company_database = create_company_database(
        company.company_name
    )

    Employee = company_database["Employee"]

    company_session = company_database[
        "session_local"
    ]()

    try:
        employees = (
            company_session.query(Employee)
            .order_by(Employee.id.desc())
            .all()
        )

        return {
            "success": True,
            "company": company.company_name,
            "employees": [
                {
                    "id": employee.id,
                    "employee_id": employee.employee_id,
                    "name": employee.name,
                    "email": employee.email,
                    "department": employee.department,
                    "phone": employee.phone,
                    "face_registered": (
                        employee.face_registered
                    ),
                    "created_at": employee.created_at,
                }
                for employee in employees
            ],
        }

    finally:
        company_session.close()