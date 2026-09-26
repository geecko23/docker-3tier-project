import app as app_module


def test_homepage(monkeypatch):
    # Mock Redis
    monkeypatch.setattr(
        app_module.redis_client,
        "incr",
        lambda key: 1
    )

    # Mock MySQL
    class FakeCursor:
        def execute(self, query):
            pass

        def fetchall(self):
            return [
                (1, "Abrar", "DevOps Student"),
                (2, "Alice", "Cloud Engineer")
            ]

        def close(self):
            pass

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

        def close(self):
            pass

    monkeypatch.setattr(
        app_module,
        "get_db_connection",
        lambda: FakeConnection()
    )

    # Create Flask test client
    client = app_module.app.test_client()

    # Request homepage
    response = client.get("/")

    # Verify response
    assert response.status_code == 200
    assert b"Docker 3-Tier Application" in response.data


