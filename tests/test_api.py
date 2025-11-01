"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi import status
from src.app import activities


class TestRootEndpoint:
    """Test the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Test the GET /activities endpoint"""
    
    def test_get_activities_success(self, client):
        """Test successful retrieval of activities"""
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Check structure of first activity
        first_activity = list(data.values())[0]
        required_fields = ["description", "schedule", "max_participants", "participants"]
        for field in required_fields:
            assert field in first_activity
    
    def test_get_activities_contains_expected_activities(self, client):
        """Test that response contains expected default activities"""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        for activity in expected_activities:
            assert activity in data


class TestSignupForActivity:
    """Test the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify the participant was actually added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_already_registered(self, client):
        """Test signup when student is already registered"""
        # First signup
        client.post("/activities/Chess Club/signup?email=duplicate@mergington.edu")
        
        # Second signup (should fail)
        response = client.post(
            "/activities/Chess Club/signup?email=duplicate@mergington.edu"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert data["detail"] == "Student already signed up for this activity"
    
    def test_signup_activity_full(self, client):
        """Test signup when activity is at max capacity"""
        # Fill up Chess Club (max 12 participants, already has some)
        current_participants = len(activities["Chess Club"]["participants"])
        max_participants = activities["Chess Club"]["max_participants"]
        spots_to_fill = max_participants - current_participants
        
        # Fill remaining spots
        for i in range(spots_to_fill):
            response = client.post(
                f"/activities/Chess Club/signup?email=student{i}@mergington.edu"
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Try to add one more (should fail)
        response = client.post(
            "/activities/Chess Club/signup?email=overflow@mergington.edu"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert data["detail"] == "Activity is full"
    
    def test_signup_invalid_email_format(self, client):
        """Test signup with missing email parameter"""
        response = client.post("/activities/Chess Club/signup")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUnregisterFromActivity:
    """Test the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        # First, register a student
        email = "testunregister@mergington.edu"
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        # Then unregister
        response = client.delete(f"/activities/Chess Club/unregister?email={email}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Unregistered" in data["message"]
        
        # Verify the participant was actually removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_activity_not_found(self, client):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_student_not_registered(self, client):
        """Test unregister when student is not registered"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert data["detail"] == "Student is not registered for this activity"
    
    def test_unregister_missing_email(self, client):
        """Test unregister with missing email parameter"""
        response = client.delete("/activities/Chess Club/unregister")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestIntegrationScenarios:
    """Integration tests for complex scenarios"""
    
    def test_signup_and_unregister_workflow(self, client):
        """Test complete signup and unregister workflow"""
        email = "workflow@mergington.edu"
        activity = "Programming Class"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == status.HTTP_200_OK
        
        # Verify signup
        after_signup = client.get("/activities")
        assert len(after_signup.json()[activity]["participants"]) == initial_count + 1
        assert email in after_signup.json()[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == status.HTTP_200_OK
        
        # Verify unregister
        after_unregister = client.get("/activities")
        assert len(after_unregister.json()[activity]["participants"]) == initial_count
        assert email not in after_unregister.json()[activity]["participants"]
    
    def test_multiple_students_same_activity(self, client):
        """Test multiple students signing up for the same activity"""
        activity = "Art Club"
        emails = [f"student{i}@mergington.edu" for i in range(3)]
        
        # Sign up multiple students
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == status.HTTP_200_OK
        
        # Verify all are registered
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity]["participants"]
        
        for email in emails:
            assert email in participants
    
    def test_student_multiple_activities(self, client):
        """Test one student signing up for multiple activities"""
        email = "multisport@mergington.edu"
        activities_list = ["Chess Club", "Art Club", "Drama Club"]
        
        # Sign up for multiple activities
        for activity in activities_list:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == status.HTTP_200_OK
        
        # Verify student is in all activities
        all_activities = client.get("/activities").json()
        
        for activity in activities_list:
            assert email in all_activities[activity]["participants"]


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_special_characters_in_activity_name(self, client):
        """Test activity names with special characters are properly encoded"""
        # Chess Club should work with URL encoding
        response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
        assert response.status_code == status.HTTP_200_OK
    
    def test_email_with_special_characters(self, client):
        """Test emails with special characters"""
        special_email = "test+tag@mergington.edu"
        # Need to properly URL encode the email with + character
        import urllib.parse
        encoded_email = urllib.parse.quote(special_email)
        response = client.post(f"/activities/Chess Club/signup?email={encoded_email}")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify in activities list
        activities_response = client.get("/activities")
        assert special_email in activities_response.json()["Chess Club"]["participants"]
    
    def test_empty_email_parameter(self, client):
        """Test with empty email parameter"""
        response = client.post("/activities/Chess Club/signup?email=")
        # Current API accepts empty emails, so this should return 200
        # In a production system, this should be validated and return 422
        assert response.status_code == status.HTTP_200_OK