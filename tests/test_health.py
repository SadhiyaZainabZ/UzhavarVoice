
def test_health_is_fast_and_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {
        "status": "ok",
        "app": "examate-rag",
        "environment": "test",
    }


def test_ready_without_database(client, monkeypatch):

    monkeypatch.setattr("app.main.check_database", lambda: False)

    response = client.get("/ready")

    assert response.status_code == 503
    assert "database" in response.text.lower()
