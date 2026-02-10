#!/usr/bin/env python3
"""
Simple Rate Limit Test - Check if rate limiting headers are present
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://resilient-api-1.preview.emergentagent.com/api"
TEST_EMAIL = "test@moradabad.com"
TEST_PASSWORD = "Test@123"

async def test_rate_limit_headers():
    """Test for rate limiting headers on a simple endpoint"""
    
    session = aiohttp.ClientSession()
    
    try:
        # Login first
        login_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
        async with session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
            if response.status == 200:
                data = await response.json()
                token = data["access_token"]
                print("✅ Authentication successful")
            else:
                print("❌ Authentication failed")
                return
        
        # Test on login endpoint to see headers
        print("\n🔍 Testing rate limit headers on login endpoint...")
        
        async with session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
            headers = dict(response.headers)
            
            print(f"Status: {response.status}")
            print("All response headers:")
            for key, value in headers.items():
                print(f"  {key}: {value}")
            
            # Look specifically for rate limit headers
            rate_headers = {k: v for k, v in headers.items() if 
                          'ratelimit' in k.lower() or 
                          'rate-limit' in k.lower() or
                          'x-ratelimit' in k.lower() or
                          'x-rate-limit' in k.lower()}
            
            if rate_headers:
                print(f"\n✅ Rate limiting headers found: {rate_headers}")
            else:
                print("\n❌ No rate limiting headers found")
        
        # Test on a different endpoint
        print("\n🔍 Testing rate limit headers on health endpoint...")
        async with session.get(f"{BACKEND_URL}/health") as response:
            headers = dict(response.headers)
            
            rate_headers = {k: v for k, v in headers.items() if 
                          'ratelimit' in k.lower() or 
                          'rate-limit' in k.lower() or
                          'x-ratelimit' in k.lower() or
                          'x-rate-limit' in k.lower()}
            
            print(f"Health endpoint status: {response.status}")
            if rate_headers:
                print(f"✅ Rate limiting headers found: {rate_headers}")
            else:
                print("❌ No rate limiting headers found")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(test_rate_limit_headers())