from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
import json
import os
# from ../../models import BotUser
from api.models import People, Company, Friend


# from .Companies.json import HERITAGE_DATA, EVENT_DATA, USER_DATA, NEWS_DATA


class Command(BaseCommand):
    help = 'Sets up database with initial data.'

    def handle(self, *args, **options):
        with open("./api/management/commands/Companies.json") as company_file:
            companies_data = company_file.read()
        companies = json.loads(companies_data)

        with open("./api/management/commands/people.json") as people_file:
            people_data = people_file.read()
        people = json.loads(people_data)

        for company in companies:
            new_company = Company(**company)
            new_company.save()

        for person in people:
            # person = person.update({})
            employee_index = person.get("index")
            friends = person.pop('friends')
            friends_indices = []
            for friend in friends:
                if friend.get("index") != employee_index:
                    friends_indices.append(friend.get("index"))
            eye_color = person.pop('eyeColor')
            favouriteFood = person.pop('favouriteFood')
            person.pop('_id')
            fruit_list = [fruit.strip().lower() for fruit in open("./api/management/commands/fruits.txt", "r").readlines()]
            registered = "".join(person.pop('registered').split())
            favourite_fruit = []
            favourite_vegetable = []
            person.pop('about')
            for food in favouriteFood:
                if food.lower() in fruit_list:
                    favourite_fruit.append(food)
                else:
                    favourite_vegetable.append(food)
            new_person = People(eye_color=eye_color, favourite_fruit=favourite_fruit, registered=registered,
                                favourite_vegetable=favourite_vegetable, **person)
            new_person.save()
            friend_object = Friend(people_id=new_person, friends=friends_indices)
            friend_object.save()
