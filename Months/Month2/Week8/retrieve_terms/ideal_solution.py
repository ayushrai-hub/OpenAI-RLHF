import re
from typing import List

def retrieve_terms(purpose_question: str) -> List[str]:
    # Define keywords that often indicate actions or technical terms
    action_keywords = ["process", "function", "calculate", "extract", "analyze", "compare", "determine", "evaluate", "implement"]
    
    # Preprocess the purpose question
    cleaned_question = re.sub(r'\[.*?\]', '', purpose_question).strip()
    
    # Extract multi-word technical terms (adjacent capitalized words)
    multi_word_terms = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b', cleaned_question)
    
    # Extract single-word technical terms (capitalized words not part of multi-word terms)
    single_word_terms = [word for word in re.findall(r'\b[A-Z][a-zA-Z]*\b', cleaned_question)
                         if not any(word in term for term in multi_word_terms)]
    
    # Check for presence of action keywords in the question (these are verbs/commands)
    actions = [word.lower() for word in cleaned_question.split() if word.lower() in action_keywords]
    
    # Extract analytical terms
    analytical_terms = [word.lower() for word in cleaned_question.split() if word.lower().startswith("analytic")]
    
    # Combine all extracted terms
    all_terms = multi_word_terms + single_word_terms + actions + analytical_terms
    
    # Remove duplicates while preserving order
    unique_terms = []
    for term in all_terms:
        if term.lower() not in [t.lower() for t in unique_terms]:
            unique_terms.append(term)
    
    # Capitalize the first letter of action words only if they appear at the beginning of the question
    final_terms = []
    for term in unique_terms:
        if term.lower() in action_keywords and term.lower() == cleaned_question.split()[0].lower():
            final_terms.append(term.capitalize())
        else:
            final_terms.append(term)
    
    return final_terms


purpose_question = "[Purpose Question]: Analyze the performance of Machine Learning algorithms in a multi-dimensional space."
print(f"Retrieved terms: {retrieve_terms(purpose_question)}")