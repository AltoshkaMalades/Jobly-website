# Jobly Project - Week 3 Security Deliverables Guide

**Project:** Jobly Django Application  
**Stack:** Django 5.x, django-allauth, PostgreSQL, Celery, Redis  
**Deployment:** Render.com  
**Last Updated:** 2026-06-08

---

## Table of Contents
1. [Security Checklist](#security-checklist)
2. [API Endpoints for Testing](#api-endpoints-for-testing)
3. [Live Demonstration Scenarios](#live-demonstration-scenarios)
4. [curl Commands for Postman/Testing](#curl-commands-for-postman-testing)
5. [Verification Steps](#verification-steps)
6. [Troubleshooting](#troubleshooting)

---

## Security Checklist

### SEC-001: Project Setup ✓
- ✅ Django 5.x configured with security middleware
- ✅ PostgreSQL database for production
- ✅ Celery + Redis for async tasks
- ✅ Environment variables in `.env` (not committed)

### SEC-002: Google Sign-In ✓
- ✅ OAuth integration with django-allauth
- ✅ Login template uses POST form with `{% csrf_token %}`
- ✅ Proper redirect to `{% provider_login_url 'google' process='login' %}`
- ✅ JWT/session token generated on successful auth
- **File:** `accounts/templates/accounts/login.html`

### SEC-003: RBAC (Role-Based Access Control) ✓
- ✅ `@role_required(allowed_roles=['employer'])` decorator
- ✅ Returns HTTP 403 Forbidden for unauthorized access
- ✅ Logging of unauthorized access attempts
- **Test Endpoint:** GET `/api/admin/jobs/` (employer only)
- **File:** `accounts/views.py` (decorators: `role_required`, `admin_required`)

### SEC-004: CAPTCHA (reCAPTCHA v3) ✓
- ✅ django_recaptcha v3 integrated
- ✅ Registration form includes CAPTCHA field
- ✅ Fallback simple CAPTCHA for development
- ✅ CAPTCHA token sent in POST request body
- **Files:** `accounts/forms.py`, `accounts/templates/accounts/register.html`

### SEC-005: OWASP Vulnerabilities ✓

#### A01 - Broken Access Control
- ✅ All endpoints check `request.user == owner` before data access
- ✅ Example: `/api/user/<user_id>/` returns 403 if accessing other user's data
- **Test:** Try to access `/api/user/2/` as user ID 1

#### A03 - Injection Prevention
- ✅ All queries use Django ORM (no raw SQL with user input)
- ✅ Verified: no `.raw()`, `db.execute()` with user data
- **Safe Files:** accounts/views.py, learning/views.py

### SEC-006: Password Validation ✓
- ✅ Weak passwords (e.g., '12345678', 'password') rejected
- ✅ Returns HTTP 422 Unprocessable Entity with error details
- ✅ Error message lists specific validation failures
- **Test Endpoint:** POST `/api/register/` with weak password
- **Example Error:**
```json
{
  "status": "error",
  "message": "Password validation failed",
  "errors": {
    "password1": ["This password is too common."],
    "password2": ["This password is entirely numeric."]
  }
}
```

### SEC-007: Security Logging ✓
- ✅ Failed login attempts logged to `debug.log`
- ✅ Log format: `[SECURITY] LOGIN_FAILED | User: None | IP: 127.0.0.1 | Details: Username: admin`
- ✅ Logs include: event type, username/email, IP address, timestamp
- **Log Location:** `classes-main/debug.log`
- **Monitored Events:**
  - `LOGIN_SUCCESS`
  - `LOGIN_FAILED`
  - `UNAUTHORIZED_ACCESS`
  - `USER_REGISTERED`
  - `LOGOUT`

### SEC-008: Security Headers ✓
- ✅ SECURE_SSL_REDIRECT = True
- ✅ SESSION_COOKIE_SECURE = True
- ✅ CSRF_COOKIE_SECURE = True
- ✅ SECURE_HSTS_SECONDS = 31536000
- ✅ SECURE_HSTS_INCLUDE_SUBDOMAINS = True
- ✅ SECURE_HSTS_PRELOAD = True
- ✅ SECURE_CONTENT_TYPE_NOSNIFF = True
- ✅ SECURE_BROWSER_XSS_FILTER = True
- ✅ X_FRAME_OPTIONS = 'DENY'
- ✅ SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
- **File:** `core/settings.py` (lines 131-158)
- **Test:** https://securityheaders.com (target B+ or higher)

### SEC-009: Trufflehog Secret Scanning ✓
- ✅ `.env` file in `.gitignore`
- ✅ No secrets committed to repository
- ✅ `SECRET_KEY` from environment variable

---

## API Endpoints for Testing

### Authentication & Authorization

#### 1. Login (Form-based)
```
POST /login/
Content-Type: application/x-www-form-urlencoded

username=testuser&password=SecurePass123!
```

#### 2. Google OAuth Sign-In
```
POST /accounts/google/login/process/login/
(Handled by django-allauth)
```

#### 3. Register (Form-based)
```
POST /register/
Content-Type: application/x-www-form-urlencoded

username=newuser&email=test@example.com&password1=SecurePass123!&password2=SecurePass123!&role=student
```

#### 4. Register (API with validation)
```
POST /api/register/
Content-Type: application/x-www-form-urlencoded

username=apiuser&email=api@test.com&password1=weak123&password2=weak123&role=student
```
**Expected Response (422):**
```json
{
  "status": "error",
  "message": "Password validation failed",
  "errors": {
    "password1": ["This password is too common."],
    "password2": ["This password is entirely numeric."]
  }
}
```

---

### RBAC (Role-Based Access Control) - SEC-003

#### 5. Admin Jobs API (Employer Only)
```
GET /api/admin/jobs/
Authorization: Bearer <token> OR Session Cookie
```
**Expected if logged in as employer (200 OK):**
```json
{
  "status": "success",
  "user": "employer_username",
  "role": "employer",
  "jobs_count": 5,
  "jobs": [...]
}
```
**Expected if logged in as student (403 Forbidden):**
```json
{
  "message": "403: Access Denied - Insufficient Permissions"
}
```

#### 6. Student Profile API (Student Only)
```
GET /api/student/profile/
Authorization: Bearer <token> OR Session Cookie
```
**Expected if logged in as student (200 OK):**
```json
{
  "status": "success",
  "user": "student_username",
  "role": "student",
  "applications_count": 3,
  "favorites_count": 2
}
```
**Expected if logged in as employer (403 Forbidden):**
```json
{
  "message": "403: Access Denied - Insufficient Permissions"
}
```

#### 7. User Data Access (Owner Only)
```
GET /api/user/<user_id>/
Authorization: Bearer <token> OR Session Cookie
```
**Expected if accessing own data (200 OK):**
```json
{
  "status": "success",
  "user_id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "role": "student",
  "bio": "..."
}
```
**Expected if accessing other user's data (403 Forbidden):**
```json
{
  "error": "Forbidden: Cannot access other users data"
}
```

---

## Live Demonstration Scenarios

### Scenario 1: Google Sign-In Demo (SEC-002)
1. Navigate to `/login/`
2. Inspect the "Continue with Google" button using Browser Dev Tools
3. **Show:** It's a POST form, not an `<a>` tag, with `{% csrf_token %}`
4. Click the button and complete Google authentication
5. **Show:** JWT/Session token in cookies (DevTools → Application → Cookies)

### Scenario 2: RBAC 403 Forbidden Demo (SEC-003)
1. Open Postman or use curl
2. Create two test users:
   - User A: role = `employer`
   - User B: role = `student`

**Test as Student (should get 403):**
```bash
curl -H "Authorization: Bearer <student_token>" \
  https://jobly.kz/api/admin/jobs/
```
**Show Terminal Output:**
```
HTTP/1.1 403 Forbidden
{"message": "403: Access Denied - Insufficient Permissions"}
```

**Test as Employer (should get 200):**
```bash
curl -H "Authorization: Bearer <employer_token>" \
  https://jobly.kz/api/admin/jobs/
```

### Scenario 3: CAPTCHA Verification (SEC-004)
1. Navigate to `/register/`
2. **Show in Browser Console/DevTools:**
   - If django-recaptcha enabled: Show the reCAPTCHA v3 badge
   - Inspect form, show `g-recaptcha-response` hidden field
3. Try to register with weak password
4. **Show:** Validation error includes CAPTCHA verification

### Scenario 4: Password Validation (SEC-006)
1. Use the API endpoint:
```bash
curl -X POST https://jobly.kz/api/register/ \
  -d "username=testuser&email=test@test.com&password1=12345678&password2=12345678&role=student"
```
2. **Show:** HTTP 422 response with detailed password errors

### Scenario 5: Access Control Violation (SEC-005)
1. Login as User A (ID: 1)
2. Try to access User B's data (ID: 2):
```bash
curl https://jobly.kz/api/user/2/ \
  -H "Cookie: sessionid=<user_a_session>"
```
3. **Show:** HTTP 403 Forbidden response
4. Check `debug.log` to see security event logged:
```
[SECURITY] UNAUTHORIZED_DATA_ACCESS | User: 1 (user_a) | IP: 192.168.1.100 | Details: Attempted to access user 2 data
```

### Scenario 6: Security Headers Verification (SEC-008)
1. Open browser DevTools → Network tab
2. Make request to any page
3. **Show Response Headers:**
   - `Strict-Transport-Security: max-age=31536000`
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: DENY`
   - `Referrer-Policy: strict-origin-when-cross-origin`

### Scenario 7: Security Logging (SEC-007)
1. Attempt to login with wrong password 3 times
2. SSH into server: `tail -f debug.log`
3. **Show log output:**
```
WARNING 2026-06-08 15:30:45 accounts [SECURITY] LOGIN_FAILED | User: None | IP: 127.0.0.1 | Details: Username: admin
WARNING 2026-06-08 15:30:52 accounts [SECURITY] LOGIN_FAILED | User: None | IP: 127.0.0.1 | Details: Username: admin
WARNING 2026-06-08 15:30:58 accounts [SECURITY] LOGIN_FAILED | User: None | IP: 127.0.0.1 | Details: Username: admin
```

### Scenario 8: Trufflehog Secret Scanning (SEC-009)
1. In terminal, run:
```bash
cd /path/to/project
trufflehog filesystem . --json | grep -i secret
```
2. **Show:** Empty output (no secrets found)
3. Verify `.env` is in `.gitignore`:
```bash
cat .gitignore | grep ".env"
```

---

## curl Commands for Postman/Testing

### Setup Variables
```bash
BASE_URL="http://localhost:8000"
EMPLOYER_TOKEN="<employer_bearer_token>"
STUDENT_TOKEN="<student_bearer_token>"
EMPLOYER_SESSION="<employer_sessionid>"
STUDENT_SESSION="<student_sessionid>"
```

### 1. Register New User (Student)
```bash
curl -X POST "$BASE_URL/register/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=student1&email=student@test.com&password1=SecurePass123!&password2=SecurePass123!&role=student"
```

### 2. Register New User (Employer)
```bash
curl -X POST "$BASE_URL/register/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=employer1&email=employer@test.com&password1=SecurePass123!&password2=SecurePass123!&role=employer"
```

### 3. Test Weak Password Validation (422 Response)
```bash
curl -X POST "$BASE_URL/api/register/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=weakpass&email=weak@test.com&password1=password&password2=password&role=student"
```

### 4. Test RBAC: Employer Accesses Admin Jobs (200 OK)
```bash
curl -X GET "$BASE_URL/api/admin/jobs/" \
  -H "Cookie: sessionid=$EMPLOYER_SESSION"
```

### 5. Test RBAC: Student Tries to Access Admin Jobs (403 Forbidden)
```bash
curl -X GET "$BASE_URL/api/admin/jobs/" \
  -H "Cookie: sessionid=$STUDENT_SESSION"
```

### 6. Test Access Control: Access Own Data (200 OK)
```bash
curl -X GET "$BASE_URL/api/user/1/" \
  -H "Cookie: sessionid=$EMPLOYER_SESSION"
```

### 7. Test Access Control: Access Other User's Data (403 Forbidden)
```bash
curl -X GET "$BASE_URL/api/user/2/" \
  -H "Cookie: sessionid=$STUDENT_SESSION"
```

### 8. Student Profile API
```bash
curl -X GET "$BASE_URL/api/student/profile/" \
  -H "Cookie: sessionid=$STUDENT_SESSION"
```

### 9. Login (Get Session Cookie)
```bash
curl -X POST "$BASE_URL/login/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -c cookies.txt \
  -d "username=student1&password=SecurePass123!"
```

### 10. Failed Login (Check Security Logging)
```bash
curl -X POST "$BASE_URL/login/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=student1&password=WrongPassword"
```

---

## Verification Steps

### Pre-Demo Checklist

1. **Database Setup**
   ```bash
   cd classes-main
   python manage.py migrate
   python manage.py createsuperuser  # Create admin user
   ```

2. **Test Users Creation**
   ```bash
   # Via Django shell
   python manage.py shell
   ```
   ```python
   from django.contrib.auth.models import User
   from accounts.models import Profile
   
   # Create test users
   student = User.objects.create_user('student1', 'student@test.com', 'SecurePass123!')
   prof_s = Profile.objects.create(user=student, role='student')
   
   employer = User.objects.create_user('employer1', 'employer@test.com', 'SecurePass123!')
   prof_e = Profile.objects.create(user=employer, role='employer')
   ```

3. **Environment Variables**
   ```bash
   # .env file should contain:
   DJANGO_DEBUG=False
   SECRET_KEY=your-secret-key-here
   RECAPTCHA_PUBLIC_KEY=your-public-key
   RECAPTCHA_PRIVATE_KEY=your-private-key
   GOOGLE_OAUTH2_KEY=your-google-key
   GOOGLE_OAUTH2_SECRET=your-google-secret
   ```

4. **Run Server**
   ```bash
   python manage.py runserver
   ```

5. **Check Security Headers**
   ```bash
   # In another terminal
   curl -I http://localhost:8000/
   ```

6. **Verify Logs**
   ```bash
   tail -f debug.log
   ```

---

## Troubleshooting

### Issue: 403 Forbidden Not Returning
**Solution:** Ensure `role_required` decorator is applied to the view:
```python
@login_required
@role_required(allowed_roles=['employer'])
def api_admin_jobs(request):
    ...
```

### Issue: CAPTCHA Not Working
**Solution:** Check if django_recaptcha is installed:
```bash
pip install django-recaptcha
```
And RECAPTCHA keys are set in `.env`

### Issue: Security Headers Not Showing
**Solution:** Ensure `DEBUG=False` in production:
```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    # ... other headers
```

### Issue: Logging Not Working
**Solution:** Check `debug.log` path and permissions:
```bash
ls -la debug.log
tail -n 50 debug.log
```

### Issue: Google OAuth Failing
**Solution:** Verify Social Application in Django Admin:
1. Go to `/admin/socialaccount/socialapp/`
2. Add/edit Google app
3. Ensure Client ID and Secret match `.env` values

---

## Code Files Modified for Security

| Component | File | Changes |
|-----------|------|---------|
| Login Template | `accounts/templates/accounts/login.html` | Changed Google button from `<a>` to POST form with CSRF |
| Decorators | `accounts/views.py` | Enhanced `role_required`, added `admin_required` with proper logging |
| API Endpoints | `accounts/views.py` | Added `/api/admin/jobs/`, `/api/student/profile/`, `/api/user/<id>/`, `/api/register/` |
| Forms | `accounts/forms.py` | Added reCAPTCHA v3 field to registration form |
| Registration Template | `accounts/templates/accounts/register.html` | Integrated django-recaptcha field |
| URL Routing | `accounts/urls.py` | Added new API endpoint routes |
| Settings | `core/settings.py` | Enhanced security headers (HSTS, CSP, XSS protection) |
| Git Ignore | `classes-main/.gitignore` | Added `.env`, secrets, cache patterns |

---

## Contact & Support

For questions about the security implementation:
- Check logs: `tail -f classes-main/debug.log`
- Run tests: `pytest tests/ -v`
- Django admin: `/admin/`

---

**Document Version:** 1.0  
**Last Verified:** 2026-06-08  
**Status:** ✅ Ready for Week 3 Deliverables Submission
