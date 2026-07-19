def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_redis_health(client):
    response = client.get("/health/redis")
    assert response.status_code == 200
    assert "status" in response.json()

def test_faiss_health(client):
    response = client.get("/health/faiss")
    assert response.status_code == 200
    assert "status" in response.json()