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
    # registered = serializers.DateTimeField()

    class Meta:
        model = People
        exclude = ['favourite_fruit', 'favourite_vegetable', 'tags', 'eye_color', 'registered', 'company']
        # fields = '__all__'

    def validate(self, attrs):
        if self.initial_data.get('eyeColor', ''):
            attrs['eye_color'] = self.initial_data.get('eyeColor')
        if self.initial_data.get('company_id', ''):
            attrs['company'] = Company.objects.get(id=self.initial_data['company_id'])
        if self.initial_data.get('registered', ''):
            attrs['registered'] = "".join(self.initial_data.get("registered").split())
        return attrs

    # def validate_registered(self, value):
    #     return "".join(value.split())

    def create(self, validated_data):
        data = validated_data
        if self.initial_data.get('favouriteFood'):
            data['favourite_fruit'], data['favourite_vegetable'] = categorize_food(self.initial_data.get('favouriteFood'))
        if self.initial_data.get('tags'):
            if isinstance(self.initial_data.get('tags'), str):
                data['tags'] = json.loads(self.initial_data.get('tags'))
            else:
                data['tags'] = self.initial_data.get('tags')
        # if self.initial_data.get('eyeColor'):
        #     data['eye_color'] = self.initial_data.get('eyeColor')
        # data['favourite_fruit'] = self.initial_data['favourite_fruit']
        # data['favourite_vegetable'] = self.initial_data['favourite_vegetable']
        return super(CompanyEmployeePostSerializer, self).create(data)
        # super(CompanyEmployeeSerializer, self).create(data)


class CompanyEmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = People
        fields = '__all__'

    def to_representation(self, instance):
        representation = super(CompanyEmployeeSerializer, self).to_representation(instance)
        friend_instance = Friend.objects.get(people_id=instance.pk)
        friends = []
        for friend in friend_instance.friends:
            friends.append({"index": friend})
        representation["friends"] = friends
        return representation


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
