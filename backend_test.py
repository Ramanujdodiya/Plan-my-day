
import requests
import json
import sys
import time
from datetime import datetime

class PlanMyDayAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.plan_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.text}")
                except:
                    pass
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health(self):
        """Test health endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        if success:
            print(f"Health status: {response.get('status')}")
        return success

    def test_venues(self):
        """Test venues endpoint"""
        success, response = self.run_test(
            "Get Venues",
            "GET",
            "api/venues",
            200
        )
        if success:
            venues = response.get('venues', [])
            print(f"Retrieved {len(venues)} venues")
            if len(venues) > 0:
                print(f"Sample venue: {venues[0]['name']}")
        return success

    def test_weather(self, lat=40.7128, lng=-74.0060):
        """Test weather endpoint"""
        success, response = self.run_test(
            "Get Weather",
            "GET",
            "api/weather",
            200,
            params={"lat": lat, "lng": lng}
        )
        if success:
            print(f"Weather: {response.get('temperature')}°C, {response.get('description')}")
        return success

    def test_create_plan(self):
        """Test plan creation"""
        test_data = {
            "location": {
                "lat": 40.7128,
                "lng": -74.0060,
                "address": "New York, NY"
            },
            "budget": 200,
            "interests": ["Food & Dining", "Museums & Culture", "Outdoor Activities"],
            "duration": "full-day",
            "groupSize": 2
        }
        
        success, response = self.run_test(
            "Create Day Plan",
            "POST",
            "api/plan",
            200,
            data=test_data
        )
        
        if success:
            self.plan_id = response.get('id')
            print(f"Created plan with ID: {self.plan_id}")
            print(f"Plan has {len(response.get('itinerary', []))} itinerary items")
        return success

    def test_get_plan(self):
        """Test getting a specific plan"""
        if not self.plan_id:
            print("❌ Cannot test get_plan - no plan ID available")
            return False
            
        success, response = self.run_test(
            "Get Specific Plan",
            "GET",
            f"api/plans/{self.plan_id}",
            200
        )
        
        if success:
            print(f"Retrieved plan for: {response.get('location', {}).get('address')}")
        return success

def main():
    # Get backend URL from frontend .env
    backend_url = "https://8857e74b-3c72-4dbf-9c48-a7f958ee5e7f.preview.emergentagent.com"
    
    print(f"Testing API at: {backend_url}")
    
    # Setup tester
    tester = PlanMyDayAPITester(backend_url)
    
    # Run tests
    health_ok = tester.test_health()
    venues_ok = tester.test_venues()
    weather_ok = tester.test_weather()
    plan_ok = tester.test_create_plan()
    
    # Only test get_plan if create_plan succeeded
    get_plan_ok = False
    if plan_ok:
        get_plan_ok = tester.test_get_plan()
    
    # Print results
    print("\n📊 Test Results:")
    print(f"Health Check: {'✅' if health_ok else '❌'}")
    print(f"Get Venues: {'✅' if venues_ok else '❌'}")
    print(f"Get Weather: {'✅' if weather_ok else '❌'}")
    print(f"Create Plan: {'✅' if plan_ok else '❌'}")
    print(f"Get Plan: {'✅' if get_plan_ok else '❌'}")
    print(f"\nTests passed: {tester.tests_passed}/{tester.tests_run}")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
