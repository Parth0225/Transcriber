from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime
from io import BytesIO

from app.db import get_db
from app.models import Transcript, Line
from app.schemas import (
    TranscriptCreate,
    TranscriptUpdate,
    TranscriptOut,
)

router = APIRouter(prefix="/transcripts", tags=["transcripts"])


@router.get("/", response_model=List[TranscriptOut])
def list_transcripts(db: Session = Depends(get_db)):
    transcripts = db.query(Transcript).order_by(Transcript.id).all()
    return transcripts


@router.post("/", response_model=TranscriptOut, status_code=status.HTTP_201_CREATED)
def create_transcript(
    payload: TranscriptCreate, db: Session = Depends(get_db)
):
    transcript = Transcript(**payload.model_dump())
    db.add(transcript)
    db.commit()
    db.refresh(transcript)
    return transcript


@router.get("/{transcript_id}", response_model=TranscriptOut)
def get_transcript(transcript_id: int, db: Session = Depends(get_db)):
    transcript = (
        db.query(Transcript)
        .options(joinedload(Transcript.lines))
        .filter(Transcript.id == transcript_id)
        .first()
    )
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transcript with id {transcript_id} not found",
        )
    return transcript


@router.put("/{transcript_id}", response_model=TranscriptOut)
def update_transcript(
    transcript_id: int,
    payload: TranscriptUpdate,
    db: Session = Depends(get_db),
):
    transcript = db.query(Transcript).filter(Transcript.id == transcript_id).first()
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transcript with id {transcript_id} not found",
        )
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(transcript, field, value)
    db.commit()
    db.refresh(transcript)
    return transcript


@router.delete("/{transcript_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transcript(transcript_id: int, db: Session = Depends(get_db)):
    transcript = db.query(Transcript).filter(Transcript.id == transcript_id).first()
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transcript with id {transcript_id} not found",
        )
    db.delete(transcript)
    db.commit()
    return


@router.get("/{transcript_id}/download")
def download_transcript(transcript_id: int, db: Session = Depends(get_db)):
    transcript = (
        db.query(Transcript)
        .options(joinedload(Transcript.lines))
        .filter(Transcript.id == transcript_id)
        .first()
    )
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transcript with id {transcript_id} not found",
        )
    lines = sorted(transcript.lines, key=lambda l: l.start_time)
    content_lines = [
        f"[{line.start_time:.2f}] {line.speaker + ': ' if line.speaker else ''}{line.text}"
        for line in lines
    ]
    header = f"{transcript.date.date()} - {transcript.title}\nLanguage: {transcript.language}\n\n"
    full_content = header + "\n".join(content_lines) + "\n"
    byte_content = full_content.encode("utf-8")
    file_like = BytesIO(byte_content)
    filename = f"{transcript.date.date()}-{transcript.title}.txt".replace(" ", "_")
    return StreamingResponse(
        file_like,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/search", response_model=List[TranscriptOut])
def search_transcripts(
    body: dict = Body(...), db: Session = Depends(get_db)
):
    query = body.get("query", "").strip()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query string must be provided",
        )
    matching_transcripts = (
        db.query(Transcript)
        .join(Line)
        .filter(Line.text.ilike(f"%{query}%"))
        .distinct()
        .all()
    )
    return matching_transcripts
