from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to match results
    match_results = db.relationship('MatchResult', backref='user', lazy=True, cascade='all, delete-orphan')

class MatchResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    resume_filename = db.Column(db.String(255), nullable=False)
    job_description_filename = db.Column(db.String(255), nullable=False)
    match_score = db.Column(db.Float, nullable=False)
    resume_keywords = db.Column(db.Text)  # JSON string
    job_keywords = db.Column(db.Text)  # JSON string
    suggestions = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
