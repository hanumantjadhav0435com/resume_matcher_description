# Resume Matcher - Replit.md

## Overview

Resume Matcher is a Flask-based web application that analyzes the compatibility between resumes and job descriptions using natural language processing and machine learning techniques. The application allows users to upload PDF resumes and TXT job descriptions, then provides a match score along with keyword analysis and improvement suggestions.

## System Architecture

### Backend Architecture
- **Framework**: Flask web framework with SQLAlchemy ORM
- **Database**: SQLite for development (configurable via DATABASE_URL environment variable)
- **Authentication**: Flask-Login for user session management
- **File Processing**: PyPDF2 for PDF text extraction, standard file I/O for TXT files
- **NLP Processing**: spaCy for keyword extraction and text analysis
- **ML/AI Integration**: Google Gemini API for text embeddings and cosine similarity calculations

### Frontend Architecture
- **Templates**: Jinja2 templating with Bootstrap 5 for responsive UI
- **Styling**: Custom CSS with Bootstrap dark theme integration
- **JavaScript**: Vanilla JavaScript for form validation, progress animations, and UI interactions
- **Icons**: Font Awesome for consistent iconography

### File Structure
```
/
├── app.py                 # Flask application factory and configuration
├── main.py               # Application entry point
├── models.py             # SQLAlchemy database models
├── routes.py             # Flask route handlers
├── templates/            # Jinja2 HTML templates
├── static/               # CSS, JavaScript, and static assets
└── utils/                # Utility modules for processing
```

## Key Components

### Database Models
- **User**: Authentication and user management with cascading relationships
- **MatchResult**: Stores analysis results with foreign key to users, including match scores, keywords, and suggestions

### Core Processing Modules
- **file_processor.py**: Handles PDF and TXT file text extraction
- **nlp_analyzer.py**: spaCy-based keyword extraction and entity recognition
- **match_calculator.py**: Gemini API integration for embeddings and similarity calculations

### Authentication System
- Flask-Login integration with session management
- Password hashing using Werkzeug security utilities
- User registration and login with validation

### File Upload System
- Secure filename handling with Werkzeug utilities
- File type validation (PDF for resumes, TXT for job descriptions)
- 16MB file size limit with proper error handling

## Data Flow

1. **User Registration/Login**: Users create accounts or authenticate using username/password
2. **File Upload**: Users upload PDF resumes and TXT job descriptions through web interface
3. **Text Extraction**: Backend extracts text content from uploaded files
4. **NLP Processing**: spaCy analyzes text to extract keywords and entities
5. **Similarity Calculation**: Gemini API generates embeddings and calculates cosine similarity
6. **Result Storage**: Match results saved to database with user association
7. **Visualization**: Results displayed with progress bars, keyword clouds, and suggestions

## External Dependencies

### Python Packages
- **Flask**: Web framework and extensions (SQLAlchemy, Login)
- **PyPDF2**: PDF text extraction
- **spaCy**: Natural language processing ("en_core_web_sm" model required)
- **scikit-learn**: Machine learning utilities for similarity calculations
- **google-genai**: Google Gemini API client for embeddings
- **numpy**: Numerical computing for array operations

### External APIs
- **Google Gemini API**: Text embedding generation using "text-embedding-004" model
- Requires GEMINI_API_KEY environment variable

### Frontend Dependencies
- **Bootstrap 5**: CSS framework with dark theme
- **Font Awesome 6**: Icon library
- **Bootstrap JavaScript**: UI component functionality

## Deployment Strategy

### Environment Configuration
- **DATABASE_URL**: Database connection string (defaults to SQLite)
- **SESSION_SECRET**: Flask session encryption key
- **GEMINI_API_KEY**: Google Gemini API authentication
- **Upload directory**: Configurable file storage location

### Production Considerations
- ProxyFix middleware for reverse proxy deployment
- Database connection pooling with automatic reconnection
- File upload size limits and security validation
- Logging configuration for debugging and monitoring

### Development Setup
- Debug mode enabled in development
- Auto-reload functionality for code changes
- SQLite database with automatic table creation
- Local file storage in uploads directory

## Changelog
- July 05, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.