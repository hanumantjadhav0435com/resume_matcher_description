import spacy
import logging
from collections import Counter

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logging.error("spaCy English model not found. Please install it with: python -m spacy download en_core_web_sm")
    nlp = None

def extract_keywords(text, max_keywords=20):
    """Extract keywords from text using spaCy NLP"""
    if not nlp:
        logging.error("spaCy model not loaded")
        return []
    
    try:
        doc = nlp(text)
        
        # Extract meaningful tokens (nouns, proper nouns, verbs, adjectives)
        keywords = []
        for token in doc:
            # Filter out stop words, punctuation, spaces, and short tokens
            if (token.pos_ in ['NOUN', 'PROPN', 'VERB', 'ADJ'] and 
                not token.is_stop and 
                not token.is_punct and 
                not token.is_space and 
                len(token.text) > 2 and
                token.text.isalpha()):
                
                # Use lemmatized form for consistency
                keywords.append(token.lemma_.lower())
        
        # Count frequency and return most common keywords
        keyword_freq = Counter(keywords)
        most_common = keyword_freq.most_common(max_keywords)
        
        return [keyword for keyword, freq in most_common]
        
    except Exception as e:
        logging.error(f"Error extracting keywords: {e}")
        return []

def extract_entities(text):
    """Extract named entities from text"""
    if not nlp:
        return []
    
    try:
        doc = nlp(text)
        entities = []
        
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT', 'SKILL']:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_
                })
        
        return entities
        
    except Exception as e:
        logging.error(f"Error extracting entities: {e}")
        return []
