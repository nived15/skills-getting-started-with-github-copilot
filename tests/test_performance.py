"""
Performance and load tests for the FastAPI application
"""

import pytest
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestPerformance:
    """Performance tests for API endpoints"""
    
    def test_get_activities_response_time(self, client):
        """Test that GET /activities responds within reasonable time"""
        start_time = time.time()
        response = client.get("/activities")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 1.0, f"Response time too slow: {response_time:.3f}s"
    
    def test_signup_response_time(self, client):
        """Test that signup endpoint responds within reasonable time"""
        start_time = time.time()
        response = client.post("/activities/Chess Club/signup?email=performance@mergington.edu")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 1.0, f"Signup response time too slow: {response_time:.3f}s"
    
    def test_multiple_concurrent_signups(self, client):
        """Test handling multiple concurrent signups"""
        activity = "Programming Class"
        base_email = "concurrent{0}@mergington.edu"
        num_requests = 5
        
        def make_signup_request(index):
            email = base_email.format(index)
            return client.post(f"/activities/{activity}/signup?email={email}")
        
        # Execute requests concurrently
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(make_signup_request, i) for i in range(num_requests)]
            results = [future.result() for future in as_completed(futures)]
        
        # All requests should succeed
        for response in results:
            assert response.status_code == 200
        
        # Verify all participants were added
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity]["participants"]
        
        for i in range(num_requests):
            expected_email = base_email.format(i)
            assert expected_email in participants


class TestLoadHandling:
    """Test the application's ability to handle load"""
    
    def test_many_sequential_requests(self, client):
        """Test handling many sequential requests"""
        num_requests = 20
        
        for i in range(num_requests):
            response = client.get("/activities")
            assert response.status_code == 200
            
            # Ensure response is consistent
            data = response.json()
            assert isinstance(data, dict)
            assert len(data) > 0
    
    def test_rapid_signup_unregister_cycles(self, client):
        """Test rapid signup and unregister cycles"""
        email = "rapidcycle@mergington.edu"
        activity = "Art Club"
        num_cycles = 10
        
        for i in range(num_cycles):
            # Signup
            signup_response = client.post(f"/activities/{activity}/signup?email={email}")
            assert signup_response.status_code == 200
            
            # Verify signup
            activities_response = client.get("/activities")
            assert email in activities_response.json()[activity]["participants"]
            
            # Unregister
            unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
            assert unregister_response.status_code == 200
            
            # Verify unregister
            activities_response = client.get("/activities")
            assert email not in activities_response.json()[activity]["participants"]


class TestStressScenarios:
    """Stress test scenarios"""
    
    def test_fill_activity_to_capacity(self, client):
        """Test filling an activity to its maximum capacity"""
        activity = "Debate Team"  # Has capacity of 14
        
        # Get current capacity
        initial_response = client.get("/activities")
        activity_data = initial_response.json()[activity]
        current_count = len(activity_data["participants"])
        max_capacity = activity_data["max_participants"]
        spots_available = max_capacity - current_count
        
        # Fill all available spots
        for i in range(spots_available):
            email = f"stresstest{i}@mergington.edu"
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify activity is now full
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity]["participants"]
        assert len(final_participants) == max_capacity
        
        # Try to add one more (should fail)
        overflow_response = client.post(f"/activities/{activity}/signup?email=overflow@mergington.edu")
        assert overflow_response.status_code == 400
    
    def test_large_participant_list_handling(self, client):
        """Test handling activities with many participants"""
        activity = "Gym Class"  # Has highest capacity (30)
        
        # Get current state
        initial_response = client.get("/activities")
        activity_data = initial_response.json()[activity]
        current_count = len(activity_data["participants"])
        max_capacity = activity_data["max_participants"]
        
        # Add participants up to a reasonable number to test
        target_participants = min(15, max_capacity - current_count)
        
        for i in range(target_participants):
            email = f"largelist{i}@mergington.edu"
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Test that GET request still performs well with many participants
        start_time = time.time()
        response = client.get("/activities")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 2.0, f"Response too slow with many participants: {response_time:.3f}s"
        
        # Verify data integrity
        data = response.json()
        participants = data[activity]["participants"]
        assert len(participants) >= current_count + target_participants