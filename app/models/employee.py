from datetime import datetime


def get_employee_model(CompanyBase):
    """
    Create the Employee model for a specific company database.
    """

    from sqlalchemy import (
        Boolean,
        Column,
        DateTime,
        Integer,
        String,
    )

    class Employee(CompanyBase):
        """
        Employee data belonging to one company.
        """

        __tablename__ = "employees"

        id = Column(
            Integer,
            primary_key=True,
            index=True,
        )

        employee_id = Column(
            String(50),
            unique=True,
            nullable=False,
            index=True,
        )

        name = Column(
            String(150),
            nullable=False,
        )

        email = Column(
            String(255),
            nullable=False,
        )

        department = Column(
            String(100),
            nullable=True,
        )

        phone = Column(
            String(30),
            nullable=True,
        )

        face_registered = Column(
            Boolean,
            default=False,
            nullable=False,
        )

        created_at = Column(
            DateTime,
            default=datetime.utcnow,
            nullable=False,
        )

        updated_at = Column(
            DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            nullable=False,
        )

    return Employee