"""Tests for the POST /activities/{activity_name}/signup endpoint"""
import pytest


def test_signup_success(client):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "newstudent@mergington.edu" in data["message"]
    assert "Chess Club" in data["message"]


def test_signup_adds_participant_to_activity(client):
    """Test that signup actually adds the participant to the activity"""
    # Get initial participant count
    activities_response = client.get("/activities")
    initial_count = len(activities_response.json()["Chess Club"]["participants"])
    
    # Sign up new participant
    client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    
    # Check that participant was added
    activities_response = client.get("/activities")
    updated_count = len(activities_response.json()["Chess Club"]["participants"])
    assert updated_count == initial_count + 1
    assert "newstudent@mergington.edu" in activities_response.json()["Chess Club"]["participants"]


def test_signup_duplicate_student_returns_error(client):
    """Test that signing up twice fails with 400 error"""
    email = "newstudent@mergington.edu"
    
    # First signup should succeed
    response1 = client.post(
        "/activities/Chess Club/signup",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Second signup should fail
    response2 = client.post(
        "/activities/Chess Club/signup",
        params={"email": email}
    )
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_signup_nonexistent_activity_returns_404(client):
    """Test that signing up for non-existent activity returns 404"""
    response = client.post(
        "/activities/Nonexistent Activity/signup",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_already_registered_student(client):
    """Test that a student already in the activity cannot sign up again"""
    # Michael is already in Chess Club
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"}
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_special_characters_in_activity_name(client):
    """Test signup with special characters in activity name (URL encoded)"""
    # This should fail because the activity doesn't exist
    response = client.post(
        "/activities/Non-existent%20Activity/signup",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404


def test_signup_multiple_students_different_activities(client):
    """Test that multiple students can sign up for different activities"""
    email1 = "student1@mergington.edu"
    email2 = "student2@mergington.edu"
    
    # Sign up for different activities
    response1 = client.post(
        "/activities/Chess Club/signup",
        params={"email": email1}
    )
    response2 = client.post(
        "/activities/Programming Class/signup",
        params={"email": email2}
    )
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    # Verify both were added
    activities = client.get("/activities").json()
    assert email1 in activities["Chess Club"]["participants"]
    assert email2 in activities["Programming Class"]["participants"]


def test_signup_same_student_multiple_activities(client):
    """Test that same student can sign up for multiple activities"""
    email = "student@mergington.edu"
    
    # Sign up for two different activities
    response1 = client.post(
        "/activities/Chess Club/signup",
        params={"email": email}
    )
    response2 = client.post(
        "/activities/Programming Class/signup",
        params={"email": email}
    )
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    # Verify student is in both
    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]
    assert email in activities["Programming Class"]["participants"]


def test_signup_empty_email(client):
    """Test signup with empty email is not rejected at HTTP level"""
    # Note: Current implementation doesn't validate email format
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": ""}
    )
    # The endpoint accepts it, adds to participants
    assert response.status_code == 200


def test_signup_with_query_parameter(client):
    """Test signup works with email as query parameter"""
    response = client.post(
        "/activities/Gym Class/signup?email=testuser@mergington.edu"
    )
    assert response.status_code == 200
    activities = client.get("/activities").json()
    assert "testuser@mergington.edu" in activities["Gym Class"]["participants"]
