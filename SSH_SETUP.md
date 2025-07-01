# 🔐 SSH Setup for AR Sandbox RC GitHub Repository

This guide will help you set up SSH authentication for secure, password-free access to your GitHub repository.

## 🎯 **Why Use SSH?**

- 🔒 **Secure authentication** without passwords
- ⚡ **Faster operations** - no password prompts
- 🛡️ **Better security** with key-based authentication
- 🔄 **Seamless automation** for CI/CD and scripts

## 🚀 **Step-by-Step SSH Setup**

### **Step 1: Check for Existing SSH Keys**

```bash
# Check if you already have SSH keys
ls -la ~/.ssh

# Look for files like:
# id_rsa (private key)
# id_rsa.pub (public key)
# id_ed25519 (newer format private key)
# id_ed25519.pub (newer format public key)
```

### **Step 2: Generate New SSH Key (if needed)**

```bash
# Generate a new SSH key (recommended: Ed25519)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Or if your system doesn't support Ed25519:
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# When prompted:
# - Press Enter to save in default location (~/.ssh/id_ed25519)
# - Enter a secure passphrase (recommended)
# - Confirm the passphrase
```

### **Step 3: Add SSH Key to SSH Agent**

**On Windows (PowerShell):**
```powershell
# Start SSH agent
Start-Service ssh-agent

# Add your SSH key
ssh-add ~/.ssh/id_ed25519
```

**On macOS/Linux:**
```bash
# Start SSH agent
eval "$(ssh-agent -s)"

# Add your SSH key
ssh-add ~/.ssh/id_ed25519

# On macOS, also add to keychain:
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

### **Step 4: Copy Public Key**

```bash
# Copy public key to clipboard

# Windows (PowerShell):
Get-Content ~/.ssh/id_ed25519.pub | Set-Clipboard

# Windows (Git Bash):
cat ~/.ssh/id_ed25519.pub | clip

# macOS:
pbcopy < ~/.ssh/id_ed25519.pub

# Linux:
xclip -selection clipboard < ~/.ssh/id_ed25519.pub
# or
cat ~/.ssh/id_ed25519.pub
# Then manually copy the output
```

### **Step 5: Add SSH Key to GitHub**

1. **Go to GitHub Settings:**
   - Navigate to https://github.com/settings/keys
   - Or: GitHub → Profile → Settings → SSH and GPG keys

2. **Add New SSH Key:**
   - Click **"New SSH key"**
   - **Title**: `AR-Sandbox-RC-Development` (or descriptive name)
   - **Key type**: `Authentication Key`
   - **Key**: Paste your public key
   - Click **"Add SSH key"**

### **Step 6: Test SSH Connection**

```bash
# Test SSH connection to GitHub
ssh -T git@github.com

# Expected output:
# Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

## 🔄 **Configure Repository for SSH**

### **For New Repository Clone:**

```bash
# Clone using SSH (replace 'yourusername' with your GitHub username)
git clone git@github.com:yourusername/AR-Sandbox-RC.git
cd AR-Sandbox-RC
```

### **For Existing Repository (Switch from HTTPS to SSH):**

```bash
# Check current remote URL
git remote -v

# Change remote URL to SSH
git remote set-url origin git@github.com:yourusername/AR-Sandbox-RC.git

# Verify the change
git remote -v
```

## 🛠️ **SSH Configuration File (Optional)**

Create `~/.ssh/config` for easier management:

```bash
# Create/edit SSH config file
nano ~/.ssh/config
# or
code ~/.ssh/config
```

Add this configuration:

```
# GitHub configuration for AR Sandbox RC
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    
# Optional: Custom host alias
Host ar-sandbox
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

With the alias, you can clone using:
```bash
git clone ar-sandbox:yourusername/AR-Sandbox-RC.git
```

## 🔧 **Common SSH Commands for Development**

### **Daily Git Operations:**
```bash
# Push changes (no password required)
git push origin main

# Pull latest changes
git pull origin main

# Push new branch
git push -u origin feature/new-feature
```

### **SSH Key Management:**
```bash
# List loaded SSH keys
ssh-add -l

# Remove all keys from agent
ssh-add -D

# Add key with specific lifetime (1 hour)
ssh-add -t 3600 ~/.ssh/id_ed25519
```

## 🛡️ **Security Best Practices**

### **SSH Key Security:**
- ✅ **Use strong passphrases** for SSH keys
- ✅ **Use Ed25519 keys** (more secure than RSA)
- ✅ **Regularly rotate keys** (annually recommended)
- ✅ **Keep private keys secure** (never share)
- ✅ **Use different keys** for different services

### **GitHub Security:**
- ✅ **Enable 2FA** on your GitHub account
- ✅ **Review SSH keys** regularly in GitHub settings
- ✅ **Remove unused keys** from GitHub
- ✅ **Monitor account activity** for suspicious access

## 🚨 **Troubleshooting**

### **Permission Denied Error:**
```bash
# Check SSH agent is running
ssh-add -l

# Re-add your key
ssh-add ~/.ssh/id_ed25519

# Test connection with verbose output
ssh -vT git@github.com
```

### **Wrong Key Being Used:**
```bash
# Specify exact key to use
ssh -i ~/.ssh/id_ed25519 -T git@github.com

# Or update SSH config file
```

### **Passphrase Prompts:**
```bash
# On macOS, add to keychain:
ssh-add --apple-use-keychain ~/.ssh/id_ed25519

# On Windows, ensure SSH agent is running:
Start-Service ssh-agent
```

## 🔄 **Multiple GitHub Accounts**

If you have multiple GitHub accounts:

```bash
# Create separate keys
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_work -C "work@example.com"
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_personal -C "personal@example.com"

# SSH config for multiple accounts
Host github-work
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_work

Host github-personal
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_personal

# Clone with specific account
git clone git@github-work:company/AR-Sandbox-RC.git
git clone git@github-personal:yourusername/AR-Sandbox-RC.git
```

## 📱 **Mobile/Remote Development**

For development from different machines:

```bash
# Generate machine-specific keys
ssh-keygen -t ed25519 -C "laptop-ar-sandbox"
ssh-keygen -t ed25519 -C "desktop-ar-sandbox"

# Add each key to GitHub with descriptive names:
# - "AR-Sandbox-Laptop-2025"
# - "AR-Sandbox-Desktop-2025"
# - "AR-Sandbox-Server-2025"
```

## ✅ **Verification Checklist**

- [ ] SSH key generated successfully
- [ ] Public key added to GitHub account
- [ ] SSH connection test passes
- [ ] Repository remote URL uses SSH
- [ ] Can push/pull without password prompts
- [ ] SSH agent configured for automatic key loading
- [ ] Backup of SSH keys stored securely

---

**🎯 You're now ready for secure, efficient Git operations with your AR Sandbox RC repository!**

For additional help, see:
- [GitHub SSH Documentation](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [Git SSH Troubleshooting](https://docs.github.com/en/authentication/troubleshooting-ssh)
