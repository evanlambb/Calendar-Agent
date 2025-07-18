# 🔐 Credential Management - Best Practices

## 🎯 **Solution Summary**

**Problem**: After reorganizing the project, Google Calendar credentials couldn't be found because the code was looking in the wrong directory.

**Solution**: Implemented robust, absolute path handling that works from any directory.

---

## 🔧 **What We Fixed**

### **Before (❌ Problematic)**
```python
# tools.py had hardcoded relative paths
if os.path.exists("token.json"):  # Only works from project root
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

flow = InstalledAppFlow.from_client_secrets_file(
    "credentials.json", SCOPES  # Only works from project root
)
```

### **After (✅ Robust)**
```python
# tools.py now uses absolute paths that work from anywhere
credentials_path = ensure_credentials_exist()  # Absolute path + validation
token_path = get_token_path()  # Absolute path

if os.path.exists(token_path):
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)

flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
```

---

## 📁 **File Structure for Credentials**

```
Calendar-Agent/                    # 📁 Project Root
├── credentials.json              # 🔑 Google API credentials (from Google Cloud Console)
├── token.json                    # 🎫 OAuth tokens (auto-generated)
├── .env                          # 🔧 Environment variables
├── .gitignore                    # 🚫 MUST include credentials files
│
├── backend/                      # 🐍 Python backend
│   ├── tools.py                 # ✅ Uses absolute paths now
│   ├── utils.py                 # 🛠️ Path utilities (NEW)
│   └── config.py                # ⚙️ Configuration management
│
└── docs/
    └── CREDENTIAL_SETUP.md       # 📚 This guide
```

---

## 🛠️ **New Utility Functions**

### **backend/utils.py** (NEW)
```python
def get_project_root():
    """Find project root from any subdirectory"""
    
def get_credentials_path():
    """Absolute path to credentials.json"""
    
def get_token_path():
    """Absolute path to token.json"""
    
def ensure_credentials_exist():
    """Check if credentials exist, show helpful error if not"""
```

### **Benefits:**
- ✅ **Works from any directory** (backend/, tests/, root, etc.)
- ✅ **Helpful error messages** if credentials are missing
- ✅ **Centralized path management** 
- ✅ **Uses configuration system** (config.py)

---

## 🚀 **Setup Instructions**

### **1. Download Google Calendar Credentials**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select your project
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials
5. Download as `credentials.json`

### **2. Place Credentials in Project Root**
```bash
# Make sure credentials.json is in project root
Calendar-Agent/
├── credentials.json              # 🔑 Place here (not in backend/)
└── backend/
    └── agent.py
```

### **3. Update .gitignore (CRITICAL)**
```bash
# Add to .gitignore to avoid committing secrets
credentials.json
token.json
.env
*.json
!package.json
```

### **4. Test the Setup**
```bash
cd backend
python -c "from utils import get_credentials_path; print('✅ Credentials found at:', get_credentials_path())"
```

---

## 🔒 **Security Best Practices**

### **✅ DO**
- Keep `credentials.json` in project root
- Add credentials files to `.gitignore`
- Use environment variables for API keys
- Use absolute paths in code
- Regular credential rotation

### **❌ DON'T**
- Commit credentials to git
- Hardcode paths in multiple files
- Store credentials in subdirectories
- Share credentials in plain text
- Use relative paths for critical files

---

## 🧪 **Testing Your Setup**

### **Test from backend/ directory:**
```bash
cd backend
python agent.py
# Should work without credential errors
```

### **Test from tests/ directory:**
```bash
cd tests
python test_timezone_fix.py
# Should work without credential errors
```

### **Test from project root:**
```bash
cd backend
python agent.py
# Should work from anywhere
```

---

## 🛠️ **Troubleshooting**

### **Error: "No such file or directory: 'credentials.json'"**
**Solution**: 
1. Check if `credentials.json` is in project root (not backend/)
2. Download fresh credentials from Google Cloud Console
3. Verify file name is exactly `credentials.json`

### **Error: "ModuleNotFoundError: No module named 'config'"**
**Solution**: Make sure you're running from the backend/ directory or update PYTHONPATH

### **Error: "Permission denied"**
**Solution**: Check file permissions on credentials.json

### **Credentials work but can't write token.json**
**Solution**: Check write permissions in project root directory

---

## 🔄 **Environment Variable Alternative**

For production deployments, use environment variables:

### **Option 1: Environment Variable Paths**
```bash
# .env file
GOOGLE_CREDENTIALS_FILE=/absolute/path/to/credentials.json
GOOGLE_TOKEN_FILE=/absolute/path/to/token.json
```

### **Option 2: Credential Content as Environment Variable**
```bash
# .env file  
GOOGLE_CREDENTIALS_JSON='{"type":"service_account",...}'
```

Then update `config.py` to handle these scenarios.

---

## ✅ **Current Status**

- ✅ **Robust path handling** implemented
- ✅ **Works from any directory** (backend/, tests/, root)
- ✅ **Helpful error messages** for missing credentials
- ✅ **Uses centralized configuration** 
- ✅ **Security best practices** documented
- ✅ **Ready for mobile app development**

---

**Your credential management is now production-ready! 🚀** 