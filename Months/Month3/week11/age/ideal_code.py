def identify_middle_sibling(*relations):
    siblings = set()
    scores = {}
    
    for relation in relations:
        if len(relation) != 3 or relation[1] not in ['>', '<', '=']:
            raise ValueError(f"Invalid relation format: {relation}")
        
        a, op, b = relation
        siblings.update([a, b])
        
        if a not in scores:
            scores[a] = 0
        if b not in scores:
            scores[b] = 0
        
        if op == '>':
            scores[a] += 1
            scores[b] -= 1
        elif op == '<':
            scores[a] -= 1
            scores[b] += 1
        # For '=', we don't change scores
    
    if len(siblings) < 3:
        raise ValueError("At least three siblings are required")
    
    sorted_siblings = sorted(siblings, key=lambda x: (scores[x], x))
    middle_index = len(sorted_siblings) // 2
    
    if len(sorted_siblings) % 2 == 0:
        middle_score = scores[sorted_siblings[middle_index - 1]]
    else:
        middle_score = scores[sorted_siblings[middle_index]]
    
    return [s for s in sorted_siblings if scores[s] == middle_score]

# Example usage and testing
test_cases = [
    ('X>Y', 'X<Z', 'Y<Z'),
    ('X<Y', 'X>Z', 'Y>Z'),
    ('X=Y', 'X<Z', 'Y<Z'),
    ('A>B', 'B>C', 'C>D', 'D>E'),
]

for case in test_cases:
    try:
        result = identify_middle_sibling(*case)
        print(f"Relations: {case}")
        print(f"Middle sibling(s): {result}\n")
    except ValueError as e:
        print(f"Error: {e}\n")

# Interactive mode
while True:
    try:
        user_input = input("Enter relations (or 'q' to quit): ").split()
        if user_input[0].lower() == 'q':
            break
        result = identify_middle_sibling(*user_input)
        print(f"The middle sibling(s): {result}\n")
    except (ValueError, IndexError) as e:
        print(f"Error: {e}\n")
    except KeyboardInterrupt:
        print("\nExiting...")
        break