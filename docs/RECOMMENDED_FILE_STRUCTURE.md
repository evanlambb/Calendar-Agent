# 📁 Recommended File Structure

## 🎯 **Goal**: Clean, scalable organization for backend + mobile app

---

## 🗂️ **Proposed Structure**

```
Calendar-Agent/
├── 📁 backend/                    # Python backend code
│   ├── 📁 src/
│   │   ├── 📁 api/               # FastAPI routes and endpoints
│   │   │   ├── __init__.py
│   │   │   ├── chat.py           # Chat endpoint
│   │   │   └── health.py         # Health check endpoint
│   │   ├── 📁 core/              # Core business logic
│   │   │   ├── __init__.py
│   │   │   ├── agent.py          # LangGraph agent (renamed from agent.py)
│   │   │   ├── tools.py          # Calendar tools (moved from root)
│   │   │   └── config.py         # Configuration management
│   │   ├── 📁 services/          # External service integrations
│   │   │   ├── __init__.py
│   │   │   ├── google_calendar.py # Google Calendar service
│   │   │   └── llm_service.py    # LLM interaction service
│   │   └── main.py               # FastAPI app entry point
│   ├── 📁 tests/                 # Backend tests
│   │   ├── __init__.py
│   │   ├── test_agent.py
│   │   ├── test_tools.py
│   │   ├── test_create_event.py  # Moved from root
│   │   └── test_delete_event.py  # Moved from root
│   ├── requirements.txt          # Backend dependencies
│   ├── .env.example             # Environment template
│   └── README.md                # Backend-specific docs
│
├── 📁 mobile/                    # React Native app
│   ├── 📁 src/
│   │   ├── 📁 components/        # Reusable UI components
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   └── LoadingIndicator.tsx
│   │   ├── 📁 screens/           # App screens
│   │   │   ├── ChatScreen.tsx
│   │   │   └── SettingsScreen.tsx
│   │   ├── 📁 services/          # API communication
│   │   │   ├── api.ts
│   │   │   └── types.ts
│   │   ├── 📁 utils/             # Helper functions
│   │   │   └── constants.ts
│   │   └── App.tsx              # Main app component
│   ├── package.json
│   ├── app.json                 # Expo configuration
│   ├── tsconfig.json
│   └── README.md               # Mobile-specific docs
│
├── 📁 docs/                     # Project documentation
│   ├── API.md                  # API documentation
│   ├── SETUP.md                # Setup instructions
│   ├── DEPLOYMENT.md           # Deployment guide
│   └── ARCHITECTURE.md         # System architecture
│
├── 📁 scripts/                  # Utility scripts
│   ├── setup_env.py           # Environment setup
│   ├── deploy.sh              # Deployment script
│   └── generate_docs.py       # Documentation generator
│
├── 📁 .github/                 # GitHub workflows (optional)
│   └── 📁 workflows/
│       ├── backend-tests.yml
│       └── mobile-build.yml
│
├── .gitignore                  # Global gitignore
├── LICENSE                     # Project license
├── README.md                   # Main project README
├── PROJECT_ROADMAP.md          # Development roadmap
└── docker-compose.yml          # For future containerization
```

---

## 📋 **Migration Plan**

### **Phase 1: Create Directory Structure**
```bash
# Create backend structure
mkdir -p backend/src/api
mkdir -p backend/src/core  
mkdir -p backend/src/services
mkdir -p backend/tests

# Create mobile structure
mkdir -p mobile/src/components
mkdir -p mobile/src/screens
mkdir -p mobile/src/services
mkdir -p mobile/src/utils

# Create docs and scripts
mkdir -p docs
mkdir -p scripts
```

### **Phase 2: Move Existing Files**
```bash
# Move Python files to backend
mv agent.py backend/src/core/
mv tools.py backend/src/core/
mv config.py backend/src/core/
mv requirements.txt backend/

# Move tests to backend
mv test_create_event.py backend/tests/
mv test_delete_event.py backend/tests/

# Clean up root
rm demonstrate_tool_decorator.py  # (if not needed)
```

### **Phase 3: Update Import Statements**
Update all imports to reflect new structure:
```python
# Old imports:
from tools import create_event, get_events
from agent import graph

# New imports:
from backend.src.core.tools import create_event, get_events
from backend.src.core.agent import graph
```

---

## 🔧 **Benefits of This Structure**

### **Separation of Concerns**
- ✅ **Backend**: All Python/AI logic isolated
- ✅ **Mobile**: All React Native code separate
- ✅ **Docs**: Centralized documentation
- ✅ **Tests**: Organized by component

### **Scalability**
- ✅ Easy to add new API endpoints
- ✅ Simple to add new mobile screens
- ✅ Clear place for new services/integrations
- ✅ Supports multiple deployment strategies

### **Developer Experience**
- ✅ Clear mental model of codebase
- ✅ Easy onboarding for new developers
- ✅ Supports IDE workspace configuration
- ✅ Enables proper CI/CD pipelines

### **Future-Proof**
- ✅ Ready for microservices if needed
- ✅ Supports Docker containerization
- ✅ Works with mono-repo tools
- ✅ Enables independent versioning

---

## 📝 **Updated File Purposes**

### **Backend Files**
- `backend/src/main.py` → FastAPI app entry point
- `backend/src/api/chat.py` → Chat endpoint logic
- `backend/src/core/agent.py` → LangGraph agent (your current agent.py)
- `backend/src/core/tools.py` → Calendar tools (your current tools.py)
- `backend/src/services/google_calendar.py` → Google Calendar API wrapper

### **Mobile Files**
- `mobile/src/App.tsx` → Main React Native app
- `mobile/src/screens/ChatScreen.tsx` → Chat interface
- `mobile/src/services/api.ts` → Backend communication
- `mobile/src/components/ChatMessage.tsx` → Individual message component

### **Root Files**
- `README.md` → Project overview and quick start
- `PROJECT_ROADMAP.md` → Development plan
- `.gitignore` → Ignore patterns for both backend and mobile

---

## 🚀 **Implementation Steps**

1. **Create the directory structure** (5 minutes)
2. **Move existing files** (10 minutes)  
3. **Update import statements** (15 minutes)
4. **Update .gitignore** (5 minutes)
5. **Create new README files** (10 minutes)

**Total time**: ~45 minutes of reorganization

---

## 💡 **Alternative: Minimal Reorganization**

If you prefer a lighter touch:

```
Calendar-Agent/
├── backend/
│   ├── agent.py
│   ├── tools.py
│   ├── api_server.py
│   └── requirements.txt
├── mobile/
│   └── (Expo app files)
├── tests/
│   ├── test_create_event.py
│   └── test_delete_event.py
└── docs/
    └── PROJECT_ROADMAP.md
```

This gives you separation without deep nesting.

---

## 🤔 **Your Preference?**

**Option A**: Full professional structure (recommended for long-term)
**Option B**: Minimal reorganization (faster to implement)
**Option C**: Custom hybrid approach

Which approach feels right for your project goals? 