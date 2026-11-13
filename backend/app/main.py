import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (register tables)
from app.db import Base, engine
from app.routers import transcripts, lines

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Transcriber App")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(transcripts.router)
app.include_router(lines.router)
