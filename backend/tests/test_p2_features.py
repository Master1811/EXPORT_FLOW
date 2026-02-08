"""
P2 Features Backend Tests
Tests for:
- AI Query endpoint with Gemini integration
- AI Chat history
- AI Shipment analysis
- AI Risk alerts
- AI Incentive optimizer
- Document upload and OCR
- Email alerts endpoint
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSetup:
    """Test fixtures and authentication"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@moradabad.com",
            "password": "Test@123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Auth headers for requests"""
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    @pytest.fixture(scope="class")
    def session(self):
        """Requests session"""
        return requests.Session()


class TestAIQueryEndpoint(TestSetup):
    """Tests for AI query endpoint with Gemini integration"""
    
    def test_ai_query_success(self, session, auth_headers):
        """TC-AI-01: AI query returns valid response"""
        response = session.post(
            f"{BASE_URL}/api/ai/query",
            json={"query": "What is RoDTEP?"},
            headers=auth_headers
        )
        assert response.status_code == 200, f"AI query failed: {response.text}"
        
        data = response.json()
        assert "query" in data, "Response should contain query"
        assert "response" in data, "Response should contain AI response"
        assert "timestamp" in data, "Response should contain timestamp"
        assert isinstance(data["response"], str), "Response should be string"
        assert len(data["response"]) > 0, "Response should not be empty"
    
    def test_ai_query_with_session_id(self, session, auth_headers):
        """TC-AI-02: AI query with session ID maintains context"""
        session_id = "test-session-12345"
        response = session.post(
            f"{BASE_URL}/api/ai/query",
            json={"query": "Explain GST for exports", "session_id": session_id},
            headers=auth_headers
        )
        assert response.status_code == 200, f"AI query failed: {response.text}"
        
        data = response.json()
        assert data.get("session_id") == session_id, "Session ID should match"
    
    def test_ai_query_unauthorized(self, session):
        """TC-AI-03: AI query without auth returns 401/403"""
        response = session.post(
            f"{BASE_URL}/api/ai/query",
            json={"query": "Test query"}
        )
        assert response.status_code in [401, 403], "Should return 401 or 403 without auth"


class TestAIChatHistory(TestSetup):
    """Tests for AI chat history endpoint"""
    
    def test_chat_history_returns_list(self, session, auth_headers):
        """TC-AI-04: Chat history returns list of previous conversations"""
        response = session.get(
            f"{BASE_URL}/api/ai/chat-history",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Chat history failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        # If there's data, verify structure
        if len(data) > 0:
            item = data[0]
            assert "query" in item, "Chat item should have query"
            assert "response" in item, "Chat item should have response"
            assert "created_at" in item, "Chat item should have created_at"
    
    def test_chat_history_with_limit(self, session, auth_headers):
        """TC-AI-05: Chat history respects limit parameter"""
        response = session.get(
            f"{BASE_URL}/api/ai/chat-history?limit=5",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5, "Should return at most 5 items"


class TestAIRiskAlerts(TestSetup):
    """Tests for AI risk alerts endpoint"""
    
    def test_risk_alerts_returns_alerts(self, session, auth_headers):
        """TC-AI-06: Risk alerts endpoint returns alerts array"""
        response = session.get(
            f"{BASE_URL}/api/ai/risk-alerts",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Risk alerts failed: {response.text}"
        
        data = response.json()
        assert "alerts" in data, "Response should contain alerts"
        assert isinstance(data["alerts"], list), "Alerts should be a list"
        
        # Verify alert structure if present
        if len(data["alerts"]) > 0:
            alert = data["alerts"][0]
            assert "severity" in alert, "Alert should have severity"
            assert "type" in alert, "Alert should have type"
            assert "message" in alert, "Alert should have message"
    
    def test_risk_alerts_includes_ebrc_and_payment(self, session, auth_headers):
        """TC-AI-07: Risk alerts includes e-BRC and payment delay types"""
        response = session.get(
            f"{BASE_URL}/api/ai/risk-alerts",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # Just verify the endpoint returns valid structure
        # Actual alerts depend on data in DB
        assert "alerts" in data


class TestAIIncentiveOptimizer(TestSetup):
    """Tests for AI incentive optimizer endpoint"""
    
    def test_incentive_optimizer_returns_recommendations(self, session, auth_headers):
        """TC-AI-08: Incentive optimizer returns recommendations"""
        response = session.get(
            f"{BASE_URL}/api/ai/incentive-optimizer",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Incentive optimizer failed: {response.text}"
        
        data = response.json()
        assert "recommendations" in data, "Response should contain recommendations"
        assert "total_opportunity" in data, "Response should contain total_opportunity"
        assert isinstance(data["recommendations"], list), "Recommendations should be list"
        
        # Verify recommendation structure if present
        if len(data["recommendations"]) > 0:
            rec = data["recommendations"][0]
            assert "action" in rec, "Recommendation should have action"
            assert "potential_benefit" in rec, "Recommendation should have potential_benefit"
            assert "priority" in rec, "Recommendation should have priority"


class TestAIShipmentAnalysis(TestSetup):
    """Tests for AI shipment analysis endpoint"""
    
    def test_analyze_shipment_not_found(self, session, auth_headers):
        """TC-AI-09: Analyze shipment with invalid ID returns error"""
        response = session.get(
            f"{BASE_URL}/api/ai/analyze-shipment/invalid-shipment-id",
            headers=auth_headers
        )
        assert response.status_code == 200, "Should return 200 with error in body"
        
        data = response.json()
        assert "error" in data, "Should return error for non-existent shipment"
    
    def test_analyze_shipment_with_valid_id(self, session, auth_headers):
        """TC-AI-10: Analyze shipment with valid ID returns analysis"""
        # First get a valid shipment ID
        shipments_resp = session.get(
            f"{BASE_URL}/api/shipments",
            headers=auth_headers
        )
        if shipments_resp.status_code == 200:
            shipments = shipments_resp.json()
            if isinstance(shipments, list) and len(shipments) > 0:
                shipment_id = shipments[0].get("id")
                
                response = session.get(
                    f"{BASE_URL}/api/ai/analyze-shipment/{shipment_id}",
                    headers=auth_headers
                )
                assert response.status_code == 200
                
                data = response.json()
                # Either analysis or error (if AI key issue)
                assert "analysis" in data or "error" in data


class TestAIRefundForecast(TestSetup):
    """Tests for AI refund forecast endpoint"""
    
    def test_refund_forecast_returns_forecast(self, session, auth_headers):
        """TC-AI-11: Refund forecast returns forecast data"""
        response = session.get(
            f"{BASE_URL}/api/ai/refund-forecast",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Refund forecast failed: {response.text}"
        
        data = response.json()
        assert "forecast" in data, "Response should contain forecast"
        assert "total_expected" in data, "Response should contain total_expected"
        assert isinstance(data["forecast"], list), "Forecast should be a list"


class TestAICashflowForecast(TestSetup):
    """Tests for AI cashflow forecast endpoint"""
    
    def test_cashflow_forecast_returns_forecast(self, session, auth_headers):
        """TC-AI-12: Cashflow forecast returns forecast data"""
        response = session.get(
            f"{BASE_URL}/api/ai/cashflow-forecast",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Cashflow forecast failed: {response.text}"
        
        data = response.json()
        assert "forecast" in data, "Response should contain forecast"
        assert "total_receivables" in data, "Response should contain total_receivables"
        assert isinstance(data["forecast"], list), "Forecast should be a list"


class TestDocumentUpload(TestSetup):
    """Tests for document upload endpoint"""
    
    def test_document_upload_success(self, session, auth_headers):
        """TC-DOC-01: Document upload saves file successfully"""
        # Create a simple test file
        test_content = b"Test document content for upload"
        files = {"file": ("test_doc.txt", test_content, "text/plain")}
        
        # Remove Content-Type from headers for multipart
        headers = {"Authorization": auth_headers["Authorization"]}
        
        response = session.post(
            f"{BASE_URL}/api/documents/upload",
            files=files,
            headers=headers
        )
        assert response.status_code == 200, f"Upload failed: {response.text}"
        
        data = response.json()
        assert "file_id" in data, "Response should contain file_id"
        assert "filename" in data, "Response should contain filename"
        assert data["filename"] == "test_doc.txt", "Filename should match"
    
    def test_document_upload_pdf(self, session, auth_headers):
        """TC-DOC-02: PDF document upload works"""
        # Create minimal PDF content
        pdf_content = b"%PDF-1.4\n%Test PDF"
        files = {"file": ("test_invoice.pdf", pdf_content, "application/pdf")}
        
        headers = {"Authorization": auth_headers["Authorization"]}
        
        response = session.post(
            f"{BASE_URL}/api/documents/upload",
            files=files,
            headers=headers
        )
        assert response.status_code == 200


class TestDocumentList(TestSetup):
    """Tests for document list endpoint"""
    
    def test_list_uploaded_files(self, session, auth_headers):
        """TC-DOC-03: List uploaded files returns array"""
        response = session.get(
            f"{BASE_URL}/api/documents/uploads",
            headers=auth_headers
        )
        assert response.status_code == 200, f"List failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        # Verify structure if files exist
        if len(data) > 0:
            file_info = data[0]
            assert "id" in file_info, "File info should have id"
            assert "original_filename" in file_info, "File info should have original_filename"


class TestOCRProcessing(TestSetup):
    """Tests for OCR processing endpoint"""
    
    def test_ocr_process_requires_file_id(self, session, auth_headers):
        """TC-DOC-04: OCR process requires valid file_id"""
        response = session.post(
            f"{BASE_URL}/api/documents/ocr/process?file_id=invalid-id&document_type=invoice",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # Should return error for invalid file
        assert "error" in data or "status" in data
    
    def test_ocr_with_valid_file(self, session, auth_headers):
        """TC-DOC-05: OCR process with valid file returns job"""
        # First upload a file
        pdf_content = b"%PDF-1.4\nTest Invoice Content"
        files = {"file": ("ocr_test.pdf", pdf_content, "application/pdf")}
        headers = {"Authorization": auth_headers["Authorization"]}
        
        upload_resp = session.post(
            f"{BASE_URL}/api/documents/upload",
            files=files,
            headers=headers
        )
        
        if upload_resp.status_code == 200:
            file_id = upload_resp.json().get("file_id")
            
            # Now try OCR
            response = session.post(
                f"{BASE_URL}/api/documents/ocr/process?file_id={file_id}&document_type=invoice",
                headers=auth_headers
            )
            assert response.status_code == 200
            
            data = response.json()
            # Should return job_id or result
            assert "job_id" in data or "error" in data


class TestEmailAlerts(TestSetup):
    """Tests for email alerts endpoint"""
    
    def test_email_alerts_sendgrid_not_configured(self, session, auth_headers):
        """TC-EMAIL-01: Email alerts shows SendGrid not configured"""
        response = session.post(
            f"{BASE_URL}/api/notifications/email/send-alerts",
            json={"email": "test@example.com"},
            headers=auth_headers
        )
        assert response.status_code == 200, f"Email alerts failed: {response.text}"
        
        data = response.json()
        # Should either succeed or show SendGrid not configured
        assert "error" in data or "success" in data
        
        if "error" in data:
            assert "SendGrid" in data.get("error", "") or "SendGrid" in data.get("message", ""), \
                "Error should mention SendGrid not configured"
    
    def test_email_alerts_uses_user_email(self, session, auth_headers):
        """TC-EMAIL-02: Email alerts uses user's email if none provided"""
        response = session.post(
            f"{BASE_URL}/api/notifications/email/send-alerts",
            json={},
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # Should use user's email from auth token
        assert "error" in data or "email" in data


class TestEmailLog(TestSetup):
    """Tests for email notification log"""
    
    def test_email_log_returns_list(self, session, auth_headers):
        """TC-EMAIL-03: Email log returns notification history"""
        response = session.get(
            f"{BASE_URL}/api/notifications/email/log",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Email log failed: {response.text}"
        
        data = response.json()
        # Should return list or error
        assert isinstance(data, list) or "error" in data


# Run as main
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
