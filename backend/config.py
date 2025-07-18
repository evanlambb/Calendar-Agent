"""
Configuration management for Calendar Agent
"""
import os
from typing import Optional

class CalendarConfig:
    """Centralized configuration for calendar agent"""
    
    # Timezone settings
    TIMEZONE: str = os.getenv("CALENDAR_TIMEZONE", "America/Toronto")
    
    # Google Calendar API settings
    CREDENTIALS_FILE: str = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    TOKEN_FILE: str = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
    CALENDAR_SCOPES: list = ["https://www.googleapis.com/auth/calendar"]
    
    # LangSmith settings
    LANGSMITH_TRACING: bool = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    LANGSMITH_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "calendar-agent")
    
    # AI Model settings
    DEFAULT_MODEL: str = os.getenv("CALENDAR_AI_MODEL", "google_genai:gemini-2.5-flash")
    
    # Agent behavior settings
    MAX_EVENTS_RETURNED: int = int(os.getenv("MAX_EVENTS_RETURNED", "50"))
    DEFAULT_EVENT_DURATION: int = int(os.getenv("DEFAULT_EVENT_DURATION", "60"))  # minutes
    
    # Session settings
    THREAD_ID: str = os.getenv("AGENT_THREAD_ID", "1")
    
    @classmethod
    def validate_config(cls) -> tuple[bool, list[str]]:
        """Validate configuration and return (is_valid, error_messages)"""
        errors = []
        
        # Check required files exist
        if not os.path.exists(cls.CREDENTIALS_FILE):
            errors.append(f"Google credentials file not found: {cls.CREDENTIALS_FILE}")
            
        # Validate timezone
        try:
            import pytz
            pytz.timezone(cls.TIMEZONE)
        except ImportError:
            errors.append("pytz library not installed - run: pip install pytz>=2023.3")
        except pytz.UnknownTimeZoneError:
            errors.append(f"Invalid timezone: {cls.TIMEZONE}")
        except Exception as e:
            errors.append(f"Timezone validation error: {e}")
            
        return len(errors) == 0, errors
    
    @classmethod
    def get_env_template(cls) -> str:
        """Return template for .env file"""
        return """# Calendar Agent Configuration

# Timezone (default: America/Toronto)
CALENDAR_TIMEZONE=America/Toronto

# Google Calendar API files
GOOGLE_CREDENTIALS_FILE=credentials.json  
GOOGLE_TOKEN_FILE=token.json

# AI Model (default: google_genai:gemini-2.5-flash)
CALENDAR_AI_MODEL=google_genai:gemini-2.5-flash

# Agent Behavior
MAX_EVENTS_RETURNED=50
DEFAULT_EVENT_DURATION=60
AGENT_THREAD_ID=1

# LangSmith Configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=calendar-agent

# Google AI Configuration  
GOOGLE_API_KEY=your_google_api_key_here
""" 