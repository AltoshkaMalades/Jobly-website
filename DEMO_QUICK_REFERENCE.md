# 🎯 QUICK DEMO REFERENCE CARD

**Print this page and bring it to your presentation!**

---

## SEC-002: Google OAuth (2 min)

```
1. Go to: https://jobly.kz/accounts/login/
2. Click: [Войти через Google]
3. Sign in with Google account
4. ✅ Redirected to /profile/ page
```

**What graders see**: You're logged in without password!

---

## SEC-003: RBAC Roles (2 min)

```bash
# Terminal 1: Get Student Token
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"student_user","password":"StudentPass123!"}'

# Terminal 2: Student tries admin endpoint
curl -X GET http://127.0.0.1:8000/api/jobs/create/ \
  -H "Authorization: Bearer <STUDENT_TOKEN>"

# ✅ Result: HTTP 403 Forbidden
```

**What graders see**: Error message "permission_denied"

---

## SEC-004: CAPTCHA (2 min)

```
1. Go to: https://jobly.kz/register/
2. Press: F12 (open DevTools)
3. Click: Network tab
4. Fill registration form
5. Click: [Register] button
6. Look for: "captcha_token" in Request Body
```

**What graders see**: Long token string in network request

---

## SEC-005: OWASP (4 min)

### A01: Access Control
```bash
curl -X GET http://127.0.0.1:8000/api/profile/other_user/ \
  -H "Authorization: Bearer <TOKEN>"
# ✅ Result: 403 Forbidden
```

### A03: No Raw SQL
```bash
grep -r "cursor.execute" classes-main/
# ✅ Result: No matches
```

### A05: Password Validation
```bash
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456"}'
# ✅ Result: 422 Unprocessable Entity (too weak)
```

### A07: Argon2 Hashing
```
Show: core/settings.py
PASSWORD_HASHERS = ['Argon2PasswordHasher', ...]
# ✅ Most secure algorithm
```

---

## SEC-006: Security Headers (2 min)

```
1. Go to: https://securityheaders.com
2. Paste: https://jobly.kz
3. Click: Scan
```

**What graders see**: Grade A or B+ with all headers listed

**Or with curl:**
```bash
curl -i https://jobly.kz/ | grep "Strict-Transport-Security\|Content-Security-Policy"
# ✅ Headers present
```

---

## SEC-007: Secret Scanning (1 min)

```bash
cd classes-main
pip install trufflehog
python scan_secrets.py
# ✅ Result: NO SECRETS FOUND
```

---

## SEC-008: Logging (1 min)

```bash
# Try failed login
curl -X POST http://127.0.0.1:8000/api/login/ \
  -d '{"username":"test","password":"wrong"}'

# Check logs
tail -10 classes-main/debug.log
# ✅ See: [SECURITY] FAILED_LOGIN | User: test | IP: 127.0.0.1
```

---

## 📱 Test Account Credentials

**Student User:**
```
Username: student_demo
Password: StudentPass123!
Role: Student
```

**Employer User:**
```
Username: employer_demo
Password: EmployerPass123!
Role: Employer
```

**Admin User:**
```
Username: admin
Password: AdminPass123!
Role: Admin
```

---

## 🛠️ Tools You'll Need

- [ ] Chrome/Firefox browser
- [ ] Terminal with curl installed
- [ ] VS Code or text editor
- [ ] Internet connection (for Google OAuth)
- [ ] Running Django app (local or deployed)
- [ ] Python with trufflehog installed

---

## ⏱️ Timing

- SEC-002 OAuth: 2 min
- SEC-003 RBAC: 2 min
- SEC-004 CAPTCHA: 2 min
- SEC-005 OWASP: 4 min
- SEC-006 Headers: 2 min
- SEC-007 Secrets: 1 min
- SEC-008 Logging: 1 min

**Total: 14 minutes + Q&A**

---

## 🚨 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Google OAuth fails | Check CLIENT_ID/SECRET in env |
| 403 not showing | Wrong user role, try another token |
| CAPTCHA token missing | Open DevTools BEFORE submitting |
| Headers not showing | Use HTTPS, check middleware |
| Secrets found | Update .gitignore |
| App not running | Run: `python manage.py runserver` |

---

## 📍 Key Files to Reference

```
accounts/oauth_url_handlers.py      → OAuth implementation
accounts/decorators.py               → RBAC @role_required
accounts/forms.py                    → CAPTCHA in registration
accounts/security.py                 → Access control checks
core/middleware.py                   → Security headers
core/settings.py                     → Configuration
scan_secrets.py                      → Secret scanning
debug.log                            → Security logs
```

---

## ✨ Demo Order

1. **Start with**: SEC-002 (impressive - Google auth)
2. **Then**: SEC-003 (technical - RBAC)
3. **Then**: SEC-004 (visual - DevTools)
4. **Then**: SEC-005 (comprehensive - OWASP)
5. **Then**: SEC-006 (impressive - securityheaders.com)
6. **Then**: SEC-007 (technical - trufflehog)
7. **Finally**: SEC-008 (quick - logs)

---

**Good luck! You've got this! 🎉**
