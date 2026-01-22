import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()

    # Check that we have activities
    assert isinstance(activities, dict)
    assert len(activities) > 0

    # Check structure of an activity
    activity = next(iter(activities.values()))
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_signup_for_activity():
    """Test signing up for an activity"""
    # Get initial activities
    response = client.get("/activities")
    activities = response.json()
    activity_name = "Basketball Team"
    initial_participants = activities[activity_name]["participants"].copy()

    # Sign up a new participant
    email = "test@example.com"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    result = response.json()
    assert "message" in result

    # Check that participant was added
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate():
    """Test signing up the same email twice should fail"""
    activity_name = "Basketball Team"
    email = "duplicate@example.com"

    # Sign up first time
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200

    # Sign up second time should fail
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"]


def test_signup_activity_full():
    """Test signing up for a full activity"""
    activity_name = "Mathletes"  # Has max 10 participants, starts empty
    email = "full@example.com"

    # Fill up the activity
    for i in range(10):  # Add 10 to reach max
        client.post(f"/activities/{activity_name}/signup?email=fill{i}@example.com")

    # Try to sign up when full
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    result = response.json()
    assert "full" in result["detail"]


def test_unregister_from_activity():
    """Test unregistering from an activity"""
    activity_name = "Soccer Club"
    email = "unregister@example.com"

    # First sign up
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Then unregister
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    result = response.json()
    assert "message" in result

    # Check that participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert email not in activities[activity_name]["participants"]


def test_unregister_not_registered():
    """Test unregistering someone who is not registered"""
    activity_name = "Art Club"
    email = "notregistered@example.com"

    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    result = response.json()
    assert "detail" in result


def test_unregister_nonexistent_activity():
    """Test unregistering from a nonexistent activity"""
    response = client.delete("/activities/Nonexistent/unregister?email=test@example.com")
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result


def test_root_redirect():
    """Test root endpoint redirects to static index"""
    response = client.get("/")
    assert response.status_code == 200  # Should serve the HTML file