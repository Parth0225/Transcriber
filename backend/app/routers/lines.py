from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.models import Line
from app.schemas import LineCreate, LineUpdate, LineOut

router = APIRouter(prefix="/lines", tags=["lines"])


@router.get("/", response_model=List[LineOut])
def list_lines(db: Session = Depends(get_db)):
    return db.query(Line).all()


@router.post("/", response_model=LineOut, status_code=status.HTTP_201_CREATED)
def create_line(payload: LineCreate, db: Session = Depends(get_db)):
    line = Line(**payload.model_dump())
    db.add(line)
    db.commit()
    db.refresh(line)
    return line


@router.get("/{line_id}", response_model=LineOut)
def get_line(line_id: int, db: Session = Depends(get_db)):
    line = db.get(Line, line_id)
    if not line:
        raise HTTPException(status_code=404, detail=f"Line with id {line_id} not found")
    return line


@router.put("/{line_id}", response_model=LineOut)
def update_line(line_id: int, payload: LineUpdate, db: Session = Depends(get_db)):
    line = db.get(Line, line_id)
    if not line:
        raise HTTPException(status_code=404, detail=f"Line with id {line_id} not found")
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(line, key, value)
    db.commit()
    db.refresh(line)
    return line


@router.delete("/{line_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_line(line_id: int, db: Session = Depends(get_db)):
    line = db.get(Line, line_id)
    if not line:
        raise HTTPException(status_code=404, detail=f"Line with id {line_id} not found")
    db.delete(line)
    db.commit()
    return None
