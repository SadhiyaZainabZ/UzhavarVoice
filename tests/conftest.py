
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import app


@pytest.fixture
def client():
    app.dependency_overrides[get_settings] = lambda: Settings(
        app_name="examate-rag",
        environment="test",
    )

    with (
        patch("app.main.initialize_usage_table"),
        patch("app.main.record_usage"),
        patch("app.main.get_usage_totals") as mock_usage,
        TestClient(app) as test_client,
    ):
        mock_usage.return_value = {
            "requests": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "estimated_cost_usd": 0.0,
            "fallback_requests": 0,
        }
        yield test_client

    app.dependency_overrides.clear()
