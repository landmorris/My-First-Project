# GitHub Personal Access Token Setup for PythonAnywhere

## Why You Need This

GitHub no longer accepts password authentication for Git operations. You need a **Personal Access Token (PAT)** to clone private repositories.

**Error you're seeing:**
```
remote: Invalid username or token. Password authentication is not supported for Git operations.
fatal: Authentication failed
```

---

## Step-by-Step: Create Your Token (5 minutes)

### 1. Go to GitHub Settings

**Option A - Direct Link:**
Visit: https://github.com/settings/tokens/new

**Option B - Navigate Manually:**
1. Go to GitHub.com and log in
2. Click your profile picture (top-right)
3. Click **Settings**
4. Scroll down on left sidebar
5. Click **Developer settings** (near bottom)
6. Click **Personal access tokens**
7. Click **Tokens (classic)**
8. Click **Generate new token** → **Generate new token (classic)**

---

### 2. Configure Your Token

Fill out the form:

**Note (Description):**
```
PythonAnywhere Deployment Token
```

**Expiration:**
- Choose: `90 days` (or longer if you prefer)

**Select Scopes (Permissions):**
- ✅ Check **`repo`** (Full control of private repositories)
  - This will automatically check all sub-items under `repo`

**That's it!** You only need the `repo` scope for cloning and pulling.

---

### 3. Generate and Copy Token

1. Scroll to bottom and click **Generate token** (green button)
2. **IMPORTANT:** GitHub will show your token **ONLY ONCE**
3. **Copy the token immediately** - it looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
4. **Save it securely** - You'll need it for deployment

**⚠️ WARNING:** Once you leave this page, you can't see the token again. If you lose it, you'll need to create a new one.

---

## How to Use Your Token on PythonAnywhere

### Method 1: Clone with Token in URL (Easiest)

In PythonAnywhere Bash console:

```bash
cd ~
git clone https://YOUR_TOKEN@github.com/landmorris/My-First-Project.git
cd My-First-Project
git checkout claude/django-dealer-monitor-app-011CUoLqGfGBrc4VsFsW1vAP
cd seca_monitor
```

**Replace `YOUR_TOKEN`** with your actual token.

**Example:**
```bash
git clone https://ghp_abc123xyz789@github.com/landmorris/My-First-Project.git
```

---

### Method 2: Let Git Prompt You

If you run the normal clone command:
```bash
git clone https://github.com/landmorris/My-First-Project.git
```

Git will prompt:
```
Username: [enter your GitHub username]
Password: [paste your TOKEN here, not your GitHub password]
```

**⚠️ Important:** When prompted for "Password", paste your **TOKEN**, not your GitHub password!

---

### Method 3: Use Updated Deployment Script

The updated deployment script will prompt you for your token and handle authentication automatically:

```bash
cd ~
curl -o deploy_pythonanywhere.sh https://raw.githubusercontent.com/landmorris/My-First-Project/claude/django-dealer-monitor-app-011CUoLqGfGBrc4VsFsW1vAP/seca_monitor/deploy_pythonanywhere.sh
bash deploy_pythonanywhere.sh
```

---

## Quick Reference Commands

### Clone with Token:
```bash
cd ~
git clone https://YOUR_GITHUB_TOKEN@github.com/landmorris/My-First-Project.git
cd My-First-Project
git checkout claude/django-dealer-monitor-app-011CUoLqGfGBrc4VsFsW1vAP
cd seca_monitor
```

### Future Git Operations:
Once cloned with token, you can pull updates:
```bash
cd ~/My-First-Project
git pull origin claude/django-dealer-monitor-app-011CUoLqGfGBrc4VsFsW1vAP
```

Git will remember your credentials for future operations in this repository.

---

## Troubleshooting

### "Invalid username or token"
- Make sure you copied the entire token (starts with `ghp_`)
- Token must have `repo` scope selected
- Check token hasn't expired

### "Authentication failed"
- Don't use your GitHub password - use the token
- Make sure token is in URL: `https://TOKEN@github.com/...`
- No spaces or extra characters in token

### "Repository not found"
- Make sure you have access to the repository
- Check the repository URL is correct
- Verify token has `repo` scope

### Token Expired
- Go back to GitHub Settings → Personal Access Tokens
- Generate a new token with same settings
- Use new token for git operations

---

## Security Best Practices

### ✅ DO:
- Store token in a password manager
- Use descriptive token names
- Set reasonable expiration dates
- Revoke tokens you're no longer using
- Create separate tokens for different purposes

### ❌ DON'T:
- Commit tokens to Git repositories
- Share tokens publicly
- Use tokens in CI/CD logs
- Leave tokens in command history (use environment variables)

---

## Alternative: SSH Keys (More Secure)

If you prefer SSH authentication instead of tokens:

### 1. Generate SSH Key on PythonAnywhere:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub
```

### 2. Add to GitHub:
1. Copy the output from `cat` command
2. Go to GitHub Settings → SSH and GPG keys
3. Click "New SSH key"
4. Paste key and save

### 3. Clone with SSH:
```bash
git clone git@github.com:landmorris/My-First-Project.git
```

**Note:** PythonAnywhere may have SSH restrictions on free/hacker plans. Token method is more reliable.

---

## Summary

**Fastest Solution:**
1. Create token: https://github.com/settings/tokens/new
2. Select `repo` scope, generate, copy token
3. Clone: `git clone https://YOUR_TOKEN@github.com/landmorris/My-First-Project.git`
4. Continue with deployment

**Time Required:** 5 minutes
**Difficulty:** Easy

---

**Need Help?**
- GitHub Token Documentation: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
- If you have questions, check the deployment walkthrough or ask for help!
