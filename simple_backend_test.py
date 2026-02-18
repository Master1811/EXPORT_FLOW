#!/usr/bin/env python3
"""
Simple ExportFlow Backend Test for Review Request
"""
import requests
import json

BASE_URL = "http://localhost:8001/api"
TEST_USER = {
    "email": "test@moradabad.com", 
    "password": "Test@123"
}

def test_payment_currency_validation():
    """Test payment currency validation"""
    print("🧪 Testing Payment Currency Validation...")
    
    # Login
    login_resp = requests.post(f'{BASE_URL}/auth/login', json=TEST_USER, timeout=10)
    if login_resp.status_code != 200:
        print("❌ Login failed")
        return False
    
    token = login_resp.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print("✅ Login successful")
    
    # Create USD shipment
    shipment_data = {
        'shipment_number': 'TEST-PAYMENT-CURRENCY',
        'buyer_name': 'Test Buyer', 
        'buyer_country': 'United States',
        'destination_port': 'New York',
        'origin_port': 'Mumbai',
        'currency': 'USD',
        'total_value': 50000.00,
        'status': 'in_transit',
        'expected_ship_date': '2024-01-15T00:00:00Z'
    }
    
    shipment_resp = requests.post(f'{BASE_URL}/shipments', json=shipment_data, headers=headers, timeout=10)
    if shipment_resp.status_code != 200:
        print("❌ Shipment creation failed")
        return False
    
    shipment_id = shipment_resp.json()['id']
    print(f"✅ USD Shipment created: {shipment_id}")
    
    # Test 1: Try EUR payment for USD shipment (should fail)
    payment_data_eur = {
        'shipment_id': shipment_id,
        'currency': 'EUR',
        'amount': 45000.00,
        'payment_date': '2024-01-20T00:00:00Z',
        'payment_mode': 'wire_transfer',
        'bank_reference': 'TEST-MISMATCH'
    }
    
    payment_resp = requests.post(f'{BASE_URL}/payments', json=payment_data_eur, headers=headers, timeout=10)
    
    if payment_resp.status_code == 400:
        detail = payment_resp.json().get('detail', '')
        if 'currency' in detail.lower() and 'match' in detail.lower():
            print("✅ Currency mismatch validation works: Payment correctly rejected")
        else:
            print(f"⚠️  Wrong error message: {detail}")
    else:
        print(f"❌ Expected 400, got {payment_resp.status_code}: {payment_resp.text[:100]}")
        return False
    
    # Test 2: Try USD payment for USD shipment (should succeed)  
    payment_data_usd = {
        'shipment_id': shipment_id,
        'currency': 'USD',
        'amount': 45000.00,
        'payment_date': '2024-01-20T00:00:00Z',
        'payment_mode': 'wire_transfer', 
        'bank_reference': 'TEST-MATCH'
    }
    
    payment_resp = requests.post(f'{BASE_URL}/payments', json=payment_data_usd, headers=headers, timeout=10)
    
    if payment_resp.status_code == 200:
        payment_id = payment_resp.json()['id']
        print(f"✅ Currency match validation works: Payment created {payment_id}")
    else:
        print(f"❌ Expected 200, got {payment_resp.status_code}: {payment_resp.text[:100]}")
        return False
    
    return True

def test_forex_api():
    """Test forex API format"""
    print("\n🧪 Testing Forex API...")
    
    resp = requests.get(f'{BASE_URL}/forex/latest', timeout=10)
    if resp.status_code != 200:
        print(f"❌ Forex API failed: {resp.status_code}")
        return False
    
    data = resp.json()
    rates = data.get('rates', {})
    
    if 'USD' not in rates:
        print("❌ USD rate not found")
        return False
    
    usd_rate = rates['USD']
    if not isinstance(usd_rate, dict) or 'rate' not in usd_rate or 'source' not in usd_rate:
        print(f"❌ Wrong USD rate format: {usd_rate}")
        return False
    
    print(f"✅ Forex API format correct: USD rate={usd_rate['rate']}, source={usd_rate['source']}")
    print(f"✅ Found {len(rates)} currency rates")
    return True

def test_health_check():
    """Test health check endpoint"""
    print("\n🧪 Testing Health Check...")
    
    resp = requests.get(f'{BASE_URL}/health', timeout=10)
    if resp.status_code != 200:
        print(f"❌ Health check failed: {resp.status_code}")
        return False
    
    data = resp.json()
    status = data.get('status')
    
    if status != 'healthy':
        print(f"❌ Expected status 'healthy', got '{status}'")
        return False
    
    print(f"✅ Health check passed: status={status}")
    return True

if __name__ == "__main__":
    print("🚀 ExportFlow Backend Test Suite - Review Request\n")
    
    tests = [
        test_health_check,
        test_forex_api,
        test_payment_currency_validation
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print("❌ Test failed")
        except Exception as e:
            print(f"❌ Test error: {e}")
    
    total = len(tests)
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  Some tests failed")