import json

def store_all_categories(category_list: dict):
    """
    Save categories to a JSON file in a structured format with single-line dish entries.

    Args:
        category_list (dict): A dictionary where keys are category names and values are lists of dish dictionaries.
    """
    organized_categories = {}

    for category, dishes in category_list.items():
        organized_dishes = []
        for dish in dishes:
            structured_dish = {
                "food_item": dish.get("dish_name", ""),
                "price": dish.get("dish_price", ""),
                "position_row": dish.get("row", 0),
                "position_col": dish.get("column", 0)
            }
            organized_dishes.append(structured_dish)

        organized_categories[category] = organized_dishes

    with open("category_data.json", "w") as file:
        file.write('{\n')
        first_category = True
        for category, dishes in organized_categories.items():
            if not first_category:
                file.write(',\n')
            first_category = False
            file.write(f'    "{category}": [\n')
            first_dish = True
            for dish in dishes:
                if not first_dish:
                    file.write(',\n')
                first_dish = False
                dish_str = json.dumps(dish, separators=(', ', ': '))
                file.write(f'        {dish_str}')
            file.write('\n    ]')
        file.write('\n}')
