import json

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import Company, People, Friend
from api.utils import categorize_food


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class CompanyEmployeePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = People
        exclude = ['favourite_fruit', 'favourite_vegetable', 'tags']
        # fields = '__all__'

    def create(self, validated_data):
        data = validated_data
        if self.initial_data.get('favouriteFood'):
            data['favourite_fruit'], data['favourite_vegetable'] = categorize_food(self.initial_data.get('favouriteFood'))
        if self.initial_data.get('tags'):
            data['tags'] = json.loads(self.initial_data.get('tags'))
        # data['favourite_fruit'] = self.initial_data['favourite_fruit']
        # data['favourite_vegetable'] = self.initial_data['favourite_vegetable']
        return super(CompanyEmployeePostSerializer, self).create(data)
        # super(CompanyEmployeeSerializer, self).create(data)


class CompanyEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = People
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = People
        fields = ['name', 'age', 'favourite_fruit', 'favourite_vegetable']


class FilteredListSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        data = data.filter(eye_color="brown", has_died=False)
        return super().to_representation(data)


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = People
        fields = ['name', 'eye_color', 'has_died']
        list_serializer_class = FilteredListSerializer


class CommonFriendSerializer(serializers.ModelSerializer):
    # friends = FriendSerializer(many=True)

    class Meta:
        model = People
        fields = ['name', 'age', 'address', 'phone']


class FriendModelPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = ['people_id', 'friends']

    def validate(self, attrs):
        data = self.initial_data
        for friend in data['friends']:
            try:
                People.objects.get(index=friend)
            except ObjectDoesNotExist:
                raise ValidationError({friend: 'Index '+str(friend)+' provided as friend index does not exist'})
        return attrs
