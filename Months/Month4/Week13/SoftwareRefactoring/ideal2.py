# idealCompletion.py

from typing import List, Generator

def sequence_expander(start: str, end: str) -> List[str]:
    """
    Converts a range of numbers or letters into a comprehensive list of those elements.
    
    Args:
        start (str): The beginning of the sequence.
        end (str): The termination of the sequence.
    
    Returns:
        List[str]: A complete list containing all elements within the specified range.
        
    Raises:
        ValueError: If inputs have invalid format or range.
    """
    if is_basic_sequence(start, end):
        return broaden_basic_sequence(start, end)
    
    return broaden_complex_sequence(start, end)

def is_basic_sequence(start: str, end: str) -> bool:
    """
    Determine if the sequence is a basic numeric or alphabetic sequence.
    
    Args:
        start (str): Start of sequence
        end (str): End of sequence
        
    Returns:
        bool: True if sequence is basic (all numbers or all letters)
    """
    return (start.isdigit() and end.isdigit()) or (start.isalpha() and end.isalpha())

def expand_range(start: str, end: str) -> Generator[str, None, None]:
    """
    Core logic for expanding a range of either numbers or letters.
    
    Args:
        start (str): Start value
        end (str): End value
        
    Returns:
        Generator[str, None, None]: Generator yielding sequence elements
        
    Raises:
        ValueError: If elements are not of the same type or range is invalid
    """
    if start.isdigit() and end.isdigit():
        start_val, end_val = int(start), int(end)
        if start_val > end_val:
            raise ValueError(f"Start value {start_val} cannot be greater than end value {end_val}")
        for i in range(start_val, end_val + 1):
            yield str(i)
    elif start.isalpha() and end.isalpha():
        start_val, end_val = ord(start), ord(end)
        if start_val > end_val:
            raise ValueError(f"Start letter '{start}' cannot come after end letter '{end}'")
        for i in range(start_val, end_val + 1):
            yield chr(i)
    else:
        raise ValueError("Elements must be either both digits or both letters")

def broaden_basic_sequence(start: str, end: str) -> List[str]:
    """
    Broaden a basic numeric or alphabetic sequence.
    
    Args:
        start (str): Start of sequence
        end (str): End of sequence
        
    Returns:
        List[str]: List of elements in the sequence
    """
    return list(expand_range(start, end))

def broaden_complex_sequence(start: str, end: str) -> List[str]:
    """
    Broaden a complex sequence with dot-separated sections.
    
    Args:
        start (str): Start of sequence with dot-separated sections
        end (str): End of sequence with dot-separated sections
        
    Returns:
        List[str]: List of all combinations in the sequence
    """
    start_components = start.split('.')
    end_components = end.split('.')
    
    ensure_structure(start_components, end_components, start, end)
    
    # Find the varying component
    varying_index = None
    for i in range(len(start_components)):
        if start_components[i] != end_components[i]:
            varying_index = i
            break
    
    # If no varying component found, return just the start sequence
    if varying_index is None:
        return [start]
    
    # Generate sequence only for the varying component
    result = []
    base_components = start_components.copy()
    for element in expand_range(start_components[varying_index], end_components[varying_index]):
        base_components[varying_index] = element
        result.append('.'.join(base_components))
    
    return result

def ensure_structure(start_components: List[str], end_components: List[str], 
                    start: str, end: str) -> None:
    """
    Ensure both start and end have similar structure.
    
    Args:
        start_components (List[str]): Components of start sequence
        end_components (List[str]): Components of end sequence
        start (str): Original start sequence
        end (str): Original end sequence
        
    Raises:
        ValueError: If components don't match in count or type
    """
    if len(start_components) != len(end_components):
        raise ValueError("The start and end of the sequence must have similar element counts.")
    
    for s, e in zip(start_components, end_components):
        if not ((s.isdigit() and e.isdigit()) or (s.isalpha() and e.isalpha())):
            raise ValueError(f"Matched elements required in start ({start}) and end ({end}).")