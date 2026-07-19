from unittest.mock import patch

@patch("app.recommend_user")
def test_recommendations_mock(mock_recommend_user, client):

    mock_recommend_user.return_value = [
        {
            "movieId": 1,
            "title": "Toy Story"
        }
    ]

    response = client.get("/recommend/user/101")

    assert response.status_code == 200

    data = response.json()

    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["movieId"] == 1
    assert data["recommendations"][0]["title"] == "Toy Story"