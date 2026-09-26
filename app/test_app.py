from app import app


def test_homepage():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Docker 3-Tier Application" in response.data
