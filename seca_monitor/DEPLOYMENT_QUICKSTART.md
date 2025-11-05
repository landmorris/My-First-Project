# PythonAnywhere Deployment - Quick Reference Card

**⏱️ Total Time: 15-20 minutes**

---

## 🚀 Four-Step Deployment

### STEP 0: Create GitHub Token (3 min) - **REQUIRED**
GitHub requires a Personal Access Token (PAT) for cloning repositories.

**Quick Setup:**
1. Visit: https://github.com/settings/tokens/new
2. **Note:** `PythonAnywhere Deployment`
3. **Expiration:** 90 days (or longer)
4. **Select scopes:** ✅ `repo` (Full control of private repositories)
5. Click **Generate token**
6. **Copy token immediately** (starts with `ghp_`)
7. **Save it securely** - you'll need it in Step 2

📘 **Detailed Instructions:** See GITHUB_TOKEN_SETUP.md

### STEP 1: Create Database (2 min)
1. Go to **Databases** tab → MySQL section
2. Create database: `seca_monitor`
3. Set MySQL password → **SAVE THIS PASSWORD**

### STEP 2: Run Script (10 min)
1. Open **Bash** console
2. Run ONE command:
```bash
curl -sSL https://raw.githubusercontent.com/landmorris/My-First-Project/claude/django-dealer-monitor-app-011CUoLqGfGBrc4VsFsW1vAP/seca_monitor/deploy_pythonanywhere.sh | bash
```
3. Answer prompts:
   - Confirm username: `y`
   - Enter DB password: `[your password from Step 1]`
   - **Enter GitHub token: `[paste token from Step 0]`**
   - Repo URL: `[press Enter]`
   - Branch: `[press Enter]`
   - Confirm: `y`
   - Create superuser when prompted

### STEP 3: Configure Web App (5 min)
1. Go to **Web** tab
2. **WSGI File:**
   - Click WSGI configuration file link
   - Delete all content
   - Run in console: `cat ~/My-First-Project/seca_monitor/config/pythonanywhere_wsgi.py`
   - Copy output and paste into WSGI file
   - Save
3. **Virtualenv:** `/home/yourusername/My-First-Project/seca_monitor/venv`
4. **Static Files:**
   - URL: `/static/`
   - Directory: `/home/yourusername/My-First-Project/seca_monitor/staticfiles`
5. Click green **Reload** button

---

## ✅ Test Your Site

Visit: `https://yourusername.pythonanywhere.com`

**Login:**
- Dashboard Password: `Archer`
- Admin URL: `/admin/`
- Admin Username: (your superuser)

---

## 🐛 Quick Fixes

**502 Error?**
- Check WSGI file is correct
- Verify virtualenv path
- Check error log on Web tab

**No CSS?**
- Verify static files mapping
- Reload web app

**Database error?**
- Check .env file: `cat ~/My-First-Project/seca_monitor/.env`
- Verify password is correct

---

## 📋 Information You'll Need

**Before Starting:**
- GitHub Personal Access Token (from Step 0): `[write it here]`

**During Deployment:**
- PythonAnywhere username: `yourusername`
- MySQL password: `[write it here]`
- Superuser username: `[write it here]`
- Superuser password: `[write it here]`

**After Deployment:**
- Site URL: `https://yourusername.pythonanywhere.com`
- Dashboard password: `Archer`

---

## 🔑 Key Paths (replace `yourusername`)

```
Project: /home/yourusername/My-First-Project/seca_monitor
Virtualenv: /home/yourusername/My-First-Project/seca_monitor/venv
Static: /home/yourusername/My-First-Project/seca_monitor/staticfiles
WSGI: ~/My-First-Project/seca_monitor/config/pythonanywhere_wsgi.py
```

---

## 📞 Help

- Error logs: Web tab → Error log link
- Forums: https://www.pythonanywhere.com/forums/
- Email: help@pythonanywhere.com

---

**💡 Pro Tip:** Keep this card open while deploying!
