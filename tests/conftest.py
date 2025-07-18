"""
Pytest configuration file that sets up the Python path for testing.
This file is automatically recognized by pytest and most IDEs.
"""
import sys
import os

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, os.path.abspath(backend_path))

# Add project root to Python path as well (for alternative imports)
project_root = os.path.join(os.path.dirname(__file__), '..')
if project_root not in sys.path:
    sys.path.insert(0, os.path.abspath(project_root)) 