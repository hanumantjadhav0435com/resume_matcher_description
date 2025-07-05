# Resume Matcher - Local Setup Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)

## Installation Steps

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd resume-matcher
```

### 2. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r local_requirements.txt
```

### 4. Install spaCy Language Model
```bash
python -m spacy download en_core_web_sm
```

### 5. Set Environment Variables

Create a `.env` file in the root directory:
```bash
# Database (SQLite for local development)
DATABASE_URL=sqlite:///instance/resume_matcher.db

# Flask session secret (generate a random string)
SESSION_SECRET=your-secret-key-here

# Google Gemini API Key (required for AI features)
GEMINI_API_KEY=your-gemini-api-key-here
```

**Important**: Replace `your-gemini-api-key-here` with your actual Google Gemini API key.

### 6. Create Required Directories
```bash
mkdir -p instance uploads
```

### 7. Initialize Database
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 8. Run the Application
```bash
# Development mode
python main.py

# Or using gunicorn (production-like)
gunicorn --bind 127.0.0.1:5000 --reload main:app
```

The application will be available at `http://localhost:5000`

## Getting Your Google Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" in the left sidebar
4. Create a new API key
5. Copy the key and add it to your `.env` file

## Environment Variables Explained

- **DATABASE_URL**: Database connection string (SQLite for local development)
- **SESSION_SECRET**: Secret key for Flask sessions (use a random string)
- **GEMINI_API_KEY**: Google Gemini API key for AI-powered analysis

## File Structure
```
resume-matcher/
├── app.py                 # Flask app configuration
├── main.py               # Application entry point
├── models.py             # Database models
├── routes.py             # Route handlers
├── local_requirements.txt # Python dependencies
├── templates/            # HTML templates
├── static/               # CSS, JS, and static files
├── utils/                # Utility modules
├── instance/             # Database files (created automatically)
└── uploads/              # Uploaded files (created automatically)
```

## Troubleshooting

### Common Issues

1. **spaCy model not found**
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **Database errors**
   - Delete the `instance/` folder and run step 7 again

3. **Missing environment variables**
   - Make sure your `.env` file is in the root directory
   - Check that all required variables are set

4. **API key issues**
   - Verify your Gemini API key is correct
   - Check your API quota and billing status

### Development Tips

- Use `python main.py` for development with auto-reload
- Check the console for detailed error messages
- The database file is created in `instance/resume_matcher.db`
- Uploaded files are stored in the `uploads/` directory

## Features

- User registration and authentication
- PDF resume upload and text extraction
- Job description text input
- AI-powered match scoring using Google Gemini
- Keyword extraction and analysis
- Match result history and management
- Delete functionality for analysis results

## Tech Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: Bootstrap 5, JavaScript
- **AI/ML**: Google Gemini API, spaCy NLP
- **Database**: SQLite (local), PostgreSQL (production)
- **File Processing**: PyPDF2