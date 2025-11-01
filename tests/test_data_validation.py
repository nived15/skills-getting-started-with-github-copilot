"""
Tests for data validation and model structure
"""

import pytest
from src.app import activities


class TestDataStructure:
    """Test the structure and validity of activities data"""
    
    def test_activities_data_structure(self):
        """Test that activities data has the correct structure"""
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
        for activity_name, activity_data in activities.items():
            # Test activity name is string
            assert isinstance(activity_name, str)
            assert len(activity_name) > 0
            
            # Test activity data structure
            assert isinstance(activity_data, dict)
            required_fields = ["description", "schedule", "max_participants", "participants"]
            
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in activity '{activity_name}'"
            
            # Test field types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            
            # Test constraints
            assert activity_data["max_participants"] > 0
            assert len(activity_data["participants"]) <= activity_data["max_participants"]
            
            # Test participant emails
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation
    
    def test_activities_have_valid_emails(self):
        """Test that all participant emails contain @mergington.edu"""
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                assert "@mergington.edu" in participant, f"Invalid email '{participant}' in '{activity_name}'"
    
    def test_no_duplicate_participants_per_activity(self):
        """Test that there are no duplicate participants in any activity"""
        for activity_name, activity_data in activities.items():
            participants = activity_data["participants"]
            unique_participants = set(participants)
            assert len(participants) == len(unique_participants), f"Duplicate participants found in '{activity_name}'"
    
    def test_activity_capacity_constraints(self):
        """Test that no activity exceeds its maximum capacity"""
        for activity_name, activity_data in activities.items():
            current_count = len(activity_data["participants"])
            max_count = activity_data["max_participants"]
            assert current_count <= max_count, f"Activity '{activity_name}' exceeds capacity: {current_count}/{max_count}"


class TestActivityDefaultData:
    """Test specific default activities and their data"""
    
    def test_chess_club_exists(self):
        """Test that Chess Club exists with expected data"""
        assert "Chess Club" in activities
        chess_club = activities["Chess Club"]
        
        assert "chess" in chess_club["description"].lower()
        assert chess_club["max_participants"] == 12
        assert isinstance(chess_club["participants"], list)
    
    def test_programming_class_exists(self):
        """Test that Programming Class exists with expected data"""
        assert "Programming Class" in activities
        programming_class = activities["Programming Class"]
        
        assert "programming" in programming_class["description"].lower()
        assert programming_class["max_participants"] == 20
        assert isinstance(programming_class["participants"], list)
    
    def test_all_default_activities_present(self):
        """Test that all expected default activities are present"""
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Soccer Team",
            "Swimming Club", "Art Club", "Drama Club", "Debate Team", "Robotics Club"
        ]
        
        for expected_activity in expected_activities:
            assert expected_activity in activities, f"Missing expected activity: {expected_activity}"
    
    def test_activities_have_reasonable_capacity(self):
        """Test that all activities have reasonable capacity limits"""
        for activity_name, activity_data in activities.items():
            max_participants = activity_data["max_participants"]
            # Reasonable range for school activities
            assert 5 <= max_participants <= 50, f"Unreasonable capacity for '{activity_name}': {max_participants}"


class TestDataConsistency:
    """Test data consistency across the application"""
    
    def test_participant_email_format_consistency(self):
        """Test that all participant emails follow the same format"""
        all_emails = []
        for activity_data in activities.values():
            all_emails.extend(activity_data["participants"])
        
        for email in all_emails:
            # All should end with @mergington.edu
            assert email.endswith("@mergington.edu"), f"Email '{email}' doesn't end with @mergington.edu"
            # Should have username part
            username = email.split("@")[0]
            assert len(username) > 0, f"Empty username in email '{email}'"
    
    def test_activity_descriptions_are_meaningful(self):
        """Test that activity descriptions contain meaningful content"""
        for activity_name, activity_data in activities.items():
            description = activity_data["description"]
            assert len(description) > 10, f"Description too short for '{activity_name}'"
            assert description[0].isupper(), f"Description should start with capital letter for '{activity_name}'"
    
    def test_schedules_contain_time_information(self):
        """Test that activity schedules contain time information"""
        time_indicators = ["AM", "PM", ":", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        for activity_name, activity_data in activities.items():
            schedule = activity_data["schedule"]
            has_time_info = any(indicator in schedule for indicator in time_indicators)
            assert has_time_info, f"Schedule for '{activity_name}' doesn't contain time information: '{schedule}'"