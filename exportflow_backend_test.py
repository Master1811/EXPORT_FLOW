#!/usr/bin/env python3
"""
ExportFlow Backend Test Suite - Specific Testing for Review Request
Tests specific backend improvements as requested:
1. Forex API latest endpoint format validation
2. Payment currency validation with shipment currency matching
3. Health check endpoint functionality
"""
import requests
import json
import time
import sys
from typing import Dict, Any, Optional

# Test Configuration
BASE_URL = "http://localhost:8001/api"
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

class ExportFlowTestSuite:
    def __init__(self):
        self.session = requests.Session()
        self.auth_headers = {}
        self.test_user_id = None
        self.test_shipment_id = None
    
    def test_01_login(self):
        """Login to get authentication token"""
        print(f"\n{Colors.BLUE}=== Test 1: User Login ==={Colors.END}")
        
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
                self.test_user_id = data.get("user", {}).get("id", "test-user-id")
                
                log_test("Login success", "PASS", f"Authenticated as {TEST_USER['email']}")
                return True
            except Exception as e:
                log_test("Login response parsing", "FAIL", str(e))
                return False
        else:
            log_test("Login", "FAIL", f"Status {response.status_code}: {response.text[:200]}")
            return False

    def test_02_health_check(self):
        """Test GET /api/health endpoint"""
        print(f"\n{Colors.BLUE}=== Test 2: Health Check Endpoint ==={Colors.END}")
        
        response = make_request("GET", "/health")
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                status = data.get("status")
                timestamp = data.get("timestamp")
                
                if status == "healthy":
                    log_test("Health check status", "PASS", f"Status: {status}, Timestamp: {timestamp}")
                else:
                    log_test("Health check status", "FAIL", f"Expected 'healthy', got: {status}")
                
                return True
            except Exception as e:
                log_test("Health check parsing", "FAIL", f"Response parsing error: {e}")
                return False
        else:
            status = response.status_code if response else "No response"
            log_test("Health check", "FAIL", f"Status: {status}")
            return False

    def test_03_forex_latest_format(self):
        """Test GET /api/forex/latest endpoint format"""
        print(f"\n{Colors.BLUE}=== Test 3: Forex Latest Rates Format ==={Colors.END}")
        
        response = make_request("GET", "/forex/latest")
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                rates = data.get("rates", {})
                
                # Check if response has 'rates' key
                if "rates" not in data:
                    log_test("Forex latest structure", "FAIL", "Missing 'rates' key in response")
                    return False
                
                # Check format: rates should be { "USD": { "rate": 83.5, "source": "default" }, ... }
                if len(rates) == 0:
                    log_test("Forex latest rates", "FAIL", "No rates found in response")
                    return False
                
                # Test with USD currency (should be present)
                usd_rate = rates.get("USD")
                if usd_rate is None:
                    log_test("USD rate presence", "FAIL", "USD rate not found in response")
                    return False
                
                # Check USD rate format
                if isinstance(usd_rate, dict):
                    if "rate" in usd_rate and "source" in usd_rate:
                        rate_value = usd_rate.get("rate")
                        source_value = usd_rate.get("source")
                        log_test("Forex latest format", "PASS", 
                               f"Correct format - USD: rate={rate_value}, source={source_value}")
                    else:
                        log_test("Forex latest format", "FAIL", 
                               f"USD rate missing 'rate' or 'source' keys: {usd_rate}")
                        return False
                else:
                    log_test("Forex latest format", "FAIL", 
                           f"USD rate is not an object: {type(usd_rate)} - {usd_rate}")
                    return False
                
                # Verify multiple currencies
                currency_count = len(rates)
                log_test("Forex currencies count", "PASS", f"Found rates for {currency_count} currencies")
                
                return True
                
            except Exception as e:
                log_test("Forex latest parsing", "FAIL", f"Response parsing error: {e}")
                return False
        else:
            status = response.status_code if response else "No response"
            log_test("Forex latest", "FAIL", f"Status: {status}")
            return False

    def test_04_create_test_shipment(self):
        """Create a test shipment with USD currency"""
        print(f"\n{Colors.BLUE}=== Test 4: Create Test Shipment (USD) ==={Colors.END}")
        
        if not self.auth_headers:
            log_test("Create shipment", "SKIP", "No auth token available")
            return False
        
        shipment_data = {
            "shipment_number": f"TEST-USD-{int(time.time())}",
            "buyer_name": "Test Buyer Corporation",
            "buyer_country": "United States",
            "currency": "USD",
            "total_value": 50000.00,
            "status": "in_transit",
            "export_date": "2024-01-15T00:00:00Z"
        }
        
        response = make_request(
            "POST",
            "/shipments",
            headers=self.auth_headers,
            json_data=shipment_data
        )
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                self.test_shipment_id = data.get("id")
                currency = data.get("currency")
                
                log_test("Test shipment created", "PASS", 
                       f"Shipment ID: {self.test_shipment_id}, Currency: {currency}")
                return True
            except Exception as e:
                log_test("Shipment creation parsing", "FAIL", f"Response parsing error: {e}")
                return False
        else:
            status = response.status_code if response else "No response"
            text = response.text[:200] if response else "No response"
            log_test("Create shipment", "FAIL", f"Status: {status}, Response: {text}")
            return False

    def test_05_payment_currency_mismatch(self):
        """Test payment currency validation - should FAIL with EUR for USD shipment"""
        print(f"\n{Colors.BLUE}=== Test 5: Payment Currency Mismatch (Should Fail) ==={Colors.END}")
        
        if not self.auth_headers or not self.test_shipment_id:
            log_test("Payment currency mismatch", "SKIP", "No auth token or shipment ID available")
            return False
        
        # Try to create payment with EUR currency for USD shipment
        payment_data = {
            "shipment_id": self.test_shipment_id,
            "currency": "EUR",  # Mismatched currency - should fail
            "amount": 45000.00,
            "payment_method": "wire_transfer",
            "reference": "TEST-EUR-MISMATCH"
        }
        
        response = make_request(
            "POST",
            "/payments",
            headers=self.auth_headers,
            json_data=payment_data
        )
        
        if response and response.status_code == 400:
            try:
                data = response.json()
                detail = data.get("detail", "")
                
                if "currency" in detail.lower() and "match" in detail.lower():
                    log_test("Currency mismatch validation", "PASS", 
                           f"Correctly rejected mismatched currency: {detail}")
                    return True
                else:
                    log_test("Currency mismatch validation", "FAIL", 
                           f"Wrong error message: {detail}")
                    return False
            except Exception as e:
                log_test("Currency mismatch parsing", "FAIL", f"Response parsing error: {e}")
                return False
        else:
            status = response.status_code if response else "No response"
            text = response.text[:200] if response else "No response"
            log_test("Currency mismatch validation", "FAIL", 
                   f"Expected 400 Bad Request, got Status: {status}, Response: {text}")
            return False

    def test_06_payment_currency_match(self):
        """Test payment currency validation - should SUCCEED with USD for USD shipment"""
        print(f"\n{Colors.BLUE}=== Test 6: Payment Currency Match (Should Succeed) ==={Colors.END}")
        
        if not self.auth_headers or not self.test_shipment_id:
            log_test("Payment currency match", "SKIP", "No auth token or shipment ID available")
            return False
        
        # Create payment with matching USD currency
        payment_data = {
            "shipment_id": self.test_shipment_id,
            "currency": "USD",  # Matching currency - should succeed
            "amount": 45000.00,
            "payment_method": "wire_transfer",
            "reference": "TEST-USD-MATCH"
        }
        
        response = make_request(
            "POST",
            "/payments",
            headers=self.auth_headers,
            json_data=payment_data
        )
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                payment_id = data.get("id")
                currency = data.get("currency")
                shipment_id = data.get("shipment_id")
                
                log_test("Currency match validation", "PASS", 
                       f"Payment created successfully - ID: {payment_id}, Currency: {currency}")
                return True
            except Exception as e:
                log_test("Currency match parsing", "FAIL", f"Response parsing error: {e}")
                return False
        else:
            status = response.status_code if response else "No response"
            text = response.text[:200] if response else "No response"
            log_test("Currency match validation", "FAIL", 
                   f"Expected 200 OK, got Status: {status}, Response: {text}")
            return False

    def test_07_forex_endpoint_no_auth(self):
        """Verify forex endpoint works without authentication"""
        print(f"\n{Colors.BLUE}=== Test 7: Forex Endpoint No Auth Required ==={Colors.END}")
        
        # Make request without authentication headers
        response = make_request("GET", "/forex/latest")
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                rates = data.get("rates", {})
                
                if len(rates) > 0:
                    log_test("Forex no auth", "PASS", 
                           f"Forex endpoint accessible without auth - {len(rates)} currencies")
                    return True
                else:
                    log_test("Forex no auth", "FAIL", "No rates returned")
                    return False
            except Exception as e:
                log_test("Forex no auth parsing", "FAIL", f"Response parsing error: {e}")
                return False
        else:
            status = response.status_code if response else "No response"
            log_test("Forex no auth", "FAIL", f"Expected 200 OK, got Status: {status}")
            return False

def run_all_tests():
    """Run all ExportFlow backend tests"""
    print(f"{Colors.BOLD}🚀 ExportFlow Backend Test Suite - Review Request Verification{Colors.END}")
    print(f"Testing against: {BASE_URL}")
    print(f"Test user: {TEST_USER['email']}")
    print(f"\n{Colors.YELLOW}Testing specific requirements:{Colors.END}")
    print(f"1. Forex API - GET /api/forex/latest endpoint format")
    print(f"2. Payment Currency Validation - currency must match shipment currency")
    print(f"3. Health Check - GET /api/health endpoint")
    
    # Initialize test suite
    test_suite = ExportFlowTestSuite()
    
    # Run tests in sequence
    tests = [
        test_suite.test_01_login,
        test_suite.test_02_health_check,
        test_suite.test_03_forex_latest_format,
        test_suite.test_07_forex_endpoint_no_auth,
        test_suite.test_04_create_test_shipment,
        test_suite.test_05_payment_currency_mismatch,
        test_suite.test_06_payment_currency_match,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        result = test()
        if result:
            passed += 1
        else:
            failed += 1
    
    # Final summary
    print(f"\n{Colors.BOLD}📊 TEST RESULTS SUMMARY{Colors.END}")
    print(f"{Colors.GREEN}✅ Passed: {passed}{Colors.END}")
    print(f"{Colors.RED}❌ Failed: {failed}{Colors.END}")
    print(f"{Colors.BLUE}📝 Total: {passed + failed}{Colors.END}")
    
    if failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED!{Colors.END}")
        return True
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  Some tests failed. Please review the issues above.{Colors.END}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)