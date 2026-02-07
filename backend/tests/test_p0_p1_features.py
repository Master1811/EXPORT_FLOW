"""
Test P0 and P1 Features:
- P0: e-BRC rejection reason enforcement (422 if rejecting without reason)
- P1: Audit logging for PII unmasking (/api/shipments/{id}/unmasked)
- P1: /api/audit/pii-access endpoint returns PII access logs
"""
import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "test@moradabad.com",
        "password": "Test@123"
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")

@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Get headers with auth token"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }

@pytest.fixture(scope="module")
def test_shipment(auth_headers):
    """Create a test shipment with PII data for testing"""
    unique_id = str(uuid.uuid4())[:8]
    shipment_data = {
        "shipment_number": f"TEST-P0P1-{unique_id}",
        "buyer_name": f"Test Buyer P0P1 {unique_id}",
        "buyer_country": "United States",
        "destination_port": "Los Angeles",
        "origin_port": "Mumbai",
        "incoterm": "FOB",
        "currency": "USD",
        "total_value": 25000.00,
        "status": "shipped",
        "actual_ship_date": "2025-12-01T00:00:00Z",
        "product_description": "Test Product for P0P1 testing",
        "hs_codes": ["71131100"],
        "ebrc_status": "pending",
        # PII fields for testing
        "buyer_email": "testbuyer@example.com",
        "buyer_phone": "+919876543210",
        "buyer_pan": "ABCDE1234F",
        "buyer_bank_account": "1234567890123456"
    }
    
    response = requests.post(f"{BASE_URL}/api/shipments", json=shipment_data, headers=auth_headers)
    assert response.status_code == 200, f"Failed to create test shipment: {response.text}"
    shipment = response.json()
    
    yield shipment
    
    # Cleanup - delete the test shipment
    requests.delete(f"{BASE_URL}/api/shipments/{shipment['id']}", headers=auth_headers)


class TestEBRCRejectionReasonEnforcement:
    """P0 Fix: e-BRC rejection reason enforcement tests"""
    
    def test_reject_ebrc_without_reason_returns_422(self, auth_headers, test_shipment):
        """
        TC-EBRC-REJECT-01: Rejecting e-BRC without rejection_reason should return 422
        """
        shipment_id = test_shipment['id']
        
        # Try to reject without providing rejection_reason
        reject_data = {
            "ebrc_status": "rejected"
            # Missing rejection_reason intentionally
        }
        
        response = requests.put(
            f"{BASE_URL}/api/shipments/{shipment_id}/ebrc",
            json=reject_data,
            headers=auth_headers
        )
        
        # Assert 422 Unprocessable Entity
        assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"
        
        # Check error message
        error_detail = response.json().get("detail", "")
        assert "rejection_reason" in error_detail.lower(), f"Error should mention rejection_reason: {error_detail}"
        print(f"SUCCESS: Got expected 422 with message: {error_detail}")
    
    def test_reject_ebrc_with_empty_reason_returns_422(self, auth_headers, test_shipment):
        """
        TC-EBRC-REJECT-02: Rejecting e-BRC with empty rejection_reason should return 422
        """
        shipment_id = test_shipment['id']
        
        reject_data = {
            "ebrc_status": "rejected",
            "rejection_reason": ""  # Empty string
        }
        
        response = requests.put(
            f"{BASE_URL}/api/shipments/{shipment_id}/ebrc",
            json=reject_data,
            headers=auth_headers
        )
        
        # Empty string should be treated as missing - expect 422
        assert response.status_code == 422, f"Expected 422 for empty reason, got {response.status_code}: {response.text}"
        print("SUCCESS: Empty rejection_reason correctly rejected with 422")
    
    def test_reject_ebrc_with_valid_reason_succeeds(self, auth_headers, test_shipment):
        """
        TC-EBRC-REJECT-03: Rejecting e-BRC with valid rejection_reason should succeed
        """
        shipment_id = test_shipment['id']
        
        reject_data = {
            "ebrc_status": "rejected",
            "rejection_reason": "Document mismatch - incorrect buyer information"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/shipments/{shipment_id}/ebrc",
            json=reject_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify the status was updated
        shipment = response.json()
        assert shipment["ebrc_status"] == "rejected", "e-BRC status should be 'rejected'"
        print(f"SUCCESS: e-BRC rejected with reason, status is now: {shipment['ebrc_status']}")
        
        # Reset to pending for other tests
        reset_data = {"ebrc_status": "pending"}
        requests.put(f"{BASE_URL}/api/shipments/{shipment_id}/ebrc", json=reset_data, headers=auth_headers)
    
    def test_filed_status_without_reason_succeeds(self, auth_headers, test_shipment):
        """
        TC-EBRC-REJECT-04: Setting status to 'filed' should NOT require rejection_reason
        """
        shipment_id = test_shipment['id']
        
        filed_data = {
            "ebrc_status": "filed",
            "ebrc_filed_date": "2026-01-15T00:00:00Z",
            "ebrc_number": "EBRC-2026-001"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/shipments/{shipment_id}/ebrc",
            json=filed_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("SUCCESS: 'filed' status does not require rejection_reason")
        
        # Reset to pending
        reset_data = {"ebrc_status": "pending"}
        requests.put(f"{BASE_URL}/api/shipments/{shipment_id}/ebrc", json=reset_data, headers=auth_headers)
    
    def test_approved_status_without_reason_succeeds(self, auth_headers, test_shipment):
        """
        TC-EBRC-REJECT-05: Setting status to 'approved' should NOT require rejection_reason
        """
        shipment_id = test_shipment['id']
        
        approved_data = {
            "ebrc_status": "approved"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/shipments/{shipment_id}/ebrc",
            json=approved_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("SUCCESS: 'approved' status does not require rejection_reason")


class TestPIIUnmaskAuditLogging:
    """P1 Fix: Audit logging for PII unmasking tests"""
    
    def test_unmasked_endpoint_creates_audit_log(self, auth_headers, test_shipment):
        """
        TC-SEC-03-AUDIT: Accessing /api/shipments/{id}/unmasked should create audit log entry
        """
        shipment_id = test_shipment['id']
        
        # Access the unmasked endpoint
        response = requests.get(
            f"{BASE_URL}/api/shipments/{shipment_id}/unmasked",
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify PII is unmasked in response
        shipment = response.json()
        assert shipment.get("buyer_phone") is not None, "buyer_phone should be present"
        assert "****" not in str(shipment.get("buyer_phone", "")), "buyer_phone should be unmasked"
        print(f"SUCCESS: Unmasked endpoint returned full PII data")
        
        # Give a brief moment for async audit log to be written
        time.sleep(0.5)
        
        # Now check audit logs
        audit_response = requests.get(
            f"{BASE_URL}/api/audit/logs",
            params={"action": "pii_unmask", "resource_id": shipment_id},
            headers=auth_headers
        )
        
        assert audit_response.status_code == 200, f"Audit logs API failed: {audit_response.text}"
        
        audit_data = audit_response.json()
        logs = audit_data.get("logs", [])
        
        # Find log for this shipment
        matching_logs = [log for log in logs if log.get("resource_id") == shipment_id]
        assert len(matching_logs) > 0, f"No audit log found for shipment {shipment_id}"
        
        # Verify audit log structure
        latest_log = matching_logs[0]
        assert latest_log.get("action") == "pii_unmask", "Action should be 'pii_unmask'"
        assert latest_log.get("resource_type") == "shipment", "Resource type should be 'shipment'"
        assert "user_id" in latest_log, "Audit log should have user_id"
        assert "timestamp" in latest_log, "Audit log should have timestamp"
        
        # Verify details contain accessed fields
        details = latest_log.get("details", {})
        assert "accessed_fields" in details, "Details should include accessed_fields"
        accessed_fields = details.get("accessed_fields", [])
        assert "buyer_phone" in accessed_fields, "buyer_phone should be in accessed_fields"
        assert "buyer_pan" in accessed_fields, "buyer_pan should be in accessed_fields"
        
        print(f"SUCCESS: Audit log created with correct structure")
        print(f"  - Action: {latest_log.get('action')}")
        print(f"  - Resource: {latest_log.get('resource_type')}/{latest_log.get('resource_id')}")
        print(f"  - Accessed fields: {accessed_fields}")


class TestPIIAccessLogsEndpoint:
    """P1 Fix: /api/audit/pii-access endpoint tests"""
    
    def test_pii_access_logs_endpoint_exists(self, auth_headers):
        """
        TC-AUDIT-01: /api/audit/pii-access endpoint should exist and return logs
        """
        response = requests.get(
            f"{BASE_URL}/api/audit/pii-access",
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "logs" in data, "Response should contain 'logs' field"
        assert "count" in data, "Response should contain 'count' field"
        
        print(f"SUCCESS: PII access logs endpoint working, returned {data.get('count', 0)} logs")
    
    def test_pii_access_logs_only_returns_pii_unmask_actions(self, auth_headers, test_shipment):
        """
        TC-AUDIT-02: /api/audit/pii-access should only return pii_unmask action logs
        """
        shipment_id = test_shipment['id']
        
        # First, access the unmasked endpoint to create a pii_unmask log
        requests.get(f"{BASE_URL}/api/shipments/{shipment_id}/unmasked", headers=auth_headers)
        time.sleep(0.5)
        
        # Get PII access logs
        response = requests.get(
            f"{BASE_URL}/api/audit/pii-access",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        data = response.json()
        logs = data.get("logs", [])
        
        # All logs should have action = "pii_unmask"
        for log in logs:
            assert log.get("action") == "pii_unmask", f"Found non-pii_unmask log: {log.get('action')}"
        
        print(f"SUCCESS: All {len(logs)} logs have action='pii_unmask'")
    
    def test_pii_access_logs_limit_parameter(self, auth_headers):
        """
        TC-AUDIT-03: /api/audit/pii-access should respect limit parameter
        """
        # Request with limit=5
        response = requests.get(
            f"{BASE_URL}/api/audit/pii-access",
            params={"limit": 5},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        data = response.json()
        logs = data.get("logs", [])
        
        assert len(logs) <= 5, f"Expected max 5 logs, got {len(logs)}"
        print(f"SUCCESS: Limit parameter respected, returned {len(logs)} logs (max 5)")
    
    def test_audit_logs_general_endpoint(self, auth_headers):
        """
        TC-AUDIT-04: /api/audit/logs should support filtering by action
        """
        response = requests.get(
            f"{BASE_URL}/api/audit/logs",
            params={"action": "pii_unmask"},
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "logs" in data
        
        # All returned logs should have action = pii_unmask
        for log in data.get("logs", []):
            assert log.get("action") == "pii_unmask"
        
        print(f"SUCCESS: General audit logs endpoint supports action filtering")


class TestAuditLogStructure:
    """Additional tests for audit log data structure"""
    
    def test_audit_log_contains_required_fields(self, auth_headers, test_shipment):
        """
        TC-AUDIT-05: Audit log entries should contain all required fields
        """
        shipment_id = test_shipment['id']
        
        # Access unmasked to create log
        requests.get(f"{BASE_URL}/api/shipments/{shipment_id}/unmasked", headers=auth_headers)
        time.sleep(0.5)
        
        # Get the log
        response = requests.get(
            f"{BASE_URL}/api/audit/logs",
            params={"resource_id": shipment_id, "action": "pii_unmask"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        logs = response.json().get("logs", [])
        
        if logs:
            log = logs[0]
            required_fields = ["id", "user_id", "action", "resource_type", "resource_id", "timestamp"]
            for field in required_fields:
                assert field in log, f"Missing required field: {field}"
            
            print(f"SUCCESS: Audit log contains all required fields: {list(log.keys())}")
        else:
            pytest.skip("No logs found to verify structure")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
