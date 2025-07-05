import PyPDF2
import logging
import os

def extract_text_from_pdf(file_path):
    """Extract text from PDF file using PyPDF2"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            if not text.strip():
                logging.warning("No text extracted from PDF")
                return None
                
            return text.strip()
            
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        return None

def extract_text_from_txt(file_path):
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            
        if not text.strip():
            logging.warning("No text found in TXT file")
            return None
            
        return text.strip()
        
    except Exception as e:
        logging.error(f"Error reading TXT file: {e}")
        return None
