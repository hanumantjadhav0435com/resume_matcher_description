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
            content=text
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
    """Calculate cosine similarity between resume and job description"""
    try:
        # Get embeddings for both texts
        resume_embedding = get_embeddings(resume_text)
        job_embedding = get_embeddings(job_text)
        
        if resume_embedding is None or job_embedding is None:
            logging.error("Failed to get embeddings")
            return 0.0
        
        # Reshape for sklearn
        resume_embedding = resume_embedding.reshape(1, -1)
        job_embedding = job_embedding.reshape(1, -1)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(resume_embedding, job_embedding)[0][0]
        
        # Convert to percentage (0-100)
        match_score = max(0, min(100, similarity * 100))
        
        return round(match_score, 2)
        
    except Exception as e:
        logging.error(f"Error calculating match score: {e}")
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
