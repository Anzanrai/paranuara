import json


def url_id_gen():
    import string
    import random
    from hashlib import sha256
    choice = "".join(random.choice(string.ascii_letters+string.digits) for n in range(24))
    choice = sha256(choice.encode()).hexdigest()
    return choice[:24]


def categorize_food(foods):
    if type(foods) == str:
        foods = json.loads(foods)
    fruits = []
    vegetables = []
    fruits_data = [fruit.strip().lower() for fruit in open("./api/management/commands/data/fruits.txt", "r").readlines()]

    for food in foods:
        if food.lower() in fruits_data:
            fruits.append(food)
        else:
            vegetables.append(food)
    return fruits, vegetables