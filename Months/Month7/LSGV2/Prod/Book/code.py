import requests

# We will define a helper to search for a food term and return the magnesium mg per 100g
def find_food_mg(query):
    url = 'https://api.nal.usda.gov/fdc/v1/foods/search'
    params = {'query': query, 'api_key': 'DEMO_KEY', 'pageSize': 50}
    r = requests.get(url, params=params)
    foods = r.json()['foods']
    # filter for "Survey (FNDDS)" if possible, else any
    candidates = []
    for f in foods:
        desc = f['description']
        dataType = f['dataType']
        mg = None
        for nut in f.get('foodNutrients', []):
            if nut['nutrientName'] == 'Magnesium, Mg':
                mg = nut['value']
        candidates.append((f['fdcId'], dataType, desc, mg))
    # sort by mg descending
    candidates.sort(key=lambda x: (x[3] if x[3] is not None else -1), reverse=True)
    return candidates[:5]

# Now test for each
foods_to_find = ['Cashews, dry roasted', 'Almonds, dry roasted', 'Dark chocolate 70', 'Quinoa, uncooked', 'Peanut butter', 'Spinach, cooked']
for q in foods_to_find:
    print(q, find_food_mg(q))

