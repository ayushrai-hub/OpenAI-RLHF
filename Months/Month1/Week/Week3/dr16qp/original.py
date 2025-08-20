# Assume dr16qp is a predefined iterable of objects or dictionaries
dr16qp = [
    # Example elements with the necessary attributes
    {'SURVEY': 'eboss', 'PLATEQUALITY': 'good', 'Z': 2.05, 'BAL_PROB': 0.1},
    {'SURVEY': 'eboss', 'PLATEQUALITY': 'bad', 'Z': 2.05, 'BAL_PROB': 0.1},
    {'SURVEY': 'eboss', 'PLATEQUALITY': 'good', 'Z': 1.9, 'BAL_PROB': 0.1},
    {'SURVEY': 'eboss', 'PLATEQUALITY': 'good', 'Z': 2.05, 'BAL_PROB': 0.3},
    # Add more elements as needed
]

list_filtered = list(filter(lambda spec: spec['SURVEY'] == "eboss" and 
                                       spec['PLATEQUALITY'] == "good" and 
                                       2.0 < spec['Z'] < 2.1 and 
                                       spec['BAL_PROB'] < 0.2, dr16qp))

print(list_filtered)
