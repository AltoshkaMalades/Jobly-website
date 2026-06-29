# 🚀 Monitoring Stack - Quick Start Checklist

## LOCAL DEVELOPMENT ✅

### Verify Local Stack is Running
```bash
cd classes-main
docker compose ps
```

Should see: `web` (up), `prometheus` (up), `grafana` (up), `redis` (healthy), `db` (healthy)

### Test All Endpoints

#### Django Metrics
```bash
curl http://127.0.0.1:8000/metrics/raw/
# Returns: Prometheus format metrics
```

#### Health Check
```bash
curl http://127.0.0.1:8000/metrics/api/health/
# Returns: JSON with all service statuses
```

#### Prometheus Health
```bash
curl http://127.0.0.1:9090/-/healthy
# Returns: 200 OK
```

#### Grafana Health  
```bash
curl http://127.0.0.1:3000/api/health
# Returns: 200 OK
```

#### Prometheus Targets
```bash
curl http://127.0.0.1:9090/api/v1/targets | jq '.data.activeTargets[].health'
# Returns: "up"
```

---

## PRODUCTION DEPLOYMENT 📋

### 1. Prepare External Monitoring

Choose ONE option:

**Option A: Render Hosting**
- Create separate Render services for Prometheus and Grafana
- Get external URLs (e.g., https://prometheus-abc.onrender.com)

**Option B: Self-Hosted Server**
- Deploy Prometheus/Grafana on your server
- Get URLs (e.g., http://your-server.com:9090)

**Option C: SaaS Provider**
- Use Datadog, New Relic, etc.
- Get their API endpoints

### 2. Add Environment Variables to Render

In Render Dashboard → Environment:

```
PROMETHEUS_URL=<your-prometheus-url>
GRAFANA_URL=<your-grafana-url>
```

Example:
```
PROMETHEUS_URL=https://prometheus-abc.onrender.com
GRAFANA_URL=https://grafana-abc.onrender.com
```

### 3. Deploy to Production

```bash
git add .
git commit -m "Monitoring stack deployment"
git push origin <branch-name>
# Render auto-deploys on push
```

### 4. Verify Production

```bash
# Check health endpoint
curl https://your-app.onrender.com/metrics/api/health/

# Expected response:
# {
#   "services": {
#     "django": {"status": "up"},
#     "prometheus": {"status": "up"},
#     "grafana": {"status": "up"}
#   },
#   "overall_status": "healthy"
# }
```

### 5. Configure Grafana

1. Log into Grafana
2. **Configuration** → **Data Sources**
3. **Add Prometheus**:
   - URL: `https://prometheus.your-domain.com`
   - HTTP Method: GET
   - Test & Save
4. **Create Dashboard** or **Import** community dashboard

---

## TROUBLESHOOTING 🔧

| Problem | Check | Solution |
|---------|-------|----------|
| Django target DOWN | `curl http://web:8000/metrics/raw/` | Restart web: `docker compose restart web` |
| Prometheus DOWN | `curl http://localhost:9090/-/healthy` | Restart: `docker compose restart prometheus` |
| Grafana DOWN | `curl http://localhost:3000/api/health` | Restart: `docker compose restart grafana` |
| No data in Grafana | Wait 15s (scrape interval) + check targets | Verify Prometheus has Django target UP |
| Module not found error | Docker logs: `docker compose logs web` | Rebuild: `docker compose build --no-cache web` |

---

## 📊 Testing

Run unit tests:
```bash
python -m pytest tests/unit/test_monitoring.py -v
```

Expected: All tests PASS ✓

---

## 📞 Support

### Key Components
- **Django Settings**: `core/settings.py` (lines 108-115)
- **Health API**: `core/views_monitoring_dashboard.py` (line 59)
- **Prometheus Config**: `prometheus/prometheus.yml`
- **Docker Setup**: `docker-compose.yml` (prometheus & grafana services)

### Documentation
- Full guide: [MONITORING_DEPLOYMENT_GUIDE.md](MONITORING_DEPLOYMENT_GUIDE.md)
- Code reference: `core/views_monitoring_dashboard.py`

---

## ✅ SUCCESS CRITERIA

- [ ] Local stack runs with `docker compose up -d`
- [ ] All health endpoints return 200 OK
- [ ] Prometheus scrapes Django target as "up"
- [ ] Health API returns all services as "up"
- [ ] Unit tests pass
- [ ] Production URLs set in env vars
- [ ] Grafana connects to Prometheus
- [ ] Dashboards displaying metrics

---

**Status**: ✅ LOCAL COMPLETE | 📋 READY FOR PRODUCTION
