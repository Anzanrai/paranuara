from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import Company, People


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


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