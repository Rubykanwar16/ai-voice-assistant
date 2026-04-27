"""WSGI entry point for Gunicorn"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import and initialize the app
from web_app import app

# Initialize clients when app starts
if __name__ != "__main__":
    from web_app import init_clients
    init_clients()

if __name__ == "__main__":
    app.run()
