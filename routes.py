import os
import json
import logging
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import app, db
from models import User, MatchResult
from utils.file_processor import extract_text_from_pdf, extract_text_from_txt
from utils.nlp_analyzer import extract_keywords
from utils.match_calculator import calculate_match_score, generate_suggestions

ALLOWED_EXTENSIONS = {'pdf', 'txt'}

def allowed_file(filename, file_type):
    if file_type == 'resume':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'
    return False

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            logging.error(f"Registration error: {e}")
            flash('Registration failed. Please try again.', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    recent_results = MatchResult.query.filter_by(user_id=current_user.id)\
                                    .order_by(MatchResult.created_at.desc())\
                                    .limit(5).all()
    return render_template('dashboard.html', recent_results=recent_results)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_files():
    if request.method == 'POST':
        # Check if resume file and job description text are present
        if 'resume' not in request.files or not request.form.get('job_description'):
            flash('Both resume file and job description text are required.', 'danger')
            return render_template('upload.html')
        
        resume_file = request.files['resume']
        job_description_text = request.form.get('job_description', '').strip()
        
        # Check if resume file is selected and job description is provided
        if resume_file.filename == '' or not job_description_text:
            flash('Please select a resume file and provide job description text.', 'danger')
            return render_template('upload.html')
        
        # Validate resume file type
        if not allowed_file(resume_file.filename, 'resume'):
            flash('Resume must be in PDF format.', 'danger')
            return render_template('upload.html')
        
        try:
            # Save resume file
            resume_filename = secure_filename(f"{current_user.id}_{resume_file.filename}")
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
            resume_file.save(resume_path)
            
            # Process files
            resume_text = extract_text_from_pdf(resume_path)
            job_text = job_description_text
            
            if not resume_text or not job_text:
                flash('Error extracting text from resume. Please check file format.', 'danger')
                return render_template('upload.html')
            
            # Extract keywords
            resume_keywords = extract_keywords(resume_text)
            job_keywords = extract_keywords(job_text)
            
            # Calculate match score
            match_score = calculate_match_score(resume_text, job_text)
            
            # Generate suggestions if score is low
            suggestions = []
            if match_score < 80:
                suggestions = generate_suggestions(resume_keywords, job_keywords, match_score)
            
            # Save result to database
            result = MatchResult(
                user_id=current_user.id,
                resume_filename=resume_file.filename,
                job_description_filename="Direct Input",
                match_score=match_score,
                resume_keywords=json.dumps(resume_keywords),
                job_keywords=json.dumps(job_keywords),
                suggestions=json.dumps(suggestions)
            )
            
            db.session.add(result)
            db.session.commit()
            
            # Clean up uploaded resume file
            os.remove(resume_path)
            
            # Redirect to results
            return redirect(url_for('view_results', result_id=result.id))
            
        except Exception as e:
            logging.error(f"File processing error: {e}")
            flash('Error processing files. Please try again.', 'danger')
            return render_template('upload.html')
    
    return render_template('upload.html')

@app.route('/results/<int:result_id>')
@login_required
def view_results(result_id):
    result = MatchResult.query.filter_by(id=result_id, user_id=current_user.id).first()
    
    if not result:
        flash('Result not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Parse JSON data
    resume_keywords = json.loads(result.resume_keywords)
    job_keywords = json.loads(result.job_keywords)
    suggestions = json.loads(result.suggestions)
    
    return render_template('results.html', 
                         result=result,
                         resume_keywords=resume_keywords,
                         job_keywords=job_keywords,
                         suggestions=suggestions)

@app.route('/history')
@login_required
def view_history():
    results = MatchResult.query.filter_by(user_id=current_user.id)\
                              .order_by(MatchResult.created_at.desc()).all()
    return render_template('dashboard.html', recent_results=results, show_all=True)

@app.route('/delete_result/<int:result_id>', methods=['POST'])
@login_required
def delete_result(result_id):
    result = MatchResult.query.filter_by(id=result_id, user_id=current_user.id).first()
    
    if not result:
        flash('Result not found or you do not have permission to delete it.', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        db.session.delete(result)
        db.session.commit()
        flash('Analysis result deleted successfully.', 'success')
    except Exception as e:
        logging.error(f"Error deleting result: {e}")
        flash('Error deleting result. Please try again.', 'danger')
    
    return redirect(url_for('dashboard'))
