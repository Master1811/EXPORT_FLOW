import requests
import sys
import json
from datetime import datetime

class ExporterFinanceAPITester:
    def __init__(self, base_url="https://shipment-optimizer-2.preview.emergentagent.com/api"):
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
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if not success:
                details += f", Expected: {expected_status}"
                try:
                    error_data = response.json()
                    details += f", Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details += f", Response: {response.text[:100]}"

            self.log_test(name, success, details)
            
            if success:
                try:
                    return response.json()
                except:
                    return {}
            return None

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return None

    def test_health_check(self):
        """Test health endpoint"""
        return self.run_test("Health Check", "GET", "health", 200)

    def test_register(self):
        """Test user registration"""
        test_user_data = {
            "email": "test@exportflow.com",
            "password": "test123",
            "full_name": "Test User",
            "company_name": "Test Export Company"
        }
        
        response = self.run_test("User Registration", "POST", "auth/register", 200, test_user_data)
        if response:
            self.token = response.get('access_token')
            self.user_id = response.get('user', {}).get('id')
            self.company_id = response.get('user', {}).get('company_id')
            return True
        return False

    def test_login(self):
        """Test user login"""
        login_data = {
            "email": "test@exportflow.com",
            "password": "test123"
        }
        
        response = self.run_test("User Login", "POST", "auth/login", 200, login_data)
        if response:
            self.token = response.get('access_token')
            self.user_id = response.get('user', {}).get('id')
            self.company_id = response.get('user', {}).get('company_id')
            return True
        return False

    def test_auth_me(self):
        """Test get current user"""
        return self.run_test("Get Current User", "GET", "auth/me", 200)

    def test_dashboard_stats(self):
        """Test dashboard stats"""
        return self.run_test("Dashboard Stats", "GET", "dashboard/stats", 200)

    def test_export_trend(self):
        """Test export trend chart data"""
        return self.run_test("Export Trend Chart", "GET", "dashboard/charts/export-trend", 200)

    def test_payment_status_chart(self):
        """Test payment status chart data"""
        return self.run_test("Payment Status Chart", "GET", "dashboard/charts/payment-status", 200)

    def test_create_shipment(self):
        """Test shipment creation"""
        shipment_data = {
            "shipment_number": f"SH-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "buyer_name": "Test Buyer Corp",
            "buyer_country": "USA",
            "destination_port": "USLAX (Los Angeles)",
            "origin_port": "INNSA (Nhava Sheva)",
            "incoterm": "FOB",
            "currency": "USD",
            "total_value": 50000.0,
            "status": "draft",
            "product_description": "Test electronic components",
            "hs_codes": ["8471", "8542"]
        }
        
        response = self.run_test("Create Shipment", "POST", "shipments", 200, shipment_data)
        if response:
            self.test_shipment_id = response.get('id')
            return response
        return None

    def test_get_shipments(self):
        """Test get shipments list"""
        return self.run_test("Get Shipments List", "GET", "shipments", 200)

    def test_get_shipment_by_id(self, shipment_id):
        """Test get single shipment"""
        return self.run_test("Get Shipment by ID", "GET", f"shipments/{shipment_id}", 200)

    def test_update_shipment(self, shipment_id):
        """Test shipment update"""
        update_data = {
            "status": "confirmed",
            "total_value": 55000.0
        }
        return self.run_test("Update Shipment", "PUT", f"shipments/{shipment_id}", 200, update_data)

    def test_create_payment(self, shipment_id):
        """Test payment creation"""
        payment_data = {
            "shipment_id": shipment_id,
            "amount": 25000.0,
            "currency": "USD",
            "payment_date": datetime.now().isoformat(),
            "payment_mode": "wire_transfer",
            "bank_reference": "TXN123456789"
        }
        return self.run_test("Create Payment", "POST", "payments", 200, payment_data)

    def test_get_receivables(self):
        """Test get receivables"""
        return self.run_test("Get Receivables", "GET", "receivables", 200)

    def test_forex_rates(self):
        """Test forex rates"""
        return self.run_test("Get Forex Rates", "GET", "forex/latest", 200)

    def test_gst_summary(self):
        """Test GST summary"""
        return self.run_test("GST Monthly Summary", "GET", "gst/summary/monthly", 200)

    def test_lut_status(self):
        """Test LUT status"""
        return self.run_test("LUT Status", "GET", "compliance/lut-status", 200)

    def test_rodtep_eligibility(self):
        """Test RoDTEP eligibility check"""
        return self.run_test("RoDTEP Eligibility", "GET", "incentives/rodtep-eligibility?hs_code=8471", 200)

    def test_calculate_incentive(self, shipment_id):
        """Test incentive calculation"""
        incentive_data = {
            "shipment_id": shipment_id,
            "hs_codes": ["8471"],
            "fob_value": 50000.0,
            "currency": "USD"
        }
        return self.run_test("Calculate Incentive", "POST", "incentives/calculate", 200, incentive_data)

    def test_ai_query(self):
        """Test AI assistant query"""
        query_data = {
            "query": "What are the current RoDTEP rates for electronics exports?",
            "context": "export incentives"
        }
        return self.run_test("AI Query", "POST", "ai/query", 200, query_data)

    def test_company_score(self):
        """Test company credit score"""
        return self.run_test("Company Credit Score", "GET", "credit/company-score", 200)

    def test_connector_status(self):
        """Test connector status - bank sync"""
        return self.run_test("Bank Sync Status", "GET", "sync/bank", 200)

    def test_gst_sync(self):
        """Test GST sync"""
        return self.run_test("GST Sync Status", "GET", "sync/gst", 200)

    def test_notifications(self):
        """Test notifications"""
        return self.run_test("Get Notifications", "GET", "notifications/history", 200)

    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting Exporter Finance Platform API Tests")
        print("=" * 60)

        # Basic health check
        self.test_health_check()

        # Authentication flow
        print("\n📋 Testing Authentication Flow...")
        if not self.test_register():
            # Try login if registration fails (user might already exist)
            if not self.test_login():
                print("❌ Authentication failed - stopping tests")
                return False

        self.test_auth_me()

        # Dashboard tests
        print("\n📊 Testing Dashboard...")
        self.test_dashboard_stats()
        self.test_export_trend()
        self.test_payment_status_chart()

        # Shipment management
        print("\n🚢 Testing Shipment Management...")
        shipment = self.test_create_shipment()
        self.test_get_shipments()
        
        if shipment and shipment.get('id'):
            shipment_id = shipment['id']
            self.test_get_shipment_by_id(shipment_id)
            self.test_update_shipment(shipment_id)
            
            # Payment tests
            print("\n💰 Testing Payment Management...")
            self.test_create_payment(shipment_id)
            self.test_get_receivables()
            
            # Incentive tests
            print("\n🎯 Testing Incentives...")
            self.test_rodtep_eligibility()
            self.test_calculate_incentive(shipment_id)

        # Forex tests
        print("\n💱 Testing Forex...")
        self.test_forex_rates()

        # GST & Compliance tests
        print("\n📋 Testing GST & Compliance...")
        self.test_gst_summary()
        self.test_lut_status()

        # AI tests
        print("\n🤖 Testing AI Assistant...")
        self.test_ai_query()

        # Credit tests
        print("\n📈 Testing Credit Intelligence...")
        self.test_company_score()

        # Connector tests
        print("\n🔗 Testing Connectors...")
        self.test_connector_status()
        self.test_gst_sync()

        # Notification tests
        print("\n🔔 Testing Notifications...")
        self.test_notifications()

        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
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

def main():
    tester = ExporterFinanceAPITester()
    
    try:
        success = tester.run_comprehensive_test()
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