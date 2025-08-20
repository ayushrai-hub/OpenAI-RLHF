# ideal_completion.py

def filter_people_by_age(collection_of_stuff, age_threshold):
    return [stuff for stuff in collection_of_stuff if stuff.get("age") and isinstance(stuff["age"], (int, float)) and stuff["age"] > age_threshold]


def main():
    collection_of_stuff = [
        {"name": "Anna", "age": 28},
        {"name": "Dave", "age": 32},
        {"name": "Ella", "age": 40}
    ]

    result = filter_people_by_age(collection_of_stuff, 30)

    for stuff in result:
        print(f"{stuff['name']} is more than 30 years old.")


if __name__ == "__main__":
    main()