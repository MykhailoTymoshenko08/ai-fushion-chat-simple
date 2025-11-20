import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_create_chat():
    response = client.post("/api/chat/new", json={"title": "Test Chat"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test Chat"

def test_send_message_no_chat():
    response = client.post("/api/chat/send", json={"message": "Hello"})
    assert response.status_code == 200
    data = response.json()
    assert "chat_id" in data
    assert "user_message_id" in data

def test_get_chat_history_not_found():
    response = client.get("/api/chat/nonexistent/history")
    assert response.status_code == 404

def test_rating_invalid_score():
    response = client.post("/api/rating", json={
        "chat_id": "test",
        "message_id": "test", 
        "score": 2  # Invalid score
    })
    assert response.status_code == 400