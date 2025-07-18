# 🧪 Calendar Agent Tests

This directory contains test files for the Calendar Agent backend.

## 📁 Test Files

- `test_create_event.py` - Comprehensive tests for event creation
- `test_delete_event.py` - Tests for event deletion workflow  
- `test_timezone_fix.py` - Tests for timezone consistency fixes

## 🏃 Running Tests

```bash
cd tests

# Run individual test
python test_timezone_fix.py

# Run all tests with pytest
pytest

# Run specific test file
pytest test_create_event.py
```

## 📋 Test Requirements

Make sure you have:
- Google Calendar API credentials configured
- Python dependencies installed (`../backend/requirements.txt`)
- Calendar access permissions granted 