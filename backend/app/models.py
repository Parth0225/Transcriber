from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Transcript(Base):
    __tablename__ = "transcripts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    title: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[datetime] = mapped_column(nullable=False)
    language: Mapped[str] = mapped_column(nullable=False)

    lines: Mapped[List["Line"]] = relationship(
        "Line", back_populates="transcript", cascade="all, delete-orphan"
    )


class Line(Base):
    __tablename__ = "lines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    transcript_id: Mapped[int] = mapped_column(
        ForeignKey("transcripts.id"), nullable=False, index=True
    )
    start_time: Mapped[float] = mapped_column(nullable=False)
    speaker: Mapped[Optional[str]] = mapped_column(nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    transcript: Mapped["Transcript"] = relationship(
        "Transcript", back_populates="lines"
    )
