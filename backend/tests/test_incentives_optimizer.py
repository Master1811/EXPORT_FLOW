"""
Epic 5: Incentives Optimizer - Backend API Tests
Tests for HS Code eligibility, Leakage dashboard, Shipment analysis, and Calculate incentive APIs
Moradabad handicraft HS codes: 74198030, 74181022, 94032010, 94055000, 73269099, 68022190
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "test@moradabad.com"
TEST_PASSWORD = "Test@123"

# Moradabad Handicraft HS Codes
MORADABAD_HS_CODES = {
    "74198030": {"desc": "Artware/Handicrafts of Brass", "rodtep": 3.0, "drawback": 1.2},
    "74181022": {"desc": "Utensils of Copper", "rodtep": 2.0, "drawback": 0.8},
    "94032010": {"desc": "Iron/Metal Furniture", "rodtep": 1.0, "drawback": 0.5},
    "94055000": {"desc": "Non-Electrical Lamps & Lighting", "rodtep": 2.0, "drawback": 0.8},
    "73269099": {"desc": "Iron Handicraft Planters", "rodtep": 1.5, "drawback": 0.6},
    "68022190": {"desc": "Worked Marble/Stone Articles", "rodtep": 2.0, "drawback": 0.8},
}


@pytest.fixture(scope="module")
def api_session():
    """Create a requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_token(api_session):
    """Get authentication token"""
    response = api_session.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture(scope="module")
def authenticated_session(api_session, auth_token):
    """Session with auth header"""
    api_session.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_session


# ===================== HEALTH CHECK =====================

class TestHealthCheck:
    """Health check and basic connectivity tests"""
    
    def test_api_health(self, api_session):
        """Test API health endpoint"""
        response = api_session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✓ API Health: {data['status']}")


# ===================== AUTHENTICATION =====================

class TestAuthentication:
    """Authentication flow tests"""
    
    def test_login_success(self, api_session):
        """Test successful login with test user"""
        response = api_session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == TEST_EMAIL
        print(f"✓ Login successful for {TEST_EMAIL}")
    
    def test_login_invalid_credentials(self, api_session):
        """Test login with invalid credentials"""
        response = api_session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code in [401, 400]
        print("✓ Invalid login rejected correctly")


# ===================== HS CODE ELIGIBILITY CHECKER =====================

class TestHSCodeEligibility:
    """Tests for RoDTEP/RoSCTL eligibility checker API - No auth required"""
    
    @pytest.mark.parametrize("hs_code,expected_rodtep,expected_drawback", [
        ("74198030", 3.0, 1.2),  # Brass Handicrafts
        ("74181022", 2.0, 0.8),  # Copper Utensils
        ("94032010", 1.0, 0.5),  # Iron Furniture
        ("94055000", 2.0, 0.8),  # Decorative Lamps
        ("73269099", 1.5, 0.6),  # Metal Planters
        ("68022190", 2.0, 0.8),  # Stone Decor
    ])
    def test_moradabad_hs_code_eligibility(self, api_session, hs_code, expected_rodtep, expected_drawback):
        """Test all Moradabad handicraft HS codes return correct eligibility"""
        response = api_session.get(f"{BASE_URL}/api/incentives/rodtep-eligibility", params={"hs_code": hs_code})
        assert response.status_code == 200
        data = response.json()
        
        # Verify eligibility structure
        assert data["hs_code"] == hs_code
        assert data["eligible"] == True
        assert data["scheme"] == "RoDTEP"
        
        # Verify rates
        assert data["rate_percent"] == expected_rodtep
        assert "all_rates" in data
        assert data["all_rates"]["rodtep"] == expected_rodtep
        assert data["all_rates"]["drawback"] == expected_drawback
        
        print(f"✓ HS Code {hs_code}: RoDTEP {expected_rodtep}%, Drawback {expected_drawback}%")
    
    def test_hs_code_with_description(self, api_session):
        """Test that brass handicrafts HS code returns correct description"""
        response = api_session.get(f"{BASE_URL}/api/incentives/rodtep-eligibility", params={"hs_code": "74198030"})
        assert response.status_code == 200
        data = response.json()
        assert "Brass" in data["description"] or "Artware" in data["description"]
        print(f"✓ HS Code description: {data['description']}")
    
    def test_hs_code_total_rate(self, api_session):
        """Test that total rate is correctly calculated"""
        response = api_session.get(f"{BASE_URL}/api/incentives/rodtep-eligibility", params={"hs_code": "74198030"})
        assert response.status_code == 200
        data = response.json()
        # Total should be RoDTEP + RoSCTL + Drawback
        expected_total = data["all_rates"]["rodtep"] + data["all_rates"]["rosctl"] + data["all_rates"]["drawback"]
        assert data["all_rates"]["total"] == expected_total
        print(f"✓ Total incentive rate: {expected_total}%")
    
    def test_hs_code_missing_parameter(self, api_session):
        """Test error handling for missing HS code"""
        response = api_session.get(f"{BASE_URL}/api/incentives/rodtep-eligibility")
        assert response.status_code == 422  # Validation error
        print("✓ Missing HS code returns validation error")


# ===================== LEAKAGE DASHBOARD =====================

class TestLeakageDashboard:
    """Tests for Money Left on Table / Leakage dashboard API"""
    
    def test_leakage_dashboard_structure(self, authenticated_session):
        """Test leakage dashboard returns correct structure"""
        response = authenticated_session.get(f"{BASE_URL}/api/incentives/leakage-dashboard")
        assert response.status_code == 200
        data = response.json()
        
        # Verify summary structure
        assert "summary" in data
        assert "total_exports" in data["summary"]
        assert "total_potential_incentives" in data["summary"]
        assert "total_claimed" in data["summary"]
        assert "total_leakage" in data["summary"]
        assert "recovery_rate" in data["summary"]
        
        # Verify shipment stats
        assert "shipment_stats" in data
        assert "total" in data["shipment_stats"]
        assert "claimed" in data["shipment_stats"]
        assert "unclaimed" in data["shipment_stats"]
        
        # Verify money left on table
        assert "money_left_on_table" in data
        assert "amount" in data["money_left_on_table"]
        assert "formatted" in data["money_left_on_table"]
        
        print(f"✓ Leakage dashboard structure valid")
    
    def test_leakage_dashboard_values(self, authenticated_session):
        """Test leakage dashboard returns expected values for Moradabad data"""
        response = authenticated_session.get(f"{BASE_URL}/api/incentives/leakage-dashboard")
        assert response.status_code == 200
        data = response.json()
        
        # Verify sample shipments data (~₹32L exports, ~₹85,250 potential)
        assert data["summary"]["total_exports"] >= 3000000  # At least ₹30L
        assert data["summary"]["total_potential_incentives"] >= 80000  # At least ₹80k
        
        # Verify 4 sample shipments
        assert data["shipment_stats"]["total"] >= 4
        
        print(f"✓ Total exports: ₹{data['summary']['total_exports']:,.0f}")
        print(f"✓ Potential incentives: ₹{data['summary']['total_potential_incentives']:,.0f}")
        print(f"✓ Leakage: ₹{data['summary']['total_leakage']:,.0f}")
    
    def test_leakage_dashboard_priority(self, authenticated_session):
        """Test priority is calculated based on leakage amount"""
        response = authenticated_session.get(f"{BASE_URL}/api/incentives/leakage-dashboard")
        assert response.status_code == 200
        data = response.json()
        
        priority = data["money_left_on_table"]["priority"]
        assert priority in ["critical", "high", "medium", "low"]
        print(f"✓ Priority level: {priority}")
    
    def test_top_leaking_shipments(self, authenticated_session):
        """Test top leaking shipments are returned"""
        response = authenticated_session.get(f"{BASE_URL}/api/incentives/leakage-dashboard")
        assert response.status_code == 200
        data = response.json()
        
        assert "top_leaking_shipments" in data
        assert len(data["top_leaking_shipments"]) > 0
        
        # Verify shipment structure
        for ship in data["top_leaking_shipments"]:
            assert "shipment_number" in ship
            assert "fob_value" in ship
            assert "leakage" in ship
            
        print(f"✓ Top {len(data['top_leaking_shipments'])} leaking shipments returned")


# ===================== SHIPMENT ANALYSIS =====================

class TestShipmentAnalysis:
    """Tests for per-shipment incentive analysis API"""
    
    def test_shipment_analysis_structure(self, authenticated_session):
        """Test shipment analysis returns list with correct structure"""
        response = authenticated_session.get(f"{BASE_URL}/api/incentives/shipment-analysis")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 4  # At least 4 sample shipments
        
        # Verify each shipment has required fields
        for shipment in data:
            assert "shipment_id" in shipment
            assert "shipment_number" in shipment
            assert "buyer_name" in shipment
            assert "fob_value" in shipment
            assert "hs_codes" in shipment
            assert "incentive_status" in shipment
            assert "claimed_amount" in shipment
            assert "potential_incentive" in shipment
            assert "potential_breakdown" in shipment
            assert "leakage" in shipment
        
        print(f"✓ Shipment analysis returned {len(data)} shipments")
    
    def test_shipment_analysis_breakdown(self, authenticated_session):
        """Test potential breakdown includes RoDTEP, RoSCTL, Drawback"""
        response = authenticated_session.get(f"{BASE_URL}/api/incentives/shipment-analysis")
        assert response.status_code == 200
        data = response.json()
        
        for shipment in data:
            breakdown = shipment["potential_breakdown"]
            assert "rodtep" in breakdown
            assert "rosctl" in breakdown
            assert "drawback" in breakdown
            
            # Verify total potential = sum of breakdown
            expected_total = breakdown["rodtep"] + breakdown["rosctl"] + breakdown["drawback"]
            assert abs(shipment["potential_incentive"] - expected_total) < 1  # Allow small rounding
        
        print("✓ Potential breakdown structure verified for all shipments")
    
    def test_shipment_analysis_leakage_calculation(self, authenticated_session):
        """Test leakage is correctly calculated as potential - claimed"""
        response = authenticated_session.get(f"{BASE_URL}/api/incentives/shipment-analysis")
        assert response.status_code == 200
        data = response.json()
        
        for shipment in data:
            expected_leakage = shipment["potential_incentive"] - shipment["claimed_amount"]
            assert abs(shipment["leakage"] - expected_leakage) < 1
        
        print("✓ Leakage calculation verified")
    
    def test_shipment_has_moradabad_hs_codes(self, authenticated_session):
        """Test that sample shipments have Moradabad HS codes"""
        response = authenticated_session.get(f"{BASE_URL}/api/incentives/shipment-analysis")
        assert response.status_code == 200
        data = response.json()
        
        found_hs_codes = set()
        for shipment in data:
            for hs_code in shipment["hs_codes"]:
                found_hs_codes.add(hs_code)
        
        # Should have at least some of the Moradabad codes
        expected_codes = ["74198030", "74181022", "94032010", "94055000"]
        matches = [code for code in expected_codes if code in found_hs_codes]
        assert len(matches) >= 2, f"Expected Moradabad HS codes, found: {found_hs_codes}"
        
        print(f"✓ Found Moradabad HS codes: {matches}")


# ===================== CALCULATE INCENTIVE =====================

class TestCalculateIncentive:
    """Tests for incentive calculation API"""
    
    def test_calculate_incentive_brass(self, authenticated_session):
        """Test incentive calculation for brass handicrafts"""
        # First get a shipment ID
        shipments_response = authenticated_session.get(f"{BASE_URL}/api/shipments")
        assert shipments_response.status_code == 200
        shipments = shipments_response.json()
        assert len(shipments) > 0
        
        shipment_id = shipments[0]["id"]
        
        response = authenticated_session.post(f"{BASE_URL}/api/incentives/calculate", json={
            "shipment_id": shipment_id,
            "hs_codes": ["74198030"],
            "fob_value": 100000,
            "currency": "INR"
        })
        assert response.status_code == 200
        data = response.json()
        
        # Verify calculation
        assert "incentive_amount" in data
        assert "rate_percent" in data
        assert "incentives_breakdown" in data
        
        # For 74198030: 3% RoDTEP + 0% RoSCTL + 1.2% Drawback = 4.2%
        expected_rate = 4.2
        expected_amount = 100000 * 0.042
        
        assert abs(data["rate_percent"] - expected_rate) < 0.1
        assert abs(data["incentive_amount"] - expected_amount) < 10
        
        print(f"✓ Incentive calculated: ₹{data['incentive_amount']} ({data['rate_percent']}%)")
    
    def test_calculate_incentive_breakdown(self, authenticated_session):
        """Test incentive calculation returns proper breakdown"""
        shipments_response = authenticated_session.get(f"{BASE_URL}/api/shipments")
        shipments = shipments_response.json()
        shipment_id = shipments[0]["id"]
        
        response = authenticated_session.post(f"{BASE_URL}/api/incentives/calculate", json={
            "shipment_id": shipment_id,
            "hs_codes": ["74198030"],
            "fob_value": 100000,
            "currency": "INR"
        })
        assert response.status_code == 200
        data = response.json()
        
        breakdown = data["incentives_breakdown"]
        assert "rodtep" in breakdown
        assert "rosctl" in breakdown
        assert "drawback" in breakdown
        
        # Verify RoDTEP breakdown for brass (3%)
        assert breakdown["rodtep"]["rate"] == 3.0
        assert breakdown["rodtep"]["amount"] == 3000.0  # 3% of 100000
        
        print("✓ Incentive breakdown verified")
    
    def test_calculate_incentive_usd_conversion(self, authenticated_session):
        """Test incentive calculation with USD currency"""
        shipments_response = authenticated_session.get(f"{BASE_URL}/api/shipments")
        shipments = shipments_response.json()
        shipment_id = shipments[0]["id"]
        
        response = authenticated_session.post(f"{BASE_URL}/api/incentives/calculate", json={
            "shipment_id": shipment_id,
            "hs_codes": ["7419"],
            "fob_value": 1000,
            "currency": "USD"
        })
        assert response.status_code == 200
        data = response.json()
        
        # USD should be converted to INR (assuming ~83.5 rate)
        # Incentive amount should be based on INR value
        assert data["incentive_amount"] > 0
        print(f"✓ USD conversion working, incentive: ₹{data['incentive_amount']}")


# ===================== INCENTIVES SUMMARY =====================

class TestIncentivesSummary:
    """Tests for incentives summary API"""
    
    def test_summary_structure(self, authenticated_session):
        """Test summary API returns correct structure"""
        response = authenticated_session.get(f"{BASE_URL}/api/incentives/summary")
        assert response.status_code == 200
        data = response.json()
        
        assert "total_incentives" in data
        assert "claimed" in data
        assert "pending" in data
        assert "count" in data
        assert "by_scheme" in data
        assert "currency" in data
        
        print(f"✓ Summary: Total ₹{data['total_incentives']}, Count: {data['count']}")
    
    def test_summary_by_scheme(self, authenticated_session):
        """Test summary includes breakdown by scheme"""
        response = authenticated_session.get(f"{BASE_URL}/api/incentives/summary")
        assert response.status_code == 200
        data = response.json()
        
        by_scheme = data["by_scheme"]
        assert "rodtep" in by_scheme
        assert "rosctl" in by_scheme
        assert "drawback" in by_scheme
        
        # Total should equal sum of schemes
        total_from_schemes = by_scheme["rodtep"] + by_scheme["rosctl"] + by_scheme["drawback"]
        assert abs(data["total_incentives"] - total_from_schemes) < 1
        
        print(f"✓ By scheme: RoDTEP ₹{by_scheme['rodtep']}, Drawback ₹{by_scheme['drawback']}")


# ===================== SHIPMENTS API =====================

class TestShipmentsAPI:
    """Tests for shipments API used by incentives"""
    
    def test_get_shipments(self, authenticated_session):
        """Test retrieving shipments for incentive calculation"""
        response = authenticated_session.get(f"{BASE_URL}/api/shipments")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 4  # Sample data
        
        # Verify shipment structure
        for shipment in data:
            assert "id" in shipment
            assert "shipment_number" in shipment
            assert "buyer_name" in shipment
            assert "total_value" in shipment
            assert "hs_codes" in shipment
        
        print(f"✓ Retrieved {len(data)} shipments")
    
    def test_shipments_have_hs_codes(self, authenticated_session):
        """Test that shipments have HS codes for incentive calculation"""
        response = authenticated_session.get(f"{BASE_URL}/api/shipments")
        assert response.status_code == 200
        data = response.json()
        
        shipments_with_hs = [s for s in data if s.get("hs_codes") and len(s["hs_codes"]) > 0]
        assert len(shipments_with_hs) >= 4
        
        print(f"✓ {len(shipments_with_hs)} shipments have HS codes")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
