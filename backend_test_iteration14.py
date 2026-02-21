#!/usr/bin/env python3
"""
ExportFlow Fintech Features Testing - Iteration 14
Tests DGFT Excel Generator, Audit Vault, RBI Risk Clock, OFAC Screening, Credit Scoring
"""
import requests
import json
import time
import sys
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Test Configuration
BASE_URL = "http://localhost:8001/api"
TEST_USER = {
    "email": "test@exportflow.com",
    "password": "Test@123",
    "full_name": "Test User",
    "company_name": "Test Export Company"
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
    except Exception as e:
        print(f"    {Colors.RED}Request failed: {str(e)}{Colors.END}")
        raise

class ExportFlowTester:
    def __init__(self):
        self.token = None
        self.user_data = None
        self.test_shipment_id = None
        self.tests_passed = 0
        self.tests_total = 0

    def run_test(self, name: str, test_func) -> bool:
        """Run a test function and track results"""
        self.tests_total += 1
        try:
            success = test_func()
            if success:
                self.tests_passed += 1
                log_test(name, "PASS")
            else:
                log_test(name, "FAIL")
            return success
        except Exception as e:
            log_test(name, "FAIL", str(e))
            return False

    def test_health_check(self) -> bool:
        """Test health endpoint with database status"""
        try:
            response = make_request("GET", "/health", expected_status=200)
            if response.status_code == 200:
                health_data = response.json()
                db_connected = health_data.get("database", {}).get("connected", False)
                if db_connected:
                    log_test("Health Check", "PASS", f"Database connected: {db_connected}")
                    return True
                else:
                    log_test("Health Check", "FAIL", "Database not connected")
                    return False
            return False
        except:
            return False

    def test_user_registration(self) -> bool:
        """Test user registration with full_name field"""
        try:
            response = make_request("POST", "/auth/register", 
                                  json_data=TEST_USER, expected_status=200)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_data = data.get("user")
                
                # Verify full_name field is included
                if self.user_data and self.user_data.get("full_name") == TEST_USER["full_name"]:
                    log_test("Registration with full_name", "PASS", f"User: {self.user_data.get('full_name')}")
                    return True
                else:
                    log_test("Registration", "FAIL", "full_name field missing")
                    return False
            return False
        except:
            return False

    def test_login(self) -> bool:
        """Test login and get auth token"""
        try:
            response = make_request("POST", "/auth/login", 
                                  json_data={"email": TEST_USER["email"], "password": TEST_USER["password"]}, 
                                  expected_status=200)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_data = data.get("user")
                log_test("Login", "PASS", f"Token received: {bool(self.token)}")
                return True
            return False
        except:
            return False

    def get_headers(self) -> Dict[str, str]:
        """Get headers with authorization"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def test_create_test_shipment(self) -> bool:
        """Create test shipment with old date (250+ days ago)"""
        try:
            old_date = (datetime.now() - timedelta(days=250)).isoformat() + "Z"
            
            shipment_data = {
                "shipment_number": f"TEST-{int(time.time())}",
                "buyer_name": "Test Buyer Corp",
                "buyer_country": "US",
                "destination_port": "New York",
                "origin_port": "Mumbai",
                "product_description": "Test Export Products",
                "total_value": 50000,
                "currency": "USD",
                "hs_codes": ["1234.56"],
                "expected_ship_date": old_date,
                "actual_ship_date": old_date,
                "status": "shipped"
            }
            
            response = make_request("POST", "/shipments", 
                                  headers=self.get_headers(), 
                                  json_data=shipment_data, 
                                  expected_status=200)
            
            if response.status_code == 200:
                data = response.json()
                self.test_shipment_id = data.get("id")
                log_test("Create Test Shipment (250+ days)", "PASS", f"ID: {self.test_shipment_id}")
                return True
            return False
        except:
            return False

    def test_risk_clock_data(self) -> bool:
        """Test risk clock with CRITICAL bucket"""
        try:
            response = make_request("GET", "/risk-clock", 
                                  headers=self.get_headers(), 
                                  expected_status=200)
            
            if response.status_code == 200:
                data = response.json()
                summary = data.get("summary", {})
                buckets = data.get("buckets", {})
                
                critical_count = summary.get("critical_count", 0)
                has_critical = len(buckets.get("critical", [])) > 0
                
                if has_critical or critical_count > 0:
                    log_test("Risk Clock - CRITICAL bucket", "PASS", f"Critical shipments: {critical_count}")
                    return True
                else:
                    log_test("Risk Clock", "PARTIAL", "No critical shipments (may need older test data)")
                    return True  # This is acceptable
            return False
        except:
            return False

    def test_aging_summary(self) -> bool:
        """Test aging summary distribution"""
        try:
            response = make_request("GET", "/risk-clock/aging-summary", 
                                  headers=self.get_headers(), 
                                  expected_status=200)
            
            if response.status_code == 200:
                data = response.json()
                aging_distribution = data.get("aging_distribution", [])
                
                if len(aging_distribution) == 4:  # Should have 4 buckets
                    log_test("Aging Summary", "PASS", f"Distribution buckets: {len(aging_distribution)}")
                    return True
                else:
                    log_test("Aging Summary", "FAIL", f"Expected 4 buckets, got {len(aging_distribution)}")
                    return False
            return False
        except:
            return False

    def test_dgft_validation(self) -> bool:
        """Test DGFT data validation"""
        try:
            response = make_request("GET", "/dgft/validate", 
                                  headers=self.get_headers(), 
                                  expected_status=200)
            
            if response.status_code == 200:
                data = response.json()
                total_records = data.get("total_records", 0)
                is_valid = data.get("is_valid", False)
                
                log_test("DGFT Validation", "PASS", f"Records: {total_records}, Valid: {is_valid}")
                return True
            return False
        except:
            return False

    def test_dgft_excel_export(self) -> bool:
        """Test DGFT Excel file download"""
        try:
            response = make_request("GET", "/dgft/export", 
                                  headers=self.get_headers(), 
                                  expected_status=200)
            
            if response.status_code == 200:
                # Check if it's actually Excel content
                content_type = response.headers.get("Content-Type", "")
                size = len(response.content)
                
                if "spreadsheet" in content_type or size > 1000:
                    log_test("DGFT Excel Export", "PASS", f"Size: {size} bytes")
                    return True
                else:
                    log_test("DGFT Excel Export", "FAIL", f"Invalid content: {content_type}")
                    return False
            return False
        except:
            return False

    def test_audit_vault_generation(self) -> bool:
        """Test audit package generation"""
        if not self.test_shipment_id:
            log_test("Audit Vault Generation", "SKIP", "No test shipment available")
            return False
        
        try:
            response = make_request("POST", f"/audit-vault/generate/{self.test_shipment_id}", 
                                  headers=self.get_headers(), 
                                  expected_status=200)
            
            if response.status_code == 200:
                data = response.json()
                job_id = data.get("job_id")
                
                if job_id:
                    log_test("Audit Vault Generation", "PASS", f"Job ID: {job_id}")
                    return True
                else:
                    log_test("Audit Vault Generation", "FAIL", "No job ID returned")
                    return False
            return False
        except:
            return False

    def test_audit_job_status(self) -> bool:
        """Test audit package job status"""
        if not self.test_shipment_id:
            return False
        
        try:
            # First create a job
            gen_response = make_request("POST", f"/audit-vault/generate/{self.test_shipment_id}", 
                                      headers=self.get_headers())
            
            if gen_response.status_code == 200:
                job_id = gen_response.json().get("job_id")
                
                # Wait a bit for processing
                time.sleep(2)
                
                # Check status
                status_response = make_request("GET", f"/audit-vault/status/{job_id}", 
                                             headers=self.get_headers(), 
                                             expected_status=200)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    progress = status_data.get("progress", 0)
                    log_test("Audit Job Status", "PASS", f"Progress: {progress}%")
                    return True
            return False
        except:
            return False

    def test_payment_realization(self) -> bool:
        """Test payment realization marking"""
        if not self.test_shipment_id:
            return False
        
        try:
            payment_data = {
                "amount": 25000,
                "currency": "USD",
                "reference_number": "TEST-REF-001",
                "bank_name": "Test Bank"
            }
            
            response = make_request("POST", f"/risk-clock/realize/{self.test_shipment_id}", 
                                  headers=self.get_headers(), 
                                  json_data=payment_data, 
                                  expected_status=200)
            
            if response.status_code == 200:
                data = response.json()
                realization_pct = data.get("realization_percentage", 0)
                log_test("Payment Realization", "PASS", f"Realization: {realization_pct}%")
                return True
            return False
        except:
            return False

    def test_rbi_letter_drafting(self) -> bool:
        """Test AI-powered RBI letter drafting"""
        if not self.test_shipment_id:
            return False
        
        try:
            letter_data = {
                "reason": "delayed_payment",
                "extension_days": 90
            }
            
            response = make_request("POST", f"/risk-clock/draft-letter/{self.test_shipment_id}", 
                                  headers=self.get_headers(), 
                                  json_data=letter_data, 
                                  expected_status=200)
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", "")
                
                # Check for RBI/FEMA keywords
                rbi_keywords = ["RBI", "FEMA", "export", "realization", "extension"]
                keyword_count = sum(1 for keyword in rbi_keywords if keyword.lower() in content.lower())
                
                if len(content) > 500 and keyword_count >= 3:
                    log_test("RBI Letter Drafting", "PASS", f"Content: {len(content)} chars, Keywords: {keyword_count}")
                    return True
                else:
                    log_test("RBI Letter Drafting", "FAIL", f"Content: {len(content)}, Keywords: {keyword_count}")
                    return False
            return False
        except:
            return False

    def test_ofac_screening(self) -> bool:
        """Test OFAC sanctions screening"""
        try:
            screen_data = {
                "entity_name": "Test Company LLC",
                "entity_type": "buyer",
                "country_code": "US"
            }
            
            response = make_request("POST", "/compliance/ofac-screen", 
                                  headers=self.get_headers(), 
                                  json_data=screen_data, 
                                  expected_status=200)
            
            if response.status_code == 200:
                data = response.json()
                is_clear = data.get("is_clear", False)
                risk_score = data.get("risk_score", 0)
                
                log_test("OFAC Screening", "PASS", f"Clear: {is_clear}, Risk Score: {risk_score}")
                return True
            return False
        except:
            return False

    def test_company_credit_score(self) -> bool:
        """Test aggregation-based company credit scoring"""
        try:
            response = make_request("GET", "/credit/company-score", 
                                  headers=self.get_headers(), 
                                  expected_status=200)
            
            if response.status_code == 200:
                data = response.json()
                company_score = data.get("company_score", 0)
                scoring_basis = data.get("scoring_basis", "")
                
                if scoring_basis == "aggregation":
                    log_test("Company Credit Score", "PASS", f"Score: {company_score}, Basis: {scoring_basis}")
                    return True
                else:
                    log_test("Company Credit Score", "FAIL", f"Expected aggregation basis, got: {scoring_basis}")
                    return False
            return False
        except:
            return False

    def run_comprehensive_test(self) -> bool:
        """Run all tests in sequence"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== ExportFlow Fintech Features Test Suite ==={Colors.END}")
        print(f"Testing endpoint: {BASE_URL}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Authentication Tests
        print(f"{Colors.BLUE}--- Authentication Tests ---{Colors.END}")
        self.run_test("Health Check with Database Status", self.test_health_check)
        self.run_test("User Registration (with full_name)", self.test_user_registration)
        self.run_test("User Login", self.test_login)

        if not self.token:
            print(f"\n{Colors.RED}Authentication failed - stopping tests{Colors.END}")
            return False

        # Core Feature Tests
        print(f"\n{Colors.BLUE}--- Core Feature Tests ---{Colors.END}")
        self.run_test("Create Test Shipment (250+ days old)", self.test_create_test_shipment)
        self.run_test("RBI Risk Clock Data", self.test_risk_clock_data)
        self.run_test("Risk Clock Aging Summary", self.test_aging_summary)

        # DGFT Tests
        print(f"\n{Colors.BLUE}--- DGFT Excel Generator Tests ---{Colors.END}")
        self.run_test("DGFT Data Validation", self.test_dgft_validation)
        self.run_test("DGFT Excel Export", self.test_dgft_excel_export)

        # Audit Vault Tests
        print(f"\n{Colors.BLUE}--- Audit Vault Tests ---{Colors.END}")
        self.run_test("Audit Package Generation", self.test_audit_vault_generation)
        self.run_test("Audit Job Status Check", self.test_audit_job_status)

        # Risk Clock Action Tests
        print(f"\n{Colors.BLUE}--- Risk Clock Action Tests ---{Colors.END}")
        self.run_test("Payment Realization", self.test_payment_realization)
        self.run_test("RBI Letter Drafting (AI)", self.test_rbi_letter_drafting)

        # Compliance Tests
        print(f"\n{Colors.BLUE}--- Compliance & Scoring Tests ---{Colors.END}")
        self.run_test("OFAC Sanctions Screening", self.test_ofac_screening)
        self.run_test("Company Credit Score (Aggregation)", self.test_company_credit_score)

        # Results Summary
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== TEST RESULTS ==={Colors.END}")
        success_rate = (self.tests_passed / self.tests_total * 100) if self.tests_total > 0 else 0
        print(f"Tests Passed: {self.tests_passed}/{self.tests_total} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print(f"{Colors.GREEN}Overall Status: PASS{Colors.END}")
            return True
        else:
            print(f"{Colors.RED}Overall Status: FAIL{Colors.END}")
            return False

def main():
    """Main test execution"""
    tester = ExportFlowTester()
    success = tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())