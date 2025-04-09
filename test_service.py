from datetime import datetime
import pytest
from app import app


@pytest.fixture
def client():
    return app.test_client()


@pytest.fixture
def new_activity():
    return {"user_id": 321, "details": "some details", "username": "janeuser"}


def test_root_should_fail(client):
    response = client.get("/")
    assert response.status_code == 404


def test_plural_activities_returns_at_least_2(client):
    response = client.get("/api/activities")
    activities = response.get_json()
    assert len(activities["activities"]) >= 2


def test_schema_elements_present_for_first_activity(client):
    keys = ["id", "user_id", "username", "timestamp", "details", "location"]
    response = client.get("/api/activities")
    activities = response.get_json()
    id_to_retrieve = activities["activities"][0]["id"]
    response = client.get(f"/api/activities/{id_to_retrieve}")
    activity = response.get_json()
    assert all(k in activity for k in keys)


def test_can_use_location_to_find_activity(client):
    response = client.get("/api/activities")
    activities = response.get_json()
    assert "location" in activities["activities"][0]
    location = activities["activities"][0]["location"]
    response = client.get(location)
    assert response.status_code == 200
    activity = response.get_json()
    assert "id" in activity
    assert "location" in activity


def test_new_activity_without_any_data_fails(client):
    response = client.post("/api/activities")
    assert response.status_code in (400, 415)


def test_new_activity_without_all_required_data_fails(client):
    activity = {"user_id": "54321"}
    response = client.post("/api/activities", json=activity)
    assert response.status_code == 400


def test_new_activity_should_not_provide_an_id(client):
    activity = {"id": "wrong"}
    response = client.post("/api/activities", json=activity)
    assert response.status_code == 400


def test_new_activity_should_return_201(client, new_activity):
    new_activity["timestamp"] = datetime.utcnow()
    response = client.post("/api/activities", json=new_activity)
    assert response.status_code == 201


def test_new_activity_echo_elements_back(client, new_activity):
    new_activity["timestamp"] = datetime.utcnow()
    response = client.post("/api/activities", json=new_activity)
    assert response.status_code == 201
    returned_activity = response.get_json()
    assert returned_activity["user_id"] == new_activity["user_id"]
    assert returned_activity["details"] == new_activity["details"]


def test_new_activity_should_provide_valid_location(client, new_activity):
    new_activity["timestamp"] = datetime.utcnow()
    response = client.post("/api/activities", json=new_activity)
    assert response.status_code == 201
    returned_activity = response.get_json()
    assert "location" in returned_activity
    assert returned_activity["location"] == f"/api/activities/{returned_activity['id']}"
