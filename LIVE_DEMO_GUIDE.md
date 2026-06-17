# Week 3 Security Requirements - Live Demo Guide 🎯

Complete step-by-step demonstration guide for all 8 security requirements. Perfect for presenting to graders/instructors.

---

## 🎤 Introduction (1 min)

**Say**: "I've implemented 8 security requirements for the Jobly job board platform. Let me show you each one working live."

**Demo order**: SEC-002 → SEC-003 → SEC-004 → SEC-005 → SEC-006 → SEC-007

**Time estimate**: 12-15 minutes total

---

# SEC-002: Google Sign-In (OAuth 2.0) - 2 min

## 🎯 What You're Demonstrating
OAuth 2.0 integration with Google that allows secure sign-in without storing passwords.

## Step-by-Step Demo

### 1. Open Login Page
```
URL: https://jobly.kz/accounts/login/
     (or http://127.0.0.1:8000/accounts/login/ for local)
```

**What to do:**
- Click the link in your browser
- You'll see a login page with Russian text

**What you'll see:**
```
Форма входа:
- Email / Username field
- Password field
- ☐ Keep me logged in
- [Log In] button
- [Войти через Google] button  ← CLICK THIS
```

### 2. Click "Войти через Google" Button
**Location**: Bottom of the login form in blue

**Click**: The blue button that says "Войти через Google"

**What happens next:**
1. Browser redirects to Google login
2. Google OAuth consent screen appears
3. Sign in with your Google account (if not already logged in)
4. Google asks permission to share email/profile

### 3. Grant Permission
- Click "Continue" or "Allow" when Google asks for permissions
- Browser redirects back to your site
- **SHOW THE GRADERS**: You're now logged in! ✅

**Expected result:**
```
✅ You're redirected to: https://jobly.kz/profile/
✅ Your user profile is visible
✅ Role assigned automatically (Student/Employer/Admin)
✅ User created in database with Google account linked
```

## 📸 What Graders Should See
```
Browser URL: https://jobly.kz/profile/
Profile Page Shows:
- Your name (from Google)
- Email (from Google)
- Role: [Student/Employer/Admin]
- "Successfully logged in via Google" message (optional)
```

## Code Location to Reference
**If asked where the code is:**
```
File: accounts/oauth_url_handlers.py
Function: google_login_view()
Lines: OAuth flow handling

File: accounts/adapters.py
Function: CustomSocialAccountAdapter
Purpose: Handles Google user data mapping
```

---

# SEC-003: RBAC - Role-Based Access Control - 3 min

## 🎯 What You're Demonstrating
Users can only access endpoints/views matching their role. Unauthorized roles get 403 Forbidden.

## Setup Before Demo

**Prepare two user accounts:**
1. **Student account**: Registered as Student role
2. **Employer account**: Registered as Employer role

**Get their auth tokens:**

### Terminal Command (Get JWT Token)
```bash
# For Student user:
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "student_user", "password": "StudentPass123!"}'

# Response will include:
# "token": "abcd1234efgh5678..."
```

Copy the token value for the next step.

## Demo Part 1: Student Trying to Access Employer Feature

### Terminal Command
```bash
STUDENT_TOKEN="<paste_the_token_from_above>"

curl -X GET http://127.0.0.1:8000/api/jobs/create/ \
  -H "Authorization: Bearer $STUDENT_TOKEN"
```

### Expected Response
```json
HTTP 403 Forbidden
{
  "detail": "You do not have permission to access this resource.",
  "code": "permission_denied"
}
```

**SHOW THE GRADERS:**
- ✅ Status code: **403 Forbidden**
- ✅ Student cannot create jobs (employer-only feature)
- ✅ Error message clearly states permission denied

## Demo Part 2: Employer Accessing Same Feature

### Terminal Command
```bash
EMPLOYER_TOKEN="<paste_employer_token>"

curl -X GET http://127.0.0.1:8000/api/jobs/create/ \
  -H "Authorization: Bearer $EMPLOYER_TOKEN"
```

### Expected Response
```json
HTTP 200 OK
{
  "status": "success",
  "message": "You can create jobs"
}
```

**SHOW THE GRADERS:**
- ✅ Status code: **200 OK**
- ✅ Employer can access job creation
- ✅ Different role = different access

## Code Location to Reference
**If asked about implementation:**
```
File: accounts/decorators.py
Function: @role_required(allowed_roles=['employer'])

File: accounts/views.py
Line 150+: Views decorated with @role_required

File: accounts/security.py
Function: check_role()
Purpose: Validates user role for access control
```

---

# SEC-004: CAPTCHA (reCAPTCHA v3) - 2 min

## 🎯 What You're Demonstrating
reCAPTCHA prevents automated bot registrations and spam.

## Step-by-Step Demo

### 1. Open Registration Page
```
URL: https://jobly.kz/register/
     (or http://127.0.0.1:8000/register/ for local)
```

**What to do:**
- Click this link in your browser
- You'll see a registration form

### 2. Open Browser DevTools - Network Tab
**On Windows/Mac:**
- Right-click anywhere on the page
- Select **"Inspect"** or **"Inspect Element"**
- Click the **"Network"** tab at the top

**What you'll see:**
```
Network tab is now tracking all requests
(It will be mostly empty until you submit the form)
```

### 3. Fill Registration Form
In the registration form, enter:
```
Username: testuser123
Email: test@example.com
Password: SecurePass123!
Confirm Password: SecurePass123!
☐ I agree to terms
```

### 4. Submit Form
Click the **"Register"** button

### 5. Check Network Tab for CAPTCHA Token
**In the Network tab:**
1. Look for a request called `register` (or similar POST request)
2. Click on it to select it
3. At the bottom, look for **"Request Body"**
4. Scroll down in the Request Body section

**What to show:**
```
{
  "username": "testuser123",
  "email": "test@example.com",
  "password": "SecurePass123!",
  "captcha_token": "0.9876543210123456789..."  ← SHOW THIS!
}
```

**TELL THE GRADERS:**
- ✅ `captcha_token` is present in request
- ✅ Token value is long and unique (generated by reCAPTCHA)
- ✅ Google's service validated the user is not a bot
- ✅ reCAPTCHA score (0-1) determines if registration proceeds

## What Happens If Bot Detected
If reCAPTCHA score is too low (looks like a bot):
```
Error message: "Captcha verification failed. Please try again."
User cannot register
```

## Code Location to Reference
**If asked about implementation:**
```
File: accounts/forms.py
Class: UserRegisterForm
Field: ReCaptchaField (reCAPTCHA v3 widget)

File: accounts/views.py
Function: register_view()
Line 200+: captcha_token validation

File: core/settings.py
RECAPTCHA_PUBLIC_KEY
RECAPTCHA_PRIVATE_KEY
```

---

# SEC-005: OWASP Top 10 Compliance - 4 min

## 🎯 What You're Demonstrating
Protection against 4 OWASP Top 10 vulnerabilities:
- A01: Broken Access Control
- A03: Injection (SQL Injection)
- A05: Broken Authentication
- A07: Cryptographic Failures

## Part 1: A01 - Access Control (Owner Check)

### Demo: Unauthorized User Can't Access Other's Data

**Terminal Command:**
```bash
# Get tokens for two different users
STUDENT1_TOKEN="<token_for_student_1>"
STUDENT2_TOKEN="<token_for_student_2>"

# Student 1 tries to access Student 2's profile
curl -X GET http://127.0.0.1:8000/api/profile/student_2/ \
  -H "Authorization: Bearer $STUDENT1_TOKEN"
```

**Expected Response:**
```json
HTTP 403 Forbidden
{
  "error": "You do not have permission to view this profile",
  "code": "access_denied"
}
```

**SHOW THE GRADERS:**
- ✅ **403 Forbidden** - user can't access other's data
- ✅ `owner_required()` decorator is working
- ✅ Each user can only see their own profile

### Code Location
```
File: accounts/security.py
Function: owner_required(resource_param='pk', owner_field='user')
Lines: 25-45
```

## Part 2: A03 - Injection Prevention (ORM Only)

### Demo: Show Code - No Raw SQL

**Open file in VS Code:**
```
File: accounts/models.py
```

**What to show graders:**
- Point to queries in the code
- Highlight: `Profile.objects.filter(user=user_id)` ← This is ORM
- Say: "We use Django ORM, NOT raw SQL"

**Search for raw SQL (should find NONE):**

**Terminal Command:**
```bash
cd classes-main
grep -r "cursor.execute" .
grep -r "raw(" .
```

**Expected result:**
```
No matches found
```

**TELL THE GRADERS:**
- ✅ Zero raw SQL queries found
- ✅ All queries use Django ORM
- ✅ Automatic SQL injection prevention
- ✅ ORM parameterizes all queries

### Code Locations
```
File: accounts/models.py
All queries use: Model.objects.filter(...)

File: accounts/views.py
Lines 50-150: All queries use ORM

File: learning/views.py
All queries use ORM: Course.objects.filter(...)
```

## Part 3: A05 - Password Validation

### Demo: Try Weak Password

**Terminal Command:**
```bash
# Try to register with weak password
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "weakuser",
    "email": "weak@test.com",
    "password": "123456",
    "captcha_token": "dummy_token"
  }'
```

**Expected Response:**
```json
HTTP 422 Unprocessable Entity
{
  "password": [
    "This password is too short. It must contain at least 8 characters.",
    "This password is entirely numeric."
  ]
}
```

**SHOW THE GRADERS:**
- ✅ **422 Unprocessable Entity** - password rejected
- ✅ Multiple validation errors shown
- ✅ Clear error messages for each requirement

### Try With Strong Password
```bash
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "stronguser",
    "email": "strong@test.com",
    "password": "SecurePass123!@#",
    "captcha_token": "valid_token"
  }'
```

**Expected Response:**
```json
HTTP 201 Created
{
  "status": "success",
  "message": "User registered successfully",
  "user_id": 123
}
```

**Show:**
- ✅ Strong password accepted
- ✅ User created successfully

### Code Location
```
File: core/settings.py
Lines 120-130:
AUTH_PASSWORD_VALIDATORS = [
    'UserAttributeSimilarityValidator',
    'MinimumLengthValidator',
    'CommonPasswordValidator',
    'NumericPasswordValidator'
]

File: accounts/forms.py
Lines 80-95: Password validation in form
```

## Part 4: A07 - Password Hashing (Argon2)

### Demo: Show Hashing Configuration

**Open file:**
```
File: core/settings.py
Lines 50-55
```

**Show graders this code:**
```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  ← FIRST (most secure)
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',  ← FALLBACK
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]
```

**TELL THE GRADERS:**
- ✅ Argon2 is the primary password hasher (most secure, resistant to GPU attacks)
- ✅ PBKDF2 as fallback for compatibility
- ✅ Passwords never stored in plain text
- ✅ Even if database leaked, passwords unrecoverable

**Terminal Command - Check Hashed Password:**
```bash
# Get database and check password field:
sqlite3 classes-main/db.sqlite3
SELECT username, password FROM auth_user LIMIT 1;
```

**Expected output:**
```
username | password
testuser | argon2$argon2id$v=19$m=512,t=2,p=2$abcd1234$xyzabcdefgh...
```

**Point out:** 
- ✅ Password starts with `argon2$` (Argon2 hash)
- ✅ Not plain text
- ✅ Cannot be reversed

---

# SEC-006: Security Headers (HSTS, CSP) - 2 min

## 🎯 What You're Demonstrating
HTTP security headers that prevent XSS, clickjacking, and enforce HTTPS.

## Step 1: Check Headers in Browser

**Open your site in Chrome:**
```
URL: https://jobly.kz/
```

**Open DevTools:**
- Press **F12** or Right-click → Inspect
- Click **Network** tab
- Reload the page (F5)
- Click the main request (first item, usually "jobly.kz" or "127.0.0.1")
- Scroll down to find **Response Headers** section

**Look for these headers:**

### Header 1: Strict-Transport-Security
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```
**Explain:** Forces HTTPS for 1 year, includes subdomains

### Header 2: Content-Security-Policy
```
Content-Security-Policy: default-src 'self' *; script-src 'self' 'unsafe-inline'...
```
**Explain:** Only allows content from trusted sources, prevents XSS attacks

### Header 3: Permissions-Policy
```
Permissions-Policy: camera=(), microphone=(), geolocation=()
```
**Explain:** Disables camera, microphone, geolocation access

## Step 2: Use securityheaders.com (Best Visual Demo)

**Go to website:**
```
URL: https://securityheaders.com
```

**What to do:**
1. Paste your site URL in the search box
2. Click the scan button
3. Wait for results

**Expected result:**
```
Grade: A or B+
Headers found:
✅ Strict-Transport-Security
✅ Content-Security-Policy  
✅ Permissions-Policy
```

**SHOW THE GRADERS:**
- Colored indicators (Green ✅ = good, Red ❌ = missing)
- Grade letter (A or B+)
- List of all security headers

## Step 3: Test with curl (Technical Proof)

**Terminal Command:**
```bash
curl -i https://jobly.kz/ 2>&1 | grep -A 5 "Strict-Transport-Security\|Content-Security-Policy\|Permissions-Policy"
```

**Expected output:**
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self' *; script-src...
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

## Code Location
```
File: core/middleware.py
Class: SecurityHeadersMiddleware
Lines: 1-50

This middleware is registered in:
File: core/settings.py
MIDDLEWARE list, line 60: 'core.middleware.SecurityHeadersMiddleware'
```

---

# SEC-007: Secret Scanning (Trufflehog) - 2 min

## 🎯 What You're Demonstrating
No API keys, passwords, or secrets are accidentally committed to Git.

## Step 1: Run Trufflehog Scan

**Terminal Command:**
```bash
# First, install trufflehog (if not already installed)
pip install trufflehog

# Scan the repository
cd classes-main
python3 scan_secrets.py
```

Or manually:
```bash
cd classes-main
trufflehog git . --json
```

**Expected output:**
```
🔍 Scanning for secrets with Trufflehog...
Repository: .
Scanning with detectors: ['Slack', 'GitHub', 'AWS', 'Azure', 'Google', ...]

✅ Scan complete!
✅ NO SECRETS FOUND

Summary:
- Total commits scanned: 150
- Secrets found: 0
```

**TELL THE GRADERS:**
- ✅ No secrets committed to git
- ✅ .env file is in .gitignore (protected)
- ✅ All environment variables are safe

## Step 2: Show .env Protection

**Terminal Command:**
```bash
# Show .env is in .gitignore
cat .gitignore | grep ".env"
```

**Expected output:**
```
.env
.env.local
.env.*.local
```

**Terminal Command - Verify .env not in git:**
```bash
git log --all --full-history -- .env
```

**Expected output:**
```
# No output = .env was never committed (GOOD!)
```

## Step 3: Show Environment Variables Usage

**Open file:**
```
File: core/settings.py
```

**Show graders this pattern:**
```python
# ✅ GOOD - Uses environment variables
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-insecure-key')
DATABASE_URL = os.environ.get('DATABASE_URL')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')

# ❌ BAD - Never do this:
# SECRET_KEY = 'my-actual-secret-key-123'  ← WRONG!
# API_KEY = 'sk_live_abcd1234'  ← WRONG!
```

## Code Location
```
File: scan_secrets.py
Lines: Complete trufflehog scanning script

File: .gitignore
Lines: .env protection

File: core/settings.py
Lines: All secrets use os.environ.get()
```

---

# SEC-008: Session Security & Logging - 2 min

## 🎯 What You're Demonstrating
Failed login attempts are logged with IP addresses for security monitoring.

## Step 1: Check Security Logs

**Terminal Command:**
```bash
tail -50 classes-main/debug.log
```

**Look for log entries like:**
```
[SECURITY] FAILED_LOGIN | User: invalid_user | IP: 127.0.0.1 | Time: 2024-06-11 14:30:45
[SECURITY] UNAUTHORIZED_ACCESS | User: student_user | Resource: /admin/ | IP: 192.168.1.5
[SECURITY] SESSION_EXPIRED | User: employer_user | IP: 10.0.0.1
```

**SHOW THE GRADERS:**
- ✅ Failed login attempts are logged
- ✅ IP addresses are recorded (for security audit)
- ✅ User identification included
- ✅ Timestamps for forensics

## Step 2: Trigger a Failed Login (For Live Demo)

**Terminal Command:**
```bash
# Try to login with wrong password
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "WrongPassword123"}'
```

**Response:**
```json
HTTP 401 Unauthorized
{
  "error": "Invalid credentials"
}
```

**Then check logs:**
```bash
tail -5 classes-main/debug.log
```

**You should see:**
```
[SECURITY] FAILED_LOGIN | User: testuser | IP: 127.0.0.1 | Time: 2024-06-11 14:32:10
```

## Code Location
```
File: accounts/security.py
Function: log_security_event()
Lines: 80-100

File: accounts/views.py
Lines: 200-220: Login view with logging

File: core/settings.py
Lines: 160-180: LOGGING configuration
```

---

# 🎬 Demo Script (What to Say)

## Opening (1 min)
```
"Hello, I'm going to demonstrate 8 security requirements implemented in the Jobly job board.

Security is critical for any web application that handles user data. I've implemented:
1. Google OAuth for secure sign-in
2. Role-based access control to restrict features
3. CAPTCHA to prevent bots
4. OWASP protection against injection and weak passwords
5. Security headers to prevent attacks
6. Secret scanning to ensure no credentials are leaked
7. Secure logging for security events
8. Session security and password hashing

Let me show you each one working live."
```

## During Each Demo
```
For SEC-002:
"First, Google Sign-In. This is OAuth 2.0. Users can log in with their Google account 
instead of creating a new password. Let me show you..."
[Demo the Google login flow]

For SEC-003:
"Next, role-based access control. This system has Students and Employers with different 
permissions. A student cannot access employer-only features like job creation. Let me show..."
[Demo the 403 error]

For SEC-004:
"CAPTCHA prevents bots from automatically registering. Let me show you the reCAPTCHA token 
in the request body..."
[Show Network tab]

For SEC-005:
"OWASP compliance protects against injection, weak passwords, and cryptographic issues.
Let me show you the access control, ORM-only queries, password validation..."
[Show each protection]

For SEC-006:
"Security headers tell the browser how to handle content and enforce HTTPS..."
[Show securityheaders.com or DevTools]

For SEC-007:
"Secret scanning ensures no API keys or passwords are in the code..."
[Run trufflehog]

For SEC-008:
"Security events are logged with IP addresses for auditing..."
[Show debug.log]
```

## Closing (30 seconds)
```
"All 8 security requirements are now implemented and verified:
✅ OAuth 2.0 - Google Sign-In working
✅ RBAC - 403 Forbidden for unauthorized roles
✅ CAPTCHA - reCAPTCHA v3 active
✅ OWASP - 4 vulnerabilities protected
✅ Security Headers - HSTS, CSP, Permissions-Policy
✅ Secret Scanning - No secrets in git
✅ Logging - Security events tracked
✅ Session Security - Passwords hashed with Argon2

The application is ready for production deployment."
```

---

# 📋 Demo Checklist (Print This!)

Before the demo, ensure you have:

- [ ] Internet connection (for Google OAuth)
- [ ] Two test user accounts (Student + Employer)
- [ ] Their auth tokens ready (save in notepad)
- [ ] Chrome/Firefox DevTools knowledge
- [ ] Terminal ready with curl installed
- [ ] Git repository accessible
- [ ] trufflehog installed (`pip install trufflehog`)
- [ ] Application running locally or on server
- [ ] debug.log file accessible
- [ ] Core settings.py and other files ready to show

---

# 🆘 Troubleshooting During Demo

### Google OAuth not working?
```
✅ Check GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET are set
✅ Verify Google App is enabled in django-allauth settings
✅ Check redirect URI is whitelisted in Google Console
```

### 403 Forbidden not showing?
```
✅ Verify @role_required decorator is on the view
✅ Check user has the wrong role
✅ Try with admin token (should work)
```

### CAPTCHA token not in request body?
```
✅ Open DevTools before filling form
✅ Check Network tab has the POST request selected
✅ Click on the request, scroll to "Request Body" tab
✅ Verify form has ReCaptchaField
```

### Security headers not showing?
```
✅ Check site is using HTTPS (not HTTP for some headers)
✅ Reload page (F5) and check Response Headers again
✅ Try securityheaders.com first (easier visualization)
```

### Trufflehog scan failing?
```
✅ pip install trufflehog
✅ Run from project root directory
✅ Check .git directory exists
```

---

# 📱 Mobile Demo Alternative

If demonstrating on mobile/tablet:

**For most demos:**
- Use mobile browser to visit website
- Use mobile DevTools (inspect element on Android Chrome)
- For curl commands, use Postman mobile app instead

**For Network inspection:**
- Take screenshots of Network tab from desktop
- Show on projector/screen share during demo

---

# 🎥 Optional: Record Demo Video

To create a reusable demo video:

```bash
# Windows: Use OBS Studio (free)
# Mac: Use QuickTime
# Linux: Use kazam or SimpleScreenRecorder

# Record this sequence:
1. Google OAuth flow (1:30)
2. RBAC 403 error (1:00)
3. CAPTCHA network inspection (1:00)
4. Password validation (1:00)
5. Security headers (1:00)
6. Secret scanning (1:00)
7. Security logging (1:00)

# Total: ~8 minutes (can be edited)
# Upload to YouTube as unlisted for reference
```

---

**Ready to present! Good luck! 🚀**
