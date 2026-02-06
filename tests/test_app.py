"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import the app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original activities
    original_activities = {
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
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team and training",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis skills and match play",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["jessica@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater productions and performance arts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["grace@mergington.edu", "lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and visual arts",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["sarah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debating and argumentation skills",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["marcus@mergington.edu", "nina@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore scientific experiments and discoveries",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["thomas@mergington.edu"]
        }
    }
    
    # Clear and reset
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Test the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_contains_activity_details(self, client, reset_activities):
        """Test that activity details are properly included"""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert chess_club["max_participants"] == 12
        assert len(chess_club["participants"]) == 2


class TestSignUp:
    """Test the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self, client, reset_activities):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify participant was added
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_duplicate_participant_fails(self, client, reset_activities):
        """Test that duplicate signups are rejected"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signup to nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_signup_adds_participant_count(self, client, reset_activities):
        """Test that participant count increases after signup"""
        initial_count = len(activities["Tennis Club"]["participants"])
        
        response = client.post(
            "/activities/Tennis%20Club/signup?email=newplayer@mergington.edu"
        )
        assert response.status_code == 200
        
        new_count = len(activities["Tennis Club"]["participants"])
        assert new_count == initial_count + 1


class TestUnregister:
    """Test the POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant(self, client, reset_activities):
        """Test unregistering an existing participant"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """Test that unregistering a non-participant fails"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=notaperson@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        """Test that unregister to nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_unregister_decreases_participant_count(self, client, reset_activities):
        """Test that participant count decreases after unregister"""
        initial_count = len(activities["Chess Club"]["participants"])
        
        response = client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        new_count = len(activities["Chess Club"]["participants"])
        assert new_count == initial_count - 1


class TestIntegration:
    """Integration tests for signup and unregister workflows"""
    
    def test_signup_then_unregister_workflow(self, client, reset_activities):
        """Test signing up and then unregistering"""
        email = "testuser@mergington.edu"
        activity = "Basketball%20Team"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        assert email in activities["Basketball Team"]["participants"]
        
        # Unregister
        unregister_response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        assert email not in activities["Basketball Team"]["participants"]
    
    def test_activities_updated_after_operations(self, client, reset_activities):
        """Test that activities endpoint reflects changes"""
        email = "newuser@mergington.edu"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_participants = len(initial_response.json()["Art Studio"]["participants"])
        
        # Sign up
        client.post("/activities/Art%20Studio/signup?email=" + email)
        
        # Get updated state
        updated_response = client.get("/activities")
        updated_participants = len(updated_response.json()["Art Studio"]["participants"])
        
        assert updated_participants == initial_participants + 1
        assert email in updated_response.json()["Art Studio"]["participants"]
