from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    phone: Mapped[str] = mapped_column(String(15), unique=True, index=True)

    
    name: Mapped[str | None] = mapped_column(String(100))
    age: Mapped[int | None]
    gender: Mapped[str | None] = mapped_column(String(10))
    county: Mapped[str | None] = mapped_column(String(50))
    town: Mapped[str | None] = mapped_column(String(50))

    
    education: Mapped[str | None] = mapped_column(String(50))
    profession: Mapped[str | None] = mapped_column(String(50))
    marital_status: Mapped[str | None] = mapped_column(String(30))
    religion: Mapped[str | None] = mapped_column(String(30))
    ethnicity: Mapped[str | None] = mapped_column(String(50))

    
    description: Mapped[str | None] = mapped_column(Text)

    registration_stage: Mapped[str] = mapped_column(String(20), default="STARTED")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )