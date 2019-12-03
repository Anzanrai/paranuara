from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Company(models.Model):
    # id = models.AutoField(primary_key=True)
    index = models.IntegerField(unique=True, blank=False, null=False)
    company = models.CharField(verbose_name="company", blank=False, null=False, max_length=100)

    def __str__(self):
        return self.company+" "+str(self.index)


class People(models.Model):
    GENDER_CHOICES = [("male", "male"), ("female", "female")]
    # _id = models.UUIDField(primary_key=True)
    index = models.IntegerField(unique=True, blank=False, null=False)
    guid = models.UUIDField(blank=False, null=False)
    has_died = models.BooleanField(default=False, blank=False, null=False)
    balance = models.CharField(blank=False, null=False, max_length=20)
    age = models.IntegerField(blank=False, null=False)
    eye_color = models.CharField(blank=False, null=False, max_length=10)
    name = models.CharField(blank=False, null=False, max_length=50)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=6)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    email = models.EmailField(verbose_name="email", blank=False, null=False)
    phone = models.CharField(verbose_name="phone", blank=False, null=False, max_length=20)
    address = models.CharField(verbose_name="address", max_length=200)
    # about = models.CharField(max_length=1000)
    registered = models.DateTimeField(blank=False, null=False)
    tags = ArrayField(models.CharField(blank=True, null=True, max_length=30), size=30, blank=True, null=True)
    # friends = ArrayField(models.BigIntegerField(blank=True, null=True), blank=True, null=True)
    greeting = models.CharField(max_length=200)
    favourite_fruit = ArrayField(models.CharField(max_length=20, blank=True, null=True), size=20, blank=True, null=True)
    favourite_vegetable = ArrayField(models.CharField(max_length=20, blank=True, null=True), size=20, blank=True, null=True)
    picture = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return self.name + " " + str(self.id)


class Friend(models.Model):
    people_id = models.ForeignKey(People, on_delete=models.CASCADE, related_name='employee')
    friends = ArrayField(models.IntegerField(blank=True, null=True), blank=True, null=True)

    # def __str__(self):
    #     employee = People.objects.get(id=self.people_id)
    #     return employee.name + " " + str(self.people_id)