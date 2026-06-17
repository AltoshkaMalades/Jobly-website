# 🚀 Demo Preparation Checklist

**Use this checklist 1 day before your presentation!**

---

## ✅ 24 Hours Before Demo

### Environment Setup
- [ ] Application running without errors
- [ ] Test accounts created (Student, Employer, Admin)
- [ ] All test accounts can log in
- [ ] Google OAuth credentials set up
- [ ] Database has test data

### Documentation Ready
- [ ] LIVE_DEMO_GUIDE.md printed or on tablet
- [ ] DEMO_QUICK_REFERENCE.md printed
- [ ] Troubleshooting tips written down
- [ ] URLs written on paper (don't rely on memory!)

### Tools Installed
- [ ] Python 3.13+ installed
- [ ] Git installed
- [ ] curl installed (comes with Windows 10+)
- [ ] Chrome/Firefox browser up to date
- [ ] VS Code or IDE ready

---

## ✅ 1 Hour Before Demo

### Test Each Feature

#### SEC-002: Google OAuth
```bash
✅ Visit: https://jobly.kz/accounts/login/
✅ Try Google login
✅ Verify redirect to profile page
✅ Log out and repeat (ensure works twice)
```

#### SEC-003: RBAC Roles
```bash
✅ Get Student token (save to file)
✅ Get Employer token (save to file)
✅ Test: Student accessing /api/jobs/create/
✅ Verify: 403 Forbidden response
✅ Test: Employer accessing same endpoint
✅ Verify: 200 OK response
```

#### SEC-004: CAPTCHA
```bash
✅ Open browser DevTools (F12)
✅ Go to /register/
✅ Open Network tab
✅ Submit registration
✅ Verify: captcha_token in request body
```

#### SEC-005: OWASP
```bash
✅ Check git for raw SQL: grep -r "cursor.execute"
✅ Try weak password (123456)
✅ Verify: 422 Unprocessable Entity
✅ Try strong password
✅ Verify: 201 Created success
✅ Show: Argon2 in settings.py
```

#### SEC-006: Security Headers
```bash
✅ Go to: https://securityheaders.com
✅ Test your site URL
✅ Verify: Grade A or B+
✅ Verify: 3+ headers present
```

#### SEC-007: Secret Scanning
```bash
✅ Install trufflehog: pip install trufflehog
✅ Run: python scan_secrets.py
✅ Verify: "NO SECRETS FOUND"
```

#### SEC-008: Logging
```bash
✅ Trigger failed login attempt
✅ Check: debug.log file exists
✅ Verify: Security log entries present
```

---

## ✅ 15 Minutes Before Demo

### Final Checks
- [ ] Browser tabs open and ready:
  - Tab 1: Application home page
  - Tab 2: securityheaders.com
  - Tab 3: Google OAuth login page
  
- [ ] Terminal ready:
  - Logged into project directory
  - Python virtual environment activated
  - Ready to run curl commands

- [ ] VS Code ready:
  - Open files for reference ready
  - Terminal in VS Code ready

- [ ] Backup plan:
  - Screenshot of each demo step saved
  - Pre-recorded video available (if internet fails)
  - Printed documentation available

---

## 📋 Demo Setup Commands

**Run these 30 minutes before to ensure everything works:**

```bash
# 1. Navigate to project
cd "c:\Users\Altyn\Documents\GitHub\Simulator backend\-\classes-main"

# 2. Activate virtual environment
.venv\Scripts\activate

# 3. Start application
python manage.py runserver 127.0.0.1:8000

# 4. In another terminal, verify it's running
curl http://127.0.0.1:8000/
# Should get HTML response (not error)

# 5. Verify database has test users
python manage.py shell
# >>> from django.contrib.auth.models import User
# >>> User.objects.all()
# Should show test users
# >>> exit()

# 6. Test API endpoint
curl -X GET http://127.0.0.1:8000/api/health/

# 7. Install trufflehog
pip install trufflehog

# 8. Test secret scanning
python scan_secrets.py
```

---

## 🖥️ Optimal Setup for Live Demo

### Screen Layout
```
Monitor 1 (Primary - for projector):
├─ Chrome browser (full screen)
│  └─ Application running
└─ Firefox (backup)

Monitor 2 (Your screen):
├─ VS Code left half
│  └─ Code ready to show
├─ Terminal right half
│  └─ Ready to run curl commands
├─ DEMO_QUICK_REFERENCE.md (visible)
└─ Notepad with credentials
```

### Keyboard Shortcuts to Memorize
```
F12            → Open DevTools
Ctrl+Shift+C   → Inspect element
F5             → Refresh page
Ctrl+K         → Clear terminal
Alt+Tab        → Switch between applications
```

---

## 🎤 What to Say While Demo

### Opening
```
"I'll now demonstrate all 8 security requirements implemented in the Jobly application.
Each one is a real feature that protects users and prevents attacks.
Let me show you each one working live."
```

### For Each Feature
```
"This is [SEC-X]: [Feature Name]

What it does: [1 sentence explanation]

How it works: [Show the demo]

Why it matters: [Security benefit]

As you can see: [Point out what graders should notice]"
```

### If Something Goes Wrong
```
"Let me show you this a different way..."
[Switch to backup method]

OR

"I've already tested this and it works - let me move to the next demo and we can 
debug this afterward if needed."
[Continue with next feature]
```

### Closing
```
"All 8 security requirements are now implemented and verified:
✅ OAuth 2.0 working
✅ RBAC enforced
✅ CAPTCHA active
✅ OWASP protected
✅ Headers secure
✅ Secrets safe
✅ Events logged

The application is production-ready and secure."
```

---

## 🆘 Troubleshooting During Demo

### Application Won't Start
```bash
# Kill any existing processes
lsof -i :8000
kill -9 <PID>

# Try running again
python manage.py runserver
```

### Curl Commands Failing
```bash
# Check if server is running
curl http://127.0.0.1:8000/

# If not, start it in another terminal:
python manage.py runserver
```

### Google OAuth Not Working
```
Solution 1: Check credentials in settings.py
Solution 2: Use pre-recorded video instead
Solution 3: Skip to next demo, come back if time
```

### DevTools Network Tab Empty
```bash
# 1. Make sure DevTools is open BEFORE form submit
# 2. Click on Network tab
# 3. Make sure "Preserve logs" is checked
# 4. Submit form
# 5. Look for POST request
```

### Secret Scanning Errors
```bash
# Make sure in correct directory with .git
cd classes-main
cd ..

# Run from root of repository
python scan_secrets.py

# Or manually:
cd classes-main
trufflehog git . --json
```

---

## 📸 Screenshot Locations (Backup)

If live demo fails, you have screenshots:

```
/images/
├─ google-oauth-success.png
├─ rbac-403-error.png
├─ captcha-token-network.png
├─ password-validation-422.png
├─ security-headers-grade-a.png
├─ trufflehog-no-secrets.png
└─ security-logs.txt
```

---

## ✨ Pro Tips

1. **Practice the demo twice** before presenting
   - First time: follow the guide completely
   - Second time: practice the verbal explanation

2. **Prepare backup explanations**
   - If live demo fails, explain what would happen
   - Show code instead of live functionality

3. **Have test data ready**
   - Pre-created user accounts with known passwords
   - Pre-captured network requests
   - Saved API responses

4. **Keep it simple**
   - Don't over-explain technical details
   - Focus on "what" not "how"
   - Let the visual demo speak for itself

5. **Stay calm**
   - Technology sometimes fails - that's normal
   - Graders understand
   - Have backup plan

6. **Watch the time**
   - 14 minutes for demo + 6 minutes for questions
   - If running over, skip SEC-008 (least important)
   - Have a "quick summary" version ready

---

## 🎯 Success Criteria

**After your demo, graders should understand:**

- ✅ What each security feature does
- ✅ How to verify it's working
- ✅ Why it's important
- ✅ That all 8 requirements are implemented
- ✅ That application is production-ready

---

## 📞 Emergency Contacts

If something goes wrong:

1. **Application won't start**: 
   - Check: Database connection, Python version, dependencies
   - Fix: `pip install -r requirements.txt`

2. **Google OAuth fails**:
   - Have video backup
   - Explain OAuth flow verbally

3. **Internet connection down**:
   - Use local `http://127.0.0.1:8000` instead of `https://jobly.kz`
   - Run `python manage.py runserver`

4. **Forgot password for test account**:
   - Create new test user: `python manage.py createsuperuser`
   - Or: Reset password in Django admin

---

## 🚀 You're Ready!

You have:
- ✅ 8 security features implemented
- ✅ Comprehensive demo guides
- ✅ Quick reference cards
- ✅ Troubleshooting solutions
- ✅ Backup plans

**Go present with confidence!** 🎉

---

**Last Updated**: 2024-06-11
**Presenter**: [Your Name]
**Time Prepared**: [Time Started]
