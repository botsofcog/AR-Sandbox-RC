# 🔐 SSH Quick Reference - AR Sandbox RC

## ⚡ **Quick Setup Commands**

```bash
# 1. Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. Add to SSH agent
ssh-add ~/.ssh/id_ed25519

# 3. Copy public key (Windows PowerShell)
Get-Content ~/.ssh/id_ed25519.pub | Set-Clipboard

# 3. Copy public key (macOS)
pbcopy < ~/.ssh/id_ed25519.pub

# 3. Copy public key (Linux)
xclip -selection clipboard < ~/.ssh/id_ed25519.pub

# 4. Test GitHub connection
ssh -T git@github.com

# 5. Clone AR Sandbox RC
git clone git@github.com:yourusername/AR-Sandbox-RC.git
```

## 🔄 **Daily Git Commands**

```bash
# Push changes (no password needed)
git push origin main

# Pull latest changes
git pull origin main

# Create and push new branch
git checkout -b feature/kinect-improvements
git push -u origin feature/kinect-improvements

# Switch remote from HTTPS to SSH
git remote set-url origin git@github.com:yourusername/AR-Sandbox-RC.git
```

## 🛠️ **SSH Management**

```bash
# List loaded SSH keys
ssh-add -l

# Remove all keys from agent
ssh-add -D

# Add key with 1-hour timeout
ssh-add -t 3600 ~/.ssh/id_ed25519

# Start SSH agent (Windows)
Start-Service ssh-agent

# Start SSH agent (macOS/Linux)
eval "$(ssh-agent -s)"
```

## 🚨 **Troubleshooting**

```bash
# Permission denied? Re-add key:
ssh-add ~/.ssh/id_ed25519

# Test with verbose output:
ssh -vT git@github.com

# Use specific key:
ssh -i ~/.ssh/id_ed25519 -T git@github.com

# Check SSH config:
cat ~/.ssh/config
```

## 📱 **Multiple Accounts**

```bash
# SSH config for work/personal accounts
# File: ~/.ssh/config

Host github-work
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_work

Host github-personal
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_personal

# Clone with specific account:
git clone git@github-work:company/AR-Sandbox-RC.git
git clone git@github-personal:yourusername/AR-Sandbox-RC.git
```

## ✅ **Verification Checklist**

- [ ] SSH key generated: `ls ~/.ssh/id_ed25519*`
- [ ] Key added to agent: `ssh-add -l`
- [ ] Public key added to GitHub
- [ ] Connection test passes: `ssh -T git@github.com`
- [ ] Repository uses SSH URL: `git remote -v`
- [ ] Can push without password: `git push`

---

**🎯 For complete setup instructions, see [SSH_SETUP.md](SSH_SETUP.md)**
