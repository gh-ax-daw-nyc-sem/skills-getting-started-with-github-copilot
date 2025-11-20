"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        }
    })


def test_root_redirects_to_static(client):
    """Test that root URL redirects to static index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert len(data["Chess Club"]["participants"]) == 2


def test_signup_for_activity_success(client):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Chess%20Club/signup?email=john@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Signed up john@mergington.edu for Chess Club"
    
    # Verify the participant was added
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "john@mergington.edu" in activities_data["Chess Club"]["participants"]


def test_signup_for_nonexistent_activity(client):
    """Test signup for an activity that doesn't exist"""
    response = client.post(
        "/activities/Nonexistent%20Club/signup?email=john@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_signup_duplicate_participant(client):
    """Test signing up a participant who is already registered"""
    response = client.post(
        "/activities/Chess%20Club/signup?email=michael@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student already signed up for this activity"


def test_unregister_from_activity_success(client):
    """Test successful unregistration from an activity"""
    response = client.delete(
        "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Unregistered michael@mergington.edu from Chess Club"
    
    # Verify the participant was removed
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]


def test_unregister_from_nonexistent_activity(client):
    """Test unregistration from an activity that doesn't exist"""
    response = client.delete(
        "/activities/Nonexistent%20Club/unregister?email=michael@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_unregister_participant_not_registered(client):
    """Test unregistering a participant who is not registered"""
    response = client.delete(
        "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student not signed up for this activity"


def test_activity_max_participants_limit(client):
    """Test that activities respect max participant limits"""
    # Fill up Programming Class (max 20)
    activities["Programming Class"]["max_participants"] = 3
    activities["Programming Class"]["participants"] = ["student1@mergington.edu", "student2@mergington.edu"]
    
    # Try to add one more (should succeed)
    response = client.post(
        "/activities/Programming%20Class/signup?email=student3@mergington.edu"
    )
    assert response.status_code == 200
    
    # Verify we now have 3 participants
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert len(activities_data["Programming Class"]["participants"]) == 3


def test_multiple_signups_and_unregistrations(client):
    """Test a sequence of signups and unregistrations"""
    # Sign up a new participant
    response = client.post(
        "/activities/Chess%20Club/signup?email=alice@mergington.edu"
    )
    assert response.status_code == 200
    
    # Sign up another participant
    response = client.post(
        "/activities/Chess%20Club/signup?email=bob@mergington.edu"
    )
    assert response.status_code == 200
    
    # Check we have 4 participants now
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert len(activities_data["Chess Club"]["participants"]) == 4
    
    # Unregister one
    response = client.delete(
        "/activities/Chess%20Club/unregister?email=alice@mergington.edu"
    )
    assert response.status_code == 200
    
    # Check we have 3 participants now
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert len(activities_data["Chess Club"]["participants"]) == 3
    assert "alice@mergington.edu" not in activities_data["Chess Club"]["participants"]
    assert "bob@mergington.edu" in activities_data["Chess Club"]["participants"]
