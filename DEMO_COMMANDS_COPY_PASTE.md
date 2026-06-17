# 💻 Copy-Paste Demo Commands

**Copy commands from here during the live demo!**
Keep this file open in terminal or text editor.

---

## 📋 Test Credentials

### Student Account
```
username: student_demo
password: StudentPass123!
```

### Employer Account
```
username: employer_demo
password: EmployerPass123!
```

### Admin Account
```
username: admin
password: AdminPass123!
```

---

## SEC-002: Google OAuth

### URL to Visit
```
https://jobly.kz/accounts/login/
OR
http://127.0.0.1:8000/accounts/login/
```

**Action**: Click "Войти через Google" button and complete Google login

---

## SEC-003: RBAC - Get Tokens First

### Get Student Token
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "student_demo", "password": "StudentPass123!"}'
```

**Copy the "token" value from response. Save it as:**
```
STUDENT_TOKEN=<paste_token_here>
```

### Get Employer Token
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "employer_demo", "password": "EmployerPass123!"}'
```

**Copy the "token" value from response. Save it as:**
```
EMPLOYER_TOKEN=<paste_token_here>
```

### Test: Student Accessing Employer Feature (Should Fail)
```bash
curl -X GET http://127.0.0.1:8000/api/jobs/create/ \
  -H "Authorization: Bearer STUDENT_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected: 403 Forbidden**

### Test: Employer Accessing Same Feature (Should Work)
```bash
curl -X GET http://127.0.0.1:8000/api/jobs/create/ \
  -H "Authorization: Bearer EMPLOYER_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected: 200 OK**

---

## SEC-004: CAPTCHA

### URL to Visit
```
https://jobly.kz/register/
OR
http://127.0.0.1:8000/register/
```

**Actions:**
1. Press F12 to open DevTools
2. Click "Network" tab
3. Fill registration form with:
   - Username: testuser_123
   - Email: test@example.com
   - Password: SecurePass123!
   - Confirm: SecurePass123!
4. Click "Register" button
5. In Network tab, look for POST request
6. Click request and scroll to "Request Body"
7. Find and highlight: `"captcha_token": "..."`

---

## SEC-005: OWASP

### A01: Access Control Test (Should Fail)
```bash
curl -X GET http://127.0.0.1:8000/api/profile/other_user/ \
  -H "Authorization: Bearer STUDENT_TOKEN"
```

**Expected: 403 Forbidden**

### A03: Check for Raw SQL (Should Find Nothing)
```bash
cd classes-main
grep -r "cursor.execute" .
```

**Expected: No output (no raw SQL)**

### A05: Try Weak Password (Should Fail with 422)
```bash
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "weakpasstest",
    "email": "weak@test.com",
    "password": "123456",
    "captcha_token": "dummy"
  }'
```

**Expected: 422 Unprocessable Entity with error messages**

### A05: Try Strong Password (Should Succeed)
```bash
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "strongpasstest",
    "email": "strong@test.com",
    "password": "SecurePass123!@#",
    "captcha_token": "dummy"
  }'
```

**Expected: 201 Created**

### A07: Show Argon2 Configuration
```bash
cd classes-main
grep -A 5 "PASSWORD_HASHERS" core/settings.py
```

**Expected: Argon2PasswordHasher listed first**

---

## SEC-006: Security Headers

### Option 1: securityheaders.com (Visual - Best for Demo)
```
1. Go to: https://securityheaders.com
2. Paste URL: https://jobly.kz
3. Click: Scan
4. Show result: Grade and headers
```

### Option 2: curl Command
```bash
curl -i https://jobly.kz/ 2>&1 | grep -E "Strict-Transport-Security|Content-Security-Policy|Permissions-Policy"
```

**Expected: 3 headers shown**

### Option 3: Browser DevTools (F12)
```
1. Press F12
2. Click "Network" tab
3. Reload page (F5)
4. Click first request (domain name)
5. Look for "Response Headers" section
6. Scroll down to find security headers
```

**Expected: All 3 headers present**

---

## SEC-007: Secret Scanning

### Installation (if needed)
```bash
pip install trufflehog
```

### Run Scan
```bash
cd classes-main
python scan_secrets.py
```

**Expected: NO SECRETS FOUND**

### Manual Scan Alternative
```bash
cd classes-main
trufflehog git . --json
```

**Expected: Empty result or "No secrets found"**

### Verify .env is Protected
```bash
cat .gitignore | grep ".env"
```

**Expected: .env listed in .gitignore**

---

## SEC-008: Security Logging

### Trigger Failed Login
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "student_demo", "password": "WrongPassword123!"}'
```

**Expected: 401 Unauthorized**

### Check Logs
```bash
cd classes-main
tail -20 debug.log
```

**Expected: Security log entries like:**
```
[SECURITY] FAILED_LOGIN | User: student_demo | IP: 127.0.0.1
```

---

## 🔧 Quick Setup Commands

### Start Application
```bash
cd "c:\Users\Altyn\Documents\GitHub\Simulator backend\-\classes-main"
.venv\Scripts\activate
python manage.py runserver 127.0.0.1:8000
```

### Open New Terminal While Running
```bash
# Open new PowerShell/Terminal
# Navigate to same directory
cd "c:\Users\Altyn\Documents\GitHub\Simulator backend\-\classes-main"
.venv\Scripts\activate
# Now ready to run curl commands
```

### Verify Server Running
```bash
curl http://127.0.0.1:8000/
```

**Expected: HTML response (page content)**

---

## 📝 Testing Checklist

Before demo, run these to verify everything works:

```bash
# 1. Check application runs
python manage.py runserver &

# 2. Check API endpoint
curl http://127.0.0.1:8000/api/health/

# 3. Get test tokens
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "student_demo", "password": "StudentPass123!"}'

# 4. Test RBAC
curl -X GET http://127.0.0.1:8000/api/jobs/create/ \
  -H "Authorization: Bearer <TOKEN>"

# 5. Check security headers
curl -i http://127.0.0.1:8000/ | grep "Strict-Transport"

# 6. Test secret scanning
python scan_secrets.py

# 7. Check logs
tail debug.log
```

---

## ⚡ Fast Command Reference

| Feature | Command |
|---------|---------|
| Student Token | `curl -X POST http://127.0.0.1:8000/api/login/ -d '{"username":"student_demo","password":"StudentPass123!"}'` |
| Test RBAC | `curl -X GET http://127.0.0.1:8000/api/jobs/create/ -H "Authorization: Bearer TOKEN"` |
| Check Headers | `curl -i http://127.0.0.1:8000/` |
| Scan Secrets | `python scan_secrets.py` |
| Show Logs | `tail -20 debug.log` |
| Check Raw SQL | `grep -r "cursor.execute" .` |
| Show Passwords | `grep -A 5 "PASSWORD_HASHERS" core/settings.py` |

---

## 🎯 Pro Tips

1. **Test all commands BEFORE demo**
   - Run each command in order
   - Save successful outputs
   - Note any errors for fixing

2. **Copy output for reference**
   - Save token values in notepad
   - Copy successful responses
   - Have them ready to show

3. **Use Postman as alternative**
   - Import commands into Postman
   - Easier UI than terminal
   - Better formatting of responses

4. **Keep backup screenshots**
   - If command fails, show screenshot
   - Still proves feature works

5. **Have written URLs ready**
   - Don't type them live (slow)
   - Copy/paste from this file
   - More professional

---

## 🆘 Command Troubleshooting

### curl command not found
```bash
# Install curl for Windows
# (Usually already installed with Git Bash)
# Or use: Invoke-WebRequest (PowerShell)
Invoke-WebRequest -Uri "http://127.0.0.1:8000/"
```

### Port 8000 already in use
```bash
# Kill existing process
lsof -i :8000
kill -9 <PID>

# Or use different port
python manage.py runserver 8001
```

### Virtual environment not activated
```bash
# Activate it
.venv\Scripts\activate

# Verify: (venv) should appear at start of terminal line
```

### Import errors when running commands
```bash
# Install dependencies
pip install -r requirements.txt

# Try again
python scan_secrets.py
```

---

**Ready to present! Copy commands as needed during demo! 🚀**
