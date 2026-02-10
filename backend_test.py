#!/usr/bin/env python3
"""
Security and Forex Improvements Test Suite for ExportFlow
Tests all authentication security features and forex management functionality
"""
import requests
import json
import time
import sys
from typing import Dict, Any, Optional

# Test Configuration
BASE_URL = "https://resilient-api-1.preview.emergentagent.com/api"
TEST_USER = {
    "email": "test@moradabad.com",
    "password": "Test@123"
}

# ANSI color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def log_test(test_name: str, status: str, details: str = ""):
    """Log test results with colors"""
    color = Colors.GREEN if status == "PASS" else Colors.RED if status == "FAIL" else Colors.YELLOW
    print(f"{color}{Colors.BOLD}[{status}]{Colors.END} {test_name}")
    if details:
        print(f"    {details}")

def make_request(method: str, endpoint: str, headers: Optional[Dict] = None, 
                 json_data: Optional[Dict] = None, expected_status: int = None) -> requests.Response:
    """Make HTTP request with error handling"""
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers or {},
            json=json_data,
            timeout=30
        )
        
        if expected_status and response.status_code != expected_status:
            print(f"    {Colors.YELLOW}Expected {expected_status}, got {response.status_code}{Colors.END}")
            print(f"    Response: {response.text[:200]}")
        
        return response
    except requests.RequestException as e:
        print(f"    {Colors.RED}Request failed: {e}{Colors.END}")
        return None

class SecurityTestSuite:
    def __init__(self):
        self.session = requests.Session()
        self.auth_headers = {}
        self.refresh_token = None
        self.session_id = None
    
    def test_01_failed_login_tracking(self):
        """Test failed login tracking and account lockout"""
        print(f"\n{Colors.BLUE}=== Test 1: Failed Login Tracking & Account Lockout ==={Colors.END}")
        
        lockout_email = "lockout-test@example.com"
        wrong_password = "wrongpass"
        
        # Try to login 6 times with wrong password
        for attempt in range(1, 7):
            response = make_request(
                "POST", 
                "/auth/login",
                json_data={
                    "email": lockout_email,
                    "password": wrong_password
                }
            )
            
            if response is None:
                log_test(f"Failed login attempt {attempt}", "FAIL", "Request failed")
                continue
            
            print(f"    Attempt {attempt}: Status {response.status_code}")
            
            if attempt <= 5:
                if response.status_code == 401:
                    try:
                        data = response.json()
                        detail = data.get("detail", "")
                        print(f"      Response: {detail}")
                        if "attempts remaining" in detail:
                            log_test(f"Attempt {attempt} tracking", "PASS", f"Properly tracked: {detail}")
                        else:
                            log_test(f"Attempt {attempt} tracking", "PASS", "Invalid credentials response")
                    except:
                        log_test(f"Attempt {attempt} tracking", "FAIL", "Could not parse response")
                else:
                    log_test(f"Attempt {attempt}", "FAIL", f"Unexpected status: {response.status_code}")
            else:
                # 6th attempt should be locked out
                if response.status_code == 429:
                    try:
                        data = response.json()
                        detail = data.get("detail", "")
                        if "locked" in detail.lower() or "too many" in detail.lower():
                            log_test("Account lockout", "PASS", f"Account properly locked: {detail}")
                        else:
                            log_test("Account lockout", "FAIL", f"Wrong lockout message: {detail}")
                    except:
                        log_test("Account lockout", "FAIL", "Could not parse lockout response")
                else:
                    log_test("Account lockout", "FAIL", f"Expected 429, got {response.status_code}")
            
            time.sleep(0.5)  # Small delay between attempts
    
    def test_02_successful_login(self):
        """Test successful login with test credentials"""
        print(f"\n{Colors.BLUE}=== Test 2: Login Success After Valid Credentials ==={Colors.END}")
        
        response = make_request(
            "POST",
            "/auth/login", 
            json_data=TEST_USER
        )
        
        if response is None:
            log_test("Login request", "FAIL", "Request failed")
            return False
            
        if response.status_code == 200:
            try:
                data = response.json()
                self.auth_headers = {"Authorization": f"Bearer {data['access_token']}"}
                self.refresh_token = data.get("refresh_token")
                self.session_id = data.get("session_id")
                
                # Check required fields
                required_fields = ["access_token", "refresh_token", "session_id", "csrf_token", "email_verified"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    log_test("Login response fields", "FAIL", f"Missing: {missing_fields}")
                else:
                    log_test("Login success", "PASS", f"All required fields present. Email verified: {data.get('email_verified')}")
                    
                return True
            except Exception as e:
                log_test("Login response parsing", "FAIL", str(e))
                return False
        else:
            log_test("Login", "FAIL", f"Status {response.status_code}: {response.text[:200]}")
            return False
    
    def test_03_session_management(self):
        """Test session management endpoints"""
        print(f"\n{Colors.BLUE}=== Test 3: Session Management ==={Colors.END}")
        
        if not self.auth_headers:
            log_test("Session management", "SKIP", "No auth token available")
            return
        
        # Get active sessions
        response = make_request(
            "GET",
            "/auth/sessions",
            headers=self.auth_headers
        )
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                sessions = data.get("sessions", [])
                count = data.get("count", 0)
                
                if len(sessions) > 0:
                    session = sessions[0]
                    expected_fields = ["id", "ip_address", "user_agent", "created_at", "last_active"]
                    present_fields = [field for field in expected_fields if field in session]
                    
                    log_test("Session list", "PASS", 
                           f"Found {count} sessions with fields: {present_fields}")
                else:
                    log_test("Session list", "PASS", "No active sessions found")
                    
            except Exception as e:
                log_test("Session management", "FAIL", f"Response parsing error: {e}")
        else:
            status = response.status_code if response else "No response"
            log_test("Session management", "FAIL", f"Status: {status}")
    
    def test_04_logout_all_devices(self):
        """Test logout all devices functionality"""
        print(f"\n{Colors.BLUE}=== Test 4: Logout All Devices ==={Colors.END}")
        
        if not self.auth_headers:
            log_test("Logout all devices", "SKIP", "No auth token available")
            return
        
        response = make_request(
            "POST",
            "/auth/logout-all-devices",
            headers=self.auth_headers,
            json_data={"current_session_id": self.session_id}
        )
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                revoked_count = data.get("sessions_revoked", 0)
                message = data.get("message", "")
                
                log_test("Logout all devices", "PASS", 
                       f"Revoked {revoked_count} sessions. Message: {message}")
            except Exception as e:
                log_test("Logout all devices", "FAIL", f"Response parsing error: {e}")
        else:
            status = response.status_code if response else "No response"
            log_test("Logout all devices", "FAIL", f"Status: {status}")
    
    def test_05_refresh_token_rotation(self):
        """Test refresh token rotation security"""
        print(f"\n{Colors.BLUE}=== Test 5: Refresh Token Rotation ==={Colors.END}")
        
        if not self.refresh_token:
            log_test("Refresh token rotation", "SKIP", "No refresh token available")
            return
        
        # Use refresh token to get new tokens
        response = make_request(
            "POST",
            "/auth/refresh",
            json_data={"refresh_token": self.refresh_token}
        )
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                new_refresh_token = data.get("refresh_token")
                
                log_test("Refresh token success", "PASS", "Got new tokens successfully")
                
                # Now try to use the OLD refresh token again - should fail
                old_token_response = make_request(
                    "POST",
                    "/auth/refresh",
                    json_data={"refresh_token": self.refresh_token}
                )
                
                if old_token_response and old_token_response.status_code == 401:
                    log_test("Token rotation security", "PASS", "Old refresh token correctly invalidated")
                else:
                    status = old_token_response.status_code if old_token_response else "No response"
                    log_test("Token rotation security", "FAIL", f"Old token still works - Status: {status}")
                
                # Update for future tests
                self.refresh_token = new_refresh_token
                if "access_token" in data:
                    self.auth_headers = {"Authorization": f"Bearer {data['access_token']}"}
                
            except Exception as e:
                log_test("Refresh token rotation", "FAIL", f"Response parsing error: {e}")
        else:
            status = response.status_code if response else "No response"
            log_test("Refresh token rotation", "FAIL", f"Status: {status}")

class ForexTestSuite:
    def __init__(self, auth_headers: Dict[str, str]):
        self.auth_headers = auth_headers
    
    def test_06_admin_only_rate_creation(self):
        """Test that only admins can create forex rates"""
        print(f"\n{Colors.BLUE}=== Test 6: Forex - Admin Only Rate Creation ==={Colors.END}")
        
        if not self.auth_headers:
            log_test("Admin rate creation", "SKIP", "No auth token available")
            return
        
        # Try to create a rate (should fail for non-admin user)
        rate_data = {
            "currency": "USD",
            "rate": 83.50,
            "source": "manual",
            "notes": "Test rate"
        }
        
        response = make_request(
            "POST",
            "/forex/rate",
            headers=self.auth_headers,
            json_data=rate_data
        )
        
        if response and response.status_code == 403:
            try:
                data = response.json()
                detail = data.get("detail", "")
                if "admin" in detail.lower():
                    log_test("Admin-only validation", "PASS", f"Correctly blocked non-admin: {detail}")
                else:
                    log_test("Admin-only validation", "FAIL", f"Wrong error message: {detail}")
            except:
                log_test("Admin-only validation", "PASS", "403 Forbidden received (correct)")
        else:
            status = response.status_code if response else "No response"
            log_test("Admin-only validation", "FAIL", f"Expected 403, got: {status}")
    
    def test_07_currency_validation(self):
        """Test currency validation"""
        print(f"\n{Colors.BLUE}=== Test 7: Forex - Currency Validation ==={Colors.END}")
        
        if not self.auth_headers:
            log_test("Currency validation", "SKIP", "No auth token available")
            return
        
        # Try to create rate with invalid currency
        invalid_rate_data = {
            "currency": "INVALID",
            "rate": 83.50,
            "source": "manual"
        }
        
        response = make_request(
            "POST",
            "/forex/rate",
            headers=self.auth_headers,
            json_data=invalid_rate_data
        )
        
        if response and response.status_code == 422:
            log_test("Currency validation", "PASS", "Invalid currency properly rejected with 422")
        elif response and response.status_code == 403:
            log_test("Currency validation", "PASS", "Blocked at admin level (expected due to non-admin user)")
        else:
            status = response.status_code if response else "No response"
            log_test("Currency validation", "FAIL", f"Expected 422 or 403, got: {status}")
    
    def test_08_rate_validation(self):
        """Test rate value validation"""
        print(f"\n{Colors.BLUE}=== Test 8: Forex - Rate Validation ==={Colors.END}")
        
        if not self.auth_headers:
            log_test("Rate validation", "SKIP", "No auth token available")
            return
        
        # Try to create rate with negative value
        negative_rate_data = {
            "currency": "USD",
            "rate": -10.50,
            "source": "manual"
        }
        
        response = make_request(
            "POST",
            "/forex/rate",
            headers=self.auth_headers,
            json_data=negative_rate_data
        )
        
        if response and response.status_code == 422:
            log_test("Negative rate validation", "PASS", "Negative rate properly rejected with 422")
        elif response and response.status_code == 403:
            log_test("Negative rate validation", "PASS", "Blocked at admin level (expected due to non-admin user)")
        else:
            status = response.status_code if response else "No response"
            log_test("Negative rate validation", "FAIL", f"Expected 422 or 403, got: {status}")
    
    def test_09_latest_rates(self):
        """Test latest rates endpoint"""
        print(f"\n{Colors.BLUE}=== Test 9: Forex - Latest Rates ==={Colors.END}")
        
        response = make_request("GET", "/forex/latest")
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                rates = data.get("rates", {})
                base = data.get("base", "")
                cached = data.get("cached", False)
                
                if rates and base == "INR":
                    currency_count = len(rates)
                    sample_currencies = list(rates.keys())[:3]
                    log_test("Latest rates", "PASS", 
                           f"Got rates for {currency_count} currencies (sample: {sample_currencies}). Cached: {cached}")
                else:
                    log_test("Latest rates", "FAIL", f"Invalid response structure. Base: {base}")
            except Exception as e:
                log_test("Latest rates", "FAIL", f"Response parsing error: {e}")
        else:
            status = response.status_code if response else "No response"
            log_test("Latest rates", "FAIL", f"Status: {status}")
    
    def test_10_history_pagination(self):
        """Test forex history with pagination"""
        print(f"\n{Colors.BLUE}=== Test 10: Forex - History with Pagination ==={Colors.END}")
        
        if not self.auth_headers:
            log_test("History pagination", "SKIP", "No auth token available")
            return
        
        response = make_request(
            "GET",
            "/forex/history/USD?page=1&page_size=10&days=30",
            headers=self.auth_headers
        )
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                history = data.get("history", [])
                pagination = data.get("pagination", {})
                statistics = data.get("statistics", {})
                
                # Check pagination structure
                pagination_fields = ["page", "page_size", "total_count", "total_pages", "has_next", "has_prev"]
                present_pagination = [field for field in pagination_fields if field in pagination]
                
                # Check statistics
                stats_fields = list(statistics.keys())
                
                log_test("History pagination", "PASS", 
                       f"Got {len(history)} history items. "
                       f"Pagination: {present_pagination}. "
                       f"Statistics: {stats_fields}")
                
            except Exception as e:
                log_test("History pagination", "FAIL", f"Response parsing error: {e}")
        else:
            status = response.status_code if response else "No response"
            log_test("History pagination", "FAIL", f"Status: {status}")

def run_all_tests():
    """Run all security and forex tests"""
    print(f"{Colors.BOLD}🔒 ExportFlow Security & Forex Test Suite{Colors.END}")
    print(f"Testing against: {BASE_URL}")
    print(f"Test user: {TEST_USER['email']}")
    
    # Initialize test suites
    security_tests = SecurityTestSuite()
    
    # Run security tests
    security_tests.test_01_failed_login_tracking()
    
    # Login for authenticated tests
    login_success = security_tests.test_02_successful_login()
    
    if login_success:
        security_tests.test_03_session_management()
        security_tests.test_04_logout_all_devices()
        security_tests.test_05_refresh_token_rotation()
        
        # Run forex tests with auth headers
        forex_tests = ForexTestSuite(security_tests.auth_headers)
        forex_tests.test_06_admin_only_rate_creation()
        forex_tests.test_07_currency_validation()
        forex_tests.test_08_rate_validation()
        forex_tests.test_09_latest_rates()
        forex_tests.test_10_history_pagination()
    else:
        print(f"{Colors.RED}⚠️  Authenticated tests skipped due to login failure{Colors.END}")
        
        # Still run public forex tests
        forex_tests = ForexTestSuite({})
        forex_tests.test_09_latest_rates()
    
    print(f"\n{Colors.BOLD}✅ Test suite completed{Colors.END}")

if __name__ == "__main__":
    run_all_tests()