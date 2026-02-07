"""
Test New Features: Optimistic Locking (P2) and Connector APIs
Tests for iteration 8
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestOptimisticLocking:
    """Test Optimistic Locking for Shipment Updates (P2)"""
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client, auth_token):
        """Setup test - create a shipment for testing"""
        self.client = api_client
        self.client.headers.update({"Authorization": f"Bearer {auth_token}"})
        
        # Create a test shipment
        create_payload = {
            "shipment_number": f"TEST-OPTLOCK-{int(time.time())}",
            "buyer_name": "Optimistic Lock Test Buyer",
            "buyer_country": "USA",
            "destination_port": "New York",
            "origin_port": "Mumbai",
            "incoterm": "FOB",
            "currency": "USD",
            "total_value": 50000.0,
            "status": "draft"
        }
        
        response = self.client.post(f"{BASE_URL}/api/shipments", json=create_payload)
        assert response.status_code in [200, 201], f"Failed to create shipment: {response.text}"
        self.shipment = response.json()
        self.shipment_id = self.shipment["id"]
        
        yield
        
        # Cleanup
        try:
            self.client.delete(f"{BASE_URL}/api/shipments/{self.shipment_id}")
        except:
            pass
    
    def test_shipment_has_version_field(self):
        """Test that shipment response includes version field"""
        response = self.client.get(f"{BASE_URL}/api/shipments/{self.shipment_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "version" in data, "version field missing from shipment response"
        assert data["version"] == 1, f"Initial version should be 1, got {data['version']}"
    
    def test_update_with_correct_version_succeeds(self):
        """Test that update with correct version succeeds and increments version"""
        # Get current version
        response = self.client.get(f"{BASE_URL}/api/shipments/{self.shipment_id}")
        current_version = response.json()["version"]
        
        # Update with correct version
        update_payload = {
            "buyer_name": "Updated Buyer Name",
            "version": current_version
        }
        
        response = self.client.put(f"{BASE_URL}/api/shipments/{self.shipment_id}", json=update_payload)
        assert response.status_code == 200, f"Update failed: {response.text}"
        
        updated_data = response.json()
        assert updated_data["buyer_name"] == "Updated Buyer Name"
        assert updated_data["version"] == current_version + 1, "Version should be incremented"
    
    def test_update_with_old_version_returns_409_conflict(self):
        """Test that update with old version returns 409 Conflict"""
        # Get current version
        response = self.client.get(f"{BASE_URL}/api/shipments/{self.shipment_id}")
        current_version = response.json()["version"]
        
        # First update - should succeed
        update_payload1 = {
            "buyer_name": "First Update",
            "version": current_version
        }
        response1 = self.client.put(f"{BASE_URL}/api/shipments/{self.shipment_id}", json=update_payload1)
        assert response1.status_code == 200, f"First update failed: {response1.text}"
        
        # Second update with OLD version - should fail with 409
        update_payload2 = {
            "buyer_name": "Second Update",
            "version": current_version  # Using old version
        }
        response2 = self.client.put(f"{BASE_URL}/api/shipments/{self.shipment_id}", json=update_payload2)
        
        assert response2.status_code == 409, f"Expected 409 Conflict, got {response2.status_code}: {response2.text}"
        
        error_data = response2.json()
        assert "detail" in error_data
        assert "modified" in error_data["detail"].lower() or "conflict" in error_data["detail"].lower()
    
    def test_update_without_version_auto_increments(self):
        """Test that update without version field still works and increments version"""
        # Get current version
        response = self.client.get(f"{BASE_URL}/api/shipments/{self.shipment_id}")
        current_version = response.json()["version"]
        
        # Update without version field
        update_payload = {
            "buyer_name": "No Version Update"
        }
        
        response = self.client.put(f"{BASE_URL}/api/shipments/{self.shipment_id}", json=update_payload)
        assert response.status_code == 200, f"Update failed: {response.text}"
        
        updated_data = response.json()
        assert updated_data["buyer_name"] == "No Version Update"
        assert updated_data["version"] == current_version + 1, "Version should be auto-incremented"
    
    def test_concurrent_update_simulation(self):
        """Simulate concurrent updates - first succeeds, second fails with conflict"""
        # Get current version
        response = self.client.get(f"{BASE_URL}/api/shipments/{self.shipment_id}")
        initial_version = response.json()["version"]
        
        # Simulate two users reading the same version
        user_a_version = initial_version
        user_b_version = initial_version
        
        # User A updates first - should succeed
        update_a = {
            "buyer_name": "User A Update",
            "version": user_a_version
        }
        response_a = self.client.put(f"{BASE_URL}/api/shipments/{self.shipment_id}", json=update_a)
        assert response_a.status_code == 200, f"User A update failed: {response_a.text}"
        
        # User B tries to update with same (now stale) version - should fail
        update_b = {
            "buyer_name": "User B Update",
            "version": user_b_version
        }
        response_b = self.client.put(f"{BASE_URL}/api/shipments/{self.shipment_id}", json=update_b)
        
        assert response_b.status_code == 409, f"Expected 409 for User B, got {response_b.status_code}"
        
        # Verify User A's update persisted
        verify_response = self.client.get(f"{BASE_URL}/api/shipments/{self.shipment_id}")
        final_data = verify_response.json()
        assert final_data["buyer_name"] == "User A Update"
        assert final_data["version"] == initial_version + 1


class TestConnectorAPIs:
    """Test Connector API Endpoints (Bank, GST, ICEGATE)"""
    
    def test_bank_sync_endpoint_exists(self, api_client, auth_token):
        """Test /api/sync/bank endpoint exists"""
        api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
        response = api_client.get(f"{BASE_URL}/api/sync/bank")
        # Should return 200 with sync status
        assert response.status_code == 200, f"Bank sync endpoint failed: {response.text}"
        data = response.json()
        assert "status" in data, "Bank sync response should have status field"
    
    def test_gst_sync_endpoint_exists(self, api_client, auth_token):
        """Test /api/sync/gst endpoint exists"""
        api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
        response = api_client.get(f"{BASE_URL}/api/sync/gst")
        assert response.status_code == 200, f"GST sync endpoint failed: {response.text}"
        data = response.json()
        assert "status" in data, "GST sync response should have status field"
    
    def test_customs_sync_endpoint_exists(self, api_client, auth_token):
        """Test /api/sync/customs endpoint exists"""
        api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
        response = api_client.get(f"{BASE_URL}/api/sync/customs")
        assert response.status_code == 200, f"Customs sync endpoint failed: {response.text}"
        data = response.json()
        assert "status" in data, "Customs sync response should have status field"


class TestDashboardAPIs:
    """Test Dashboard API Endpoints"""
    
    def test_dashboard_stats_endpoint(self, api_client, auth_token):
        """Test /api/dashboard/stats endpoint"""
        api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
        response = api_client.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200, f"Dashboard stats failed: {response.text}"
        data = response.json()
        # Verify expected stats fields
        assert "total_shipments" in data or "total_export_value" in data
    
    def test_export_trend_chart_endpoint(self, api_client, auth_token):
        """Test /api/dashboard/charts/export-trend endpoint"""
        api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
        response = api_client.get(f"{BASE_URL}/api/dashboard/charts/export-trend")
        assert response.status_code == 200, f"Export trend chart failed: {response.text}"
        data = response.json()
        assert "labels" in data, "Export trend should have labels"
        assert "data" in data, "Export trend should have data"
    
    def test_payment_status_chart_endpoint(self, api_client, auth_token):
        """Test /api/dashboard/charts/payment-status endpoint"""
        api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
        response = api_client.get(f"{BASE_URL}/api/dashboard/charts/payment-status")
        assert response.status_code == 200, f"Payment status chart failed: {response.text}"
        data = response.json()
        assert "labels" in data, "Payment status should have labels"
        assert "data" in data, "Payment status should have data"
    
    def test_risk_alerts_endpoint(self, api_client, auth_token):
        """Test /api/ai/risk-alerts endpoint"""
        api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
        response = api_client.get(f"{BASE_URL}/api/ai/risk-alerts")
        assert response.status_code == 200, f"Risk alerts failed: {response.text}"
        data = response.json()
        assert "alerts" in data, "Risk alerts should have alerts array"


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture
def auth_token(api_client):
    """Get authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": "test@moradabad.com",
        "password": "Test@123"
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")
