import pandas as pd
from itertools import product

# Given JPD data
data = {
    'A': [True, True, True, True, True, True, True, True, False, False, False, False, False, False, False, False],
    'B': [True, True, True, True, False, False, False, False, True, True, True, True, False, False, False, False],
    'C': [True, True, False, False, True, True, False, False, True, True, False, False, True, True, False, False],
    'D': [True, False, True, False, True, False, True, False, True, False, True, False, True, False, True, False],
    'P': [0.014, 0.042, 0.0126, 0.0714, 0.056, 0.168, 0.0504, 0.2856, 0.00375, 0.01125, 0.02025, 0.11475, 0.00375, 0.01125, 0.02025, 0.11475]
}

df = pd.DataFrame(data)

def joint_probability(df, variables):
    if not variables:
        return {(): df['P'].sum()}
    
    grouped = df.groupby(variables)['P'].sum()
    
    # Convert the index to tuples if it's not already
    if not isinstance(grouped.index, pd.MultiIndex):
        return {(k,): v for k, v in grouped.items()}
    else:
        return grouped.to_dict()

def check_conditional_independence(df, X, Y, Z):
    variables = [X, Y] + Z
    joint = joint_probability(df, variables)
    marginal_Z = joint_probability(df, Z)
    marginal_XZ = joint_probability(df, [X] + Z)
    marginal_YZ = joint_probability(df, [Y] + Z)
    
    for values in product([True, False], repeat=len(variables)):
        key = tuple(values)
        key_Z = key[2:] if Z else ()
        key_XZ = (key[0],) + key_Z
        key_YZ = (key[1],) + key_Z
        
        p_Z = marginal_Z.get(key_Z, 0)
        if p_Z > 0:
            p_joint = joint.get(key, 0)
            p_X_given_Z = marginal_XZ.get(key_XZ, 0) / p_Z
            p_Y_given_Z = marginal_YZ.get(key_YZ, 0) / p_Z
            
            if abs(p_joint - p_X_given_Z * p_Y_given_Z * p_Z) > 1e-6:
                return False
    return True

# Define DAG structures
dag_a = {
    'A': ['B', 'C'],
    'B': [],
    'C': ['D'],
    'D': []
}

dag_b = {
    'A': [],
    'B': ['A'],
    'C': ['D'],
    'D': ['A']
}

# Check conditional independencies for DAG (a)
print("DAG (a) Conditional Independencies:")
print("I(B,C|A):", check_conditional_independence(df, 'B', 'C', ['A']))
print("I(B,D|A,C):", check_conditional_independence(df, 'B', 'D', ['A', 'C']))

# Check conditional independencies for DAG (b)
print("\nDAG (b) Conditional Independencies:")
print("I(A,C|B,D):", check_conditional_independence(df, 'A', 'C', ['B', 'D']))
print("I(B,D):", check_conditional_independence(df, 'B', 'D', []))
print("I(B,C):", check_conditional_independence(df, 'B', 'C', []))

# Determine which DAG matches the JPD
match_DAG_a = all([
    check_conditional_independence(df, 'B', 'C', ['A']),
    check_conditional_independence(df, 'B', 'D', ['A', 'C'])
])

match_DAG_b = all([
    check_conditional_independence(df, 'A', 'C', ['B', 'D']),
    check_conditional_independence(df, 'B', 'D', []),
    check_conditional_independence(df, 'B', 'C', [])
])

print("\nFinal Results:")
print("DAG (a) matches JPD:", match_DAG_a)
print("DAG (b) matches JPD:", match_DAG_b)