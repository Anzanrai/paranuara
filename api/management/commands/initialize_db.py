from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
import json
import os
# from ../../models import BotUser
from django.db import transaction

from api.models import People, Company, Friend


# from .Companies.json import HERITAGE_DATA, EVENT_DATA, USER_DATA, NEWS_DATA
from api.utils import categorize_food


class Command(BaseCommand):
    help = 'Sets up database with initial data.'
    data_path = "./api/management/commands/data/"

    def handle(self, *args, **options):
        with open(self.data_path+"Companies.json") as company_file:
            companies_data = company_file.read()
        companies = json.loads(companies_data)

        with open(self.data_path+"people.json") as people_file:
            people_data = people_file.read()
        people = json.loads(people_data)

        for company in companies:
            new_company = Company(**company)
            new_company.save()

        for person in people:
            # person = person.update({})
            with transaction.atomic():
                employee_index = person.get("index")
                friends_indices = []
                if person.get('friends'):
                    friends = person.pop('friends')

                    for friend in friends:
                        if friend.get("index") != employee_index:
                            friends_indices.append(friend.get("index"))

                if person.get('eyeColor'):
                    eye_color = person.pop('eyeColor')
                if person.get('favouriteFood'):
                    favourite_food = person.pop('favouriteFood')
                # categorize food into fruits and vegetables using util function.
                favourite_fruit, favourite_vegetable = categorize_food(favourite_food)
                registered = "".join(person.pop('registered').split())
                if person.get('about'):
                    person.pop('about')
                new_person = People(eye_color=eye_color, favourite_fruit=favourite_fruit, registered=registered,
                                    favourite_vegetable=favourite_vegetable, **person)
                new_person.save()
                friend_object = Friend(people_id=new_person.guid, friends=friends_indices)
                friend_object.save()
