"""
Backend tests for Epic 2 (e-BRC Monitoring) and Epic 3 (Receivables Aging Dashboard)
Tests e-BRC status tracking, aging buckets, PII masking, and IDOR protection
"""
import pytest
import requests
import os
import random
import string

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "test@moradabad.com"
TEST_PASSWORD = "Test@123"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_token(api_client):
    """Get authentication token for test user"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json().get("access_token")


@pytest.fixture(scope="module")
def authenticated_client(api_client, auth_token):
    """Session with auth header"""
    api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_client


@pytest.fixture(scope="module")
def idor_test_client(api_client):
    """Create a separate user for IDOR testing"""
    random_suffix = ''.join(random.choices(string.ascii_lowercase, k=6))
    new_email = f"idor-test-{random_suffix}@example.com"
    
    # Register new user
    register_response = api_client.post(f"{BASE_URL}/api/auth/register", json={
        "email": new_email,
        "password": "Test@123",
        "full_name": "IDOR Test User"
    })
    
    # Login or use returned token
    if register_response.status_code == 200:
        token = register_response.json().get("access_token")
    else:
        login_response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": new_email,
            "password": "Test@123"
        })
        if login_response.status_code != 200:
            pytest.skip("Could not create IDOR test user")
        token = login_response.json().get("access_token")
    
    # Create new session with different token
    idor_session = requests.Session()
    idor_session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    })
    return idor_session


class TestEBRCDashboard:
    """Test Epic 2: e-BRC Monitoring Dashboard"""
    
    def test_ebrc_dashboard_returns_200(self, authenticated_client):
        """Test e-BRC dashboard endpoint returns 200"""
        response = authenticated_client.get(f"{BASE_URL}/api/shipments/ebrc-dashboard")
        assert response.status_code == 200
        print("e-BRC dashboard endpoint returns 200")
    
    def test_ebrc_dashboard_structure(self, authenticated_client):
        """Test e-BRC dashboard has correct structure"""
        response = authenticated_client.get(f"{BASE_URL}/api/shipments/ebrc-dashboard")
        data = response.json()
        
        # Verify summary structure
        assert "summary" in data
        summary = data["summary"]
        assert "total_shipments" in summary
        assert "pending_count" in summary
        assert "filed_count" in summary
        assert "approved_count" in summary
        assert "rejected_count" in summary
        assert "overdue_count" in summary
        assert "due_soon_count" in summary
        print("e-BRC dashboard has correct summary structure")
        
        # Verify values structure
        assert "values" in data
        values = data["values"]
        assert "total_pending" in values
        assert "total_overdue" in values
        assert "total_approved" in values
        print("e-BRC dashboard has correct values structure")
        
        # Verify alerts structure
        assert "alerts" in data
        alerts = data["alerts"]
        assert "overdue" in alerts
        assert "due_soon" in alerts
        print("e-BRC dashboard has correct alerts structure")
        
        # Verify by_status structure
        assert "by_status" in data
        by_status = data["by_status"]
        assert "pending" in by_status
        assert "filed" in by_status
        assert "approved" in by_status
        assert "rejected" in by_status
        print("e-BRC dashboard has correct by_status structure")
    
    def test_ebrc_dashboard_pending_shipments(self, authenticated_client):
        """Test e-BRC dashboard returns pending shipments with correct fields"""
        response = authenticated_client.get(f"{BASE_URL}/api/shipments/ebrc-dashboard")
        data = response.json()
        
        # Should have some pending shipments
        pending = data["by_status"]["pending"]
        if len(pending) > 0:
            shipment = pending[0]
            assert "id" in shipment
            assert "shipment_number" in shipment
            assert "buyer_name" in shipment
            assert "total_value" in shipment
            assert "currency" in shipment
            assert "ebrc_status" in shipment
            print(f"Found {len(pending)} pending shipments with correct fields")
        else:
            print("No pending shipments found (data may have been modified)")


class TestEBRCStatusUpdate:
    """Test e-BRC status update functionality"""
    
    def test_update_ebrc_status_to_filed(self, authenticated_client):
        """Test updating e-BRC status to filed"""
        # Get a shipment
        shipments_response = authenticated_client.get(f"{BASE_URL}/api/shipments")
        shipments = shipments_response.json()
        assert len(shipments) > 0, "No shipments found for testing"
        
        shipment_id = shipments[0]["id"]
        
        # Update e-BRC status
        update_response = authenticated_client.put(
            f"{BASE_URL}/api/shipments/{shipment_id}/ebrc",
            json={
                "ebrc_status": "filed",
                "ebrc_filed_date": "2025-01-15",
                "ebrc_number": "eBRC-TEST-001"
            }
        )
        assert update_response.status_code == 200
        
        data = update_response.json()
        assert data["ebrc_status"] == "filed"
        assert data["ebrc_filed_date"] == "2025-01-15"
        assert data["ebrc_number"] == "eBRC-TEST-001"
        print(f"Successfully updated e-BRC status to 'filed' for shipment {shipment_id}")
    
    def test_update_ebrc_status_to_approved(self, authenticated_client):
        """Test updating e-BRC status to approved"""
        shipments_response = authenticated_client.get(f"{BASE_URL}/api/shipments")
        shipments = shipments_response.json()
        shipment_id = shipments[0]["id"]
        
        update_response = authenticated_client.put(
            f"{BASE_URL}/api/shipments/{shipment_id}/ebrc",
            json={"ebrc_status": "approved"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["ebrc_status"] == "approved"
        print("Successfully updated e-BRC status to 'approved'")
    
    def test_update_ebrc_status_to_pending(self, authenticated_client):
        """Test resetting e-BRC status back to pending"""
        shipments_response = authenticated_client.get(f"{BASE_URL}/api/shipments")
        shipments = shipments_response.json()
        shipment_id = shipments[0]["id"]
        
        update_response = authenticated_client.put(
            f"{BASE_URL}/api/shipments/{shipment_id}/ebrc",
            json={"ebrc_status": "pending"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["ebrc_status"] == "pending"
        print("Successfully reset e-BRC status to 'pending'")
    
    def test_update_ebrc_invalid_shipment_returns_404(self, authenticated_client):
        """Test that updating e-BRC for non-existent shipment returns 404"""
        response = authenticated_client.put(
            f"{BASE_URL}/api/shipments/non-existent-id/ebrc",
            json={"ebrc_status": "filed"}
        )
        assert response.status_code == 404
        print("Correctly returns 404 for non-existent shipment")


class TestAgingDashboard:
    """Test Epic 3: Receivables Aging Dashboard"""
    
    def test_aging_dashboard_returns_200(self, authenticated_client):
        """Test aging dashboard endpoint returns 200"""
        response = authenticated_client.get(f"{BASE_URL}/api/payments/receivables/aging-dashboard")
        assert response.status_code == 200
        print("Aging dashboard endpoint returns 200")
    
    def test_aging_dashboard_structure(self, authenticated_client):
        """Test aging dashboard has correct structure with buckets"""
        response = authenticated_client.get(f"{BASE_URL}/api/payments/receivables/aging-dashboard")
        data = response.json()
        
        # Verify summary
        assert "summary" in data
        summary = data["summary"]
        assert "total_receivables" in summary
        assert "total_overdue" in summary
        assert "overdue_percentage" in summary
        assert "total_shipments_with_outstanding" in summary
        print("Aging dashboard has correct summary structure")
        
        # Verify buckets exist
        assert "buckets" in data
        buckets = data["buckets"]
        assert "0_30" in buckets
        assert "31_60" in buckets
        assert "61_90" in buckets
        assert "91_plus" in buckets
        print("Aging dashboard has all 4 aging buckets")
        
        # Verify bucket structure
        for key, bucket in buckets.items():
            assert "label" in bucket
            assert "amount" in bucket
            assert "count" in bucket
            assert "shipments" in bucket
            assert "color" in bucket
            assert "percentage" in bucket
        print("All buckets have correct structure")
    
    def test_aging_dashboard_bucket_values(self, authenticated_client):
        """Test bucket values are correct"""
        response = authenticated_client.get(f"{BASE_URL}/api/payments/receivables/aging-dashboard")
        data = response.json()
        
        buckets = data["buckets"]
        
        # Verify bucket labels
        assert buckets["0_30"]["label"] == "0-30 Days"
        assert buckets["31_60"]["label"] == "31-60 Days"
        assert buckets["61_90"]["label"] == "61-90 Days"
        assert buckets["91_plus"]["label"] == "90+ Days"
        
        # Verify colors are set
        assert buckets["0_30"]["color"] == "#10B981"  # Green
        assert buckets["31_60"]["color"] == "#3B82F6"  # Blue
        assert buckets["61_90"]["color"] == "#F59E0B"  # Amber
        assert buckets["91_plus"]["color"] == "#EF4444"  # Red
        print("Aging buckets have correct labels and colors")
    
    def test_aging_dashboard_chart_data(self, authenticated_client):
        """Test chart data is present and correct"""
        response = authenticated_client.get(f"{BASE_URL}/api/payments/receivables/aging-dashboard")
        data = response.json()
        
        assert "chart_data" in data
        chart_data = data["chart_data"]
        assert len(chart_data) == 4
        
        for item in chart_data:
            assert "name" in item
            assert "value" in item
            assert "count" in item
            assert "color" in item
        print("Chart data has correct structure")
    
    def test_aging_dashboard_total_calculation(self, authenticated_client):
        """Test that bucket totals sum to total receivables"""
        response = authenticated_client.get(f"{BASE_URL}/api/payments/receivables/aging-dashboard")
        data = response.json()
        
        total_from_buckets = sum(
            data["buckets"][key]["amount"] 
            for key in ["0_30", "31_60", "61_90", "91_plus"]
        )
        
        total_receivables = data["summary"]["total_receivables"]
        
        # Allow for floating point differences
        assert abs(total_from_buckets - total_receivables) < 0.01, \
            f"Bucket total {total_from_buckets} != total receivables {total_receivables}"
        print(f"Bucket totals correctly sum to total receivables: {total_receivables}")


class TestReceivablesEndpoint:
    """Test receivables endpoint"""
    
    def test_receivables_returns_200(self, authenticated_client):
        """Test receivables endpoint returns 200"""
        response = authenticated_client.get(f"{BASE_URL}/api/payments/receivables")
        assert response.status_code == 200
        print("Receivables endpoint returns 200")
    
    def test_receivables_structure(self, authenticated_client):
        """Test receivables returns correct structure"""
        response = authenticated_client.get(f"{BASE_URL}/api/payments/receivables")
        data = response.json()
        
        if len(data) > 0:
            item = data[0]
            assert "shipment_id" in item
            assert "shipment_number" in item
            assert "buyer_name" in item
            assert "total_value" in item
            assert "paid" in item
            assert "outstanding" in item
            assert "days_outstanding" in item
            print("Receivables have correct structure")
        else:
            print("No receivables found (may all be paid)")


class TestPIIMasking:
    """Test PII masking functionality"""
    
    @pytest.fixture
    def shipment_with_pii(self, authenticated_client):
        """Create a shipment with PII data for testing"""
        random_suffix = ''.join(random.choices(string.digits, k=4))
        response = authenticated_client.post(f"{BASE_URL}/api/shipments", json={
            "shipment_number": f"EXP-PII-TEST-{random_suffix}",
            "buyer_name": "PII Test Buyer",
            "buyer_country": "United States",
            "destination_port": "Los Angeles",
            "origin_port": "Mumbai",
            "incoterm": "FOB",
            "currency": "USD",
            "total_value": 25000,
            "status": "shipped",
            "buyer_email": "test@piitest.com",
            "buyer_phone": "+1-555-987-6543",
            "buyer_pan": "XYZAB9876P",
            "buyer_bank_account": "9876543210123456"
        })
        assert response.status_code == 200
        yield response.json()
        
        # Cleanup
        shipment_id = response.json()["id"]
        authenticated_client.delete(f"{BASE_URL}/api/shipments/{shipment_id}")
    
    def test_pii_masked_by_default(self, authenticated_client, shipment_with_pii):
        """Test that PII is masked by default when fetching shipment"""
        shipment_id = shipment_with_pii["id"]
        
        response = authenticated_client.get(f"{BASE_URL}/api/shipments/{shipment_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify PII is masked
        assert "****" in data.get("buyer_pan", "") or data.get("buyer_pan") is None or "*" in str(data.get("buyer_pan", ""))
        assert "****" in data.get("buyer_phone", "") or data.get("buyer_phone") is None or "*" in str(data.get("buyer_phone", ""))
        assert "****" in data.get("buyer_bank_account", "") or data.get("buyer_bank_account") is None or "*" in str(data.get("buyer_bank_account", ""))
        print("PII fields are masked by default")
    
    def test_pii_unmasked_on_explicit_request(self, authenticated_client, shipment_with_pii):
        """Test that PII can be unmasked via explicit endpoint"""
        shipment_id = shipment_with_pii["id"]
        
        response = authenticated_client.get(f"{BASE_URL}/api/shipments/{shipment_id}/unmasked")
        assert response.status_code == 200
        data = response.json()
        
        # Verify PII is NOT masked
        assert data.get("buyer_pan") == "XYZAB9876P"
        assert data.get("buyer_phone") == "+1-555-987-6543"
        assert data.get("buyer_bank_account") == "9876543210123456"
        print("PII fields are unmasked via explicit endpoint")


class TestIDORProtection:
    """Test IDOR (Insecure Direct Object Reference) protection"""
    
    def test_idor_shipment_access_denied(self, authenticated_client, idor_test_client):
        """Test that user cannot access another user's shipment"""
        # Get a shipment owned by the main test user
        shipments_response = authenticated_client.get(f"{BASE_URL}/api/shipments")
        shipments = shipments_response.json()
        
        if len(shipments) == 0:
            pytest.skip("No shipments found for IDOR testing")
        
        shipment_id = shipments[0]["id"]
        
        # Try to access with different user
        response = idor_test_client.get(f"{BASE_URL}/api/shipments/{shipment_id}")
        assert response.status_code == 404
        print("IDOR protection: Other user cannot access shipment - returns 404")
    
    def test_idor_ebrc_update_denied(self, authenticated_client, idor_test_client):
        """Test that user cannot update another user's e-BRC status"""
        shipments_response = authenticated_client.get(f"{BASE_URL}/api/shipments")
        shipments = shipments_response.json()
        
        if len(shipments) == 0:
            pytest.skip("No shipments found for IDOR testing")
        
        shipment_id = shipments[0]["id"]
        
        response = idor_test_client.put(
            f"{BASE_URL}/api/shipments/{shipment_id}/ebrc",
            json={"ebrc_status": "approved"}
        )
        assert response.status_code == 404
        print("IDOR protection: Other user cannot update e-BRC status - returns 404")
    
    def test_idor_unmasked_endpoint_denied(self, authenticated_client, idor_test_client):
        """Test that user cannot access unmasked PII of another user's shipment"""
        shipments_response = authenticated_client.get(f"{BASE_URL}/api/shipments")
        shipments = shipments_response.json()
        
        if len(shipments) == 0:
            pytest.skip("No shipments found for IDOR testing")
        
        shipment_id = shipments[0]["id"]
        
        response = idor_test_client.get(f"{BASE_URL}/api/shipments/{shipment_id}/unmasked")
        assert response.status_code == 404
        print("IDOR protection: Other user cannot access unmasked PII - returns 404")


class TestPaymentRecording:
    """Test payment recording functionality"""
    
    def test_record_payment_success(self, authenticated_client):
        """Test recording a payment for a shipment"""
        # Get a shipment
        shipments_response = authenticated_client.get(f"{BASE_URL}/api/shipments")
        shipments = shipments_response.json()
        
        if len(shipments) == 0:
            pytest.skip("No shipments found for payment testing")
        
        shipment_id = shipments[0]["id"]
        
        # Record payment
        response = authenticated_client.post(f"{BASE_URL}/api/payments", json={
            "shipment_id": shipment_id,
            "amount": 5000,
            "currency": "USD",
            "payment_date": "2025-01-20",
            "payment_mode": "wire",
            "bank_reference": "TEST-PAY-001"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["shipment_id"] == shipment_id
        assert data["amount"] == 5000
        assert data["status"] == "received"
        print(f"Successfully recorded payment for shipment {shipment_id}")
    
    def test_record_payment_invalid_shipment(self, authenticated_client):
        """Test recording payment for non-existent shipment fails"""
        response = authenticated_client.post(f"{BASE_URL}/api/payments", json={
            "shipment_id": "non-existent-shipment-id",
            "amount": 1000,
            "currency": "USD",
            "payment_date": "2025-01-20",
            "payment_mode": "wire"
        })
        assert response.status_code == 404
        print("Correctly returns 404 for payment to non-existent shipment")
    
    def test_get_shipment_payments(self, authenticated_client):
        """Test getting payments for a shipment"""
        shipments_response = authenticated_client.get(f"{BASE_URL}/api/shipments")
        shipments = shipments_response.json()
        
        if len(shipments) == 0:
            pytest.skip("No shipments found for payment testing")
        
        shipment_id = shipments[0]["id"]
        
        response = authenticated_client.get(f"{BASE_URL}/api/payments/shipment/{shipment_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Got {len(data)} payments for shipment {shipment_id}")


class TestAgingLegacyEndpoint:
    """Test legacy aging endpoint"""
    
    def test_aging_simple_returns_200(self, authenticated_client):
        """Test simple aging endpoint"""
        response = authenticated_client.get(f"{BASE_URL}/api/payments/receivables/aging")
        assert response.status_code == 200
        data = response.json()
        
        assert "current" in data
        assert "30_days" in data
        assert "60_days" in data
        assert "90_days" in data
        assert "over_90" in data
        print("Simple aging endpoint returns correct structure")
