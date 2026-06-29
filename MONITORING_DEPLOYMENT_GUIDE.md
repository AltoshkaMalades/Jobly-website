# Prometheus & Grafana Deployment Guide

## 🎯 Overview

This guide covers the complete setup and deployment of a monitoring stack (Prometheus + Grafana) for the Django-based Simulator Backend application.

---

## ✅ Current Status: LOCAL STACK FULLY OPERATIONAL

### Local Stack Components
- ✅ **Django Web** (port 8000) - Scraped by Prometheus
- ✅ **Prometheus** (port 9090) - Time-series database for metrics
- ✅ **Grafana** (port 3000) - Visualization dashboard
- ✅ **Health API** (`/metrics/api/health/`) - Service status endpoint

### Verification
All endpoints have been tested and verified working:

```bash
# Django metrics endpoint
GET http://127.0.0.1:8000/metrics/raw/          → 200 OK (Prometheus format)
GET http://127.0.0.1:8000/metrics/api/health/   → 200 OK (JSON)

# Prometheus
GET http://127.0.0.1:9090/-/healthy             → 200 OK
GET http://127.0.0.1:9090/api/v1/targets       → Django target: UP

# Grafana  
GET http://127.0.0.1:3000/api/health            → 200 OK
Web UI: http://127.0.0.1:3000 (admin/admin)
```

---

## 📊 Architecture

### Data Flow
```
Django App (metrics/raw/) 
    ↓
Prometheus (scrapes every 15s)
    ↓  
Grafana (reads from Prometheus)
    ↓
Web Browser (visualizes)
```

### Key Metrics Collected
- HTTP request count (by endpoint, method, status)
- Request duration (latency histograms)
- Request exceptions
- Database health
- Redis health
- System metrics

---

## 🚀 Local Development

### Starting the Stack

```bash
cd classes-main
docker compose up -d prometheus grafana web redis db
```

### Accessing Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Django App | http://127.0.0.1:8000 | - |
| Prometheus | http://127.0.0.1:9090 | - |
| Grafana | http://127.0.0.1:3000 | admin / admin |

### Stopping the Stack

```bash
docker compose down
```

---

## 🔧 Configuration Files

### 1. Django Settings (`core/settings.py`)

Environment variables for monitoring:

```python
# Optional - leave empty for local development
PROMETHEUS_URL = os.environ.get('PROMETHEUS_URL', '')
GRAFANA_URL = os.environ.get('GRAFANA_URL', '')

# Auto-generated from base URLs
PROMETHEUS_HEALTH_URL = f"{PROMETHEUS_URL}/-/healthy" if PROMETHEUS_URL else ''
GRAFANA_HEALTH_URL = f"{GRAFANA_URL}/api/health" if GRAFANA_URL else ''
```

### 2. Prometheus Config (`prometheus/prometheus.yml`)

```yaml
global:
  scrape_interval: 15s
  
scrape_configs:
  - job_name: 'django'
    metrics_path: /metrics/raw/
    static_configs:
      - targets: ['web:8000']
```

**Note**: Uses Docker DNS (`web:8000` within container network)

### 3. Grafana Datasource (`grafana/provisioning/datasources/datasource.yml`)

```yaml
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    jsonData:
      httpMethod: GET
```

### 4. Docker Compose (`docker-compose.yml`)

- **Web**: Django app exposing `/metrics/raw/`
- **Prometheus**: Scrapes Django every 15 seconds
- **Grafana**: Connected to Prometheus datasource
- **Redis & PostgreSQL**: Supporting services

---

## 🌐 Production Deployment (Render.com)

### Step 1: Determine External Monitoring URLs

You need to decide HOW to run Prometheus/Grafana:

**Option A: Self-Hosted (Recommended)**
- Host Prometheus and Grafana on separate Render services or external servers
- Update environment variables to point to external URLs

**Option B: SaaS Monitoring**
- Use Datadog, New Relic, or similar services
- Update endpoints accordingly

**Option C: Localhost (Development Only)**
- Leave URLs empty to run without external monitoring

### Step 2: Set Environment Variables

In Render.com dashboard, add:

```
PROMETHEUS_URL=https://prometheus.your-domain.com
GRAFANA_URL=https://grafana.your-domain.com
PROMETHEUS_HEALTH_URL=https://prometheus.your-domain.com/-/healthy
GRAFANA_HEALTH_URL=https://grafana.your-domain.com/api/health
```

Or for self-hosted on different port:
```
PROMETHEUS_URL=http://your-server:9090
GRAFANA_URL=http://your-server:3000
```

### Step 3: Configure Health Check

Django's health endpoint will automatically:

1. **Detect configured URLs** - if set in env vars
2. **Check availability** - GET request to health endpoints
3. **Report status** - returns `up`/`down`/`unknown`

**Test in production:**
```bash
curl -X GET https://your-app.onrender.com/metrics/api/health/
```

Expected response:
```json
{
  "timestamp": "2026-06-30T01:32:25.632487",
  "services": {
    "django": {"status": "up", "url": "http://localhost:8000"},
    "prometheus": {"status": "up", "url": "https://prometheus.your-domain.com"},
    "grafana": {"status": "up", "url": "https://grafana.your-domain.com"}
  },
  "overall_status": "healthy"
}
```

### Step 4: Configure Grafana Connection

1. Log into Grafana (`https://grafana.your-domain.com`)
2. Go to **Configuration** → **Data Sources**
3. Add Prometheus datasource:
   - URL: `https://prometheus.your-domain.com` (or internal IP)
   - Access: `Server`
   - HTTP Method: `GET`
4. **Test & Save**

### Step 5: Create Dashboards

Option A: Create custom dashboards
- Click **+** → **Dashboard** → **Add Panel**
- Write PromQL queries

Option B: Import community dashboards
- Click **+** → **Import**
- Enter dashboard ID or paste JSON

### Step 6: Verify

```bash
# Check Django metrics are being scraped
curl https://prometheus.your-domain.com/api/v1/targets

# Expected: django job showing "up" status
```

---

## 🔍 Health Check API

### Endpoint
```
GET /metrics/api/health/
```

### Response Format
```json
{
  "timestamp": "ISO 8601 timestamp",
  "services": {
    "django": {
      "status": "up|down|unknown",
      "url": "URL of service or empty"
    },
    "prometheus": { ... },
    "grafana": { ... }
  },
  "overall_status": "healthy|degraded|unknown"
}
```

### Status Meanings

| Status | Meaning |
|--------|---------|
| `up` | Service is reachable and responding |
| `down` | Service is configured but unreachable |
| `unknown` | Service URL not configured (not an error) |

### Rules

- **overall_status = "healthy"**: All configured services are `up`
- **overall_status = "degraded"**: At least one service is `down`
- **overall_status = "unknown"**: No services configured (local development)

---

## 📝 Common Issues & Solutions

### Issue: "Prometheus target shows DOWN"

**Cause**: Django app not running or metrics endpoint misconfigured

**Fix**:
1. Check Django container is running: `docker compose ps`
2. Verify metrics endpoint: `curl http://web:8000/metrics/raw/`
3. Check logs: `docker compose logs web`

### Issue: "Module not found: django_recaptcha"

**Cause**: Docker image built without dependencies

**Fix**:
```bash
docker compose build --no-cache web
docker compose restart web
```

### Issue: "Grafana datasource connection failed"

**Cause**: Wrong Prometheus URL or network isolation

**Fix**:
- In Docker: Use `http://prometheus:9090` (DNS name)
- In production: Use external URL with HTTPS

### Issue: "No data showing in Grafana"

**Cause**: Prometheus scrape interval or metrics not being exported

**Fix**:
1. Wait 15 seconds for first scrape
2. Check Prometheus targets: `http://prometheus:9090/api/v1/targets`
3. Write test query in Prometheus UI

---

## 📚 PromQL Examples

### Total HTTP Requests (all time)
```promql
sum(rate(simulator_http_requests_total[5m]))
```

### Requests per Status Code
```promql
sum by (status) (rate(simulator_http_requests_total[5m]))
```

### Average Request Duration
```promql
avg(rate(simulator_request_duration_seconds_sum[5m]) / rate(simulator_request_duration_seconds_count[5m]))
```

### Request Exceptions Rate
```promql
rate(simulator_request_exceptions_total[5m])
```

---

## 🔐 Security Notes

### Local Development
- No authentication needed (localhost only)
- Grafana default credentials: `admin` / `admin`
- Change immediately in production!

### Production Recommendations
1. Use HTTPS for all external URLs
2. Enable Grafana authentication (OAuth, LDAP, etc.)
3. Use firewall rules to restrict Prometheus access
4. Set strong Grafana admin password
5. Use environment variables for sensitive URLs (never commit to git)
6. Consider using reverse proxy (nginx) with authentication

---

## 📞 Testing Checklist

- [ ] Django app starts without errors
- [ ] `/metrics/raw/` endpoint returns metrics in Prometheus format
- [ ] `/metrics/api/health/` returns JSON with service status
- [ ] Prometheus health endpoint responds
- [ ] Prometheus can scrape Django target (status = `up`)
- [ ] Grafana health endpoint responds
- [ ] Grafana datasource connects to Prometheus
- [ ] Grafana can display metrics in dashboard

---

## 🔄 Deployment Flow

### Local → Production

1. **Test locally**: `docker compose up -d` ✓
2. **Verify endpoints**: `curl` tests ✓
3. **Set Render env vars**: PROMETHEUS_URL, GRAFANA_URL
4. **Deploy to Render**: Git push to main branch
5. **Verify production health**: Check `/metrics/api/health/` endpoint
6. **Configure Grafana**: Add datasource and dashboards
7. **Monitor logs**: Check for errors in Render dashboard

---

## 📖 Files Reference

| File | Purpose |
|------|---------|
| `core/settings.py` | Django settings, env var handling |
| `core/views_monitoring_dashboard.py` | Health check and metrics views |
| `core/metrics.py` | Prometheus metric definitions |
| `prometheus/prometheus.yml` | Prometheus scrape configuration |
| `grafana/provisioning/datasources/datasource.yml` | Grafana datasource config |
| `docker-compose.yml` | Container orchestration |
| `requirements.txt` | Python dependencies (prometheus-client) |

---

## 🎓 Next Steps

1. **Set up external monitoring** (Prometheus/Grafana on separate service)
2. **Configure production environment variables** in Render
3. **Create custom dashboards** in Grafana
4. **Set up alerts** in Prometheus/Grafana for critical metrics
5. **Document runbooks** for monitoring responses

---

## ✨ Summary

✅ Local monitoring stack is **fully operational**
✅ All components tested and verified
✅ Health check API working correctly  
✅ Ready for production deployment

**Next Action**: Deploy external Prometheus/Grafana instances and set environment variables in Render.
