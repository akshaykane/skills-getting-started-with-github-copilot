"""Tests for the GET /activities endpoint"""
import pytest


def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    # Check that all expected activities are present
    expected_activities = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Tennis Club",
        "Drama Club",
        "Art Studio",
        "Debate Team",
        "Science Olympiad"
    ]
    
    for activity in expected_activities:
        assert activity in data


def test_get_activities_has_correct_structure(client):
    """Test that activity objects have correct structure"""
    response = client.get("/activities")
    data = response.json()
    
    # Check first activity has all required fields
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_get_activities_shows_correct_participant_counts(client):
    """Test that participant counts are accurate"""
    response = client.get("/activities")
    data = response.json()
    
    # Chess Club should have 2 participants
    assert len(data["Chess Club"]["participants"]) == 2
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]
    assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


def test_get_activities_shows_max_participants(client):
    """Test that max_participants is returned correctly"""
    response = client.get("/activities")
    data = response.json()
    
    # Verify max_participants values
    assert data["Chess Club"]["max_participants"] == 12
    assert data["Programming Class"]["max_participants"] == 20
    assert data["Gym Class"]["max_participants"] == 30


def test_get_activities_has_descriptions_and_schedules(client):
    """Test that activities have descriptions and schedules"""
    response = client.get("/activities")
    data = response.json()
    
    chess_club = data["Chess Club"]
    assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
    assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
