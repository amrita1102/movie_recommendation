def test_valid_user_recommendations(client):
    response = client.get("/recommend/user/101")
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) > 0
    first = data["recommendations"][0]
    assert "movieId" in first
    assert "title" in first
    assert isinstance(first["movieId"], int)
    assert isinstance(first["title"], str)

def test_print_response(client):
    response = client.get("/recommend/user/101")
    print(response.json())
    assert response.status_code == 200

def test_invalid_user(client):
    response = client.get("/recommend/user/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"