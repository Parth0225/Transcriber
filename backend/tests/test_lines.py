import pytest
from datetime import datetime, timezone
from fastapi import status

@pytest.fixture
def transcript_id(client):
    payload = {
        "title": "Test Transcript",
        "date": datetime.now(timezone.utc).isoformat(),
        "language": "en"
    }
    response = client.post("/transcripts/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()["id"]


def test_create_line_success(client, transcript_id):
    payload = {
        "transcript_id": transcript_id,
        "start_time": 12.34,
        "speaker": "Alice",
        "text": "Hello world"
    }
    response = client.post("/lines/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["transcript_id"] == transcript_id
    assert data["start_time"] == payload["start_time"]
    assert data["speaker"] == payload["speaker"]
    assert data["text"] == payload["text"]
    assert "id" in data
    assert "created_at" in data


def test_create_line_validation_error(client, transcript_id):
    # missing required field 'text'
    payload = {
        "transcript_id": transcript_id,
        "start_time": 5.0
    }
    response = client.post("/lines/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    errors = response.json()["detail"]
    assert any(err["loc"][-1] == "text" for err in errors)


def test_get_line_success(client, transcript_id):
    # create line first
    payload = {
        "transcript_id": transcript_id,
        "start_time": 1.0,
        "text": "Sample line"
    }
    create_resp = client.post("/lines/", json=payload)
    line_id = create_resp.json()["id"]

    response = client.get(f"/lines/{line_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == line_id
    assert data["transcript_id"] == transcript_id
    assert data["text"] == payload["text"]


def test_get_line_not_found(client):
    response = client.get("/lines/999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Line with id 999999 not found"


def test_update_line_success(client, transcript_id):
    # create line
    payload = {
        "transcript_id": transcript_id,
        "start_time": 2.5,
        "speaker": "Bob",
        "text": "Original"
    }
    create_resp = client.post("/lines/", json=payload)
    line_id = create_resp.json()["id"]

    update_payload = {
        "text": "Edited",
        "speaker": "Charlie"
    }
    response = client.put(f"/lines/{line_id}", json=update_payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == line_id
    assert data["text"] == "Edited"
    assert data["speaker"] == "Charlie"


def test_update_line_not_found(client):
    response = client.put("/lines/999999", json={"text": "Nope"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Line with id 999999 not found"


def test_delete_line_success(client, transcript_id):
    # create line
    payload = {
        "transcript_id": transcript_id,
        "start_time": 0.0,
        "text": "To be deleted"
    }
    create_resp = client.post("/lines/", json=payload)
    line_id = create_resp.json()["id"]

    del_resp = client.delete(f"/lines/{line_id}")
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT

    # ensure it's gone
    get_resp = client.get(f"/lines/{line_id}")
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND


def test_delete_line_not_found(client):
    response = client.delete("/lines/999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Line with id 999999 not found"


def test_list_lines(client, transcript_id):
    # ensure empty list initially
    resp_initial = client.get("/lines/")
    assert resp_initial.status_code == status.HTTP_200_OK
    initial_list = resp_initial.json()
    assert isinstance(initial_list, list)

    # create two lines
    line1 = client.post(
        "/lines/",
        json={"transcript_id": transcript_id, "start_time": 1.0, "text": "First"}
    ).json()
    line2 = client.post(
        "/lines/",
        json={"transcript_id": transcript_id, "start_time": 2.0, "text": "Second"}
    ).json()

    resp = client.get("/lines/")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    ids = {item["id"] for item in data}
    assert line1["id"] in ids
    assert line2["id"] in ids
