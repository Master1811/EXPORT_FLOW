"""
Pytest configuration and shared fixtures for backend tests
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_EMAIL = "test@moradabad.com"
TEST_PASSWORD = "Test@123"


@pytest.fixture(scope="session")
def api_session():
    """Create a requests session for API calls"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="session")
def auth_token(api_session):
    """Get authentication token"""
    response = api_session.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture(scope="session")
def authenticated_session(api_session, auth_token):
    """Session with auth header"""
    api_session.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_session
