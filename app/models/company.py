from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.database.database import Base


class Company(Base):
    """
    Stores company information in the main companies database.
    """

    __tablename__ = "companies"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    company_name = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash = Column(
        String(255),
        nullable=False,
    )

    database_name = Column(
        String(255),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )