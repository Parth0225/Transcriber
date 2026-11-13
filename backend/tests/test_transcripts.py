import pytest
from datetime import datetime, timezone, timedelta
from fastapi import status

@pytest.fixture
def transcript_payload():
    return {
        "title": "Team Meeting",
        "date": datetime(2023, 5, 17, 14, 30, tzinfo=timezone.utc).isoformat(),
        "language": "en",
    }

def test_create_transcript_success(client, transcript_payload):
    response = client.post("/transcripts/", json=transcript_payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == transcript_payload["title"]
    assert data["language"] == transcript_payload["language"]
    assert "id" in data
    assert "created_at" in data

def test_create_transcript_validation_error(client):
    # missing required field 'title'
    payload = {
        "date": datetime.now(timezone.utc).isoformat(),
        "language": "en",
    }
    response = client.post("/transcripts/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_list_transcripts(client, transcript_payload):
    # create two transcripts
    client.post("/transcripts/", json=transcript_payload)
    payload2 = transcript_payload.copy()
    payload2["title"] = "Project Kickoff"
    client.post("/transcripts/", json=payload2)

    response = client.get("/transcripts/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    titles = [t["title"] for t in data]
    assert "Team Meeting" in titles
    assert "Project Kickoff" in titles

def test_get_transcript_success(client, transcript_payload):
    create_resp = client.post("/transcripts/", json=transcript_payload)
    tid = create_resp.json()["id"]

    resp = client.get(f"/transcripts/{tid}")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["id"] == tid
    assert data["title"] == transcript_payload["title"]

def test_get_transcript_not_found(client):
    resp = client.get("/transcripts/9999")
    assert resp.status_code == status.HTTP_404_NOT_FOUND

def test_update_transcript_success(client, transcript_payload):
    create_resp = client.post("/transcripts/", json=transcript_payload)
    tid = create_resp.json()["id"]

    update_payload = {"title": "Updated Title"}
    resp = client.put(f"/transcripts/{tid}", json=update_payload)
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["title"] == "Updated Title"
    # unchanged fields remain
    assert data["language"] == transcript_payload["language"]

def test_update_transcript_not_found(client):
    resp = client.put("/transcripts/9999", json={"title": "X"})
    assert resp.status_code == status.HTTP_404_NOT_FOUND

def test_delete_transcript_success(client, transcript_payload):
    create_resp = client.post("/transcripts/", json=transcript_payload)
    tid = create_resp.json()["id"]

    del_resp = client.delete(f"/transcripts/{tid}")
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT

    # ensure it is gone
    get_resp = client.get(f"/transcripts/{tid}")
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND

def test_delete_transcript_not_found(client):
    resp = client.delete("/transcripts/9999")
    assert resp.status_code == status.HTTP_404_NOT_FOUND

def test_download_transcript_content(client, transcript_payload):
    # create transcript
    create_resp = client.post("/transcripts/", json=transcript_payload)
    tid = create_resp.json()["id"]

    # add lines directly via DB session
    from app.db import SessionLocal
    from app.models import Line

    db = SessionLocal()
    line1 = Line(
        transcript_id=tid,
        start_time=0.0,
        speaker="Alice",
        text="Welcome everyone",
    )
    line2 = Line(
        transcript_id=tid,
        start_time=12.5,
        speaker=None,
        text="Discussion started",
    )
    db.add_all([line1, line2])
    db.commit()
    db.close()

    resp = client.get(f"/transcripts/{tid}/download")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.headers["content-type"].startswith("text/plain")
    content = resp.content.decode("utf-8")
    header_line = f"{datetime.fromisoformat(transcript_payload['date']).date()} - {transcript_payload['title']}"
    assert header_line in content
    assert "Language: en" in content
    assert "[0.00] Alice: Welcome everyone" in content
    assert "[12.50] Discussion started" in content

def test_download_transcript_not_found(client):
    resp = client.get("/transcripts/9999/download")
    assert resp.status_code == status.HTTP_404_NOT_FOUND

def test_search_transcripts_success(client, transcript_payload):
    # create transcript with lines
    create_resp = client.post("/transcripts/", json=transcript_payload)
    tid = create_resp.json()["id"]

    from app.db import SessionLocal
    from app.models import Line

    db = SessionLocal()
    db.add_all([
        Line(transcript_id=tid, start_time=1.0, speaker="Bob", text="Project Alpha kickoff"),
        Line(transcript_id=tid, start_time=2.0, speaker="Alice", text="Discuss budget"),
    ])
    db.commit()
    db.close()

    resp = client.post("/transcripts/search", json={"query": "budget"})
    assert resp.status_code == status.HTTP_200_OK
    results = resp.json()
    assert any(t["id"] == tid for t in results)

def test_search_transcripts_missing_query(client):
    resp = client.post("/transcripts/search", json={})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST

def test_search_transcripts_no_match(client):
    resp = client.post("/transcripts/search", json={"query": "nonexistentterm"})
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == []
