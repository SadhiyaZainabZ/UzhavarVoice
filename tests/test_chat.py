
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import app

client = TestClient(app)


def setup_function():
    app.dependency_overrides[get_settings] = lambda: Settings(
        app_name="examate-rag",
        environment="test",
        gemini_api_key="test-key",
    )


def teardown_function():
    app.dependency_overrides.clear()


@patch("app.main.chat")
def test_chat_returns_structured_response(mock_chat):
    mock_chat.return_value = {
        "answer": "Use recommended crop practices.",
        "model": "gemini-2.5-flash",
        "input_tokens": 10,
        "output_tokens": 8,
        "estimated_cost_usd": 0.0,
        "fallback_used": False,
    }

    response = client.post("/chat", json={"message": "How do I grow paddy?"})

    assert response.status_code == 200
    assert response.json()["answer"] == "Use recommended crop practices."
    assert response.json()["model"] == "gemini-2.5-flash"


@patch("app.main.chat")
def test_chat_failure_returns_502(mock_chat):
    mock_chat.side_effect = RuntimeError("Provider unavailable")

    response = client.post("/chat", json={"message": "Test question"})

    assert response.status_code == 502


def test_usage_endpoint_returns_counters():
    response = client.get("/usage")

    assert response.status_code == 200
    body = response.json()
    assert "requests" in body
    assert "input_tokens" in body
    assert "output_tokens" in body
    assert "estimated_cost_usd" in body
