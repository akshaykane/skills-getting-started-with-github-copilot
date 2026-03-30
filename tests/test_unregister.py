"""Tests for the DELETE /activities/{activity_name}/unregister endpoint"""
import pytest


def test_unregister_success(client):
    """Test successful unregister from an activity"""
    # Michael is already in Chess Club
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "michael@mergington.edu"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "michael@mergington.edu" in data["message"]


def test_unregister_removes_participant_from_activity(client):
    """Test that unregister actually removes the participant"""
    email = "michael@mergington.edu"
    
    # Verify participant is in activity
    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]
    initial_count = len(activities["Chess Club"]["participants"])
    
    # Unregister
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify participant was removed
    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]
    assert len(activities["Chess Club"]["participants"]) == initial_count - 1


def test_unregister_nonexistent_activity_returns_404(client):
    """Test that unregistering from non-existent activity returns 404"""
    response = client.delete(
        "/activities/Nonexistent Activity/unregister",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_not_registered_student_returns_400(client):
    """Test that unregistering a student who's not registered returns 400"""
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "notregistered@mergington.edu"}
    )
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]


def test_unregister_same_student_twice_fails(client):
    """Test that unregistering same student twice fails on second attempt"""
    email = "michael@mergington.edu"
    
    # First unregister should succeed
    response1 = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Second unregister should fail
    response2 = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": email}
    )
    assert response2.status_code == 400
    assert "not registered" in response2.json()["detail"]


def test_unregister_one_student_doesn_not_affect_others(client):
    """Test that unregistering one student doesn't affect others"""
    email_to_remove = "michael@mergington.edu"
    email_to_keep = "daniel@mergington.edu"
    
    # Verify both are in Chess Club
    activities = client.get("/activities").json()
    assert email_to_remove in activities["Chess Club"]["participants"]
    assert email_to_keep in activities["Chess Club"]["participants"]
    
    # Unregister one
    client.delete(
        "/activities/Chess Club/unregister",
        params={"email": email_to_remove}
    )
    
    # Verify the other is still there
    activities = client.get("/activities").json()
    assert email_to_remove not in activities["Chess Club"]["participants"]
    assert email_to_keep in activities["Chess Club"]["participants"]


def test_unregister_student_from_different_activities(client):
    """Test unregistering a student from one activity doesn't affect others"""
    # Sign up emma for Chess Club (she's already in Programming Class)
    client.post(
        "/activities/Chess Club/signup",
        params={"email": "emma@mergington.edu"}
    )
    
    # Unregister from Chess Club
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "emma@mergington.edu"}
    )
    assert response.status_code == 200
    
    # Verify removed from Chess Club but still in Programming Class
    activities = client.get("/activities").json()
    assert "emma@mergington.edu" not in activities["Chess Club"]["participants"]
    assert "emma@mergington.edu" in activities["Programming Class"]["participants"]


def test_unregister_last_participant(client):
    """Test unregistering the last participant from an activity"""
    # Find an activity with only 1 participant
    activities = client.get("/activities").json()
    activity_with_one = None
    for name, details in activities.items():
        if len(details["participants"]) == 1:
            activity_with_one = name
            break
    
    if activity_with_one:
        last_participant = activities[activity_with_one]["participants"][0]
        
        # Unregister the last participant
        response = client.delete(
            f"/activities/{activity_with_one}/unregister",
            params={"email": last_participant}
        )
        assert response.status_code == 200
        
        # Verify activity now has no participants
        updated_activities = client.get("/activities").json()
        assert len(updated_activities[activity_with_one]["participants"]) == 0


def test_unregister_with_query_parameter(client):
    """Test unregister works with email as query parameter"""
    response = client.delete(
        "/activities/Basketball Team/unregister?email=alex@mergington.edu"
    )
    assert response.status_code == 200
    
    activities = client.get("/activities").json()
    assert "alex@mergington.edu" not in activities["Basketball Team"]["participants"]


def test_unregister_special_email_characters(client):
    """Test unregister with email containing special characters"""
    # First, sign up with a special email
    special_email = "student+test@mergington.edu"
    client.post(
        "/activities/Chess Club/signup",
        params={"email": special_email}
    )
    
    # Now unregister
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": special_email}
    )
    assert response.status_code == 200
    
    activities = client.get("/activities").json()
    assert special_email not in activities["Chess Club"]["participants"]
