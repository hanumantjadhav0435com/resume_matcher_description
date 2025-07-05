import os
import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from google import genai
from google.genai import types

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "default_key"))

def get_embeddings(text):
    """Get embeddings from Gemini API"""
    try:
        # Use Gemini's embedding model
        response = client.models.embed_content(
            model="text-embedding-004",
            contents=text
        )
        
        if response.embedding and response.embedding.values:
            return np.array(response.embedding.values)
        else:
            logging.error("No embeddings returned from Gemini API")
            return None
            
    except Exception as e:
        logging.error(f"Error getting embeddings: {e}")
        return None

def calculate_match_score(resume_text, job_text):
    """Calculate enhanced match score using multiple methods"""
    try:
        # Method 1: Semantic similarity using embeddings
        semantic_score = calculate_semantic_similarity(resume_text, job_text)
        
        # Method 2: Keyword overlap analysis
        keyword_score = calculate_keyword_similarity(resume_text, job_text)
        
        # Method 3: Skills and requirements matching
        skills_score = calculate_skills_match(resume_text, job_text)
        
        # Weighted combination for more accurate results
        final_score = (
            semantic_score * 0.4 +  # 40% semantic similarity
            keyword_score * 0.35 +  # 35% keyword overlap
            skills_score * 0.25     # 25% skills matching
        )
        
        # Apply scaling for better distribution (common resumes typically score 30-90%)
        scaled_score = min(100, max(0, final_score * 1.2))
        
        return round(scaled_score, 2)
        
    except Exception as e:
        logging.error(f"Error calculating match score: {e}")
        return 0.0

def calculate_semantic_similarity(resume_text, job_text):
    """Calculate semantic similarity using embeddings"""
    try:
        resume_embedding = get_embeddings(resume_text)
        job_embedding = get_embeddings(job_text)
        
        if resume_embedding is None or job_embedding is None:
            return 0.0
        
        # Reshape for sklearn
        resume_embedding = resume_embedding.reshape(1, -1)
        job_embedding = job_embedding.reshape(1, -1)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(resume_embedding, job_embedding)[0][0]
        
        # Convert to percentage
        return max(0, min(100, similarity * 100))
        
    except Exception as e:
        logging.error(f"Error calculating semantic similarity: {e}")
        return 0.0

def calculate_keyword_similarity(resume_text, job_text):
    """Calculate keyword overlap similarity"""
    try:
        from utils.nlp_analyzer import extract_keywords
        
        resume_keywords = set(extract_keywords(resume_text, max_keywords=30))
        job_keywords = set(extract_keywords(job_text, max_keywords=30))
        
        if not resume_keywords or not job_keywords:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(resume_keywords.intersection(job_keywords))
        union = len(resume_keywords.union(job_keywords))
        
        if union == 0:
            return 0.0
        
        jaccard_score = (intersection / union) * 100
        
        # Also consider partial matches and importance weighting
        overlap_ratio = intersection / len(job_keywords) if job_keywords else 0
        coverage_score = overlap_ratio * 100
        
        # Combine both metrics
        final_keyword_score = (jaccard_score * 0.4) + (coverage_score * 0.6)
        
        return min(100, final_keyword_score)
        
    except Exception as e:
        logging.error(f"Error calculating keyword similarity: {e}")
        return 0.0

def calculate_skills_match(resume_text, job_text):
    """Calculate skills and requirements matching"""
    try:
        # Define important skill categories and keywords
        technical_skills = ['python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 'kubernetes']
        soft_skills = ['leadership', 'communication', 'teamwork', 'problem', 'management', 'collaboration']
        experience_terms = ['years', 'experience', 'senior', 'junior', 'lead', 'manager']
        
        resume_lower = resume_text.lower()
        job_lower = job_text.lower()
        
        # Count skill matches in different categories
        tech_matches = sum(1 for skill in technical_skills if skill in resume_lower and skill in job_lower)
        soft_matches = sum(1 for skill in soft_skills if skill in resume_lower and skill in job_lower)
        exp_matches = sum(1 for term in experience_terms if term in resume_lower and term in job_lower)
        
        # Calculate scores for each category
        tech_score = (tech_matches / len(technical_skills)) * 100 if technical_skills else 0
        soft_score = (soft_matches / len(soft_skills)) * 100 if soft_skills else 0
        exp_score = (exp_matches / len(experience_terms)) * 100 if experience_terms else 0
        
        # Weight technical skills more heavily
        weighted_score = (tech_score * 0.5) + (soft_score * 0.3) + (exp_score * 0.2)
        
        return min(100, weighted_score)
        
    except Exception as e:
        logging.error(f"Error calculating skills match: {e}")
        return 0.0

def generate_suggestions(resume_keywords, job_keywords, match_score):
    """Generate improvement suggestions based on keyword analysis"""
    suggestions = []
    
    try:
        resume_set = set(resume_keywords)
        job_set = set(job_keywords)
        
        # Find missing keywords
        missing_keywords = job_set - resume_set
        common_keywords = resume_set & job_set
        
        # Generate specific suggestions
        if missing_keywords:
            missing_list = list(missing_keywords)[:10]  # Limit to top 10
            suggestions.append({
                'type': 'missing_keywords',
                'title': 'Add Missing Keywords',
                'description': f"Consider adding these keywords from the job description: {', '.join(missing_list)}"
            })
        
        if len(common_keywords) < 5:
            suggestions.append({
                'type': 'keyword_density',
                'title': 'Increase Keyword Relevance',
                'description': 'Your resume has limited overlap with job requirements. Focus on highlighting relevant skills and experience.'
            })
        
        if match_score < 50:
            suggestions.append({
                'type': 'major_revision',
                'title': 'Major Resume Revision Needed',
                'description': 'Consider significantly restructuring your resume to better align with the job requirements.'
            })
        elif match_score < 70:
            suggestions.append({
                'type': 'moderate_revision',
                'title': 'Moderate Improvements Needed',
                'description': 'Add more relevant experience and skills that match the job description.'
            })
        
        # Use Gemini for additional suggestions
        if len(suggestions) < 3:
            ai_suggestions = generate_ai_suggestions(resume_keywords, job_keywords, match_score)
            suggestions.extend(ai_suggestions)
        
        return suggestions[:5]  # Limit to 5 suggestions
        
    except Exception as e:
        logging.error(f"Error generating suggestions: {e}")
        return [{'type': 'error', 'title': 'Analysis Error', 'description': 'Unable to generate suggestions at this time.'}]

def generate_ai_suggestions(resume_keywords, job_keywords, match_score):
    """Generate AI-powered suggestions using Gemini"""
    try:
        prompt = f"""
        Based on the following analysis, provide 2-3 specific, actionable suggestions to improve a resume's match with a job description:
        
        Resume Keywords: {', '.join(resume_keywords[:15])}
        Job Keywords: {', '.join(job_keywords[:15])}
        Current Match Score: {match_score}%
        
        Provide suggestions in the following format:
        1. [Suggestion Title]: [Specific actionable advice]
        2. [Suggestion Title]: [Specific actionable advice]
        3. [Suggestion Title]: [Specific actionable advice]
        
        Focus on practical improvements like skills to highlight, sections to add, or experience to emphasize.
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        if response.text:
            # Parse the response into structured suggestions
            lines = response.text.strip().split('\n')
            ai_suggestions = []
            
            for line in lines:
                if ':' in line and any(char.isdigit() for char in line[:3]):
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        title = parts[0].strip().lstrip('0123456789. ')
                        description = parts[1].strip()
                        ai_suggestions.append({
                            'type': 'ai_suggestion',
                            'title': title,
                            'description': description
                        })
            
            return ai_suggestions[:3]
        
        return []
        
    except Exception as e:
        logging.error(f"Error generating AI suggestions: {e}")
        return []
