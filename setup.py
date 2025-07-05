#!/usr/bin/env python3
"""
Resume Matcher Local Setup Script
Run this script to set up the application locally.
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def create_env_file():
    """Create a sample .env file if it doesn't exist."""
    env_file = Path('.env')
    if not env_file.exists():
        print("🔄 Creating .env file...")
        env_content = """# Database (SQLite for local development)
DATABASE_URL=sqlite:///instance/resume_matcher.db

# Flask session secret (generate a random string)
SESSION_SECRET=your-secret-key-change-this-in-production

# Google Gemini API Key (required for AI features)
GEMINI_API_KEY=your-gemini-api-key-here
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file - Please update with your API keys!")
        return False  # Indicate that user needs to update the file
    return True

def create_directories():
    """Create necessary directories."""
    print("🔄 Creating required directories...")
    directories = ['instance', 'uploads']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directories created successfully")

def initialize_database():
    """Initialize the SQLite database."""
    print("🔄 Initializing database...")
    try:
        # Import and create database tables
        from app import app, db
        with app.app_context():
            db.create_all()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Resume Matcher Local Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    # Install dependencies
    if not run_command("pip install -r local_requirements.txt", "Installing Python dependencies"):
        return False
    
    # Install spaCy model
    if not run_command("python -m spacy download en_core_web_sm", "Installing spaCy English model"):
        return False
    
    # Create directories
    create_directories()
    
    # Create .env file
    env_created = create_env_file()
    
    if not env_created:
        print("\n⚠️  IMPORTANT: Please update the .env file with your API keys before continuing!")
        print("   - Get your Gemini API key from: https://aistudio.google.com/")
        print("   - Update the GEMINI_API_KEY in the .env file")
        print("   - Change the SESSION_SECRET to a random string")
        print("\nAfter updating .env, run: python setup.py --init-db")
        return True
    
    # Initialize database
    if not initialize_database():
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\nTo start the application:")
    print("   python main.py")
    print("\nThe application will be available at: http://localhost:5000")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--init-db":
        # Only initialize database
        initialize_database()
    else:
        # Full setup
        success = main()
        if not success:
            sys.exit(1)