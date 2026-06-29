# Operations Runbook - Simulator Backend

## Overview
This runbook provides step-by-step procedures for common operational scenarios in the Simulator Backend production environment.

---

## Scenario 1: Incident Response - API Latency Spike

### Symptoms
- Grafana alert: "High API latency" (p95 > 1 second)
- Users reporting slow payment endpoints
- Dashboard shows sustained elevated latency over 5+ minutes

### Diagnosis Steps

**1. Check Prometheus metrics:**
```
# Access http://prometheus:9090
# Query: histogram_quantile(0.95, rate(simulator_http_request_duration_seconds_bucket[5m]))
```

**2. Identify affected endpoints:**
```
# Query: histogram_quantile(0.95, rate(simulator_http_request_duration_seconds_bucket{endpoint="/api/payments/create/"}[5m]))
```

**3. Check error rate for correlation:**
```
# Query: rate(simulator_http_requests_total{status=~"5.."}[5m])
```

**4. SSH into production and check:**
```bash
# Check database connection pool
django-admin shell
# SELECT * FROM django_db_connections;

# Check Redis cache
redis-cli INFO stats

# Check Celery queue depth
celery -A core inspect active_queues

# Monitor system resources
top -p $(pgrep -f gunicorn | head -1)
```

### Remediation

**Option A: Increase gunicorn workers**
```bash
docker-compose stop web
# Edit docker-compose.yml: change --workers 4 to --workers 8
docker-compose up -d web
```

**Option B: Clear Redis cache (if cache invalidation issue)**
```bash
redis-cli FLUSHDB 1  # Clear cache DB (DB 1)
```

**Option C: Restart database connections**
```bash
docker-compose restart db
# Wait 30s for connections to re-establish
```

### Validation
1. Monitor Grafana: p95 latency should drop within 2 minutes
2. Run: `curl -w "@curl-format.txt" http://web:8000/health/`
3. Check error rate: should remain < 5%

---

## Scenario 2: Payment Processing Errors

### Symptoms
- Grafana alert: "High error rate" (5xx errors > 5%)
- Payment webhook logs show failures
- Users report "Payment processing error" messages

### Diagnosis Steps

**1. Check payment service logs:**
```bash
docker logs simulator-web | grep "payment\|ERROR" | tail -50
```

**2. Verify payment provider connectivity:**
```bash
# Check PayPal API status
curl -I https://api.sandbox.paypal.com/

# Check Bereke Bank API status  
curl -I https://api.berekebank.kz/
```

**3. Review recent payment transactions:**
```bash
# In Django shell
from payments.models import Transaction
recent = Transaction.objects.order_by('-created_at')[:10]
for t in recent:
    print(f"{t.id}: {t.status} - {t.error_message}")
```

**4. Check webhook processing:**
```bash
# View queued webhook tasks
docker-compose exec -T celery celery -A core inspect active
```

### Remediation

**Option A: Provider API unavailable**
```bash
# Switch to fallback provider
# Edit settings.py: PAYMENT_PRIMARY_PROVIDER = 'bereke'
docker-compose restart web
```

**Option B: Database connection issue**
```bash
# Verify database is responsive
docker-compose exec -T web python manage.py shell
# >>> from django.db import connections
# >>> connections['default'].cursor().execute('SELECT 1')
```

**Option C: Webhook processing backlog**
```bash
# Restart Celery workers
docker-compose restart celery
docker-compose restart celery-beat
```

### Validation
1. Monitor error rate on Grafana (should drop below 1% within 5 minutes)
2. Test payment endpoint: `curl -X POST http://web:8000/api/payments/create/ -d '{"amount":1000}'`
3. Verify webhook processing: check recent transactions are completing

---

## Scenario 3: Server Resources Exhaustion

### Symptoms
- Grafana alert: "Server Down" (up metric = 0)
- Cannot reach health endpoint: `curl http://web:8000/health/`
- System load critical: `docker stats`

### Diagnosis Steps

**1. Check container status:**
```bash
docker-compose ps
# Expected: web, redis, db, grafana, prometheus all "Up"
```

**2. Identify resource bottleneck:**
```bash
# RAM usage
docker stats --no-stream | grep -E "web|redis|db"

# Disk usage
df -h /var/lib/docker/volumes/

# CPU usage
top -b -n 1 | head -20
```

**3. Check logs for OOM or crashes:**
```bash
docker logs simulator-web | grep -i "memory\|killed\|oom"
docker logs simulator-celery | grep -i "memory\|killed"
```

**4. Verify database is not locked:**
```bash
# Check active connections
docker-compose exec -T db psql -U postgres -d simulator_db -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"
```

### Remediation

**Option A: Free disk space**
```bash
# Clean Docker images
docker image prune -a -f

# Clean logs
docker exec simulator-web sh -c "truncate -s 0 /app/debug.log /app/debug.json.log"
```

**Option B: Restart all services**
```bash
docker-compose down
docker-compose up -d
# Wait 60s for services to stabilize
```

**Option C: Scale down and increase resources**
```bash
# Kill long-running requests
docker-compose exec -T web pkill -f gunicorn

# Edit docker-compose.yml to increase memory limits
# services:
#   web:
#     mem_limit: 2g
docker-compose up -d web
```

**Option D: Emergency cache purge**
```bash
# Clear Redis entirely
redis-cli FLUSHALL
```

### Validation
1. Check health: `curl http://web:8000/health/` should return 200
2. Monitor metrics: request rate should return to normal within 2 min
3. Verify no more "Server Down" alerts
4. Check container uptime: `docker inspect simulator-web | grep -i "startedAt"`

---

## Escalation Contacts

| Role | Contact | On-call |
|------|---------|---------|
| Platform Engineer | ops@simulator.kz | 24/7 |
| Database Admin | dba@simulator.kz | Business hours |
| Payment Ops | payments@simulator.kz | 24/7 |
| Security Team | security@simulator.kz | On-demand |

---

## Post-Incident Review

After any incident:
1. Document timeline in `incident-log.md`
2. Update this runbook with new learnings
3. Create tickets for permanent fixes
4. Schedule incident review meeting within 48 hours
