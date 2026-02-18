"""
Backend tests for iteration 10 - CSS fixes and auth flow verification
Tests login, registration, dashboard stats, and core APIs
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://flow-debug-preview.preview.emergentagent.com').rstrip('/')
TEST_EMAIL = "test@moradabad.com"
TEST_PASSWORD = "Test@123"


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    @pytest.fixture(scope="class")
    def session(self):
        return requests.Session()
    
    @pytest.fixture(scope="class")
    def auth_data(self, session):
        """Login and return auth data"""
        # Wait to avoid rate limit
        time.sleep(1)
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()
    
    def test_login_returns_required_fields(self, auth_data):
        """Verify login returns all required token fields"""
        assert "access_token" in auth_data, "Missing access_token"
        assert "refresh_token" in auth_data, "Missing refresh_token"
        assert "expires_in" in auth_data, "Missing expires_in"
        assert "user" in auth_data, "Missing user object"
        print(f"✓ Login returns all required fields")
    
    def test_access_token_has_correct_ttl(self, auth_data):
        """Verify access token expires in 15 minutes (900 seconds)"""
        assert auth_data["expires_in"] == 900, f"Expected 900 seconds, got {auth_data['expires_in']}"
        print(f"✓ Access token TTL is 900 seconds (15 min)")
    
    def test_user_object_has_required_fields(self, auth_data):
        """Verify user object has required fields"""
        user = auth_data["user"]
        assert "id" in user
        assert "email" in user
        assert "full_name" in user
        assert user["email"] == TEST_EMAIL
        print(f"✓ User object has all required fields")
    
    def test_auth_me_endpoint(self, session, auth_data):
        """Test /api/auth/me endpoint"""
        session.headers.update({"Authorization": f"Bearer {auth_data['access_token']}"})
        response = session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200, f"Auth me failed: {response.text}"
        me_data = response.json()
        assert me_data["email"] == TEST_EMAIL
        print(f"✓ /api/auth/me returns user data")


class TestRegistrationEndpoint:
    """Test user registration"""
    
    def test_register_new_user(self):
        """Test new user registration"""
        timestamp = int(time.time())
        test_email = f"testauth{timestamp}@test.com"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "Test123456",
            "full_name": "Auth Test User",
            "company_name": "Test Company"
        })
        
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == test_email
        print(f"✓ User registration works - created {test_email}")


class TestDashboardEndpoints:
    """Test dashboard data endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        """Get authenticated session"""
        time.sleep(1)  # Avoid rate limit
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            token = response.json()["access_token"]
            session.headers.update({
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            })
        return session
    
    def test_dashboard_stats_endpoint(self, auth_session):
        """Test /api/dashboard/stats endpoint"""
        response = auth_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200, f"Dashboard stats failed: {response.text}"
        data = response.json()
        # Verify required stat fields exist
        assert "total_export_value" in data
        assert "total_receivables" in data
        print(f"✓ Dashboard stats endpoint works")
    
    def test_export_trend_chart_endpoint(self, auth_session):
        """Test /api/dashboard/charts/export-trend endpoint"""
        response = auth_session.get(f"{BASE_URL}/api/dashboard/charts/export-trend")
        assert response.status_code == 200, f"Export trend failed: {response.text}"
        data = response.json()
        assert "labels" in data
        assert "data" in data
        print(f"✓ Export trend chart endpoint works")
    
    def test_risk_alerts_endpoint(self, auth_session):
        """Test /api/ai/risk-alerts endpoint"""
        response = auth_session.get(f"{BASE_URL}/api/ai/risk-alerts")
        assert response.status_code == 200, f"Risk alerts failed: {response.text}"
        data = response.json()
        assert "alerts" in data
        print(f"✓ Risk alerts endpoint works")


class TestAPIHealth:
    """Basic API health checks"""
    
    def test_health_endpoint(self):
        """Test /api/health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✓ Health endpoint returns healthy")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
