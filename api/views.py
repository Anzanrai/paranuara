import copy
import json

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.models import Company, People, Friend
from api.serializers import CompanySerializer, CompanyEmployeeSerializer, CommonFriendSerializer, FriendSerializer, \
    EmployeeSerializer, FriendModelPostSerializer, CompanyEmployeePostSerializer
from api.utils import categorize_food


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(data={'body': ['Company added successfully.'], 'company': serializer.data}, status=status.HTTP_201_CREATED,
                            headers=headers)
        else:
            errors = serializer.errors
            if 'index' in errors:
                if request.data.get('index'):
                    errors.update({'index': [str(request.data.get('index'))+' index value already exist.']})
                else:
                    errors.update({'index': ['Index field not provided.']})
            return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(data={'body': ['Company updated successfully.']}, status=status.HTTP_200_OK, headers=headers)
        else:
            errors = serializer.errors
            if request.data.get('index'):
                errors.update({'index': [str(request.data.get('index')) + ' index value already exist.']})
            return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeViewSet(viewsets.ModelViewSet):
    lookup_field = 'guid'

    def get_serializer_class(self):
        if self.request.query_params.get('employee'):
            return EmployeeSerializer
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return CompanyEmployeePostSerializer
        return CompanyEmployeeSerializer

    def get_queryset(self):
        if self.request.method == 'GET':
            if self.request.query_params.get('company'):
                return People.objects.filter(company__id=self.request.query_params.get('company'))
            if self.request.query_params.get('employee'):
                return People.objects.filter(id=self.request.query_params.get('employee'))
            return People.objects.all()

    def create(self, request, *args, **kwargs):
        data = copy.deepcopy(request.data)
        serializer = self.get_serializer(data=data)
        with transaction.atomic():
            if serializer.is_valid():
                self.perform_create(serializer)
                friends_data = json.loads(data['friends'])
                data.pop('friends')
                friends = []
                for friend_data in friends_data:
                    if friend_data.get('index') != serializer.data['index']:
                        friends.append(friend_data.get('index'))
                friend_serializer = FriendModelPostSerializer(data={'people_id': serializer.data.get('guid'), 'friends': friends})
                if friend_serializer.is_valid():
                    self.perform_create(friend_serializer)
                    return Response(data={'body': ['Employee added successfully.'], 'employee': serializer.data},
                                    status=status.HTTP_201_CREATED)
                else:
                    serializer.errors.update(friend_serializer.errors)
            else:
                errors = serializer.errors
                return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        data = copy.deepcopy(request.data)
        # serializer = self.get_serializer(data=data)
        instance = People.objects.get(guid=self.kwargs.pop('guid'))
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        with transaction.atomic():
            if serializer.is_valid():
                self.perform_update(serializer)
                if data.get('friends'):
                    friend_instance = Friend.objects.get(people_id=serializer.data.get('guid'))
                    friends_data = json.loads(data['friends'])
                    data.pop('friends')
                    friends = []
                    for friend_data in friends_data:
                        if friend_data.get('index') != serializer.data['index']:
                            friends.append(friend_data.get('index'))
                    friend_serializer = FriendModelPostSerializer(friend_instance, data={'friends': friends},
                                                                  partial=True)
                    if friend_serializer.is_valid():
                        self.perform_update(friend_serializer)
                    else:
                        serializer.errors.update(friend_serializer.errors)
                        return Response(data=friend_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                headers = self.get_success_headers(serializer.data)
                return Response(data={'body': ['Employee updated successfully.'], 'employee': serializer.data,
                                      'friends': friend_serializer.data}, status=status.HTTP_200_OK, headers=headers)
            else:
                errors = serializer.errors
                if request.data.get('index'):
                    errors.update({'index': [str(request.data.get('index')) + ' index value already exist.']})
                return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)


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