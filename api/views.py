from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.models import Company, People, Friend
from api.serializers import CompanySerializer, CompanyEmployeeSerializer, CommonFriendSerializer, FriendSerializer, \
    EmployeeSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    # queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def get_queryset(self):
        if self.request.method == 'GET':
            return Company.objects.all()


class EmployeeViewSet(viewsets.ModelViewSet):

    def get_serializer_class(self):
        if self.request.query_params.get('company'):
            return CompanyEmployeeSerializer
        if self.request.query_params.get('employee'):
            return EmployeeSerializer

    # serializer_class = CompanyEmployeeSerializer

    def get_queryset(self):
        if self.request.method == 'GET':
            if self.request.query_params.get('company'):
                return People.objects.filter(company__id=self.request.query_params.get('company'))
            if self.request.query_params.get('employee'):
                return People.objects.filter(id=self.request.query_params.get('employee'))
            return People.objects.all()


@api_view(['GET'])
def common_friend_view(request):
    employee_one_param = request.query_params.get('employee_one')
    employee_two_param = request.query_params.get('employee_two')
    try:
        employee_one = People.objects.get(id=employee_one_param)
        employee_two = People.objects.get(id=employee_two_param)
        employee_one_friend = Friend.objects.get(people_id__id=employee_one_param)
        employee_one_friend_indices = set(employee_one_friend.friends)
        employee_two_friend = Friend.objects.get(people_id__id=employee_two_param)
        employee_two_friend_indices = set(employee_two_friend.friends)
        common_friends = People.objects.filter(index__in=list(
            employee_one_friend_indices.intersection(employee_two_friend_indices)))
        common_friends_data = FriendSerializer(common_friends, many=True).data
    except ObjectDoesNotExist as e:
        return Response({'error': "Requested employee data not found"})
    return Response({'employee_one': CommonFriendSerializer(employee_one).data,
                     'employee_two': CommonFriendSerializer(employee_two).data,
                     'common_friends': common_friends_data})