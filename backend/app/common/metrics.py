"""Prometheus metrics for ExportFlow platform"""
from prometheus_client import Counter, Histogram, Gauge, Info
import time
from datetime import datetime
from contextlib import asynccontextmanager

# ============ API & Request Metrics ============
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0)
)

http_errors_total = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'status_code', 'error_type']
)

# ============ Authentication Metrics ============
auth_attempts_total = Counter(
    'auth_attempts_total',
    'Total authentication attempts',
    ['method', 'status']
)

active_sessions = Gauge(
    'active_sessions_total',
    'Number of active user sessions'
)

# ============ Database Metrics ============
db_connections_active = Gauge(
    'db_connections_active',
    'Active database connections'
)

db_operations_total = Counter(
    'db_operations_total',
    'Total database operations',
    ['operation', 'collection', 'status']
)

db_operation_duration_seconds = Histogram(
    'db_operation_duration_seconds',
    'Database operation duration in seconds',
    ['operation', 'collection'],
    buckets=(0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0)
)

# ============ Business Metrics - Shipments ============
shipments_created_total = Counter(
    'shipments_created_total',
    'Total shipments created',
    ['company_id']
)

shipments_by_status = Gauge(
    'shipments_by_status',
    'Number of shipments by status',
    ['status']
)

shipment_value_total = Counter(
    'shipment_value_total',
    'Total shipment value in INR',
    ['company_id']
)

shipment_processing_duration_seconds = Histogram(
    'shipment_processing_duration_seconds',
    'Time to process shipment in seconds',
    ['status'],
    buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 300.0)
)

# ============ Business Metrics - Payments ============
payments_recorded_total = Counter(
    'payments_recorded_total',
    'Total payments recorded',
    ['status', 'payment_method']
)

payments_amount_total = Counter(
    'payments_amount_total',
    'Total payment amount in INR',
    ['payment_method', 'status']
)

outstanding_receivables = Gauge(
    'outstanding_receivables_total',
    'Outstanding receivables in INR',
    ['company_id']
)

payment_processing_duration_seconds = Histogram(
    'payment_processing_duration_seconds',
    'Time to process payment in seconds',
    ['payment_method'],
    buckets=(0.5, 2.0, 5.0, 10.0, 30.0)
)

# ============ Business Metrics - Incentives ============
incentives_calculated_total = Counter(
    'incentives_calculated_total',
    'Total incentives calculated'
)

incentives_amount_total = Counter(
    'incentives_amount_total',
    'Total incentive amount in INR',
    ['incentive_type']
)

# ============ Business Metrics - Documents ============
documents_uploaded_total = Counter(
    'documents_uploaded_total',
    'Total documents uploaded',
    ['document_type', 'status']
)

documents_size_bytes = Counter(
    'documents_size_bytes_total',
    'Total size of documents uploaded',
    ['document_type']
)

# ============ Business Metrics - Overview ============
total_export_value = Gauge(
    'total_export_value',
    'Total export value in INR'
)

companies_active = Gauge(
    'companies_active_total',
    'Number of active companies'
)

users_registered = Gauge(
    'users_registered_total',
    'Total registered users'
)

# ============ Background Job Metrics ============
background_jobs_total = Counter(
    'background_jobs_total',
    'Total background jobs',
    ['job_type', 'status']
)

background_job_duration_seconds = Histogram(
    'background_job_duration_seconds',
    'Background job duration in seconds',
    ['job_type'],
    buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0)
)

background_jobs_queue_size = Gauge(
    'background_jobs_queue_size',
    'Number of jobs in queue',
    ['job_type']
)

# ============ System Health Metrics ============
api_uptime_seconds = Gauge(
    'api_uptime_seconds',
    'API uptime in seconds'
)

api_start_time = time.time()

system_errors_total = Counter(
    'system_errors_total',
    'Total system errors by type',
    ['error_type', 'endpoint', 'severity']
)

critical_alerts = Gauge(
    'critical_alerts_total',
    'Number of critical alerts'
)

# ============ Compliance & Audit Metrics ============
audit_logs_total = Counter(
    'audit_logs_total',
    'Total audit log entries',
    ['action', 'resource_type', 'status']
)

compliance_checks_total = Counter(
    'compliance_checks_total',
    'Total compliance checks',
    ['check_type', 'result']
)

# ============ Cache & Performance Metrics ============
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type']
)


def update_uptime():
    """Update API uptime gauge"""
    api_uptime_seconds.set(time.time() - api_start_time)


def track_request(method: str, endpoint: str, status: int, duration: float, error_type: str = None):
    """Track HTTP request metrics"""
    http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
    
    if 400 <= status < 600:
        error_type = error_type or f"HTTP{status}"
        status_code = str(status)
        http_errors_total.labels(method=method, endpoint=endpoint, status_code=status_code, error_type=error_type).inc()
        system_errors_total.labels(error_type=error_type, endpoint=endpoint, severity="error" if status < 500 else "critical").inc()


def track_db_operation(operation: str, collection: str, status: str, duration: float):
    """Track database operation metrics"""
    db_operations_total.labels(operation=operation, collection=collection, status=status).inc()
    db_operation_duration_seconds.labels(operation=operation, collection=collection).observe(duration)


def track_background_job(job_type: str, status: str, duration: float):
    """Track background job metrics"""
    background_jobs_total.labels(job_type=job_type, status=status).inc()
    background_job_duration_seconds.labels(job_type=job_type).observe(duration)


def track_shipment_created(value: float = 0, company_id: str = None):
    """Track shipment creation with value"""
    if company_id:
        shipments_created_total.labels(company_id=company_id).inc()
    else:
        shipments_created_total.labels(company_id="unknown").inc()
    
    if value > 0 and company_id:
        shipment_value_total.labels(company_id=company_id).inc(value)
    elif value > 0:
        shipment_value_total.labels(company_id="unknown").inc(value)


def track_shipment_status(status: str, count: int = 1):
    """Track shipment by status"""
    shipments_by_status.labels(status=status).set(count)


def track_shipment_processing(status: str, duration: float):
    """Track shipment processing time"""
    shipment_processing_duration_seconds.labels(status=status).observe(duration)


def track_payment_recorded(amount: float, payment_method: str = "unknown", status: str = "success"):
    """Track payment recording"""
    payments_recorded_total.labels(status=status, payment_method=payment_method).inc()
    payments_amount_total.labels(payment_method=payment_method, status=status).inc(amount)


def track_payment_processing(payment_method: str, duration: float):
    """Track payment processing time"""
    payment_processing_duration_seconds.labels(payment_method=payment_method).observe(duration)


def track_incentives_calculated(amount: float, incentive_type: str = "unknown"):
    """Track incentive calculation"""
    incentives_calculated_total.inc()
    incentives_amount_total.labels(incentive_type=incentive_type).inc(amount)


def track_document_upload(document_type: str, size_bytes: int, status: str = "success"):
    """Track document upload"""
    documents_uploaded_total.labels(document_type=document_type, status=status).inc()
    documents_size_bytes.labels(document_type=document_type).inc(size_bytes)


def update_business_metrics(total_export: float, outstanding_receivables: float, active_companies: int = 0, registered_users: int = 0):
    """Update business metrics"""
    total_export_value.set(total_export)
    outstanding_receivables.set(outstanding_receivables)
    if active_companies > 0:
        companies_active.set(active_companies)
    if registered_users > 0:
        users_registered.set(registered_users)


def track_auth_attempt(method: str, status: str):
    """Track authentication attempt"""
    auth_attempts_total.labels(method=method, status=status).inc()


def update_active_sessions(count: int):
    """Update active sessions count"""
    active_sessions.set(count)


def track_audit_log(action: str, resource_type: str, status: str = "success"):
    """Track audit log event"""
    audit_logs_total.labels(action=action, resource_type=resource_type, status=status).inc()


def track_compliance_check(check_type: str, result: str):
    """Track compliance check"""
    compliance_checks_total.labels(check_type=check_type, result=result).inc()


def track_cache_hit(cache_type: str):
    """Track cache hit"""
    cache_hits_total.labels(cache_type=cache_type).inc()


def track_cache_miss(cache_type: str):
    """Track cache miss"""
    cache_misses_total.labels(cache_type=cache_type).inc()


def update_critical_alerts(count: int):
    """Update critical alerts count"""
    critical_alerts.set(count)


@asynccontextmanager
async def track_db_operation_context(operation: str, collection: str):
    """Context manager for tracking database operations without modifying logic"""
    start_time = time.time()
    try:
        yield
        duration = time.time() - start_time
        track_db_operation(operation, collection, "success", duration)
    except Exception as e:
        duration = time.time() - start_time
        track_db_operation(operation, collection, "error", duration)
        raise


def track_db_operation_sync(operation: str, collection: str, status: str, duration: float):
    """Track database operation metrics (synchronous wrapper)"""
    db_operations_total.labels(operation=operation, collection=collection, status=status).inc()
    db_operation_duration_seconds.labels(operation=operation, collection=collection).observe(duration)
