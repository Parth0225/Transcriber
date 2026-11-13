from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


class TranscriptCreate(BaseModel):
    title: str
    date: datetime
    language: str

    model_config = ConfigDict(from_attributes=True)


class TranscriptUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[datetime] = None
    language: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TranscriptOut(BaseModel):
    id: int
    created_at: datetime
    title: str
    date: datetime
    language: str

    model_config = ConfigDict(from_attributes=True)


class LineCreate(BaseModel):
    transcript_id: int
    start_time: float
    speaker: Optional[str] = None
    text: str

    model_config = ConfigDict(from_attributes=True)


class LineUpdate(BaseModel):
    transcript_id: Optional[int] = None
    start_time: Optional[float] = None
    speaker: Optional[Optional[str]] = None
    text: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class LineOut(BaseModel):
    id: int
    created_at: datetime
    transcript_id: int
    start_time: float
    speaker: Optional[str] = None
    text: str

    model_config = ConfigDict(from_attributes=True)
