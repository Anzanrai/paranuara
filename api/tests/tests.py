import json

from django.db import transaction
from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Company, People, Friend
from api.utils import categorize_food


class CompanyApiTestCase(APITestCase):
    def setUp(self):
        company_data = [
            {
                "index": 0,
                "company": "Test Company 0"
            },
            {
                "index": 1,
                "company": "Test Company 1"
            }
        ]
        for company in company_data:
            Company.objects.create(**company)

    def test_001_company_api_200_on_creation(self):
        company_data = {
            "index": 2,
            "company": "Test Company 2"
        }
        url = reverse('company-list')
        response = self.client.post(url, company_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Company.objects.count(), 3)

    def test_002_company_api_400_on_creation_with_faulty_data(self):
        companies_data = [
            {
                "index": 1,
                "company": "Company with faulty index"
            },
            {
                "index": 2,
                "company": ""
            },
            {
                "index": None,
                "company": "Company with null index"
            }
        ]
        url = reverse('company-list')
        for company_data in companies_data:
            response = self.client.post(url, company_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(Company.objects.count(), 2)

    def test_003_company_api_200_on_requesting_existing_company_data(self):
        url = reverse('company-list')
        company_data = {
            "index": 2,
            "company": "Newly created company"
        }
        response = self.client.post(url, company_data, format='json')
        company_id = response.data.get('body').get('id')
        url = "/api/company/"+str(company_id)+"/"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'id': company_id, 'index': 2, 'company': "Newly created company"})

    def test_004_company_api_404_on_requesting_non_existing_data(self):
        url = "/api/company/101/"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_005_company_api_200_on_update_with_valid_data(self):
        company_id = Company.objects.get(index=0).id
        url = "/api/company/"+str(company_id)+"/"
        new_data = {
            "index": 5,
            "company": "Test Company with new name"
        }
        response = self.client.put(url, new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_006_company_api_400_on_update_with_faulty_data(self):
        company_id = Company.objects.get(index=1).id
        url = "/api/company/"+str(company_id)+"/"
        new_data = [
            {
                "index": 0,
                "company": "Company with faulty index"
            },
            {
                "index": None,
                "company": "Company with null index"
            }
        ]
        for data in new_data:
            response = self.client.put(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_007_company_api_successful_deletion(self):
        company_id = Company.objects.get(index=1).id
        url = "/api/company/"+str(company_id)+"/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_008_company_api_404_on_deletion_of_non_existing_company(self):
        company_id = Company.objects.get(index=1).id + 100
        url = "/api/company/"+str(company_id)+"/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class EmployeeAPITestCase(APITestCase):
    data_path = "./api/tests/data/"

    def setUp(self):
        company = Company.objects.create(**{'index': 0, "company": "Test Company 0"})
        employee_data = {
            "index": 0,
            "has_died": False,
            "balance": "$1,562.58",
            "age": 60,
            "eye_color": "brown",
            "name": "Decker Mckenzie",
            "gender": "male",
            "company": company,
            "email": "deckermckenzie@earthmark.com",
            "phone": "+1 (893) 587-3311",
            "address": "492 Stockton Street, Lawrence, Guam, 4854",
            "registered": "2017-06-25T10:03:49-10:00",
            "tags": ["veniam", "irure", "mollit", "sunt", "amet", "fugiat", "ex"],
            "greeting": "Hello, Decker Mckenzie! You have 2 unread messages.",
            "favourite_fruit": ["cucumber"],
            "favourite_vegetable": ["beetroot", "carrot", "celery"]
        }
        people = People.objects.create(**employee_data)
        friend_data = {
            "people_id": people.guid,
            "friends": []
        }
        Friend.objects.create(**friend_data)

    def test_001_employee_api_201_on_successful_creation(self):
        with open(self.data_path+"people.json") as people_file:
            people_data = people_file.read()
        employees_data = json.loads(people_data)
        company = Company.objects.get(index=0).id
        url = reverse('employees-list')
        for employee in employees_data:
            employee.update({'company_id': company})
            response = self.client.post(url, employee, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_002_employee_api_400_on_faulty_input_data(self):
        with open(self.data_path+"badPeople.json") as people_file:
            people_data = people_file.read()
        employees_data = json.loads(people_data)
        company = Company.objects.get(index=0).id
        url = reverse('employees-list')
        for employee in employees_data:
            employee.update({'company_id': company})
            response = self.client.post(url, employee, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_003_employee_api_200_on_successful_data_retrieve(self):
        people = People.objects.get(index=0)
        url = "/api/employees/"+str(people.guid)+"/"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_004_employee_api_404_on_request_for_non_existing_employee(self):
        url = "/api/employees/123/"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_005_employee_api_200_on_update_with_valid_data(self):
        employee_data = {
            "has_died": True,
            "balance": "$0",
            "age": 65,
            "name": "Decker Mckenzie",
            "gender": "female",
        }
        employee = People.objects.get(index=0)
        url = "/api/employees/"+str(employee.guid)+"/"
        response = self.client.put(url, employee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_006_employee_api_200_on_requesting_company_employee(self):
        company_id = Company.objects.get(index=0).id
        url = "/api/employees/?company="+str(company_id)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_007_employee_api_200_on_requesting_employee_with_index(self):
        url = "/api/employees/?employee=0"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CommonFriendApiTestCase(TestCase):
    data_path = "./api/tests/data/"
        
    def setUp(self):
        company = Company.objects.create(**{'index': 0, "company": "Test Company 0"})
        employee_data = {
            "index": 0,
            "has_died": False,
            "balance": "$1,562.58",
            "age": 60,
            "eye_color": "brown",
            "name": "Decker Mckenzie",
            "gender": "male",
            "company": company,
            "email": "deckermckenzie@earthmark.com",
            "phone": "+1 (893) 587-3311",
            "address": "492 Stockton Street, Lawrence, Guam, 4854",
            "registered": "2017-06-25T10:03:49-10:00",
            "tags": ["veniam", "irure", "mollit", "sunt", "amet", "fugiat", "ex"],
            "greeting": "Hello, Decker Mckenzie! You have 2 unread messages.",
            "favourite_fruit": ["cucumber"],
            "favourite_vegetable": ["beetroot", "carrot", "celery"]
        }
        people = People.objects.create(**employee_data)
        friend_data = {
            "people_id": people.guid,
            "friends": []
        }
        Friend.objects.create(**friend_data)
        with open(self.data_path+"people.json") as people_file:
            people_data = people_file.read()
        employees_data = json.loads(people_data)
        company = Company.objects.get(index=0).id
        url = reverse('employees-list')
        for person in employees_data:
            # person = person.update({})
            with transaction.atomic():
                employee_index = person.get("index")
                friends = person.pop('friends')
                friends_indices = []
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
                new_person = People(eye_color=eye_color, favourite_fruit=favourite_fruit, registered=registered,
                                    favourite_vegetable=favourite_vegetable, **person)
                new_person.save()
                friend_object = Friend(people_id=new_person.guid, friends=friends_indices)
                friend_object.save()

    def test_001_common_friends_api_200_on_successful_data_retrieval(self):
        url = "/api/common-friends/?employee_one=2&employee_two=3"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CompanyModelTestCase(TestCase):
    def setUp(self):
        Company.objects.create(index=0, company="Test Company 0")
        Company.objects.create(index=1, company="Test Company 1")

    def test_001_get_company_object_successfully(self):
        """Should be able to get company object successfully that exists in db"""
        company0 = Company.objects.get(index=0)
        company1 = Company.objects.get(index=1)
        self.assertEqual(company0.index, 0)
        self.assertEqual(company0.company, "Test Company 0")
        self.assertEqual(company1.index, 1)
        self.assertEqual(company1.company, "Test Company 1")
        self.assertEqual(Company.objects.count(), 2)

    def test_002_create_company_object_successfully(self):
        data = {
            "index": 2,
            "company": "Test Company 2"
        }
        recently_created_company = Company.objects.create(**data)
        self.assertEqual(Company.objects.count(), 3)
        self.assertEqual(recently_created_company.index, data.get('index'))
        self.assertEqual(recently_created_company.company, data.get('company'))
        self.assertTrue(isinstance(recently_created_company, Company))


class PeopleModelTestCase(TestCase):
    def setUp(self):
        companies_data = [
            {
                "index": 0,
                "company": "Test Company 0"
            },
            {
                "index": 1,
                "company": "Test Company 1"
            },
        ]
        for company_data in companies_data:
            Company.objects.create(**company_data)

        employee_data = {
            "index": 1,
            "has_died": False,
            "balance": "$1,562.58",
            "age": 60,
            "eye_color": "brown",
            "name": "Decker Mckenzie",
            "gender": "male",
            "company": Company.objects.get(index=1),
            "email": "deckermckenzie@earthmark.com",
            "phone": "+1 (893) 587-3311",
            "address": "492 Stockton Street, Lawrence, Guam, 4854",
            "registered": "2017-06-25T10:03:49-10:00",
            "tags": ["veniam", "irure", "mollit", "sunt", "amet", "fugiat", "ex"],
            "greeting": "Hello, Decker Mckenzie! You have 2 unread messages.",
            "favourite_fruit": ["cucumber"],
            "favourite_vegetable": ["beetroot", "carrot", "celery"]
        }
        People.objects.create(**employee_data)

    def test_001_successful_employee_creation(self):
        company_instance = Company.objects.get(index=1)
        employee_data = {
            "index": 0,
            "has_died": True,
            "balance": "$2,418.59",
            "age": 61,
            "eye_color": "blue",
            "name": "Carmella Lambert",
            "gender": "female",
            "company": company_instance,
            "email": "carmellalambert@earthmark.com",
            "phone": "+1 (910) 567-3630",
            "address": "628 Sumner Place, Sperryville, American Samoa, 9819",
            "registered": "2016-07-13T12:29:07-10:00",
            "tags": ["id", "quis", "ullamco", "consequat", "laborum", "sint", "velit"],
            "greeting": "Hello, Carmella Lambert! You have 6 unread messages.",
            "favourite_fruit": ["orange", "apple", "banana", "strawberry"],
            "favourite_vegetable": [],
        }
        employee = People.objects.create(**employee_data)
        self.assertTrue(isinstance(employee, People))

    def test_002_retrieve_employee_data_from_db(self):
        created_employee = People.objects.get(index=1)
        self.assertEqual(created_employee.name, "Decker Mckenzie")
        self.assertEqual(created_employee.email, "deckermckenzie@earthmark.com")