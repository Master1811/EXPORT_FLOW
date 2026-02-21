"""
Locust Stress Testing for ExportFlow Platform
Simulates 1,000 concurrent users performing document bundling and risk-clock queries.
"""

import random
import string
from locust import HttpUser, task, between, tag
import json


def random_string(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


class ExportFlowUser(HttpUser):
    """Simulates an authenticated ExportFlow user."""
    
    wait_time = between(1, 3)
    token = None
    shipment_ids = []
    
    def on_start(self):
        """Login and get authentication token."""
        email = f"test_{random_string()}@example.com"
        password = "TestPassword123!"
        
        register_response = self.client.post(
            "/api/auth/register",
            json={"email": email, "password": password, "full_name": f"Test User {random_string()}", "company_name": f"Test Company {random_string()}"},
            name="/api/auth/register"
        )
        
        if register_response.status_code == 200:
            data = register_response.json()
            self.token = data.get("access_token") or data.get("token")
        
        if self.token:
            self.client.headers = {"Authorization": f"Bearer {self.token}"}
    
    @tag("risk-clock")
    @task(5)
    def get_risk_clock(self):
        """Query risk clock dashboard - high priority endpoint."""
        with self.client.get("/api/risk-clock", name="/api/risk-clock", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "summary" in data and "buckets" in data:
                    response.success()
                else:
                    response.failure("Invalid risk clock response")
            elif response.status_code == 401:
                response.failure("Authentication failed")
    
    @tag("risk-clock")
    @task(3)
    def get_aging_summary(self):
        """Query aging summary for charts."""
        self.client.get("/api/risk-clock/aging-summary", name="/api/risk-clock/aging-summary")
    
    @tag("dgft")
    @task(2)
    def validate_dgft_data(self):
        """Validate DGFT data."""
        self.client.get("/api/dgft/validate", name="/api/dgft/validate")
    
    @tag("dgft")
    @task(1)
    def export_dgft_excel(self):
        """Export DGFT Excel."""
        with self.client.get("/api/dgft/export", name="/api/dgft/export", catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()
    
    @tag("audit-vault")
    @task(2)
    def get_shipments_for_audit(self):
        """Get shipments list for audit package."""
        with self.client.get("/api/shipments", name="/api/shipments", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.shipment_ids = [s.get("id") for s in data[:10] if s.get("id")]
                response.success()
    
    @tag("audit-vault")
    @task(1)
    def generate_audit_package(self):
        """Generate audit package for a random shipment."""
        if not self.shipment_ids:
            return
        shipment_id = random.choice(self.shipment_ids)
        self.client.post(f"/api/audit-vault/generate/{shipment_id}", name="/api/audit-vault/generate/[id]")
    
    @tag("credit")
    @task(3)
    def get_company_score(self):
        """Get company credit score."""
        self.client.get("/api/credit/company-score", name="/api/credit/company-score")
    
    @tag("credit")
    @task(2)
    def get_payment_behavior(self):
        """Get payment behavior analysis."""
        self.client.get("/api/credit/payment-behavior", name="/api/credit/payment-behavior")
    
    @tag("compliance")
    @task(1)
    def ofac_screen(self):
        """Screen entity against OFAC."""
        self.client.post(
            "/api/compliance/ofac-screen",
            json={"entity_name": f"Test Buyer {random_string()}", "entity_type": "buyer", "country_code": "DE"},
            name="/api/compliance/ofac-screen"
        )
    
    @tag("health")
    @task(1)
    def health_check(self):
        """Basic health check."""
        self.client.get("/api/health", name="/api/health")


class DocumentBundlingUser(HttpUser):
    """Specialized user for document bundling stress test."""
    
    wait_time = between(2, 5)
    token = None
    
    def on_start(self):
        email = f"doc_test_{random_string()}@example.com"
        password = "DocTest123!"
        
        response = self.client.post(
            "/api/auth/register",
            json={"email": email, "password": password, "full_name": f"Doc User", "company_name": f"Doc Company"}
        )
        
        if response.status_code == 200:
            self.token = response.json().get("access_token")
        
        if self.token:
            self.client.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(5)
    def full_audit_workflow(self):
        """Complete audit package workflow."""
        shipments_response = self.client.get("/api/shipments")
        if shipments_response.status_code != 200:
            return
        
        shipments = shipments_response.json()
        if not shipments:
            return
        
        shipment_id = shipments[0].get("id")
        if not shipment_id:
            return
        
        gen_response = self.client.post(f"/api/audit-vault/generate/{shipment_id}")
        if gen_response.status_code != 200:
            return
        
        job_id = gen_response.json().get("job_id")
        if job_id:
            for _ in range(3):
                self.client.get(f"/api/audit-vault/status/{job_id}", name="/api/audit-vault/status/[id]")
    
    @task(3)
    def risk_clock_with_actions(self):
        """Risk clock with potential actions."""
        response = self.client.get("/api/risk-clock")
        if response.status_code != 200:
            return
        
        data = response.json()
        critical = data.get("buckets", {}).get("critical", [])
        
        if critical:
            shipment = critical[0]
            self.client.post(
                f"/api/risk-clock/draft-letter/{shipment.get('id')}",
                json={"reason": "delayed_payment", "extension_days": 90},
                name="/api/risk-clock/draft-letter/[id]"
            )
