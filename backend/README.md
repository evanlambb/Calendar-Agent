# 🔧 Calendar Agent Backend

This directory contains the Python backend code for the Calendar Agent.

## 📁 Structure

- `agent.py` - Main LangGraph agent with chat logic
- `tools.py` - Google Calendar integration tools  
- `config.py` - Configuration management
- `agent_improved.py` - Enhanced version with better error handling
- `requirements.txt` - Python dependencies

## 🚀 Running the Agent

```bash
cd backend
pip install -r requirements.txt
python agent.py
```

## 🔌 API Mode

To run as FastAPI server (for mobile app):

```bash
cd backend
python api_server.py  # (will be created in mobile development phase)
```

## 🧪 Testing

Tests are located in the `../tests/` directory.

```bash
cd ../tests
python test_timezone_fix.py
``` 