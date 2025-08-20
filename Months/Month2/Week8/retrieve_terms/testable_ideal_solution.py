
import re

def retrieve_terms(purpose_question):
    """
    Retrieve the most significant technical terms/scientific terms/actions 
    from the [Purpose Question] without changing the original phrasing.
    Ensures a minimal set of terms is retrieved.
    
    Parameters:
    purpose_question (str): The input purpose question from which to retrieve the terms.
    
    Returns:
    list: A list of retrieved technical/scientific terms or actions.
    """
    
    # Define keywords that often indicate actions or technical terms
    action_keywords = ["process", "function", "calculate", "extract", "analyze", "compare", "determine", "evaluate"]
    
    # Use regex to identify potential technical terms (assuming they are capitalized)
    technical_terms = re.findall(r'\b[A-Z][a-zA-Z]*\b', purpose_question)

    # Check for presence of action keywords in the question (these are verbs/commands)
    actions = [word for word in purpose_question.split() if word.lower() in action_keywords]

    # Combine technical terms and actions, ensuring they are minimal yet meaningful
    retrieved_terms = list(set(technical_terms + actions))

    # Return the retrieved list of terms, ensuring there are no duplicates
    return retrieved_terms
