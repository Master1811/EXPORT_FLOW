import requests
import sys
import json
from datetime import datetime
import os

class ProductionReadinessAPITester:
    def __init__(self, base_url="https://resilient-api-1.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.company_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if endpoint != self.base_url else self.base_url
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            # Check for rate limiting headers in response
            if 'X-RateLimit' in str(response.headers):
                rate_limit_info = {k: v for k, v in response.headers.items() if 'ratelimit' in k.lower()}
                details += f", Rate Limit Headers: {rate_limit_info}"
            
            if not success:
                details += f", Expected: {expected_status}"
                try:
                    error_data = response.json()
                    details += f", Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details += f", Response: {response.text[:200]}"

            self.log_test(name, success, details)
            
            if success:
                try:
                    return response.json()
                except:
                    return {"status": "success", "raw_response": response.text}
            return None

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return None

    def test_health_endpoint(self):
        """Test GET /api/health - Should return healthy status"""
        result = self.run_test("Health Endpoint", "GET", "health", 200)
        if result and result.get("status") == "healthy":
            return True
        return False

    def test_metrics_endpoint(self):
        """Test GET /api/metrics - Should return uptime metrics"""
        result = self.run_test("Metrics Endpoint", "GET", "metrics", 200)
        if result and "uptime" in result:
            return True
        return False

    def test_database_metrics(self):
        """Test GET /api/metrics/database - Should return connection pool stats"""
        result = self.run_test("Database Metrics", "GET", "metrics/database", 200)
        if result and "pool" in result:
            return True
        return False

    def test_circuit_breaker_metrics(self):
        """Test GET /api/metrics/circuit-breakers - Should return circuit breaker status"""
        result = self.run_test("Circuit Breaker Metrics", "GET", "metrics/circuit-breakers", 200)
        if result and "circuit_breakers" in result:
            return True
        return False

    def test_login_with_rate_limiting(self):
        """Test POST /api/auth/login - Test login works and verify rate limit headers"""
        login_data = {
            "email": "test@moradabad.com",
            "password": "Test@123"
        }
        
        result = self.run_test("Login with Rate Limiting", "POST", "auth/login", 200, login_data)
        if result:
            self.token = result.get('access_token')
            self.user_id = result.get('user', {}).get('id')
            self.company_id = result.get('user', {}).get('company_id')
            return True
        return False

    def test_create_shipment_performance(self):
        """Test creating a shipment to verify database indexes performance"""
        shipment_data = {
            "shipment_number": f"SH-PERF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "buyer_name": "Performance Test Buyer Corp",
            "buyer_country": "USA",
            "destination_port": "USLAX (Los Angeles)",
            "origin_port": "INNSA (Nhava Sheva)",
            "incoterm": "FOB",
            "currency": "USD",
            "total_value": 75000.0,
            "status": "draft",
            "product_description": "Performance test electronic components",
            "hs_codes": ["8471", "8542"]
        }
        
        import time
        start_time = time.time()
        result = self.run_test("Create Shipment (Performance)", "POST", "shipments", 200, shipment_data)
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f"    Response time: {response_time:.3f}s")
        
        if result and response_time < 2.0:  # Should be fast with indexes
            self.test_shipment_id = result.get('id')
            return True
        return False

    def test_account_aggregator_webhook(self):
        """Test POST /api/webhooks/account-aggregator with sample payload"""
        webhook_payload = {
            "event_type": "consent_approved",
            "consent_id": "test-consent-123",
            "customer_id": "cust-456",
            "fip_id": "hdfc-bank",
            "timestamp": datetime.now().isoformat() + "Z",
            "data": {
                "consent_details": "Sample consent data"
            }
        }
        
        result = self.run_test("Account Aggregator Webhook", "POST", "webhooks/account-aggregator", 200, webhook_payload)
        if result and result.get("status") == "received" and result.get("processed"):
            return True
        return False

    def test_rate_limiting_enforcement(self):
        """Test rate limiting by making multiple rapid requests"""
        print("\n🔄 Testing Rate Limiting Enforcement...")
        
        # Make 6 rapid login attempts (limit is 5/minute)
        login_data = {
            "email": "invalid@test.com",
            "password": "wrongpassword"
        }
        
        rate_limited = False
        for i in range(7):  # Try 7 requests to ensure we hit the limit
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"    Request {i+1}: Status {response.status_code}")
            
            if response.status_code == 429:  # Too Many Requests
                rate_limited = True
                print(f"    ✅ Rate limit triggered after {i+1} attempts")
                break
                
            # Check if we have rate limit headers even on successful requests
            if 'x-ratelimit-remaining' in response.headers:
                remaining = response.headers.get('x-ratelimit-remaining')
                print(f"    Rate limit remaining: {remaining}")
        
        success = rate_limited
        self.log_test("Rate Limiting Enforcement", success, 
                     "Rate limiting triggered" if success else "Rate limiting not enforced within 7 attempts")
        return success

    def run_production_readiness_tests(self):
        """Run production readiness specific tests"""
        print("🚀 Starting Production Readiness API Tests")
        print("=" * 60)

        # Test credentials from review request
        print("📋 Using test credentials: test@moradabad.com / Test@123")

        # 1. Health & Metrics Endpoints
        print("\n🏥 Testing Health & Metrics Endpoints...")
        self.test_health_endpoint()
        self.test_metrics_endpoint()
        self.test_database_metrics()
        self.test_circuit_breaker_metrics()

        # 2. Authentication with Rate Limiting
        print("\n🔐 Testing Authentication with Rate Limiting...")
        self.test_login_with_rate_limiting()
        
        # Test rate limiting enforcement
        self.test_rate_limiting_enforcement()

        # 3. Database Indexes Verification
        print("\n🗃️ Testing Database Performance (Indexes)...")
        if self.token:
            self.test_create_shipment_performance()
        else:
            print("    ❌ Skipping performance tests - no authentication token")

        # 4. Account Aggregator Webhook
        print("\n🔗 Testing Account Aggregator Webhook...")
        self.test_account_aggregator_webhook()

        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 PRODUCTION READINESS TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
        
        # Show successful tests  
        successful_tests = [r for r in self.test_results if r['success']]
        if successful_tests:
            print(f"\n✅ Successful Tests ({len(successful_tests)}):")
            for test in successful_tests:
                print(f"  • {test['test']}")

def main():
    # Check if backend URL is provided in environment
    backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'https://resilient-api-1.preview.emergentagent.com') + '/api'
    
    tester = ProductionReadinessAPITester(backend_url)
    
    try:
        success = tester.run_production_readiness_tests()
        tester.print_summary()
        
        return 0 if tester.tests_passed == tester.tests_run else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        tester.print_summary()
        return 1
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {str(e)}")
        tester.print_summary()
        return 1

if __name__ == "__main__":
    sys.exit(main())