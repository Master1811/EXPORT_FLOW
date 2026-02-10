# Grafana + Prometheus Monitoring Setup

This guide explains how to monitor your ExportFlow platform using Prometheus and Grafana.

## What's Being Monitored

✅ **System Status**: API, Database, Services health  
✅ **Real-time Metrics**: Requests/min, error rates, latency (p95, p99)  
✅ **Database Metrics**: Connection count, operation rates, slow query detection  
✅ **Background Jobs**: Completion/failure rates, execution duration  
✅ **Recent Errors**: Summary of errors by type and endpoint  
✅ **Uptime History**: API uptime tracking since startup  
✅ **Business Metrics**: Outstanding receivables, export value  

---

## Local Development Setup (Docker Compose)

### Prerequisites
- Docker and Docker Compose installed
- Backend running (or will be managed by Docker Compose)

### Quick Start

```bash
# 1. Install Prometheus client library
cd backend
pip install prometheus-client

# 2. Start all services (MongoDB, Backend, Prometheus, Grafana)
cd ..
docker-compose up -d

# 3. Access services
# - Grafana Dashboard: http://localhost:3001 (admin/admin)
# - Prometheus UI: http://localhost:9090
# - Backend API: http://localhost:8001
# - MongoDB: localhost:27017
```

### What Each Service Does

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| Grafana | 3001 | http://localhost:3001 | Visualization & Dashboards |
| Prometheus | 9090 | http://localhost:9090 | Metrics collection & storage |
| FastAPI Backend | 8001 | http://localhost:8001/metrics | Metrics endpoint |
| MongoDB | 27017 | localhost:27017 | Database |

### View Metrics Locally

**Option 1: Grafana Dashboard (Recommended)**
1. Open http://localhost:3001
2. Login with `admin` / `admin`
3. Go to **Dashboards** → **ExportFlow System Monitoring**
4. View real-time charts

**Option 2: Prometheus Query UI**
1. Open http://localhost:9090
2. Click **Graph** tab
3. Query examples:
   - `http_requests_total` - Total requests
   - `http_request_duration_seconds` - Request latency
   - `api_uptime_seconds` - API uptime
   - `errors_summary_total` - Error count by type

**Option 3: Raw Metrics Endpoint**
```bash
curl http://localhost:8001/metrics
```
Returns raw Prometheus format metrics.

### Stopping Services
```bash
docker-compose down
```

---

## Production Deployment (Free Tier)

### Option 1: Render.com + Grafana Cloud (Recommended for Free Tier)

#### Step 1: Deploy Backend to Render
1. Push your code to GitHub
2. Go to [render.com](https://render.com)
3. Click **New** → **Web Service**
4. Connect your GitHub repo
5. Configure:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8080`
   - **Environment Variables**:
     ```
     MONGODB_URL=your_mongodb_cloud_connection_string
     API_PORT=8080
     ```
6. Deploy and get your service URL (e.g., `https://exportflow.onrender.com`)

#### Step 2: Deploy Prometheus to Render
Create a separate Prometheus service:
1. Create a GitHub repo with:
   - `prometheus.yml` (modified for production)
   - `Dockerfile`
2. Deploy same way as backend
3. Update prometheus.yml to scrape your backend:
   ```yaml
   scrape_configs:
     - job_name: 'exportflow-production'
       static_configs:
         - targets: ['https://exportflow.onrender.com']
       metrics_path: '/metrics'
   ```

#### Step 3: Use Grafana Cloud (Free Tier)
1. Go to [grafana.com](https://grafana.com/cloud)
2. Sign up for **Free Tier** (includes 3 dashboards, 10K series)
3. Create a **Prometheus data source** pointing to your Render Prometheus instance
4. Import the dashboard JSON from `grafana-provisioning/dashboards/exportflow-monitoring.json`

### Option 2: Railway + Grafana Cloud

Similar to Render, but using [railway.app](https://railway.app) instead.

```bash
# Install railway CLI
npm i -g @railway/cli

# Login and init
railway login
railway init

# Deploy
railway up
```

### Option 3: Self-Hosted VPS (AWS Free Tier, Linode, etc.)

1. **Rent a small VPS** (e.g., AWS t3.micro free tier, Linode $5/month)
2. **SSH into the server**:
   ```bash
   ssh ubuntu@your-vps-ip
   ```

3. **Install Docker**:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

4. **Clone your repo and run Docker Compose**:
   ```bash
   git clone https://github.com/yourusername/exportflow.git
   cd exportflow
   docker-compose up -d
   ```

5. **Set up SSL (Let's Encrypt)**:
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot certonly --standalone -d yourdomain.com
   ```

6. **Access**:
   - Grafana: `https://yourdomain.com:3001`
   - Prometheus: `https://yourdomain.com:9090`

---

## Key Metrics Explained

### HTTP Metrics
- **http_requests_total**: Total count of all HTTP requests (grouped by method, endpoint, status)
- **http_request_duration_seconds**: Latency histogram (p50, p95, p99)
- **http_errors_total**: Error count (grouped by error type)

### Database Metrics
- **db_operations_total**: Number of DB operations (find, insert, update, delete)
- **db_operation_duration_seconds**: DB operation latency
- **db_connections_active**: Currently active DB connections

### Business Metrics
- **shipments_created_total**: Total shipments created
- **payments_recorded_total**: Total payments recorded
- **export_value_total**: Sum of all export values (current)
- **receivables_outstanding**: Current outstanding amount

### Job Metrics
- **background_jobs_total**: Count of background jobs by type and status
- **background_job_duration_seconds**: Job execution time

---

## Alert Setup (Optional)

To add alerts in Grafana:
1. Go to **Alerting** → **Alert Rules**
2. Create rule example:
   - **Name**: High Error Rate
   - **Condition**: `rate(http_errors_total[5m]) > 0.1` (>0.1 errors/sec)
   - **Action**: Send email/Slack notification

---

## Cost Summary (Free Tier)

| Service | Cost | Notes |
|---------|------|-------|
| Render Web Service | $7/month (or free tier) | Backend hosting |
| Grafana Cloud Free | $0 | 3 dashboards, 10K series |
| MongoDB Atlas Free | $0 | 512MB storage |
| **Total** | **$7-15/month** | Very economical |

---

## Troubleshooting

### Prometheus not scraping metrics
```bash
# Check if backend is responding
curl http://localhost:8001/metrics

# Check Prometheus logs
docker-compose logs prometheus
```

### Grafana dashboard blank
1. Verify Prometheus data source is working (Settings → Data Sources)
2. Check if backend is sending metrics (`curl http://localhost:8001/metrics`)
3. Wait 30 seconds for metrics to appear (Prometheus scrape interval = 10s)

### Docker Compose fails
```bash
# Check logs
docker-compose logs

# Rebuild
docker-compose down && docker-compose build && docker-compose up
```

---

## Next Steps

1. **Customize Dashboard**: Edit `grafana-provisioning/dashboards/exportflow-monitoring.json` to add more panels
2. **Add Alerts**: Configure email/Slack notifications for critical metrics
3. **Set Retention**: Prometheus stores 15 days of data by default (adjustable in docker-compose.yml)
4. **Create Recording Rules**: Pre-compute expensive queries for faster dashboards
