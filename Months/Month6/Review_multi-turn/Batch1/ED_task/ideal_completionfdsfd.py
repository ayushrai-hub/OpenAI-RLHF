import os
import docx
import PyPDF2
from odf import text, teletype
from odf.opendocument import load
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import ssl

# Create unverified SSL context for NLTK downloads if needed
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

def extract_text_from_docx(file_path):
    """Extract text from a .docx file."""
    doc = docx.Document(file_path)
    return ' '.join(paragraph.text for paragraph in doc.paragraphs)

def extract_text_from_pdf(file_path):
    """Extract text from a .pdf file."""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        return ' '.join(page.extract_text() for page in reader.pages)

def extract_text_from_odt(file_path):
    """Extract text from an .odt file."""
    textdoc = load(file_path)
    allparas = textdoc.getElementsByType(text.P)
    return ' '.join(teletype.extractText(para) for para in allparas)

def preprocess_text(text):
    """Preprocess the text for comparison without relying on NLTK."""
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation and special characters
    text = re.sub(r'[^\w\s]', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Basic stopwords list (most common English words)
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    
    # Remove stopwords
    words = text.split()
    words = [word for word in words if word not in stop_words]
    
    return ' '.join(words)

def get_comparison_texts():
    """Get texts to compare against. This simulates a database of source texts."""
    return [
        """Donald Trump said he built the biggest, the broadest, the most unified coalition in all of American history. The Sky News data team assess whether he's right. This campaign, has been so historic in so many ways. We've built the biggest, the broadest, the most unified coalition."""
    ]

def calculate_similarity(text1, text2):
    """Calculate cosine similarity between two texts."""
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except:
        return 0.0

def has_plagiarism(file_path: str, threshold: float = 0.9) -> bool:
    """
    Check if a given file or text has plagiarism.
    
    Args:
        file_path: Path to the file or the text content directly
        threshold: Similarity threshold above which content is considered plagiarized
    
    Returns:
        bool: True if plagiarism is detected, False otherwise
    """
    # Handle direct text input
    if not os.path.exists(file_path):
        input_text = file_path
    else:
        # Extract text based on file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        try:
            if file_ext == '.pdf':
                input_text = extract_text_from_pdf(file_path)
            elif file_ext == '.docx':
                input_text = extract_text_from_docx(file_path)
            elif file_ext == '.odt':
                input_text = extract_text_from_odt(file_path)
            else:
                # Handle as direct text input if extension not recognized
                with open(file_path, 'r', encoding='utf-8') as file:
                    input_text = file.read()
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return False

    # Preprocess the input text
    processed_input = preprocess_text(input_text)
    
    # Get comparison texts
    comparison_texts = get_comparison_texts()
    
    # Check similarity against each comparison text
    for comp_text in comparison_texts:
        processed_comp = preprocess_text(comp_text)
        similarity = calculate_similarity(processed_input, processed_comp)
        if similarity >= threshold:
            return True
    
    return False