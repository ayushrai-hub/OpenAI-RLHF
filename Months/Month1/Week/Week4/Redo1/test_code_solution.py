
import pandas as pd
from itertools import product

# Given JPD
data = {
    'A': [True, True, True, True, True, True, True, True, False, False, False, False, False, False, False, False],
    'B': [True, True, True, True, False, False, False, False, True, True, True, True, False, False, False, False],
    'C': [True, True, False, False, True, True, False, False, True, True, False, False, True, True, False, False],
    'D': [True, False, True, False, True, False, True, False, True, False, True, False, True, False, True, False],
    'P': [0.014, 0.042, 0.0126, 0.0714, 0.056, 0.168, 0.0504, 0.2856, 0.00375, 0.01125, 0.02025, 0.11475, 0.00375, 0.01125, 0.02025, 0.11475]
}

df = pd.DataFrame(data)

def marginal_probability(df, variable):
    return df.groupby(variable)['P'].sum().to_dict()

def joint_probability(df, variables):
    if not variables:
        return df['P'].sum()
    return df.groupby(variables)['P'].sum().to_dict()

def conditional_probability(joint, marginal, given_var):
    cond_prob = {}
    for key in joint:
        given_key = key if isinstance(key, tuple) else (key,)
        cond_prob[key] = joint[key] / marginal[given_key[given_var]]
    return cond_prob

# Check independence conditions
def check_conditional_independence(df, var1, var2, given):
    joint_vars = [var1, var2] + given
    joint_probs = joint_probability(df, joint_vars)
    marginals_given = joint_probability(df, given)
    marginals_var1_given = joint_probability(df, [var1] + given)
    marginals_var2_given = joint_probability(df, [var2] + given)

    independent = True
    for values in product([True, False], repeat=len(joint_vars)):
        key_joint = tuple(values)
        key_given = tuple(values[2:]) if given else ()
        key_var1_given = tuple(values[:1] + values[2:]) if given else (values[0],)
        key_var2_given = tuple(values[1:2] + values[2:]) if given else (values[1],)
        
        p_joint = joint_probs.get(key_joint, 0)
        p_var1_given = marginals_var1_given.get(key_var1_given, 0)
        p_var2_given = marginals_var2_given.get(key_var2_given, 0)
        p_given = marginals_given if not given else marginals_given.get(key_given, 0)
        
        if p_given > 0:  # Avoid division by zero
            if abs(p_joint - p_var1_given * p_var2_given / p_given) > 1e-6:
                independent = False
                break

    return independent

# DAG a checks
independence_a1 = check_conditional_independence(df, 'B', 'C', ['A'])  # B ⊥ C | A
independence_a2 = check_conditional_independence(df, 'B', 'D', ['A', 'C'])  # B ⊥ D | A, C

# DAG b checks
independence_b1 = check_conditional_independence(df, 'A', 'C', ['B', 'D'])  # A ⊥ C | B, D
independence_b2 = check_conditional_independence(df, 'B', 'D', [])  # B ⊥ D
independence_b3 = check_conditional_independence(df, 'B', 'C', [])  # B ⊥ C

# Determine which DAG matches the JPD
match_DAG_a = independence_a1 and independence_a2
match_DAG_b = independence_b1 and independence_b2 and independence_b3

print("DAG a matches JPD:", match_DAG_a)
print("DAG b matches JPD:", match_DAG_b)
