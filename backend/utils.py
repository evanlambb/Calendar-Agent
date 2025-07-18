"""
Utility functions for file path handling and project structure
"""
import os

def get_project_root():
    """
    Get the project root directory regardless of current working directory.
    Works whether running from root, backend/, tests/, etc.
    """
    # Get the directory where this utils.py file is located (backend/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Go up one level to project root
    project_root = os.path.dirname(current_dir)
    
    return project_root

def get_credentials_path():
    """Get the absolute path to credentials.json in project root"""
    return os.path.join(get_project_root(), "credentials.json")

def get_token_path():
    """Get the absolute path to token.json in project root"""
    return os.path.join(get_project_root(), "token.json")

def ensure_credentials_exist():
    """
    Check if credentials.json exists and provide helpful error message if not
    """
    creds_path = get_credentials_path()
    if not os.path.exists(creds_path):
        project_root = get_project_root()
        raise FileNotFoundError(
            f"❌ Google Calendar credentials not found!\n\n"
            f"Expected location: {creds_path}\n\n"
            f"📋 To fix this:\n"
            f"1. Download your credentials.json from Google Cloud Console\n"
            f"2. Place it in the project root: {project_root}\n"
            f"3. Make sure it's named exactly 'credentials.json'\n\n"
            f"📚 See docs/LANGSMITH_SETUP.md for detailed setup instructions"
        )
    return creds_path 