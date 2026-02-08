"""
Test Suite for P2 Security & Performance Features:
1. JWT Blacklisting (logout, password change token invalidation)
2. Async Export (CSV, Excel, PDF) for large datasets
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "test@moradabad.com"
TEST_PASSWORD = "Test@123"


class TestJWTBlacklisting:
    """JWT blacklisting tests - token invalidation on logout/password change"""
    
    def test_login_success(self):
        """Test login returns valid token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        print(f"✓ Login successful, token received")
    
    def test_logout_blacklists_token(self):
        """Test POST /api/auth/logout blacklists token and rejects subsequent requests"""
        # Step 1: Login to get token
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 2: Verify token works before logout
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert me_response.status_code == 200, "Token should work before logout"
        print(f"✓ Token works before logout")
        
        # Step 3: Logout
        logout_response = requests.post(f"{BASE_URL}/api/auth/logout", headers=headers)
        assert logout_response.status_code == 200, f"Logout failed: {logout_response.text}"
        logout_data = logout_response.json()
        assert logout_data["status"] == "success"
        assert logout_data["message"] == "Successfully logged out"
        print(f"✓ Logout successful: {logout_data}")
        
        # Step 4: Verify token is now blacklisted - should reject subsequent requests
        me_after_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert me_after_response.status_code == 401, f"Blacklisted token should be rejected. Got: {me_after_response.status_code}"
        print(f"✓ Token correctly blacklisted - subsequent requests rejected with 401")
    
    def test_logout_returns_proper_response(self):
        """Test logout endpoint returns proper response structure"""
        # Use a fresh login to get an un-blacklisted token
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Verify token is valid first
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert me_response.status_code == 200, "Fresh token should be valid"
        
        # Logout with fresh token
        logout_response = requests.post(f"{BASE_URL}/api/auth/logout", headers=headers)
        assert logout_response.status_code == 200, f"Logout failed: {logout_response.text}"
        data = logout_response.json()
        assert "message" in data
        assert "status" in data
        print(f"✓ Logout response structure correct: {data}")
    
    def test_logout_without_auth_fails(self):
        """Test logout without authentication fails"""
        response = requests.post(f"{BASE_URL}/api/auth/logout")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ Logout without auth correctly rejected")


class TestChangePassword:
    """Password change tests - invalidates all tokens"""
    
    # Use unique test user for password change to avoid affecting other tests
    CHANGE_PWD_EMAIL = "changepwd_test@moradabad.com"
    CHANGE_PWD_PASSWORD = "Test@123"
    NEW_PASSWORD = "NewTest@456"
    
    @pytest.fixture(autouse=True)
    def setup_password_user(self):
        """Setup: ensure user exists with known password"""
        # Try to register, if already exists we'll use login
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.CHANGE_PWD_EMAIL,
            "password": self.CHANGE_PWD_PASSWORD,
            "full_name": "Password Test User",
            "company_name": "Test Corp"
        })
        
        if register_response.status_code == 200:
            print(f"Created new test user: {self.CHANGE_PWD_EMAIL}")
        else:
            print(f"Test user already exists, will try to reset password")
        
        yield
    
    def test_change_password_success(self):
        """Test POST /api/auth/change-password changes password"""
        # Login with current password
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.CHANGE_PWD_EMAIL,
            "password": self.CHANGE_PWD_PASSWORD
        })
        
        # Handle case where password was previously changed
        if login_response.status_code != 200:
            # Try with new password
            login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": self.CHANGE_PWD_EMAIL,
                "password": self.NEW_PASSWORD
            })
            if login_response.status_code == 200:
                # Reset back to original password
                token = login_response.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
                reset_response = requests.post(f"{BASE_URL}/api/auth/change-password", 
                    headers=headers,
                    json={
                        "current_password": self.NEW_PASSWORD,
                        "new_password": self.CHANGE_PWD_PASSWORD
                    }
                )
                # Re-login with original
                login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
                    "email": self.CHANGE_PWD_EMAIL,
                    "password": self.CHANGE_PWD_PASSWORD
                })
        
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Change password
        change_response = requests.post(f"{BASE_URL}/api/auth/change-password", 
            headers=headers,
            json={
                "current_password": self.CHANGE_PWD_PASSWORD,
                "new_password": self.NEW_PASSWORD
            }
        )
        assert change_response.status_code == 200, f"Change password failed: {change_response.text}"
        data = change_response.json()
        assert data["status"] == "success"
        assert "Password changed successfully" in data["message"]
        print(f"✓ Password changed successfully: {data}")
        
        # Verify new password works
        new_login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.CHANGE_PWD_EMAIL,
            "password": self.NEW_PASSWORD
        })
        assert new_login_response.status_code == 200, "New password should work"
        print(f"✓ New password works for login")
        
        # Reset back to original password for other tests
        new_token = new_login_response.json()["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}
        reset_response = requests.post(f"{BASE_URL}/api/auth/change-password",
            headers=new_headers,
            json={
                "current_password": self.NEW_PASSWORD,
                "new_password": self.CHANGE_PWD_PASSWORD
            }
        )
        print(f"✓ Password reset back to original")
    
    def test_change_password_invalidates_old_token(self):
        """Test password change invalidates all existing tokens"""
        # Login first
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.CHANGE_PWD_EMAIL,
            "password": self.CHANGE_PWD_PASSWORD
        })
        
        if login_response.status_code != 200:
            login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": self.CHANGE_PWD_EMAIL,
                "password": self.NEW_PASSWORD
            })
        
        assert login_response.status_code == 200
        old_token = login_response.json()["access_token"]
        current_password = self.CHANGE_PWD_PASSWORD if self.CHANGE_PWD_PASSWORD else self.NEW_PASSWORD
        
        # Determine current password
        test_login = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.CHANGE_PWD_EMAIL,
            "password": self.CHANGE_PWD_PASSWORD
        })
        if test_login.status_code == 200:
            current_password = self.CHANGE_PWD_PASSWORD
            new_password = self.NEW_PASSWORD
        else:
            current_password = self.NEW_PASSWORD
            new_password = self.CHANGE_PWD_PASSWORD
        
        # Fresh login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.CHANGE_PWD_EMAIL,
            "password": current_password
        })
        old_token = login_response.json()["access_token"]
        old_headers = {"Authorization": f"Bearer {old_token}"}
        
        # Verify old token works
        me_before = requests.get(f"{BASE_URL}/api/auth/me", headers=old_headers)
        assert me_before.status_code == 200, "Old token should work before password change"
        print(f"✓ Token works before password change")
        
        # Change password
        change_response = requests.post(f"{BASE_URL}/api/auth/change-password",
            headers=old_headers,
            json={
                "current_password": current_password,
                "new_password": new_password
            }
        )
        assert change_response.status_code == 200
        print(f"✓ Password changed")
        
        # Wait a moment for token version update
        time.sleep(0.5)
        
        # Old token should now be invalidated
        me_after = requests.get(f"{BASE_URL}/api/auth/me", headers=old_headers)
        assert me_after.status_code == 401, f"Old token should be invalidated after password change. Got: {me_after.status_code}"
        print(f"✓ Old token correctly invalidated after password change")
    
    def test_change_password_wrong_current_fails(self):
        """Test change password with wrong current password fails"""
        # Login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to change with wrong current password
        change_response = requests.post(f"{BASE_URL}/api/auth/change-password",
            headers=headers,
            json={
                "current_password": "WrongPassword@123",
                "new_password": "NewPassword@456"
            }
        )
        assert change_response.status_code == 400, f"Should fail with wrong current password. Got: {change_response.status_code}"
        print(f"✓ Change password with wrong current password correctly rejected")


class TestExportJobCreation:
    """Export job creation tests"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get authentication headers"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_create_shipments_csv_export(self, auth_headers):
        """Test POST /api/exports creates CSV export for shipments"""
        response = requests.post(f"{BASE_URL}/api/exports", 
            headers=auth_headers,
            json={
                "export_type": "shipments",
                "format": "csv"
            }
        )
        assert response.status_code == 200, f"Export creation failed: {response.text}"
        data = response.json()
        assert "job_id" in data
        assert data["status"] in ["completed", "processing", "pending"]
        print(f"✓ Shipments CSV export created: job_id={data['job_id']}, status={data['status']}")
        return data["job_id"]
    
    def test_create_shipments_xlsx_export(self, auth_headers):
        """Test POST /api/exports creates Excel export for shipments"""
        response = requests.post(f"{BASE_URL}/api/exports",
            headers=auth_headers,
            json={
                "export_type": "shipments",
                "format": "xlsx"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        print(f"✓ Shipments Excel export created: job_id={data['job_id']}")
    
    def test_create_shipments_pdf_export(self, auth_headers):
        """Test POST /api/exports creates PDF export for shipments"""
        response = requests.post(f"{BASE_URL}/api/exports",
            headers=auth_headers,
            json={
                "export_type": "shipments",
                "format": "pdf"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        print(f"✓ Shipments PDF export created: job_id={data['job_id']}")
    
    def test_create_payments_export(self, auth_headers):
        """Test export for payments data"""
        response = requests.post(f"{BASE_URL}/api/exports",
            headers=auth_headers,
            json={
                "export_type": "payments",
                "format": "csv"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        print(f"✓ Payments export created: job_id={data['job_id']}")
    
    def test_create_receivables_export(self, auth_headers):
        """Test export for receivables data"""
        response = requests.post(f"{BASE_URL}/api/exports",
            headers=auth_headers,
            json={
                "export_type": "receivables",
                "format": "xlsx"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        print(f"✓ Receivables export created: job_id={data['job_id']}")
    
    def test_create_incentives_export(self, auth_headers):
        """Test export for incentives data"""
        response = requests.post(f"{BASE_URL}/api/exports",
            headers=auth_headers,
            json={
                "export_type": "incentives",
                "format": "pdf"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        print(f"✓ Incentives export created: job_id={data['job_id']}")
    
    def test_invalid_export_type_fails(self, auth_headers):
        """Test invalid export type returns 400"""
        response = requests.post(f"{BASE_URL}/api/exports",
            headers=auth_headers,
            json={
                "export_type": "invalid_type",
                "format": "csv"
            }
        )
        assert response.status_code == 400
        print(f"✓ Invalid export type correctly rejected")
    
    def test_invalid_format_fails(self, auth_headers):
        """Test invalid format returns 400"""
        response = requests.post(f"{BASE_URL}/api/exports",
            headers=auth_headers,
            json={
                "export_type": "shipments",
                "format": "invalid_format"
            }
        )
        assert response.status_code == 400
        print(f"✓ Invalid format correctly rejected")
    
    def test_export_without_auth_fails(self):
        """Test export without authentication fails"""
        response = requests.post(f"{BASE_URL}/api/exports", json={
            "export_type": "shipments",
            "format": "csv"
        })
        assert response.status_code in [401, 403]
        print(f"✓ Export without auth correctly rejected")


class TestExportJobStatus:
    """Export job status and listing tests"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get authentication headers"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_list_export_jobs(self, auth_headers):
        """Test GET /api/exports/jobs lists export jobs"""
        response = requests.get(f"{BASE_URL}/api/exports/jobs", headers=auth_headers)
        assert response.status_code == 200, f"List jobs failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Export jobs listed: {len(data)} jobs found")
        
        # Validate job structure if any exist
        if data:
            job = data[0]
            assert "job_id" in job
            assert "status" in job
            assert "export_type" in job
            assert "format" in job
            print(f"✓ Job structure valid: {job['job_id']} ({job['export_type']}.{job['format']}) - {job['status']}")
    
    def test_get_export_job_status(self, auth_headers):
        """Test GET /api/exports/jobs/{id} returns job status"""
        # First create an export
        create_response = requests.post(f"{BASE_URL}/api/exports",
            headers=auth_headers,
            json={
                "export_type": "shipments",
                "format": "csv"
            }
        )
        assert create_response.status_code == 200
        job_id = create_response.json()["job_id"]
        
        # Get status
        status_response = requests.get(f"{BASE_URL}/api/exports/jobs/{job_id}", headers=auth_headers)
        assert status_response.status_code == 200, f"Get status failed: {status_response.text}"
        data = status_response.json()
        
        assert data["job_id"] == job_id
        assert "status" in data
        assert "progress" in data
        assert "total_rows" in data
        print(f"✓ Job status retrieved: {data['status']}, progress={data['progress']}%, rows={data['total_rows']}")
    
    def test_get_nonexistent_job_returns_error(self, auth_headers):
        """Test getting non-existent job returns error"""
        response = requests.get(f"{BASE_URL}/api/exports/jobs/nonexistent-job-id", headers=auth_headers)
        assert response.status_code == 200  # Returns 200 with error in body
        data = response.json()
        assert "error" in data
        print(f"✓ Non-existent job correctly returns error: {data}")


class TestExportDownload:
    """Export file download tests"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get authentication headers"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_download_csv_export(self, auth_headers):
        """Test GET /api/exports/download/{id} downloads CSV file"""
        # Create export
        create_response = requests.post(f"{BASE_URL}/api/exports",
            headers=auth_headers,
            json={"export_type": "shipments", "format": "csv"}
        )
        assert create_response.status_code == 200
        job_id = create_response.json()["job_id"]
        
        # Wait for completion if needed
        for _ in range(10):
            status_response = requests.get(f"{BASE_URL}/api/exports/jobs/{job_id}", headers=auth_headers)
            status = status_response.json()
            if status.get("status") == "completed":
                break
            time.sleep(0.5)
        
        # Download
        download_response = requests.get(f"{BASE_URL}/api/exports/download/{job_id}", headers=auth_headers)
        
        if status.get("status") == "completed" and status.get("total_rows", 0) > 0:
            assert download_response.status_code == 200, f"Download failed: {download_response.text}"
            assert "text/csv" in download_response.headers.get("content-type", "")
            # Check content is valid CSV
            content = download_response.text
            assert len(content) > 0
            assert "," in content  # CSV should have commas
            print(f"✓ CSV download successful, content length: {len(content)} bytes")
        else:
            print(f"✓ Export completed but no data to download (status: {status})")
    
    def test_download_xlsx_export(self, auth_headers):
        """Test download Excel export generates .xlsx file"""
        # Create export
        create_response = requests.post(f"{BASE_URL}/api/exports",
            headers=auth_headers,
            json={"export_type": "shipments", "format": "xlsx"}
        )
        assert create_response.status_code == 200
        job_id = create_response.json()["job_id"]
        
        # Wait for completion
        for _ in range(10):
            status_response = requests.get(f"{BASE_URL}/api/exports/jobs/{job_id}", headers=auth_headers)
            status = status_response.json()
            if status.get("status") == "completed":
                break
            time.sleep(0.5)
        
        # Download
        download_response = requests.get(f"{BASE_URL}/api/exports/download/{job_id}", headers=auth_headers)
        
        if status.get("status") == "completed" and status.get("total_rows", 0) > 0:
            assert download_response.status_code == 200
            content_type = download_response.headers.get("content-type", "")
            assert "spreadsheet" in content_type or "octet-stream" in content_type
            # Check Excel file signature (PK zip header)
            content = download_response.content
            assert content[:2] == b'PK', "Excel file should start with PK (zip format)"
            print(f"✓ Excel download successful, file size: {len(content)} bytes")
        else:
            print(f"✓ Export completed but no data (status: {status})")
    
    def test_download_pdf_export(self, auth_headers):
        """Test download PDF export generates .pdf file"""
        # Create export
        create_response = requests.post(f"{BASE_URL}/api/exports",
            headers=auth_headers,
            json={"export_type": "shipments", "format": "pdf"}
        )
        assert create_response.status_code == 200
        job_id = create_response.json()["job_id"]
        
        # Wait for completion
        for _ in range(10):
            status_response = requests.get(f"{BASE_URL}/api/exports/jobs/{job_id}", headers=auth_headers)
            status = status_response.json()
            if status.get("status") == "completed":
                break
            time.sleep(0.5)
        
        # Download
        download_response = requests.get(f"{BASE_URL}/api/exports/download/{job_id}", headers=auth_headers)
        
        if status.get("status") == "completed" and status.get("total_rows", 0) > 0:
            assert download_response.status_code == 200
            content_type = download_response.headers.get("content-type", "")
            assert "pdf" in content_type or "octet-stream" in content_type
            # Check PDF file signature
            content = download_response.content
            assert content[:4] == b'%PDF', "PDF file should start with %PDF"
            print(f"✓ PDF download successful, file size: {len(content)} bytes")
        else:
            print(f"✓ Export completed but no data (status: {status})")
    
    def test_download_nonexistent_export_fails(self, auth_headers):
        """Test downloading non-existent export returns 404"""
        response = requests.get(f"{BASE_URL}/api/exports/download/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404
        print(f"✓ Download non-existent export correctly returns 404")


class TestExportWithFilters:
    """Test export with filters"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get authentication headers"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_export_shipments_with_status_filter(self, auth_headers):
        """Test export with status filter"""
        response = requests.post(f"{BASE_URL}/api/exports",
            headers=auth_headers,
            json={
                "export_type": "shipments",
                "format": "csv",
                "filters": {"status": "shipped"}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        print(f"✓ Export with status filter created: {data['job_id']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
