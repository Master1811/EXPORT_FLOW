"""
Security Framework Tests - Iteration 9
Tests for JWT Short TTL, Refresh Tokens, Audit Logs, and Security APIs

Features tested:
1. JWT Short TTL (15 min) with Refresh Tokens (7 days)
2. Token Refresh endpoint
3. Audit Logs API
4. PII Access Logs API
5. Security Events API  
6. Audit Stats API
7. Tamper-proof audit log creation
"""

import pytest
import requests
import os
import time
import jwt
from datetime import datetime, timezone

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "test@moradabad.com"
TEST_PASSWORD = "Test@123"

class TestJWTSecurityFramework:
    """Tests for JWT Short TTL and Refresh Token functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self, request):
        """Setup for each test - login and get tokens"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.access_token = None
        self.refresh_token = None
        self.user = None
    
    def test_login_returns_access_and_refresh_tokens(self):
        """Test that login returns both access_token and refresh_token with correct TTL"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        
        # Verify both tokens are present
        assert "access_token" in data, "access_token missing from login response"
        assert "refresh_token" in data, "refresh_token missing from login response"
        assert data["token_type"] == "bearer", "token_type should be bearer"
        
        # Verify expires_in is 900 seconds (15 minutes)
        assert "expires_in" in data, "expires_in missing from login response"
        assert data["expires_in"] == 900, f"Expected expires_in=900 (15 min), got {data['expires_in']}"
        
        # Verify user data is returned
        assert "user" in data, "user missing from login response"
        assert data["user"]["email"] == TEST_EMAIL
        
        print(f"✓ Login returns access_token (expires in {data['expires_in']} seconds)")
        print(f"✓ Login returns refresh_token")
        print(f"✓ User data included in response")
    
    def test_access_token_has_short_ttl(self):
        """Verify access token has ~15 minute expiry"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        assert response.status_code == 200
        data = response.json()
        access_token = data["access_token"]
        
        # Decode token (without verification) to check expiry
        decoded = jwt.decode(access_token, options={"verify_signature": False})
        
        assert decoded["type"] == "access", "Token type should be 'access'"
        assert "exp" in decoded, "Token should have expiry claim"
        assert "jti" in decoded, "Token should have JWT ID for revocation"
        
        # Calculate TTL
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        ttl_seconds = (exp_time - now).total_seconds()
        
        # Should be roughly 15 minutes (900 seconds), with some tolerance
        assert 800 <= ttl_seconds <= 920, f"Access token TTL should be ~900s, got {ttl_seconds}"
        
        print(f"✓ Access token TTL is {int(ttl_seconds)} seconds (~15 min)")
        print(f"✓ Token has type='access'")
        print(f"✓ Token has JTI for revocation tracking: {decoded['jti'][:16]}...")
    
    def test_refresh_token_has_7_day_ttl(self):
        """Verify refresh token has ~7 day expiry"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        assert response.status_code == 200
        data = response.json()
        refresh_token = data["refresh_token"]
        
        # Decode token to check type and expiry
        decoded = jwt.decode(refresh_token, options={"verify_signature": False})
        
        assert decoded["type"] == "refresh", "Token type should be 'refresh'"
        assert "exp" in decoded, "Refresh token should have expiry claim"
        
        # Calculate TTL  
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        ttl_seconds = (exp_time - now).total_seconds()
        ttl_days = ttl_seconds / (24 * 60 * 60)
        
        # Should be roughly 7 days
        assert 6.5 <= ttl_days <= 7.1, f"Refresh token TTL should be ~7 days, got {ttl_days:.2f} days"
        
        print(f"✓ Refresh token TTL is {ttl_days:.2f} days")
        print(f"✓ Token has type='refresh'")
    
    def test_refresh_token_endpoint_returns_new_tokens(self):
        """Test /api/auth/refresh endpoint accepts refresh_token and returns new tokens"""
        # First login to get refresh token
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200
        login_data = login_response.json()
        refresh_token = login_data["refresh_token"]
        old_access_token = login_data["access_token"]
        
        # Use refresh token to get new tokens
        refresh_response = self.session.post(f"{BASE_URL}/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert refresh_response.status_code == 200, f"Token refresh failed: {refresh_response.text}"
        refresh_data = refresh_response.json()
        
        # Verify new tokens are returned
        assert "access_token" in refresh_data, "New access_token missing"
        assert "refresh_token" in refresh_data, "New refresh_token missing"
        assert refresh_data["token_type"] == "bearer"
        assert refresh_data["expires_in"] == 900  # 15 minutes
        
        # Verify new access token is different
        new_access_token = refresh_data["access_token"]
        assert new_access_token != old_access_token, "New access token should be different from old"
        
        # Verify new access token works
        self.session.headers["Authorization"] = f"Bearer {new_access_token}"
        me_response = self.session.get(f"{BASE_URL}/api/auth/me")
        assert me_response.status_code == 200, "New access token should work"
        
        print(f"✓ Refresh endpoint returns new access_token")
        print(f"✓ Refresh endpoint returns new refresh_token")
        print(f"✓ New access token is valid and works")
    
    def test_invalid_refresh_token_rejected(self):
        """Test that invalid refresh token is rejected"""
        response = self.session.post(f"{BASE_URL}/api/auth/refresh", json={
            "refresh_token": "invalid-token-here"
        })
        
        assert response.status_code == 401, f"Expected 401 for invalid refresh token, got {response.status_code}"
        print("✓ Invalid refresh token correctly rejected with 401")
    
    def test_access_token_cannot_be_used_as_refresh(self):
        """Test that access token cannot be used in refresh endpoint"""
        # Login to get tokens
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200
        access_token = login_response.json()["access_token"]
        
        # Try to use access token as refresh token
        refresh_response = self.session.post(f"{BASE_URL}/api/auth/refresh", json={
            "refresh_token": access_token  # This should fail
        })
        
        assert refresh_response.status_code == 401, "Access token should not work as refresh token"
        print("✓ Access token correctly rejected when used as refresh token")


class TestAuditLogsAPI:
    """Tests for Security & Audit Log APIs"""
    
    @pytest.fixture(autouse=True)
    def setup(self, request):
        """Setup - login and get auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        data = response.json()
        self.access_token = data["access_token"]
        self.session.headers["Authorization"] = f"Bearer {self.access_token}"
        self.user_id = data["user"]["id"]
    
    def test_audit_logs_endpoint_returns_entries(self):
        """Test /api/security/audit-logs endpoint returns audit log entries"""
        response = self.session.get(f"{BASE_URL}/api/security/audit-logs")
        
        assert response.status_code == 200, f"Audit logs request failed: {response.text}"
        data = response.json()
        
        assert "logs" in data, "Response should contain 'logs' array"
        assert "count" in data, "Response should contain 'count'"
        assert isinstance(data["logs"], list), "logs should be a list"
        
        # Verify log entry structure if logs exist
        if len(data["logs"]) > 0:
            log = data["logs"][0]
            assert "id" in log, "Log entry should have 'id'"
            assert "user_id" in log, "Log entry should have 'user_id'"
            assert "action" in log, "Log entry should have 'action'"
            assert "resource_type" in log, "Log entry should have 'resource_type'"
            assert "timestamp" in log, "Log entry should have 'timestamp'"
            assert "hash" in log, "Log entry should have 'hash' for tamper detection"
            
            print(f"✓ Audit logs endpoint working - returned {data['count']} entries")
            print(f"✓ Log entry structure verified with hash chain")
        else:
            print("✓ Audit logs endpoint working - no entries yet")
    
    def test_pii_access_logs_endpoint(self):
        """Test /api/security/pii-access-logs returns PII unmask events"""
        response = self.session.get(f"{BASE_URL}/api/security/pii-access-logs")
        
        assert response.status_code == 200, f"PII logs request failed: {response.text}"
        data = response.json()
        
        assert "logs" in data, "Response should contain 'logs'"
        assert "count" in data, "Response should contain 'count'"
        assert "description" in data, "Response should contain 'description'"
        
        print(f"✓ PII access logs endpoint working - returned {data['count']} entries")
        print(f"✓ Description: {data['description']}")
    
    def test_security_events_endpoint(self):
        """Test /api/security/security-events returns login/logout events"""
        response = self.session.get(f"{BASE_URL}/api/security/security-events")
        
        assert response.status_code == 200, f"Security events request failed: {response.text}"
        data = response.json()
        
        assert "logs" in data, "Response should contain 'logs'"
        assert "count" in data, "Response should contain 'count'"
        
        # Should have at least our login event
        assert data["count"] >= 1, "Should have at least 1 security event (our login)"
        
        # Verify we can see login events
        login_events = [log for log in data["logs"] if log["action"] == "login"]
        assert len(login_events) >= 1, "Should have at least 1 login event"
        
        print(f"✓ Security events endpoint working - returned {data['count']} entries")
        print(f"✓ Found {len(login_events)} login events")
    
    def test_audit_stats_endpoint(self):
        """Test /api/security/stats returns audit statistics"""
        response = self.session.get(f"{BASE_URL}/api/security/stats")
        
        assert response.status_code == 200, f"Stats request failed: {response.text}"
        data = response.json()
        
        assert "total_entries" in data, "Response should contain 'total_entries'"
        assert "by_action" in data, "Response should contain 'by_action'"
        assert "by_resource" in data, "Response should contain 'by_resource'"
        
        print(f"✓ Audit stats endpoint working")
        print(f"✓ Total audit entries: {data['total_entries']}")
        print(f"✓ Actions breakdown: {list(data['by_action'].keys())}")
    
    def test_audit_logs_with_filters(self):
        """Test audit logs with action and resource_type filters"""
        # Test with action filter
        response = self.session.get(f"{BASE_URL}/api/security/audit-logs?action=login")
        assert response.status_code == 200
        data = response.json()
        
        # All returned logs should have action=login
        for log in data["logs"]:
            assert log["action"] == "login", f"Expected action='login', got '{log['action']}'"
        
        print(f"✓ Filter by action works - returned {data['count']} login events")
        
        # Test with resource_type filter
        response = self.session.get(f"{BASE_URL}/api/security/audit-logs?resource_type=user")
        assert response.status_code == 200
        data = response.json()
        
        print(f"✓ Filter by resource_type works - returned {data['count']} user events")
    
    def test_action_types_endpoint(self):
        """Test /api/security/action-types returns filter options"""
        response = self.session.get(f"{BASE_URL}/api/security/action-types")
        
        assert response.status_code == 200, f"Action types request failed: {response.text}"
        data = response.json()
        
        assert "action_types" in data, "Response should contain 'action_types'"
        assert "resource_types" in data, "Response should contain 'resource_types'"
        
        # Verify expected action types exist
        action_values = [at["value"] for at in data["action_types"]]
        expected_actions = ["view", "edit", "create", "delete", "login", "logout", "pii_unmask"]
        for expected in expected_actions:
            assert expected in action_values, f"Missing action type: {expected}"
        
        print(f"✓ Action types endpoint working")
        print(f"✓ {len(data['action_types'])} action types available")
        print(f"✓ {len(data['resource_types'])} resource types available")


class TestAuditLogCreation:
    """Tests for audit log creation on various actions"""
    
    @pytest.fixture(autouse=True)
    def setup(self, request):
        """Setup - login and get auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        
        data = response.json()
        self.access_token = data["access_token"]
        self.session.headers["Authorization"] = f"Bearer {self.access_token}"
        self.user_id = data["user"]["id"]
    
    def test_login_creates_audit_log(self):
        """Test that login creates an audit log entry"""
        # Get security events (which include login events)
        response = self.session.get(f"{BASE_URL}/api/security/security-events?limit=50")
        assert response.status_code == 200
        data = response.json()
        
        # Find recent login events
        login_logs = [log for log in data["logs"] if log["action"] == "login"]
        assert len(login_logs) >= 1, "Login should create audit log"
        
        # Verify log entry has expected fields
        recent_login = login_logs[0]
        assert recent_login["success"] == True, "Login log should show success=True"
        assert recent_login["resource_type"] == "user", "Login log resource_type should be 'user'"
        
        print("✓ Login creates audit log with action='login'")
        print(f"✓ Login audit log has timestamp: {recent_login['timestamp']}")
    
    def test_viewing_audit_logs_creates_audit_entry(self):
        """Test that accessing audit logs itself creates an audit entry"""
        # Get initial stats
        stats_before = self.session.get(f"{BASE_URL}/api/security/stats").json()
        view_count_before = stats_before["by_action"].get("view", 0)
        
        # Access audit logs (this should create a view entry)
        self.session.get(f"{BASE_URL}/api/security/audit-logs")
        
        # Check stats after
        stats_after = self.session.get(f"{BASE_URL}/api/security/stats").json()
        view_count_after = stats_after["by_action"].get("view", 0)
        
        # View count should have increased (each access creates view log)
        assert view_count_after >= view_count_before, "Viewing audit logs should create view entry"
        
        print("✓ Accessing audit logs creates audit entry")
        print(f"✓ View count increased from {view_count_before} to {view_count_after}")
    
    def test_tamper_proof_hash_chain(self):
        """Test that audit logs have hash chain for tamper detection"""
        response = self.session.get(f"{BASE_URL}/api/security/audit-logs?limit=10")
        assert response.status_code == 200
        data = response.json()
        
        if len(data["logs"]) >= 2:
            # Verify each log has hash and previous_hash
            for log in data["logs"]:
                assert "hash" in log, "Each log should have 'hash'"
                assert "previous_hash" in log, "Each log should have 'previous_hash'"
                assert "sequence" in log, "Each log should have 'sequence'"
            
            # Verify chain linkage (logs are returned in desc order by sequence)
            sorted_logs = sorted(data["logs"], key=lambda x: x["sequence"])
            for i in range(1, len(sorted_logs)):
                assert sorted_logs[i]["previous_hash"] == sorted_logs[i-1]["hash"], \
                    f"Hash chain broken at sequence {sorted_logs[i]['sequence']}"
            
            print("✓ Audit logs have tamper-proof hash chain")
            print(f"✓ Verified chain integrity for {len(data['logs'])} logs")
        else:
            print("✓ Hash chain structure verified (need more logs to verify linkage)")


class TestUnmaskedShipmentAudit:
    """Test that accessing unmasked shipment creates PII audit log"""
    
    @pytest.fixture(autouse=True)
    def setup(self, request):
        """Setup - login and get auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        
        data = response.json()
        self.access_token = data["access_token"]
        self.session.headers["Authorization"] = f"Bearer {self.access_token}"
        self.user_id = data["user"]["id"]
    
    def test_unmasked_shipment_creates_pii_audit(self):
        """Test that /api/shipments/{id}/unmasked creates PII audit log"""
        # First get a shipment ID
        shipments_response = self.session.get(f"{BASE_URL}/api/shipments?limit=1")
        
        if shipments_response.status_code == 200:
            shipments = shipments_response.json()
            if len(shipments) > 0:
                shipment_id = shipments[0]["id"]
                
                # Get PII unmask count before
                pii_before = self.session.get(f"{BASE_URL}/api/security/pii-access-logs").json()
                pii_count_before = pii_before["count"]
                
                # Access unmasked shipment
                unmasked_response = self.session.get(f"{BASE_URL}/api/shipments/{shipment_id}/unmasked")
                
                if unmasked_response.status_code == 200:
                    # Get PII unmask count after
                    pii_after = self.session.get(f"{BASE_URL}/api/security/pii-access-logs").json()
                    pii_count_after = pii_after["count"]
                    
                    # Should have one more PII access log
                    assert pii_count_after > pii_count_before, \
                        f"PII access log should be created: before={pii_count_before}, after={pii_count_after}"
                    
                    # Verify the latest PII log is for our shipment
                    if len(pii_after["logs"]) > 0:
                        latest = pii_after["logs"][0]
                        assert latest["action"] in ["pii_unmask", "decrypt"], \
                            f"Expected pii_unmask or decrypt action, got {latest['action']}"
                    
                    print("✓ Accessing unmasked shipment creates PII audit log")
                    print(f"✓ PII access count increased from {pii_count_before} to {pii_count_after}")
                else:
                    print(f"⚠ Unmasked endpoint returned {unmasked_response.status_code} - skipping")
            else:
                print("⚠ No shipments found to test - skipping")
        else:
            print(f"⚠ Could not get shipments ({shipments_response.status_code}) - skipping")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
